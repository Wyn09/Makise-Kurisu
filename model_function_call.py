from openai import OpenAI
from dotenv import load_dotenv
import os
import asyncio
from screen_grap import screenshot

load_dotenv("./.env")


INTENT_PROMPT = """用户会有以下意图:
1.天气查询
2.看屏幕: 例如："帮我看看这是什么?", "你看到了什么？", "我的屏幕上有什么？", "哇！你看！"......
3.播放音乐
4.搜索内容: 例如: "最近有什么新出的游戏或动漫吗？", "GTA6什么时候出啊", "听说那边出车祸了，后续怎么样了"......
5.普通聊天
根据用户的输入，输出意图:天气查询,看屏幕,播放音乐,搜索内容,普通聊天"""




class FunctionCallModel:

    def __init__(self,
            base_model="GLM-4-Flash",
            api_key=os.getenv("ZHIPU_API_KEY"),
            base_url=os.getenv("ZHIPU_API_KEY_URL"),
            temperature=0.1,
            top_p=0.2,
        ):

        global INTENT_PROMPT

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.base_model = base_model
        self.temperature = temperature
        self.top_p = top_p
        self.language = "中文"
        self.system_prompt = INTENT_PROMPT
        self.intent = None

    def recognition(self, inputs):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": inputs}
        ]
        response = self.chat_completion(messages)
        self.intent = response.choices[0].message.content
        return self.intent

    # def function_call(self, chatModel, img2textModel, inputs):
    #     self.recognition(inputs)
    #     if self.intent == "天气查询":
    #         print("今天天气不错哦，温度23度，微微春风，很适合出行呢！")
    #         return 
        
    #     elif self.intent == "看屏幕":
    #         img_path = screenshot()
    #         text_of_img = img2textModel.img2text(img_path)

    #         return 


    #     elif self.intent == "播放音乐":
    #         print("播放《罗密欧与朱丽叶》")
    #         return

    #     elif self.intent == "搜索内容":
    #         print("搜索相关内容")
    #         return

    #     else:
    #         return "普通聊天"
        
    def chat_completion(self, messages):
        res = self.client.chat.completions.create(
            model = self.base_model,
            messages=messages,
            temperature=self.temperature,
            top_p=self.top_p
        )

        return res


if __name__ == "__main__":

    model = FunctionCallModel()
    while 1:
        query = input(">>")
        if query.lower() == "exit":
            break
        response = model.recognition(query)
        print(response)
