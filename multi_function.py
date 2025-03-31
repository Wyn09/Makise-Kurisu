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

async def get_random_sleep_time(response, alpha=5):
    min_sleep_time = len(response) / alpha
    time_size = min_sleep_time ** 0.5
    sleep_time = np.random.randint(min_sleep_time, min_sleep_time + time_size)
    return sleep_time

async def random_sleep_with_response(response, alpha=5):
    sleep_time = await get_random_sleep_time(response, alpha)
    await asyncio.sleep(sleep_time)

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
    if chatModel.language not in ["中文", "粤语", "中英混合"]:
        translated_text = await translate(response.replace("\n", ""))
        print(f"\n\t({translated_text})")

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


async def functionCall_or_not(
    chatModel, 
    img2textModel,
    funcCallModel, 
    user_inputs, 
    chat_history,
    loop
):
    asyncio.gather(delay_screenshot_time_or_not(loop))

    intent = await funcCallModel.recognition(user_inputs[3:])  
    # print(intent)
    if intent in "天气查询":
        result = "查询结果：今天天气不错哦，温度23度，东南微风，湿度70，空气质量清新，很适合出行呢！"
        response = await chatWithTTS(chatModel, result + user_inputs, chat_history)
        
    elif intent in "看屏幕":
        # 屏幕要延长auto screenshot多一点
        await asyncio.sleep(2)  # 给2秒钟准备来让她看屏幕
        asyncio.gather(
            chatWithImg(chatModel, img2textModel, chat_history, user_inputs),
            delay_screenshot_time_or_not(loop, freeze_time=Img2TextModelConfig.freeze_time * 2)
        )
        
    elif intent in "播放音乐":
        print("播放《罗密欧与朱丽叶》")

    elif intent in "搜索内容":
        print("搜索相关内容")

    else:

        return False 
    
    return True



async def handle_user_inputs(
    chatModel, 
    img2textModel, 
    funcCallModel, 
    user_inputs, 
    chat_history, 
    loop
):

    user_inputs = "用户:" + user_inputs
    res = await functionCall_or_not(chatModel, img2textModel, funcCallModel, user_inputs, chat_history, loop)
    if not res:
        response = await chatWithTTS(chatModel, user_inputs, chat_history)


async def delay_screenshot_time_or_not(loop, state=Img2TextModelConfig.state, freeze_time=Img2TextModelConfig.freeze_time):
        current_time = loop.time()
        desired_next_run = current_time + freeze_time  # freeze_time 保护期
        async with state.lock:
            # 如果指定的执行时间比真实执行时间要晚，那么就赋值为指定的执行时间
            if desired_next_run > state.next_run_time:  # 需要延长计划
                state.next_run_time = desired_next_run
                if state.current_sleep and not state.current_sleep.done():
                    state.current_sleep.cancel()  # 打碎旧闹钟
        print(f"\nstate.next_run_time: ", state.next_run_time)


async def execute_chatWithImg_sleep_correction(
    chatModel,
    img2textModel,
    chat_history,
    loop,
    user_inputs="",
    state=Img2TextModelConfig.state,
):
    async with state.lock:
            now = loop.time()
            wait_time = state.next_run_time - now  # 计算剩余等待时间

            if wait_time <= 0:  # 到工作时间了
                # print("Task A: Performing async IO...")
                response = await chatWithImg(chatModel, img2textModel, chat_history, user_inputs)
                sleep_time = await get_random_sleep_time(response)
                state.next_run_time = now + sleep_time  # 计划下次工作时间
                return

            # 设置新闹钟
            state.current_sleep = asyncio.create_task(asyncio.sleep(wait_time))
    try:
        await state.current_sleep
    except asyncio.CancelledError:
        return  # 闹钟被取消，重新检查计划本
    finally:
        async with state.lock:
            state.current_sleep = None  # 清空当前闹钟
    response = await chatWithImg(chatModel, img2textModel, chat_history)
    sleep_time = await get_random_sleep_time(response)
    async with state.lock:
        state.next_run_time = loop.time() + sleep_time

async def chatWithImg_sleep_correction(
    chatModel,
    img2textModel,
    chat_history,
    loop,
    user_inputs="",
    init_sleep_time=Img2TextModelConfig.init_sleep_time,
    state=Img2TextModelConfig.state,
):
    # 初始化计划本
    async with state.lock:
        if state.next_run_time is None:
            state.next_run_time = loop.time() + init_sleep_time

    await asyncio.sleep(init_sleep_time)
    while True:     
        await execute_chatWithImg_sleep_correction(
                chatModel,
                img2textModel,
                chat_history,
                loop,
                user_inputs="",
                state=Img2TextModelConfig.state
            )
        