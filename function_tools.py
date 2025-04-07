import asyncio
from config import *
from utils import *
import pygame
import io
import glob
import os
import numpy as np
from model_find_music import FindMusicModel, FILE_PATHS, MUSIC_REPOSITORY

class Params:
    chatModel = None
    img2textModel = None
    user_input = None
    slots_dict = None
    loop = None
    freeze_time_factor = None
    prfix_prompt = ""

async def init_params(chatModel, img2textModel, user_input, slots_dict, loop, freeze_time_factor):
    Params.chatModel = chatModel
    Params.img2textModel = img2textModel
    Params.user_input = user_input
    Params.slots_dict = slots_dict
    Params.loop = loop
    Params.freeze_time_factor = freeze_time_factor

async def execute_weather_query():  #TODO
    Params.prfix_prompt = f"查询结果：{Params.slots_dict["position"]}{Params.slots_dict["time"]}天气不错哦，温度23度，东南微风，湿度70，空气质量清新。"
    asyncio.create_task(
        delay_screenshot_time_or_not(Params.loop, freeze_time=Img2TextModelConfig.freeze_time * Params.freeze_time_factor)
    )
    await chatWithTTS(Params.chatModel, Params.prfix_prompt + Params.user_input)

async def execute_screenshot():
    # 屏幕要延长auto screenshot多一点
    await asyncio.sleep(2)  # 给2秒钟准备来让她看屏幕
    asyncio.create_task(
        delay_screenshot_time_or_not(Params.loop, freeze_time=Img2TextModelConfig.freeze_time * Params.freeze_time_factor)
    )
    await chatWithImg(Params.chatModel, Params.img2textModel, Params.user_input)


async def execute_music_play(): 

    async def find_music():
        model = FindMusicModel()
        index = await model.recognition(Params.user_input)
        return int(index)

    async def play():
        # 初始化音频模块
        pygame.mixer.init()
        # 找到音乐
        index = await find_music()
        if index == -1:
            index = np.random.randint(0, len(FILE_PATHS))
            Params.prfix_prompt = f"未找到音乐，随机播放一首音乐给用户:{MUSIC_REPOSITORY[index]}。"
            print(f"**未找到音乐，随机播放: {MUSIC_REPOSITORY[index]}**")
        else:
            Params.prfix_prompt = f"成功播放音乐: {MUSIC_REPOSITORY[index]}"
            print(f"**成功播放: {MUSIC_REPOSITORY[index]}**")

        # 读取文件到内存
        with open(FILE_PATHS[index], "rb") as f:
            audio_data = f.read()
        # 从内存加载音频
        # 如果之前已经播放了一个音乐，则停止之前的音乐
        if SoundObj.value["object"]:
            SoundObj.value["object"].stop()
        SoundObj.value["object"] = pygame.mixer.Sound(io.BytesIO(audio_data))
        SoundObj.value["object"].play()
        
    
    asyncio.create_task(
        delay_screenshot_time_or_not(Params.loop, freeze_time=Img2TextModelConfig.freeze_time * Params.freeze_time_factor)
    )

    await play()
    await chatWithTTS(Params.chatModel, Params.prfix_prompt + Params.user_input)
    


async def execute_stop_music():
    if SoundObj.value["object"]:
        SoundObj.value["object"].stop()
        Params.prfix_prompt = f"你成功停止播放音乐。"
        SoundObj.value["object"] = None
        asyncio.create_task(
            delay_screenshot_time_or_not(Params.loop, freeze_time=Img2TextModelConfig.freeze_time * Params.freeze_time_factor)
        )

    else:
        Params.prfix_prompt = f"用户没有点歌，所以并没有音乐在播放哦。"
        asyncio.create_task(
            delay_screenshot_time_or_not(Params.loop, freeze_time=Img2TextModelConfig.freeze_time * Params.freeze_time_factor)
        )

    await chatWithTTS(Params.chatModel, Params.prfix_prompt + Params.user_input)


async def execute_search_content(): #TODO
    asyncio.create_task(
        delay_screenshot_time_or_not(Params.loop, freeze_time=Img2TextModelConfig.freeze_time * Params.freeze_time_factor)
    )
    Params.prfix_prompt = f"搜索{Params.slots_dict["search content"]}"
    print(Params.prfix_prompt)



FUNCTION_CALL_MAPPING = {
    "[天气查询]": [True, execute_weather_query],
    "[看屏幕]": [True, execute_screenshot],
    "[播放音乐]": [True, execute_music_play],
    "[停止音乐]": [True, execute_stop_music],
    "[搜索内容]": [True, execute_search_content],
}




