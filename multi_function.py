import asyncio
import numpy as np
from config import *
from function_tools import init_params, FUNCTION_CALL_MAPPING
from utils import delay_screenshot_time_or_not, chatWithTTS, chatWithImg, get_random_sleep_time


async def functionCall_or_not(
    chatModel, 
    img2textModel,
    intentModel, 
    user_inputs, 
    loop,
    freeze_time_factor=2
):
    asyncio.create_task(delay_screenshot_time_or_not(loop))
    
    outputs = await intentModel.recognition(user_inputs[3:])  
    # print(outputs)
    
    try:
        intent = outputs.split(" ")[0]
        slots_dict = eval(outputs.split("]")[-1].strip())
        assert all(v is not None for v in slots_dict.values()), "提供的信息不完整！"
        await init_params(chatModel, img2textModel, user_inputs, slots_dict, loop, freeze_time_factor)
        func_call_res = FUNCTION_CALL_MAPPING.get(intent, [False, None])
        if func_call_res[0]:
            # asyncio.create_task(func_call_res[1]())
            await func_call_res[1]()
        else:
            return False 
        return True
    except Exception as e:
        print(f"\n提供信息不完整:{slots_dict}\n")
        prfix_prompt = f"用户意图:{intent}，但提供信息不完整:{slots_dict}。"
        asyncio.create_task(
            delay_screenshot_time_or_not(loop, freeze_time=Img2TextModelConfig.freeze_time * freeze_time_factor)
        )
        await chatWithTTS(chatModel, prfix_prompt + user_inputs)
        return True


async def handle_user_inputs(
    chatModel, 
    img2textModel, 
    intentModel, 
    user_inputs, 
    loop
):
    user_inputs = "用户:" + user_inputs
    res = await functionCall_or_not(chatModel, img2textModel, intentModel, user_inputs, loop)
    if not res:
        await chatWithTTS(chatModel, user_inputs)



async def execute_chatWithImg_sleep_correction(
    chatModel,
    img2textModel,
    loop,
    user_inputs="",
    state=Img2TextModelConfig.state,
):
    async with state.lock:
            now = loop.time()
            wait_time = state.next_run_time - now  # 计算剩余等待时间

            if wait_time <= 0:  # 到工作时间了
                # print("Task A: Performing async IO...")
                await chatWithImg(chatModel, img2textModel, user_inputs)
                sleep_time = await get_random_sleep_time(ChatModelResponse.outputs["response"])
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
    await chatWithImg(chatModel, img2textModel)
    sleep_time = await get_random_sleep_time(ChatModelResponse.outputs["response"])
    async with state.lock:
        state.next_run_time = loop.time() + sleep_time


async def chatWithImg_sleep_correction(
    chatModel,
    img2textModel,
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
                loop,
                user_inputs="",
                state=Img2TextModelConfig.state
            )
        