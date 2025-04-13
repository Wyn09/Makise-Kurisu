from aip import AipSpeech
import pyaudio
import wave
import asyncio
import keyboard
import io
import time
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


BAIDU_ASR_APP_ID = os.getenv("BAIDU_ASR_APP_ID")
BAIDU_ASR_API_KEY = os.getenv("BAIDU_ASR_API_KEY")
BAIDU_ASR_SECRET_KEY = os.getenv("BAIDU_ASR_SECRET_KEY")


class AsyncVoiceRecorder:
    def __init__(self):
        # 初始化百度语音识别客户端
        self.client = AipSpeech(BAIDU_ASR_APP_ID, BAIDU_ASR_API_KEY, BAIDU_ASR_SECRET_KEY)
        
        # 麦克风录音参数
        self.CHUNK = 1024  # 每个缓冲区的帧数
        self.FORMAT = pyaudio.paInt16  # 采样位数
        self.CHANNELS = 1  # 声道数
        self.RATE = 16000  # 采样率
        
        # 录音状态控制
        self.is_recording = False
        self.p = pyaudio.PyAudio()
        self.frames = []
        
    async def _record_audio_chunk(self, stream):
        """异步读取一个音频块"""
        loop = asyncio.get_event_loop()
        chunk = await loop.run_in_executor(None, lambda: stream.read(self.CHUNK, exception_on_overflow=False))
        return chunk
    
    async def record_on_key_press(self, key='t'):
        """
        异步函数: 按下指定键开始录音，松开键停止录音
        
        参数:
            key: 触发录音的键，默认为't'
            
        返回:
            bytes: 录音的音频数据
        """
        self.frames = []
        key_pressed = False
        
        # print(f"准备录音，按住{key}键开始，松开结束...")
        
        # 打开音频流但不立即开始录音
        stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        try:
            # 使用异步方式监听按键
            while True:
                # 检查按键状态
                if keyboard.is_pressed(key) and not key_pressed:
                    key_pressed = True
                    self.is_recording = True
                    print("\n#Hold-on")
                
                elif not keyboard.is_pressed(key) and key_pressed:
                    key_pressed = False
                    self.is_recording = False
                    print("\n#Hold-off")
                    break
                
                # 如果正在录音，读取音频块
                if self.is_recording:
                    chunk = await self._record_audio_chunk(stream)
                    self.frames.append(chunk)
                
                # 短暂等待，避免CPU占用过高
                await asyncio.sleep(0.01)
        
        finally:
            # 关闭音频流
            stream.stop_stream()
            stream.close()
            
        # 返回录音数据
        audio_data = b''.join(self.frames)
        return audio_data
    
    async def record_on_key_toggle(self, key='t'):
        """
        异步函数: 按一下指定键开始录音，再按一下停止录音
        
        参数:
            key: 触发录音的键，默认为't'
            
        返回:
            bytes: 录音的音频数据
        """
        self.frames = []
        key_down = False
        toggle_state = False  # 用于跟踪按键开关状态
        
        # print(f"准备录音，按一下{key}键开始，再按一下结束...")
        
        # 打开音频流但不立即开始录音
        stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        try:
            # 使用异步方式监听按键
            while True:
                # 检测按键状态变化（只在按下后释放时切换录音状态）
                if keyboard.is_pressed(key) and not key_down:
                    key_down = True
                elif not keyboard.is_pressed(key) and key_down:
                    key_down = False
                    toggle_state = not toggle_state  # 切换状态
                    
                    if toggle_state:  # 开始录音
                        self.is_recording = True
                        print("\n#Toggle-on")
                    else:  # 停止录音
                        if self.is_recording:
                            self.is_recording = False
                            print("\n#Toggle-off")
                            break
                
                # 如果正在录音，读取音频块
                if self.is_recording:
                    chunk = await self._record_audio_chunk(stream)
                    self.frames.append(chunk)
                
                # 短暂等待，避免CPU占用过高
                await asyncio.sleep(0.1)
        
        finally:
            # 关闭音频流
            stream.stop_stream()
            stream.close()
            
        # 返回录音数据
        audio_data = b''.join(self.frames)
        return audio_data
    
    async def recognize_speech(self, audio_data):
        """
        异步函数: 识别语音
        
        参数:
            audio_data: 音频数据
            
        返回:
            str: 识别结果文本
        """
        if not audio_data or len(audio_data) == 0:
            return "未检测到有效音频数据"
            
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: self.client.asr(audio_data, 'pcm', self.RATE, {'dev_pid': 1537})
        )
        
        if isinstance(result, dict) and 'result' in result and result['result']:
            return result['result'][0]
        else:
            return "识别失败或无语音输入"
    
    def close(self):
        """关闭PyAudio资源"""
        self.p.terminate()

recorder = AsyncVoiceRecorder()

async def record_and_recognize(mode="toggle", key="t"):
    """
    异步函数: 录音并识别语音的完整流程
    
    参数:
        mode: 录音模式，"hold"为按住录音，"toggle"为按一下开始/结束录音
        
    返回:
        str: 语音识别结果
    """
        
    try:
        if mode == "hold":
            audio_data = await recorder.record_on_key_press(key)
        elif mode == "toggle":
            audio_data = await recorder.record_on_key_toggle(key)
        else:
            print("未知的录音模式")
            return None
            
        if audio_data and len(audio_data) > 0:
            # print("正在识别语音...")
            text = await recorder.recognize_speech(audio_data)
            return text
        else:
            return None
    except Exception as e:
        print("音频识别错误:", e)
        return None

# 示例使用，可以选择录音模式
async def select_record_mode():
    print("请选择录音模式:")
    print("1. 按住t键录音，松开停止")
    print("2. 按一下t键开始录音，再按一下停止")
    choice = input("请输入选择 (1/2): ")
    
    if choice == "2":
        return await record_and_recognize("toggle")
    else:
        return await record_and_recognize("hold")
        
async def main():
    while True:
        result = await select_record_mode()
        print(f"识别结果: {result}")
        
        response = input("继续录音? (y/n): ")
        if response.lower() != 'y':
            break

# 如果要直接使用某一种模式，可以这样调用
async def main_toggle_mode():
    while True:
        result = await record_and_recognize("toggle", "ctrl+t")
        print(f"识别结果: {result}")
        
        # response = input("继续录音? (y/n): ")
        # if response.lower() != 'y':
        #     break

# 示例用法
if __name__ == "__main__":
    # 可以选择运行哪个主函数
    # asyncio.run(main())  # 每次录音前选择模式
    asyncio.run(main_toggle_mode())  # 直接使用按一下开始/结束模式