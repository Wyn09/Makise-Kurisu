import asyncio
from aioconsole import ainput

async def task_a_loop():
    while True:
        await asyncio.sleep(10)
        print("Task A: Performing async IO...")

async def handle_user_input(input_str, result_queue):
    print(f"Task B: Processing '{input_str}'...")
    await asyncio.sleep(2)  # 模拟异步操作
    result = f"Result for '{input_str}'"
    await result_queue.put(result)  # 将结果放入队列
    return result

async def task_b_loop(result_queue):
    while True:
        user_input = await ainput("Enter command: ")
        # 提交任务，并传递队列用于存储结果
        asyncio.create_task(handle_user_input(user_input, result_queue))

async def result_processor(result_queue):
    """独立协程：从队列中获取结果并处理"""
    while True:
        result = await result_queue.get()
        print(f"\n[Result] {result}")
        # 保持输入行在最后一行
        print("\033[2K\rEnter command: ", end="")

async def main():
    result_queue = asyncio.Queue()
    # 启动所有任务
    await asyncio.gather(
        task_a_loop(),
        task_b_loop(result_queue),
        result_processor(result_queue)
    )

if __name__ == "__main__":
    asyncio.run(main())