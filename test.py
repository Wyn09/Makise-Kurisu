import asyncio
from aioconsole import ainput  # 异步输入库

async def task_a_loop():
    while True:
        await asyncio.sleep(10)  # 每隔10秒执行一次
        await async_io_operation()  # 异步IO操作（如aiohttp请求）

async def async_io_operation():
    # 使用异步库实现IO（例如aiohttp）
    print("Task A: Performing async IO...")

async def task_b_loop():
    while True:
        # 非阻塞读取用户输入
        user_input = await ainput("Enter command: ")
        
        # 提交IO操作到事件循环（不阻塞输入）
        asyncio.create_task(handle_user_input(user_input))

async def handle_user_input(input_str):
    print(f"Task B: Processing '{input_str}'...")
    await async_io_response(input_str)  # 异步处理并返回结果
    return 1

async def async_io_response(input_str):
    # 模拟异步IO（如数据库查询）
    await asyncio.sleep(2)
    print(f"Task B: Result for '{input_str}' received.")    
async def main():
    # 启动任务A和任务B
    task_a = asyncio.create_task(task_a_loop())
    task_b = asyncio.create_task(task_b_loop())
    
    # 等待任意任务结束（按需调整）
    await asyncio.gather(task_a, task_b)

if __name__ == "__main__":
    asyncio.run(main())