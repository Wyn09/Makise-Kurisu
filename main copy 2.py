import asyncio
import threading
import signal
import sys
import asyncio
from qwen_vl_3B_Instruct import Img2TextModel
from model_hf_Qwen2d5 import ChatModel
from model_from_api import APIChatModel
from model_function_call import FunctionCallModel
from concurrent.futures import ThreadPoolExecutor
import os
from config import *
from multi_function import *
# 全局变量，用于控制线程退出
running = True

CHAT_HISTORY = []

async def read_input(chatModel, img2textModel, funcCallModel):
    global CHAT_HISTORY, running
    try:
        while running:
            loop = asyncio.get_running_loop()
            user_inputs = await loop.run_in_executor(None, input, ">> ")
            user_inputs = user_inputs.strip().lower()
            
            if user_inputs in ["quit", "exit"]:
                print("Exiting...")
                running = False  # 设置全局标志以通知其他线程退出
                break
            else:
                print(f"You: {user_inputs}")
                user_inputs = "用户" + user_inputs
                res = await functionCall_or_not(chatModel, img2textModel, funcCallModel, user_inputs, CHAT_HISTORY)
                if ~res:
                    await chatWithTTS(chatModel, user_inputs, CHAT_HISTORY)
    except Exception as e:
        print(f"发生错误: {e}")
    return False

async def recognize_screenshot(chatModel, img2textModel, init_sleep_time):
    global CHAT_HISTORY, running
    await asyncio.sleep(init_sleep_time)
    try:
        while running:  # 检查全局运行标志                
            response = await chatWithImg(chatModel, img2textModel, CHAT_HISTORY)
            min_sleep_time, time_size = await random_sleep_with_response(response)
            # 检查是否应该退出
            if not running:
                break
    except Exception as e:
        print(f"截图识别错误: {e}")

def execute_screenshot(chatModel, img2textModel, init_sleep_time=5):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(recognize_screenshot(chatModel, img2textModel, init_sleep_time))
        loop.close()
    except Exception as e:
        print(f"截图识别错误: {e}")

def execute_inputText(chatModel, img2textModel, funcCallModel):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(read_input(chatModel, img2textModel, funcCallModel))
        loop.close()
        return result
    except Exception as e:
        print(f"输入处理错误: {e}")
        return False

# 添加信号处理函数，用于优雅退出
def signal_handler(sig, frame):
    global running
    print("收到退出信号，正在关闭...")
    running = False
    # 给线程一些时间清理
    threading.Timer(2.0, sys.exit).start()

if __name__ == "__main__":
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 加载模型代码保持不变...
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
    img2textModel = Img2TextModel(Img2TextModelConfig.quantization)
    funcCallModel = FunctionCallModel()


    chatModel.set_model_language(TTSModelConfig.text_language)
    # 使用自定义线程类（确保FunctionThread类正确实现）
    th_screenshot = FunctionThread(
        target=execute_screenshot, 
        args=[
            chatModel,
            img2textModel,
            Img2TextModelConfig.init_sleep_time, 
        ]
    )
    th_screenshot.daemon = True  # 设为守护线程，主线程结束时会自动终止
    th_screenshot.start()
    
    th_inptutText = FunctionThread(
        target=execute_inputText,
        args=[
            chatModel,
            img2textModel,
            funcCallModel
        ]
    )
    th_inptutText.daemon = True  # 设为守护线程
    th_inptutText.start()
    
    # 等待输入线程完成
    th_inptutText.join()
    
    # 如果输入线程退出，设置运行标志为False
    running = False
    
    # 给线程一些时间清理
    print("正在关闭程序...")
    time.sleep(1)
    sys.exit(0)  # 使用sys.exit而不是os._exit