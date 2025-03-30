# import asyncio
# from aioconsole import ainput
# import time


# async def task_a_loop():
#     global last_task_a_execute_time
#     while True:
#         await asyncio.sleep(10)
#         print("Task A: Performing async IO...")
#         last_task_a_execute_time = asyncio.get_running_loop().time()
# async def handle_user_input(input_str, result_queue):
#     print(f"Task B: Processing '{input_str}'...")
#     await asyncio.sleep(2)  # 模拟异步操作
#     result = f"Result for '{input_str}'"
#     await result_queue.put(result)  # 将结果放入队列
#     return result

# async def task_b_loop(result_queue):
#     global last_input_time
#     while True:  
#         user_input = await ainput("Enter command: ")
#         last_input_time = time.time()
#         # 提交任务，并传递队列用于存储结果
#         asyncio.create_task(handle_user_input(user_input, result_queue))

# async def result_processor(result_queue):
#     """独立协程：从队列中获取结果并处理"""
#     while True:
#         result = await result_queue.get()
#         print(f"\n[Result] {result}")


# async def main():
#     result_queue = asyncio.Queue()
#     # 启动所有任务
#     await asyncio.gather(
#         task_a_loop(),
#         task_b_loop(result_queue),
#         result_processor(result_queue)
#     )

# if __name__ == "__main__":
#     asyncio.run(main())






import asyncio
from aioconsole import ainput

class TaskAState:
    def __init__(self):
        # 记录任务A的下次计划执行时间
        self.next_run_time = None
        # 跟踪当前的睡眠任务以便取消
        self.current_sleep = None
        # 确保对共享状态的原子操作
        self.lock = asyncio.Lock()

async def task_a_loop(state):
    loop = asyncio.get_event_loop()
    # 初始化计划本
    async with state.lock:
        if state.next_run_time is None:
            state.next_run_time = loop.time() + 10

    while True:
        async with state.lock:
            now = loop.time()
            wait_time = state.next_run_time - now  # 计算剩余等待时间

            if wait_time <= 0:  # 到工作时间了
                print("Task A: Performing async IO...")
                state.next_run_time = now + 10  # 计划10秒后再工作
                continue

            # 设置新闹钟
            state.current_sleep = asyncio.create_task(asyncio.sleep(wait_time))
        try:
            await state.current_sleep
        except asyncio.CancelledError:
            continue  # 闹钟被取消，重新检查计划本
        finally:
            async with state.lock:
                state.current_sleep = None  # 清空当前闹钟
        print("Task A: Performing async IO...")
        async with state.lock:
            state.next_run_time = loop.time() + 10

async def handle_user_input(input_str, result_queue):
    print(f"Task B: Processing '{input_str}'...")
    await asyncio.sleep(2)  # Simulate async processing
    result = f"Result for '{input_str}'"
    await result_queue.put(result)
    return result

async def task_b_loop(result_queue, state):
    loop = asyncio.get_event_loop()
    while True:
        user_input = await ainput("Enter command: ")
        current_time = loop.time()
        desired_next_run = current_time + 5  # 5秒保护期

        async with state.lock:
            if desired_next_run > state.next_run_time:  # 需要延长计划
                state.next_run_time = desired_next_run
                if state.current_sleep and not state.current_sleep.done():
                    state.current_sleep.cancel()  # 打碎旧闹钟
        asyncio.create_task(handle_user_input(user_input, result_queue))

async def result_processor(result_queue):
    while True:
        result = await result_queue.get()
        print(f"\n[Result] {result}")

async def main():
    result_queue = asyncio.Queue()
    state = TaskAState()
    await asyncio.gather(
        task_a_loop(state),
        task_b_loop(result_queue, state),
        result_processor(result_queue)
    )

if __name__ == "__main__":
    asyncio.run(main())