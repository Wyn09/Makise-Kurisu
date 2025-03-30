import asyncio
from aioconsole import ainput
from qwen_vl_3B_Instruct import Img2TextModel
from model_hf_Qwen2d5 import ChatModel as LocalChatModel
from model_from_api import APIChatModel
from model_function_call import FunctionCallModel
from concurrent.futures import ThreadPoolExecutor
import os
import time
from config import *
from multi_function import *

CHAT_HISTORY = []
thread_pool = ThreadPoolExecutor()

async def recognize_screenshot(
    chatModel,
    img2textModel,
    init_sleep_time
):
    global CHAT_HISTORY
    await asyncio.sleep(init_sleep_time)
    while True:                
        response = await chatWithImg(chatModel, img2textModel, CHAT_HISTORY)
        min_sleep_time, time_size = await random_sleep_with_response(response)
        # print(f"sleep time: {min_sleep_time}sec to {min_sleep_time + time_size}sec")


async def read_user_inputs(
        chatModel,
        img2textModel,
        funcCallModel
    ):
        global CHAT_HISTORY
        while True:
            user_inputs = await ainput("🤗 >> ")
            user_inputs = user_inputs.strip().lower()
            if user_inputs in ["quit", "exit"]:
                print("Exiting...")
                for x in "🙀🐾🐾🐾":
                    print(x)
                    time.sleep(0.5)
                # 当检测到退出命令时，结束进程
                os._exit(0)
            else:
                print(f"🤓 : {user_inputs}")
                asyncio.create_task(handle_user_inputs(chatModel, img2textModel, funcCallModel, user_inputs, CHAT_HISTORY))


async def main():
    # task1 = asyncio.create_task(recognize_screenshot(chatModel, img2textModel, 5))
    # task2 = asyncio.create_task(read_user_inputs(chatModel, img2textModel, funcCallModel))
    # await task1
    # await task2

    await asyncio.gather(
        #  recognize_screenshot(chatModel, img2textModel, 5),
         read_user_inputs(chatModel, img2textModel, funcCallModel)
    )

if __name__ == "__main__":

    # chatModel = LocalChatModel(
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

    asyncio.run(main())

    pass