import json
from typing import Any
import csv
import numpy as np
import pandas as pd
import random
from mcp.server.fastmcp import FastMCP


# 初始化 MCP 服务器
mcp = FastMCP("PythonServer")
USER_AGENT = "Pythonserver-app/1.0"

@mcp.tool()
async def python_inter(py_code: str):
    """
    专门用于执行.py文件的python代码，并获取最终查询或处理结果。必须将结果赋值给一个变量。
    :param py_code: 字符串形式的Python代码，
    :return：代码运行的最终结果
    """    
    wrapped_code = ""
    global_vars_before = ""
    __user_func__ = ""
    line = ""

    g = locals()
    

    try:
        # 若是表达式，直接运行并返回
        result = eval(py_code, g)
        return json.dumps(str(result), ensure_ascii=False)


    except Exception:
        global_vars_before = set(g.keys())
        print(f"global_vars_before: {global_vars_before}")
        try:
            # 检查用户代码是否包含 return 语句
            if "return" in py_code:
                # 构造包装函数，将用户代码整体缩进
                wrapped_code = "def __user_func__():\n"
                for line in py_code.splitlines():
                    wrapped_code += "\t" + line + "\n"
                wrapped_code += "\nresult = __user_func__()\n"
                py_code = wrapped_code
            # 执行代码
            exec(py_code, g)
        except Exception as e:
            return json.dumps(f"代码执行时报错: {e}", ensure_ascii=False)
        global_vars_after = set(g.keys())
        new_vars = global_vars_after - global_vars_before
        print(f"new_vars: {new_vars}")
        if new_vars:
            # 只返回可序列化的变量值
            safe_result = {}
            for var in new_vars:
                try:
                    json.dumps(g[var]) # 尝试序列化，确保可以转换为 JSON
                    safe_result[var] = g[var]
                except (TypeError, OverflowError):
                    safe_result[var] = str(g[var]) # 如果不能序列化，则转换为字符串

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
