from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import asyncio
from aioconsole import ainput

load_dotenv("./.env")

class APIChatModel:

    def __init__(self,
            base_model="GLM-4-Flash",
            api_key=os.getenv("ZHIPU_API_KEY"),
            base_url=os.getenv("ZHIPU_API_KEY_URL"),
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
        self.base_model = base_model
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
                "中英混合": r"./system_prompts/Kurisu_sys_prompt_ZH.txt",
                "日英混合": r"./system_prompts/Kurisu_sys_prompt_JP.txt",
                "多语种混合": r"./system_prompts/Kurisu_sys_prompt_ZH.txt"
            }
        }
    
    async def chat_with_history(self, query, history=[]):
        def build_multiturn_prompt(history, query):
            messages = [{"role": "system", "content": self.system_prompt}]
            for message_dict in history:
                messages += [message_dict]
            messages += [{"role": "user", "content": query}]
            return messages
        
        messages = build_multiturn_prompt(history, query)

        response = await self.chat_completion(messages)  # 异步等待响应
        response = response.choices[0].message.content.replace("\n\n","")

        history.extend([
            {"role": "user", "content": query},
            {"role": "assistant", "content": response}
        ])

        return history, response

    def set_model_language(self, language="中文"):
        self.language = language
        with open(self.sys_prompt_dic[self.role][language], "r", encoding="utf-8") as f:
            self.system_prompt += "".join(f.readlines())

    async def chat_completion(self, messages):  # 异步方法
        res = await self.client.chat.completions.create(
            model=self.base_model,
            messages=messages,
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_new_tokens,
            frequency_penalty=self.repetition_penalty,
        )
        return res

async def handle_inputs(model, query, history):
    history, response = await model.chat_with_history(query, history)
    print(response)
    
    
async def main():
    model = APIChatModel(role="2b")
    model.set_model_language("日文")
    history = []
    while True:
        query = await ainput(">> ")  # 异步输入
        if query.lower() == "exit":
            break
        asyncio.create_task(handle_inputs(model, query, history))
    print(history)   

if __name__ == "__main__":
    asyncio.run(main())  # 运行异步主函数