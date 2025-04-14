import asyncio
import numpy as np
# from config import *
from aioconsole import ainput
from function_tools import init_params, FUNCTION_CALL_MAPPING
from utils import *
from var_bridge_flow import SHARE_STATE
from baidu_asr import record_and_recognize



async def functionCall_or_not(
    chatModel, 
    img2textModel,
    intentModel, 
    user_input, 
    loop,
    freeze_time_factor=2
):
    asyncio.create_task(delay_screenshot_time_or_not(loop))
    
    outputs = await intentModel.recognition(user_input)  
    # print(f"\nintent: {outputs}\n")
    

    try:
        intent = outputs.split(" ")[0]
        slots_dict = eval(outputs.split("]")[-1].strip())
        # assert all(v is not None for v in slots_dict.values()), "提供的信息不完整！"
        await init_params(chatModel, img2textModel, user_input, slots_dict, loop, freeze_time_factor)
        func_call_res = FUNCTION_CALL_MAPPING.get(intent, [False, None])
        if func_call_res[0]:
            # asyncio.create_task(func_call_res[1]())
            await func_call_res[1]()
        else:
            return False 
        return True
    
    except Exception as e:
        prfix_prompt = ""
        if intent[0] != "[" or intent[-1] != "]":
            intent = "[普通聊天]"
            slots_dict = '{"other":"true"}'
            
        # try:
        #     if not all(v is not None for v in slots_dict.values()):
        #         print(f"\n拒绝用户请求，因为提供信息不完整:{slots_dict}\n")
        #         prfix_prompt = f"用户意图:{intent}，但提供信息不完整:{slots_dict}。"
        # except Exception:
        #     pass

        asyncio.create_task(
            delay_screenshot_time_or_not(loop, freeze_time=Img2TextModelConfig.freeze_time * freeze_time_factor)
        )
        await chatWithTTS(chatModel, prfix_prompt + user_input)
        return True


async def handle_user_inputs(
    chatModel, 
    user_input, 
    loop
):
    # res = await functionCall_or_not(chatModel, img2textModel, intentModel, user_input, loop)
    # if not res:
    await chatWithTTS(chatModel, user_input)



async def execute_chatWithImg_sleep_correction(
    chatModel,
    img2textModel,
    loop,
    user_input="",
    state=Img2TextModelConfig.state,
):
    async with state.lock:
            now = loop.time()
            wait_time = state.next_run_time - now  # 计算剩余等待时间

            if wait_time <= 0:  # 到工作时间了
                # print("Task A: Performing async IO...")
                await chatWithImg(chatModel, img2textModel, user_input)
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


async def init_next_run_time(
    loop,
    init_sleep_time=Img2TextModelConfig.init_sleep_time,
    state=Img2TextModelConfig.state,
):
    # 初始化计划本
    async with state.lock:
        if state.next_run_time is None:
            state.next_run_time = loop.time() + init_sleep_time

async def chatWithImg_sleep_correction(
    chatModel,
    img2textModel,
    loop,
    user_input="",
    init_sleep_time=Img2TextModelConfig.init_sleep_time,
    state=Img2TextModelConfig.state,
):

    await init_next_run_time(loop, init_sleep_time, state)
    await asyncio.sleep(init_sleep_time)
    while True:     
        await execute_chatWithImg_sleep_correction(
                chatModel,
                img2textModel,
                loop,
                user_input=user_input,
                state=Img2TextModelConfig.state
            )
        

async def write_current_time():
    time = datetime.datetime.now()
    SHARE_STATE.user_last_input_time = time

async def get_user_uninput_timePeriod():

    user_last_input_time = SHARE_STATE.user_last_input_time
    time_diff = (datetime.datetime.now() - user_last_input_time).total_seconds()
    hours = int(time_diff / 3600)
    minutes = int((time_diff / 60) - hours * 60)
    seconds = int(time_diff - hours * 3600 - minutes * 60)
    timePeriod = f"{hours}时{minutes}分{seconds}秒"
    return timePeriod, int(time_diff)



async def agenda_to_datetime():

    # 将字符串字典转换回 datetime.datetime 对象字典
    agenda = {datetime.datetime.fromisoformat(k): "&".join(v) for k, v in SHARE_STATE.agenda.items()}

    return agenda   

async def monitor_user_input_time(chatModel, time_size=40, time_step=40):
    
    while True:
        await asyncio.sleep(0.5)
        # 如果还没记录用户输入时间
        if SHARE_STATE.user_last_input_time == 0.0:
            continue
        time_period, time_diff = await get_user_uninput_timePeriod()
        if time_diff != 0:
            if len(SHARE_STATE.agenda) == 0:
                time_window = np.random.randint(time_size, time_size + time_step)
                # 设定time_window秒未输入则判定True
                if time_diff % time_window == 0:
                    input_text = {"role": "assistant", "content": f"({str(await get_now_datetime())}) 已经{time_period}用户没理你啦!主动询问用户在干嘛!可以向用户发邮件进行询问"}

                    await chatWithTTS(chatModel, input_text)

            else:
                # agenda: {datetime.datetime: [content]}
                agenda = await agenda_to_datetime()
                agenda_arr = np.asarray(list(agenda.items()))
                # 超过日程时间了的日程
                agenda_todo_arr = agenda_arr[agenda_arr[:,0] <= datetime.datetime.now()]
                if len(agenda_todo_arr) != 0:
                    agenda_todo_time_content = {k.isoformat(): v for k,v in agenda.items() if k in agenda_todo_arr[:,0]}
                    input_text = {"role": "assistant", "content": f"({str(await get_now_datetime())}) 现在是日程任务的时间,完成日程任务:{agenda_todo_time_content},并且快到时间的日程任务也要提前提醒!"}
                    
                    # 更新主进程的agenda
                    SHARE_STATE.agenda = {k.isoformat(): v for k,v in agenda.items() if k not in agenda_todo_arr[:,0]}
                    delete_todo_time =np.vectorize(datetime.datetime.isoformat)(agenda_todo_arr[:,0]).tolist()
                    # 更新服务端的agenda
                    await chatModel._execute_tool("ScheduleServer", "delete_agenda", {"time": delete_todo_time})
                    await chatWithTTS(chatModel, input_text)











async def text_input():
    while True:
        query = await ainput(">> ")  # 异步输入
        if query.strip():
            return query.strip()

async def voice_input():
    while True:
        query = await record_and_recognize(key="ctrl+t")
        if query.strip():
            return query.strip()
        




