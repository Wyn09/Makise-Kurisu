import asyncio
from text2audio import synthesize_and_play
from screen_grap import screenshot
import time
import sounddevice as sd
from concurrent.futures import ThreadPoolExecutor
import os
import sys
import numpy as np
from baidu_translate import translate
from config import *

async def random_sleep_with_response(response):
    min_sleep_time = len(response) / 5
    time_size = min_sleep_time ** 0.5
    sleep_time = np.random.randint(min_sleep_time, min_sleep_time + time_size)
    await asyncio.sleep(sleep_time)
    return min_sleep_time, time_size

async def chatWithTTS(
        chatModel,
        text,
        chat_history,
        text_language=TTSModelConfig.text_language,
        cut_punc=TTSModelConfig.cut_punc,
        top_k=TTSModelConfig.top_k,
        top_p=TTSModelConfig.top_p,
        temperature=TTSModelConfig.temperature,
        speed=TTSModelConfig.speed,
    ):

    # async def execute_function(chat_history):
            chat_history, response = await chatModel.chat_with_history(text, chat_history)
            await synthesize_and_play(
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

            if len(chat_history) >= 5:
                    chat_history = chat_history[-5:]
            return response


async def chatWithImg(
    chatModel,
    img2textModel,
    chat_history,
    user_inputs="",
    screenshot_folder_path=Img2TextModelConfig.screenshot_folder_path, 
    max_new_tokens=Img2TextModelConfig.max_new_tokens,
    
):
    print("*" * 80)
    img_file_path = screenshot(screenshot_folder_path)
    # print("截图已保存在: ", img_file_path)
    text_of_img = await img2textModel.img2text(img_file_path, user_inputs=user_inputs, max_new_tokens=max_new_tokens)
    # print(f"\nText Of Img:\n\t{text_of_img}")
    response = await chatWithTTS(chatModel, text_of_img + user_inputs, chat_history)

    # print(f"Length of chat_history:\t{len(chat_history)}\n")

    # 删除抓取的图片
    os.remove(img_file_path)
    return response


async def functionCall_or_not(chatModel, img2textModel, funcCallModel, user_inputs, chat_history):
    intent = funcCallModel.recognition(user_inputs)
    if intent == "天气查询":
        print("今天天气不错哦，温度23度，微微春风，很适合出行呢！")

    elif intent == "看屏幕":
        response = await chatWithImg(chatModel, img2textModel, chat_history, user_inputs)
        await random_sleep_with_response(response)

    elif intent == "播放音乐":
        print("播放《罗密欧与朱丽叶》")

    elif intent == "搜索内容":
        print("搜索相关内容")

    else:
        return 0 
    
    return 1