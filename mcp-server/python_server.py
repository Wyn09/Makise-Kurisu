import json
from typing import Any
import csv
import numpy as np
import pandas as pd
import random
from mcp.server.fastmcp import FastMCP
import asyncio
import matplotlib.pyplot as plt
import os
import glob

# 初始化 MCP 服务器
mcp = FastMCP("PythonServer")
USER_AGENT = "Pythonserver-app/1.0"


@mcp.tool()
async def python_inter(py_code: str):
    """
    1.专门用于执行.py文件的python代码，并获取最终查询或处理结果  
    2.如果用户要求绘图，禁止展示图片，直接将图片保存到本地，并告知用户图片已保存和保存的路径  
    3.必须将结果赋值给一个变量result  
    4.如果用户要求删除或修改文件，则再次询问用户删除或修改的文件的路径并要求用户输入"确认执行"，才可执行删除或修改文件代码！执行代码完毕后告知用户路径和删除或修改的文件  

    :param str py_code: 字符串形式的Python代码，
    :return: 代码运行的最终结果
    """    
    env = globals().copy()
        # 创建一个全新的局部环境，包含__builtins__
    env.update({
        "__name__": "__main__",
        "np": np,
        "pd": pd,
        "json": json,
        "plt": plt,
        "os": os,
        "glob": glob
    })
    
    try:
        # 尝试将代码当作表达式执行（例如 "3+4"）
        result = eval(py_code, env)
        return json.dumps(str(result), ensure_ascii=False)
    except Exception:
        global_vars_before = set(env.keys())
        # 如果当作表达式执行失败，则尝试用exec执行代码
        try:
            # 如果代码中含有 return 关键字，则将代码包装为一个函数，方便获取返回值
            if "return" in py_code:
                wrapped_code = "def __user_func__():\n"
                for line in py_code.splitlines():
                    wrapped_code += "\t" + line + "\n"
                wrapped_code += "\nresult = __user_func__()\n"
                py_code = wrapped_code

            exec(py_code, env)
        except Exception as e:
            return json.dumps(f"代码执行时报错: {e}", ensure_ascii=False)
        global_vars_after = set(env.keys())
        new_vars = global_vars_after - global_vars_before
        print(f"new_vars: {new_vars}")
        if new_vars:
            # 只返回可序列化的变量值
            safe_result = {}
            for var in new_vars:
                try:
                    json.dumps(env[var]) # 尝试序列化，确保可以转换为 JSON
                    safe_result[var] = env[var]
                except (TypeError, OverflowError):
                    safe_result[var] = str(env[var]) # 如果不能序列化，则转换为字符串

            return json.dumps(safe_result, ensure_ascii=False)
        else:
            return json.dumps("已经顺利执行代码", ensure_ascii=False)


async def main():
    # print(await python_inter("n1 = 3\nn2=4\nprint(n1+n2)"))
    # print(await python_inter("n3=5\nn4=n2+n3"))
    # print(await python_inter("import datetime\nnow = datetime.datetime.now()\nreturn now", "locals()"))
    print(await python_inter("import datetime\ndef f1():\n\tnow = datetime.datetime.now()\n\treturn now\ndef f2():\n\tnow=f1()\n\treturn now\nreturn f2()\nif __name__ == '__main__':\n\tf2()"))

if __name__ == "__main__":
    # 以标准 I/O 方式运行 MCP 服务器
    mcp.run(transport='stdio')
    # import asyncio
    # asyncio.run(main())
