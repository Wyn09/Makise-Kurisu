from openai import AsyncOpenAI
from dotenv import load_dotenv, find_dotenv
import os
import asyncio
from aioconsole import ainput
import glob
from config import MUSIC_FILE_FOLDER
load_dotenv(find_dotenv())


FILE_PATHS = glob.glob(MUSIC_FILE_FOLDER)
# 提取纯文件名（不带后缀）
filenames = [
    os.path.splitext(os.path.basename(path))[0]  # 分割路径并去除扩展名
    for path in FILE_PATHS
]
MUSIC_REPOSITORY = {i: n for i, n in enumerate(filenames)}

SYSTEM_PROMPT = f"""在音乐库里找出用户要播放的音乐，返回:索引值(取值范围:0~{len(MUSIC_REPOSITORY)})，如果未找到则索引值为-1。只输出结果，禁止输出多余文本！
音乐库:
{MUSIC_REPOSITORY}
例如:
input: 我想听周杰伦的枫 output:索引值:4
input: 我想听陈奕迅的马季 output:索引值:-1
"""




class FindMusicModel:

    def __init__(self,
            base_model="GLM-4-Flash",
            api_key=os.getenv("ZHIPU_API_KEY"),
            base_url=os.getenv("ZHIPU_API_KEY_URL"),
            temperature=0,
            top_p=0.0,
        ):

        global SYSTEM_PROMPT



        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.base_model = base_model
        self.temperature = temperature
        self.top_p = top_p
        self.system_prompt = SYSTEM_PROMPT


    async def recognition(self, inputs):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": inputs}
        ]
        try:
            response = await self.chat_completion(messages)
            self.response = response.choices[0].message.content
            
            self.index = self.response.split(":")[-1]
            
        except Exception as e:
            self.index = -1
            
        finally:
            return self.index
        
        
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
    index = await model.recognition(query)
    print(MUSIC_REPOSITORY)
    print(model.response)
    print(index)
   
    

async def main():
    model = FindMusicModel()
    while True:
        query = await ainput(">> ")  # 异步输入
        if query.lower() == "exit":
            break
        asyncio.create_task(handle_inputs(model, "用户:" + query))  

if __name__ == "__main__":
    asyncio.run(main())  # 运行异步主函数