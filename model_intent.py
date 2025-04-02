from openai import AsyncOpenAI
from dotenv import load_dotenv, find_dotenv
import os
import asyncio
from aioconsole import ainput
from screen_grap import screenshot

load_dotenv(find_dotenv())


SLOTS_DICT = {
    "position": None,
    "time": "现在",
    "singer": None,
    "music name": "随机",
    "search content": None,
    "other": "true or false"
}

INTENT_PROMPT = f"""槽位(slot):{SLOTS_DICT}
用户会有以下意图(intent):
1.[天气查询]
2.[看屏幕]: 例如："帮我看看这是什么?", "你看到了什么？", "我的屏幕上有什么？", "哇！你看！"......
3.[播放音乐]
4.[停止音乐]
5.[搜索内容]: 例如: "最近有什么新出的游戏或动漫吗？", "GTA6什么时候出啊", "听说那边出车祸了，后续怎么样了", "现在几点了"......
6.[普通聊天]
根据用户的输入，输出意图和对应的槽位，未提取到槽位则保持默认值:
[天气查询] {{"position":...,"time":...}}
[看屏幕] {{"ohter":"true"}}
[播放音乐] {{"singer":...,"music name":...}}
[停止音乐] {{"ohter":"true"}}
[搜索内容] {{"search content":...}}
[普通聊天] {{"ohter":"true"}}
例如：input：杭州明天天气怎么样？output：[天气查询] {{"position":"杭州","time":"明天"}} 
input: 我想听音乐 output: [播放音乐] {{"singer":None,"music name":"随机"}}
input: 天气怎么样 output：[天气查询] {{"position":None,"time":"现在"}} """




class IntentModel:

    def __init__(self,
            base_model="GLM-4-Flash",
            api_key=os.getenv("ZHIPU_API_KEY"),
            base_url=os.getenv("ZHIPU_API_KEY_URL"),
            temperature=0,
            top_p=0.1,
        ):

        global INTENT_PROMPT

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.base_model = base_model
        self.temperature = temperature
        self.top_p = top_p
        self.language = "中文"
        self.system_prompt = INTENT_PROMPT
        self.intent = None

    async def recognition(self, inputs):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": inputs}
        ]
        try:
            response = await self.chat_completion(messages)
            self.intent = response.choices[0].message.content
            
        except Exception as e:
            self.intent = "普通聊天"
            
        finally:
            return self.intent
        
        
    async def chat_completion(self, messages):
        try:
            res = await self.client.chat.completions.create(
                model = self.base_model,
                messages=messages,
                temperature=self.temperature,
                top_p=self.top_p
            )
        
        except Exception as e:
            res = e 

        finally:
            return res
    
async def handle_inputs(model, query):
    response = await model.recognition(query)
    print(response)
    

async def main():
    model = IntentModel()
    while True:
        query = await ainput(">> ")  # 异步输入
        if query.lower() == "exit":
            break
        asyncio.create_task(handle_inputs(model, "用户:" + query))  

if __name__ == "__main__":
    asyncio.run(main())  # 运行异步主函数