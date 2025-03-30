import asyncio
import sys

async def f():
    """一个会持续运行的协程，用 while True + asyncio.sleep 实现。"""
    while True:
        # 假装做点耗时的事
        await asyncio.sleep(2)
        print("f() is running...")

async def read_input():
    """
    协程里读取用户输入。
    由于 input() 是同步阻塞，可以放到 run_in_executor 里，以免卡住事件循环。
    """

    #获取当前正在运行的事件循环（event loop）对象，并赋给变量 loop。
    #在 asyncio 中，所有协程的调度都是由此事件循环来负责。

    loop = asyncio.get_running_loop()
    while True:
        # 在后台线程执行阻塞IO，并等待结果

        # None 表示使用默认的线程池执行器。
        # loop.run_in_executor(...) 会返回一个 Future 对象，代表在线程中异步执行
        # await 等待此 Future 完成，在完成前，事件循环还能去处理其他协程（不会卡住）。
        line = await loop.run_in_executor(None, input)
        line = line.strip().lower()
        if line in ["quit", "exit"]:
            print("Exiting...")
            # 当检测到退出命令时，结束此协程
            break
        else:
            print(f"You entered: {line}")

async def main():
    # 1) 创建一个后台任务，让 f() 不断运行
    asyncio.create_task(f())

    # 2) 并发地在此协程里读用户输入
    await read_input()

    # read_input() 结束后(用户输入了quit/exit)，我们就可以结束整个事件循环
    # 也可以做一些清理操作，再结束

if __name__ == "__main__":
    asyncio.run(main())
