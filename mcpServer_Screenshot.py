import json
import asyncio
from mcp.server.fastmcp import FastMCP
from utils import delay_screenshot_time_or_not, chatWithImg
from screen_grap import screenshot_buffer
from config import Img2TextModelConfig
from qwen_vl_3B_Instruct import Img2TextModel



mcp = FastMCP("ScreenshotServer")
USER_AGENT = "ScreenshotServer-app/1.0"



img2textModel = Img2TextModel(Img2TextModelConfig.quantization)




@mcp.tool()
async def execute_screenshot(user_input=""):
    """
    查看user的屏幕内容  
    
    :param str user_input: user输入的文本内容,query
    :return: 返回识别屏幕的内容
    """
    
    # 屏幕要延长auto screenshot多一点
    await asyncio.sleep(2)  # 给2秒钟准备来让她看屏幕
    
    # 这里换成了直接用内存传输数据，避免了io
    img_buffer = await screenshot_buffer()
    # print("截图已保存在: ", img_file_path)
    text_of_img = await img2textModel.img2text(img_buffer, user_input=user_input, max_new_tokens=Img2TextModelConfig.max_new_tokens)
    return json.dumps({"result": text_of_img}, ensure_ascii=False)


if __name__ == "__main__":
   
    mcp.run("stdio")