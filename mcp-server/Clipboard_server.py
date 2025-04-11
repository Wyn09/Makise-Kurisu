from mcp.server.fastmcp import FastMCP
import json
import pyperclip
import os
import sys
current_dir = os.getcwd()
sys.path.append(current_dir) 
from baidu_translate import translate


mcp = FastMCP("ClipboardServer")
USER_AGENT = "ClipboardServer-app/1.0"


async def read_clipboard():
    """
    读取user剪贴板最后一次复制的内容  

    :return: 用户剪贴板的内容
    """
    content = pyperclip.paste()
    return json.dumps({"result": content}, ensure_ascii=False)

@mcp.tool()
async def write_clipboard(content):
    """
    将内容写入user的剪贴板,帮用户复制内容  

    :param str content: 写入user剪贴板的内容
    :return: 写入结果
    """
    try:
        pyperclip.copy(content)
        return json.dumps({"result": "Successful!"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"result": f"Failed: {e}"}, ensure_ascii=False)

@mcp.tool()
async def translate_clipboard_content(text="", lang="中文"):
    """
    翻译文本。该函数可以直接读取剪贴板并翻译
    
    :param str text: 可选参数,默认为空字符串,为空字符串则翻译最近一条剪切板内容。也可翻译传入的文本。
    :param str lang: 可选参数,默认为中文。可选翻译的语言: 中文 英文 日文
    :return: 翻译后的文本
    """
    try:
        if text == "":
            text = await read_clipboard()
            text = json.loads(text)["result"]
        trans_result = await translate(text, lang)
        return json.dumps({"result": trans_result}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"result": f"Failed: {e}"}, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run("stdio")