from openai import AsyncOpenAI
from dotenv import load_dotenv, find_dotenv
import os
import asyncio
from aioconsole import ainput
from screen_grap import screenshot

load_dotenv(find_dotenv())


SLOTS_DICT = {
    "other": "true or false"
}

INTENT_PROMPT = f"""槽位(slot):{SLOTS_DICT}
用户会有以下意图(intent):
1.[看屏幕]: 例如："帮我看看这是什么?", "你看到了什么？", "我的屏幕上有什么？", "哇！你看！"......
2.[普通聊天]
根据用户的输入，输出意图和对应的槽位，未提取到槽位则保持默认值，只输出给定格式的结果，禁止输出其他文本！
[看屏幕] {{"ohter":"true"}}
[普通聊天] {{"ohter":"true"}}"""




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