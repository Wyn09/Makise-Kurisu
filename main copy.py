import asyncio
from text2audio import synthesize_and_play
from qwen_vl_3B_Instruct import Img2TextModel
from model_hf_Qwen2d5 import ChatModel
from model_from_api import APIChatModel
from model_function_call import FunctionCallModel
from screen_grap import screenshot
import time
import sounddevice as sd
from concurrent.futures import ThreadPoolExecutor
import os
import sys
import numpy as np
from baidu_translate import translate
from config import *

CHAT_HISTORY = []
thread_pool = ThreadPoolExecutor()








async def random_sleep_with_response(response):
    min_sleep_time = len(response) / 3
    time_size = min_sleep_time ** 0.5
    sleep_time = np.random.randint(min_sleep_time, min_sleep_time + time_size)
    await asyncio.sleep(sleep_time)
    return min_sleep_time, time_size


def chatWithTTS(
        chatModel,
        text,
        text_language=TTSModelConfig.text_language,
        cut_punc=TTSModelConfig.cut_punc,
        top_k=TTSModelConfig.top_k,
        top_p=TTSModelConfig.top_p,
        temperature=TTSModelConfig.temperature,
        speed=TTSModelConfig.speed,
    ):
    def execute_function():
            global CHAT_HISTORY
            CHAT_HISTORY, response = chatModel.chat_with_history(text, CHAT_HISTORY)
            synthesize_and_play(
                response,     
                text_language=text_language,
                cut_punc=cut_punc,
                top_k=top_k,
                top_p=top_p,
                temperature=temperature,
                speed=speed,
            )
            print(f"\nResponse:\n\t{response}")

            # 如果是本地部署的Model，并且不是中文或者粤语，那么就调用翻译API
            if chatModel.language not in ["中文", "粤语"]:
                print(f"\n\t({translate(response.replace("\n", ""))})")

            if len(CHAT_HISTORY) >= 5:
                    CHAT_HISTORY = CHAT_HISTORY[-5:]
            return response

    th = FunctionThread(
        target=execute_function
    )
    th.start()
    return th

async def chatWithImg(
    chatModel,
    screenshot_folder_path=Img2TextModelConfig.screenshot_folder_path, 
    max_new_tokens=Img2TextModelConfig.max_new_tokens,
    text_language=TTSModelConfig.text_language,
    cut_punc=TTSModelConfig.cut_punc,
    top_k=TTSModelConfig.top_k,
    top_p=TTSModelConfig.top_p,
    temperature=TTSModelConfig.temperature,
    speed=TTSModelConfig.speed,
):
    # print("Random Screenshot start.")

    img_file_path = screenshot(screenshot_folder_path)
    # print("截图已保存在: ", img_file_path)
    text_of_img = img2textModel.img2text(img_file_path, max_new_tokens)
    # print(f"\nText Of Img:\n\t{text_of_img}")
    chat_tts_th = chatWithTTS(chatModel, text_of_img)
    
    # print(f"Length of CHAT_HISTORY:\t{len(CHAT_HISTORY)}\n")
    # 删除抓取的图片
    os.remove(img_file_path)
    response = chat_tts_th.get_result()
    min_sleep_time, time_size = await random_sleep_with_response(response)
    # max_sleep_time = min_sleep_time + time_size
    # print(f"\nSleep Time: {min_sleep_time:.2f}sec to {max_sleep_time:.2f}sec.")


"""
TTS与输入异步实现
1.async修饰recognize_screenshot，线程调用execute_screenshot，里面用asyncio.run运行recognize_screenshot，再await synthesize_and_play
2.线程直接调用recognize_screenshot，里面用asyncio.run运行synthesize_and_play。
不知道为什么有时候会自动结束进程。
"""
async def recognize_screenshot(
    chatModel,
    screenshot_folder_path, 
    max_new_tokens,
    text_language="zh",
    cut_punc=None,
    top_k=20,
    top_p=0.7,
    temperature=1.0,
    speed=1,
    init_sleep_time=5
):
    global CHAT_HISTORY
    await asyncio.sleep(init_sleep_time)
    while True:                
        print("*" * 80)

        await chatWithImg(chatModel)

def execute_screenshot(
    chatModel,
    screenshot_folder_path, 
    max_new_tokens,
    text_language="zh",
    cut_punc=None,
    top_k=20,
    top_p=0.7,
    temperature=1.0,
    speed=1,
    init_sleep_time=5
):        

    asyncio.run(recognize_screenshot(
        chatModel,
        screenshot_folder_path, 
        max_new_tokens,
        text_language,
        cut_punc,
        top_k,
        top_p,
        temperature,
        speed,
        init_sleep_time
    ))


async def read_input(
        chatModel,
        text_language="zh",
        cut_punc=None,
        top_k=20,
        top_p=0.7,
        temperature=1.0,
        speed=1,
    ):
        while True:
            line = input("\n>>")
            line = line.strip().lower()
            if line in ["quit", "exit"]:
                print("Exiting...")
                # 当检测到退出命令时，结束进程
                os._exit(0)
            else:
                print(f"You: {line}")
                intent = funcCallModel.recognition(line)
                if intent == "天气查询":
                    print("今天天气不错哦，温度23度，微微春风，很适合出行呢！")
                
                elif intent == "看屏幕":
                    await chatWithImg(chatModel)

                elif intent == "播放音乐":
                    print("播放《罗密欧与朱丽叶》")

                elif intent == "搜索内容":
                    print("搜索相关内容")

                else:
                    chatWithTTS(chatModel, "用户:" + line)

def execute_inputText(
    chatModel,
    text_language="zh",
    cut_punc=None,
    top_k=20,
    top_p=0.7,
    temperature=1.0,
    speed=1,
):

    
    asyncio.run(read_input(
        chatModel,
        text_language,
        cut_punc,
        top_k,
        top_p,
        temperature,
        speed,
    ))



if __name__ == "__main__":

    img2textModel = Img2TextModel(Img2TextModelConfig.quantization)
    
    # 本地部署的Model
    # chatModel = ChatModel(
    #     base_model=ChatModelConfig.base_model, 
    #     lora_path=ChatModelConfig.lora_path, 
    #     quantization=ChatModelConfig.quantization, 
    #     system_prompt=ChatModelConfig.system_prompt,
    #     temperature=ChatModelConfig.temperature,
    #     top_k=ChatModelConfig.top_k,
    #     top_p=ChatModelConfig.top_p,
    #     max_new_tokens=ChatModelConfig.max_new_tokens,
    #     repetition_penalty=ChatModelConfig.repetition_penalty
    # )

    # 调用API的Model
    chatModel = APIChatModel(
        base_model=APIChatModelConfig.base_model, 
        api_key=APIChatModelConfig.api_key,
        base_url=APIChatModelConfig.base_url,
        system_prompt=APIChatModelConfig.system_prompt,
        temperature=APIChatModelConfig.temperature,
        top_p=APIChatModelConfig.top_p,
        max_new_tokens=APIChatModelConfig.max_new_tokens,
        repetition_penalty=APIChatModelConfig.repetition_penalty,
        role=APIChatModelConfig.role
    )


    chatModel.set_model_language(TTSModelConfig.text_language)

    funcCallModel = FunctionCallModel()


    th_screenshot = FunctionThread(
        target=execute_screenshot, 
        args=[
            chatModel,
            Img2TextModelConfig.screenshot_folder_path, 
            Img2TextModelConfig.max_new_tokens,
            TTSModelConfig.text_language,
            TTSModelConfig.cut_punc,
            TTSModelConfig.top_k,
            TTSModelConfig.top_p,
            TTSModelConfig.temperature,
            TTSModelConfig.speed,
            Img2TextModelConfig.init_sleep_time, 
        ]
    )
    th_screenshot.start()
    
    th_inptutText = FunctionThread(
        target=execute_inputText,
        args=[
            chatModel,
            TTSModelConfig.text_language,
            TTSModelConfig.cut_punc,
            TTSModelConfig.top_k,
            TTSModelConfig.top_p,
            TTSModelConfig.temperature,
            TTSModelConfig.speed,
        ]
    )
    th_inptutText.start()
 
    
    

    pass