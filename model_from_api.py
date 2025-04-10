from openai import AsyncOpenAI
from dotenv import load_dotenv, find_dotenv
import os
import asyncio
from aioconsole import ainput
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json
from typing import Optional, Dict
from contextlib import AsyncExitStack
from datetime import datetime
from utils import get_now_datetime


load_dotenv(find_dotenv())

class APIChatModel:

    def __init__(self,
            base_model="deepseek-chat",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_KEY_URL"),
            system_prompt="",
            temperature=1.0,
            top_p=0.8,
            max_new_tokens=128,
            repetition_penalty=1.2,
            role="kurisu"
        ):

        self.client = AsyncOpenAI(  # 使用异步客户端
            api_key=api_key,
            base_url=base_url
        )
        self.model = base_model
        self.temperature = temperature
        self.top_p = top_p
        self.max_new_tokens = max_new_tokens
        self.repetition_penalty = repetition_penalty
        self.language = "中文"
        self.system_prompt = system_prompt
        self.role = role
        self.sys_prompt_dic = {
            "kurisu": {
                "中文": r"./system_prompts/Kurisu_sys_prompt_ZH.txt",
                "粤语": r"./system_prompts/Kurisu_sys_prompt_ZH.txt",
                "英文": r"./system_prompts/Kurisu_sys_prompt_EN.txt",
                "日文": r"./system_prompts/Kurisu_sys_prompt_JP.txt",
                "中英混合": r"./system_prompts/Kurisu_sys_prompt_ZH.txt",
                "日英混合": r"./system_prompts/Kurisu_sys_prompt_JP.txt",
                "多语种混合": r"./system_prompts/Kurisu_sys_prompt_ZH.txt"
            },
            "2b":{
                "中文": r"./system_prompts/2B_sys_prompt_ZH.txt",
                "粤语": r"./system_prompts/2B_sys_prompt_ZH.txt",
                "英文": r"./system_prompts/2B_sys_prompt_EN.txt",
                "日文": r"./system_prompts/2B_sys_prompt_JP.txt",
                "中英混合": r"./system_prompts/2B_sys_prompt_ZH.txt",
                "日英混合": r"./system_prompts/2B_sys_prompt_JP.txt",
                "多语种混合": r"./system_prompts/2B_sys_prompt_ZH.txt"
            }
        }
    
        self.exit_stack = AsyncExitStack()
        # 存储 (server_name -> MCP ClientSession) 映射
        self.sessions: Dict[str, ClientSession] = {}
        # 存储工具信息
        self.tools_by_session: Dict[str, list] = {}  # 每个 session 的 tools 列表
        self.all_tools = []  # 合并所有工具的列表
        
        

    async def post_init(self):
        # 服务器脚本
        servers = {
            # "write": "./mcp-server/write_server.py",
            "WeatherServer": "./mcp-server/Weather_server.py",
            # "SQLServer": "./mcp-server/SQL_server.py",
            "PythonServer": "./mcp-server/Python_server.py",
            "EmailServer": "./mcp-server/Email_server.py"
        }
    
        try:
            await self.connect_to_servers(servers)
            # await self.chat_loop()
        except Exception as e:
            print("post_init报错: ", e)

    async def chat_with_history(self, query, history=[]):
        # def build_multiturn_prompt(history, query):
        #     messages = [{"role": "system", "content": self.system_prompt}]
        #     for message_dict in history:
        #         messages += [message_dict]
        #     messages += [{"role": "user", "content": query}]
        #     return messages
        
        # messages = build_multiturn_prompt(history, query)

        # response = await self.chat_completion(messages)  # 异步等待响应
        # response = response.choices[0].message.content.replace("\n\n","")

        ## 这一步是否重复加入了user记录？
        # history.extend([
        #     {"role": "user", "content": query},
        #     {"role": "assistant", "content": response}
        # ])

        ## 改成这样赋值
        # history.append({"role": "assistant", "content": response}) 
        # return history, response

        try:
            history.append({"role": "user", "content": "(" + str(await get_now_datetime())+") user:" + query})
            # print(messages)
            response = await self.chat_base(history.copy())
            result = response.choices[0].message.content.replace("\n\n","")

            # history[-1]["content"] = "(" + str(await get_now_datetime())+") " + history[-1]["content"]
            history.append({"role": "assistant", "content": result})

        except Exception as e:
            print(f"\nchat_with_history调用过程出错: {e}")
            return history, ""
        
        return history, result




    def set_model_language(self, language="中文"):
        self.language = language
        with open(self.sys_prompt_dic[self.role][language], "r", encoding="utf-8") as f:
            self.system_prompt = "".join(f.readlines()) + self.system_prompt

    async def chat_completion(self, messages):  # 异步方法
        res = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_new_tokens,
            frequency_penalty=self.repetition_penalty,
        )
        return res

    # 以下是mcp-client相关函数

    async def connect_to_servers(self, servers: dict):
        """
        同时启动多个服务器并获取工具
        servers: 形如 {"weather": "weather_server.py", "rag": "rag_server.py"}
        """
        for server_name, script_path in servers.items():
            session = await self._start_one_server(script_path)
            self.sessions[server_name] = session
            # 列出此服务器的工具
            resp = await session.list_tools()
            self.tools_by_session[server_name] = resp.tools  # 保存到对应 session
            for tool in resp.tools:
                # OpenAI Function Calling 格式修正
                function_name = f"{server_name}_{tool.name}"
                # print(tool.name)
                self.all_tools.append({
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema
                    }
                })

        # 转化 function calling 格式
        self.all_tools = await self.transform_json(self.all_tools)
        # print(self.all_tools)
        print("\n✅ 已连接到下列服务器:")
        for name in servers:
            print(f" - {name}: {servers[name]}")
        print("\n汇总的工具:")
        for t in self.all_tools:
            print(f" - {t['function']['name']}")

    async def transform_json(self, json2_data):
        """
        将类似 json2 的格式转换为类似 json1 的格式，多余字段会被直接删除。
        :param json2_data: 一个可被解释为列表的 Python 对象（或已解析的 JSON 数据）
        :return: 转换后的新列表
        """
        result = []
        for item in json2_data:
            # 确保有 "type" 和 "function" 两个关键字段
            if not isinstance(item, dict) or "type" not in item or "function" not in item:
                continue
            old_func = item["function"]
            # 确保 function 下有我们需要的关键子字段
            if not isinstance(old_func, dict) or "name" not in old_func or "description" not in old_func:
                continue
            # 处理新 function 字段
            new_func = {
                "name": old_func["name"],
                "description": old_func["description"],
                "parameters": {}
            }
            # 读取 input_schema 并转成 parameters
            if "input_schema" in old_func and isinstance(old_func["input_schema"], dict):
                old_schema = old_func["input_schema"]
                # 新的 parameters 保留 type, properties, required 这三个字段
                new_func["parameters"]["type"] = old_schema.get("type", "object")
                new_func["parameters"]["properties"] = old_schema.get("properties", {})
                new_func["parameters"]["required"] = old_schema.get("required", [])
            new_item = {
                "type": item["type"],
                "function": new_func
            }
            result.append(new_item)
        return result

    async def _start_one_server(self, script_path: str) -> ClientSession:
        """启动单个 MCP 服务器子进程，并返回 ClientSession"""
        is_python = script_path.endswith(".py")
        is_js = script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("服务器脚本必须是 .py 或 .js 文件")
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[script_path],
            env=None
        )
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read_stream, write_stream = stdio_transport
        session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await session.initialize()
        return session

    async def chat_base(self, messages: list) -> list:
        # messages = [{"role": "user", "content": query}]
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.all_tools
        )

        if response.choices[0].finish_reason == "tool_calls":
            
            for _ in range(10): # 限制重试次数
                messages = await self.create_function_response_messages(
                    messages, response
                )
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.all_tools
                )
                if response.choices[0].finish_reason != "tool_calls":
                    break

        # return response.choices[0].message.content
        return response

    async def create_function_response_messages(self, messages, response):
        function_call_messages = response.choices[0].message.tool_calls
        messages.append(response.choices[0].message.model_dump())
        for function_call_message in function_call_messages:
            tool_name = function_call_message.function.name
            tool_args = json.loads(function_call_message.function.arguments)
            # 运行外部函数
            function_response = await self._call_mcp_tool(tool_name, tool_args)
            # 拼接消息队列
            messages.append({
                "role": "tool",
                "content": function_response[0].text,
                "tool_call_id": function_call_message.id,
            })
        return messages

    async def process_query(self, user_query: str) -> str:
        """
        OpenAI 最新 Function Calling 逻辑:
        1. 发送用户消息 + tools 信息
        2. 若模型 `finish_reason == "tool_calls"`，则解析 toolCalls 并执行相应 MCP 工具
        3. 把调用结果返回给 OpenAI，让模型生成最终回答
        """
        messages = [{"role": "user", "content": user_query}]
        # 第一次请求
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.all_tools
        )
        content = response.choices[0]
        print(content)
        print(self.all_tools)
        # 如果模型调用了 MCP 工具
        if content.finish_reason == "tool_calls":
            # 解析 tool_calls
            tool_call = content.message.tool_calls[0]
            tool_name = tool_call.function.name  # 形如 "weather_query_weather"
            tool_args = json.loads(tool_call.function.arguments)
            print(f"\n[ 调用工具: {tool_name}, 参数: {tool_args} ]\n")
            # 执行 MCP 工具
            result = await self._call_mcp_tool(tool_name, tool_args)

            # 把工具调用历史写进 messages
            messages.append(content.message.model_dump())
            messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call.id,
            })
            # 第二次请求，让模型整合工具结果，生成最终回答
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        # 如果模型没调用工具，直接返回回答
        return content.message.content

    async def _call_mcp_tool(self, tool_full_name: str, tool_args: dict) -> str:
        """
        根据 "serverName_toolName" 调用相应的服务器工具
        """
        parts = tool_full_name.split("_", 1)  # 拆分 "weather_query_weather" -> ["weather", "query_weather"]
        if len(parts) != 2:
            return f"无效的工具名称: {tool_full_name}"
        server_name, tool_name = parts
        session = self.sessions.get(server_name)
        if not session:
            return f"找不到服务器: {server_name}"
        # 执行 MCP 工具
        resp = await session.call_tool(tool_name, tool_args)
        print(f"{resp}\n")
        return resp.content if len(resp.content) > 0 else "工具执行无输出"

    async def cleanup(self):
        try:
            # 确保 AsyncExitStack 被正确关闭
            await self.exit_stack.aclose()
        except Exception as e:
            print(f"Cleanup error: {e}")



async def handle_inputs(model, query, history):
    history, response = await model.chat_with_history(query, history)
    print(response)
    
    
async def main():
    model = APIChatModel(role="2b", system_prompt="")
    model.set_model_language("中文")
    await model.post_init()

    # 这里历史记录改成了提前传入系统提示词
    history = [{"role": "system", "content": model.system_prompt}]

    while True:
        query = await ainput(">> ")  # 异步输入
        if query.lower() == "exit":
            # 这里要执行清理
            await model.cleanup()
            break
        asyncio.create_task(handle_inputs(model, query, history))
    print(history)   

if __name__ == "__main__":
    asyncio.run(main())  # 运行异步主函数