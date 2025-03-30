import sounddevice as sd
import soundfile as sf
from io import BytesIO
import asyncio
import threading
import time
import aiohttp

# 用一个全局变量记录当前播放的任务引用
g_current_play_task = None
g_lock = asyncio.Lock()

def interrupt_playback():
    """
    打断当前正在播放的音频（如果有），让 sd.wait() 提前返回。
    """
    # 直接调用 sd.stop()，会使正在播放的语音立刻停止
    sd.stop()

async def request_and_play(url, params):
    """异步请求并播放音频"""
    # 使用异步HTTP客户端发送请求
    async with aiohttp.ClientSession() as session:
        # 发送GET请求
        async with session.get(url, params=params) as resp:
            # 判断是否成功
            if resp.status == 200:
                # 读取响应内容
                content = await resp.read()
                # 从响应的二进制数据中读取WAV音频
                wav_io = BytesIO(content)
                data, samplerate = sf.read(wav_io)
                
                # 播放音频（这是同步操作，但我们会在异步协程中运行它）
                sd.play(data, samplerate=samplerate)
                
            #     # 创建一个事件用于等待播放完成或被中断
            #     played_event = asyncio.Event()
                
            #     def callback(outdata, frames, time, status):
            #         if status:
            #             print(f"状态: {status}")
            #         if not played_event.is_set():
            #             played_event.set()
                
            #     # 等待播放完成（可以被中断）
            #     try:
            #         await asyncio.get_event_loop().run_in_executor(
            #             None, 
            #             lambda: sd.wait()
            #         )
            #     except Exception as e:
            #         print(f"播放中断: {e}")
            # else:
            #     print(f"请求失败: {resp.status} {await resp.text()}")

async def synthesize_and_play(
    text,
    text_language="zh",
    cut_punc=None,
    top_k=20,
    top_p=0.7,
    temperature=1.0,
    speed=1,
):
    """
    向已经启动的 api.py 发送异步推理请求，
    得到 wav 音频后使用 sounddevice 直接播放。
    """
    # 构造请求
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

    # 更新全局任务引用，如果有旧任务正在进行，先取消它
    async with g_lock:
        global g_current_play_task
        if g_current_play_task and not g_current_play_task.done():
            # 中断当前播放
            # interrupt_playback()
            try:
                # 给予任务取消时间
                await asyncio.wait_for(g_current_play_task, timeout=0.5)
            except asyncio.TimeoutError:
                pass
        
    #     # 创建新任务
    #     g_current_play_task = asyncio.create_task(request_and_play(url, params))
    
    # # 返回任务，调用者可以选择await它
    # return g_current_play_task
    return await request_and_play(url, params)

async def demo():
    text1 = """こんにちは！実はこの手紙は私の心の中で長い間温めていたが、今日やっと勇気を出してあなたに書いた。あなたは意外に感じるかもしれませんが、私はずっとあなたに言いたいことがあります。私はもう言わないと、いくつかの素晴らしい可能性を逃すかもしれないと思っているからです。"""

    text2 = """Hello, world! Where are you?"""

    # 1. 先播放一段长音频
    print("开始播放第一段...")
    task1 = await synthesize_and_play(text1, "ja")

    # 等待3秒，然后打断
    await asyncio.sleep(len(text1) / 10)
    print("打断当前播放!")
    interrupt_playback()
    
    # 2. 播放下一段
    await asyncio.sleep(1)  # 给一点时间让前一个任务清理
    print("播放第二段...")
    task2 = await synthesize_and_play(text2, "en")
    
    # 可选：等待第二个任务完成
    await task2

async def main():
    """主异步循环处理用户输入"""
    while True:
        # 使用线程执行器运行阻塞的input函数
        inputs = await asyncio.get_running_loop().run_in_executor(
            None, lambda: input(">> ")
        )
        if inputs.lower() == "exit":
            interrupt_playback()
            break
        
        # 直接在异步环境中调用synthesize_and_play
        await synthesize_and_play(inputs, text_language="ja", cut_punc="。")

if __name__ == "__main__":
    # 选择运行demo或主交互循环
    # asyncio.run(demo())
    asyncio.run(main())