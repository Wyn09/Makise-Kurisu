import json
import asyncio
from mcp.server.fastmcp import FastMCP
import sys
import os
current_dir = os.getcwd()
sys.path.append(current_dir) 
from utils import delay_screenshot_time_or_not, chatWithImg
from screen_grap import screenshot
import config
from var_bridge_flow import SHARE_STATE


mcp = FastMCP("ScreenshotServer")
USER_AGENT = "ScreenshotServer-app/1.0"



@mcp.tool()
async def execute_screenshot():
    """
    查看user的屏幕内容  

    :return: 返回识别屏幕的内容
    """

    loop = asyncio.get_running_loop()
    # 屏幕要延长auto screenshot多一点
    await asyncio.sleep(2)  # 给2秒钟准备来让她看屏幕
    asyncio.create_task(
        delay_screenshot_time_or_not(loop, freeze_time=config.Img2TextModelConfig.freeze_time * 2.5)
    )

    print("*" * 80)
    img_file_path = screenshot(config.Img2TextModelConfig.screenshot_folder_path)
    text_of_img = await config.Img2TextModelConfig.model[0].img2text(img_file_path, user_input=SHARE_STATE.user_input[0], max_new_tokens=config.Img2TextModelConfig.max_new_tokens)
    return json.dumps({"result": text_of_img}, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run("stdio")