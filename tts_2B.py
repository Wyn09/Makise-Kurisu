import subprocess
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

def start_2B(port=9880):
    # 执行命令（无需捕获输出，结果会显示在新窗口）
    subprocess.run(os.getenv("2B") + str(port), shell=True)
    return port

start_2B()