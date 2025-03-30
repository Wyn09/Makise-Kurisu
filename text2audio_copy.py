import requests
import sounddevice as sd
import soundfile as sf
from io import BytesIO
import asyncio
import threading
import time
import aiohttp

# 用一个全局变量记录当前播放的线程引用（可选）
g_current_play_thread = None
g_lock = threading.Lock()

def interrupt_playback():
    """
    打断当前正在播放的音频（如果有），让 sd.wait() 提前返回。
    """
    # 直接调用 sd.stop()，会使正在播放的语音立刻停止
    sd.stop()
    # 如果你还想等旧线程彻底结束，可在此处选择是否 join()
    # with g_lock:
    #     if g_current_play_thread and g_current_play_thread.is_alive():
    #         g_current_play_thread.join()

def request_in_thread(url, params):
    # 2. 发 GET 请求（阻塞）
    resp = requests.get(url, params=params, proxies={"http": None, "https": None})

    # 3. 判断是否成功
    if resp.status_code == 200:
        # 4. 从响应的二进制数据中读取 WAV 音频
        wav_io = BytesIO(resp.content)
        data, samplerate = sf.read(wav_io)
        # interrupt_playback()
        # 5. 播放并阻塞到播放结束或被打断
        sd.play(data, samplerate=samplerate)
        # sd.wait()  # 如果被 interrupt_playback() 调用 sd.stop()，这里会立刻返回
        
    else:
        print("请求失败:", resp.status_code, resp.text)

def synthesize_and_play(
    text,
    text_language="zh",
    cut_punc=None,
    top_k=20,
    top_p=0.7,
    temperature=1.0,
    speed=1,
):
    """
    向已经启动的 api.py 发送推理请求（GET），
    得到 wav 音频后使用 sounddevice 直接播放。
    """
    # （可选）先打断上一次播放，避免多路播放互相干扰
    

    # 1. 构造请求
    url = "http://127.0.0.1:9880"
    params = {
        "text": text,
        "text_language": text_language,
        "cut_punc": cut_punc,
        "top_k": top_k,
        "top_p": top_p,
        "temperature": temperature,
        "speed": speed,
    }

    # # 2. 启动后台线程
    # th = threading.Thread(target=request_in_thread, args=(url, params))

    # # 更新全局引用（可选，看自己是否需要管理线程）
    # with g_lock:
    #     global g_current_play_thread
    #     g_current_play_thread = th

    # th.start()
    # # 立即返回，播放会在子线程中继续
    # return th

    request_in_thread(url, params)


async def demo():
    text1 = """こんにちは！実はこの手紙は私の心の中で長い間温めていたが、今日やっと勇気を出してあなたに書いた。あなたは意外に感じるかもしれませんが、私はずっとあなたに言いたいことがあります。私はもう言わないと、いくつかの素晴らしい可能性を逃すかもしれないと思っているからです。"""

    text2 = """Hello, world! Where are you?"""

    # 1. 先播放一段长音频
    print("开始播放第一段...")
    _ = await synthesize_and_play(text1, "ja")

    # if 播放中途输入新的变量

    # 等待3秒，然后打断
    await asyncio.sleep(len(text1) / 10)
    print("打断当前播放!")
    # interrupt_playback()
    
    # 2. 播放下一段
    await asyncio.sleep(len(text2) / 10)
    print("播放第二段...")
    _ = await synthesize_and_play(text2, "en")




if __name__ == "__main__":
    # asyncio.run(demo())
    
    while 1:
        inputs = input(">> ")
        if inputs.lower() == "exit":
            interrupt_playback()
            break
        th = threading.Thread(target=synthesize_and_play, args=(inputs, "ja", "。"))
        th.start()
        # asyncio.run(synthesize_and_play(inputs, text_language="ja", cut_punc="。"))
