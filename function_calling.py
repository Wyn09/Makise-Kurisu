import asyncio
from config import *
from utils import *
import pygame
import io
from constant import SOUND_OBJ

class Params:
    chatModel = None
    img2textModel = None
    user_inputs = None
    chat_history = None
    slots_dict = None
    loop = None
    freeze_time_factor = None


async def init_params(chatModel, img2textModel, user_inputs, chat_history, slots_dict, loop, freeze_time_factor):
    Params.chatModel = chatModel
    Params.img2textModel = img2textModel
    Params.user_inputs = user_inputs
    Params.chat_history = chat_history
    Params.slots_dict = slots_dict
    Params.loop = loop
    Params.freeze_time_factor = freeze_time_factor

async def execute_weather_query():  #TODO
    result = f"查询结果：{Params.slots_dict["position"]}{Params.slots_dict["time"]}天气不错哦，温度23度，东南微风，湿度70，空气质量清新。"
    asyncio.gather(
        chatWithTTS(Params.chatModel, result + Params.user_inputs, Params.chat_history),
        delay_screenshot_time_or_not(Params.loop, freeze_time=Img2TextModelConfig.freeze_time * Params.freeze_time_factor)
    )

async def execute_screenshot():
    # 屏幕要延长auto screenshot多一点
    await asyncio.sleep(2)  # 给2秒钟准备来让她看屏幕
    asyncio.gather(
        chatWithImg(Params.chatModel, Params.img2textModel, Params.chat_history, Params.user_inputs),
        delay_screenshot_time_or_not(Params.loop, freeze_time=Img2TextModelConfig.freeze_time * Params.freeze_time_factor)
    )

async def execute_music_play(): 
    async def play():
        # 初始化音频模块
        pygame.mixer.init()

        # 读取文件到内存
        with open("./music/02. 周杰伦 - 蓝色风暴.wav", "rb") as f:
            audio_data = f.read()
        # 从内存加载音频
        SOUND_OBJ.value = pygame.mixer.Sound(io.BytesIO(audio_data))
        SOUND_OBJ.value.play()
        
    result = f"播放音乐: {Params.slots_dict["singer"]} - {Params.slots_dict["music name"]}"
    asyncio.gather(
        chatWithTTS(Params.chatModel, result + Params.user_inputs, Params.chat_history),
        delay_screenshot_time_or_not(Params.loop, freeze_time=Img2TextModelConfig.freeze_time * Params.freeze_time_factor)
    )

    print(result)
    asyncio.create_task(play())


async def execute_stop_music():
    if SOUND_OBJ.value:
        SOUND_OBJ.value.stop()
        result = f"已停止播放音乐。"
        SOUND_OBJ.value = None
        asyncio.gather(
            chatWithTTS(Params.chatModel, result + Params.user_inputs, Params.chat_history),
            delay_screenshot_time_or_not(Params.loop, freeze_time=Img2TextModelConfig.freeze_time * Params.freeze_time_factor)
        )

    else:
        result = f"用户没有点歌，所以并没有音乐在播放哦。"
        asyncio.gather(
            chatWithTTS(Params.chatModel, result + Params.user_inputs, Params.chat_history),
            delay_screenshot_time_or_not(Params.loop, freeze_time=Img2TextModelConfig.freeze_time * Params.freeze_time_factor)
        )


async def execute_search_content(): #TODO
    asyncio.gather(
        delay_screenshot_time_or_not(Params.loop, freeze_time=Img2TextModelConfig.freeze_time * Params.freeze_time_factor)
    )
    result = f"搜索{Params.slots_dict["search content"]}"
    print(result)



FUNCTION_CALL_MAPPING = {
    "[天气查询]": [True, execute_weather_query],
    "[看屏幕]": [True, execute_screenshot],
    "[播放音乐]": [True, execute_music_play],
    "[停止音乐]": [True, execute_stop_music],
    "[搜索内容]": [True, execute_search_content],
}




