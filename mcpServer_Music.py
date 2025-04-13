import pygame
import json
import io
import numpy as np
import os
import glob
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MusicServer")
USER_AGENT = "MusicServer-app/1.0"


class SoundObj:
    value = {"object": None}


MUSIC_FILE_FOLDER = r"./music/*"
FILE_PATHS = glob.glob(MUSIC_FILE_FOLDER)
# 提取纯文件名（不带后缀）
filenames = [
    os.path.splitext(os.path.basename(path))[0]  # 分割路径并去除扩展名
    for path in FILE_PATHS
]
MUSIC_REPOSITORY = {i: n for i, n in enumerate(filenames, start=1)}


@mcp.tool()
async def read_music_repository() -> dict:
    """
    获取音乐库所有的音乐

    :return: 以字典(索引:文件名)形式返回音乐库所有的音乐
    """
    return json.dumps(MUSIC_REPOSITORY, ensure_ascii=False)



@mcp.tool()
async def play_music(index: int): 
    """
    根据索引播放音乐  

    :param int index: 音乐的索引,如果没有user点的音乐,则赋值-1
    :return: 是否成功播放
    """

    async def play(index):
        # 初始化音频模块
        pygame.mixer.init()
        # 如果未找到目标音乐
        if index == -1:
            index = np.random.randint(0, len(FILE_PATHS))

        # 读取文件到内存
        with open(FILE_PATHS[index - 1], "rb") as f:
            audio_data = f.read()
        # 从内存加载音频
        # 如果之前已经播放了一个音乐，则停止之前的音乐
        if SoundObj.value["object"]:
            SoundObj.value["object"].stop()
        SoundObj.value["object"] = pygame.mixer.Sound(io.BytesIO(audio_data))
        SoundObj.value["object"].play()

    try:
        await play(index)
        return json.dumps({"result": "成功播放."}, ensure_ascii=False) 
    except Exception as e:
        return json.dumps({"result": f"播放失败: {e}"}, ensure_ascii=False)


@mcp.tool()
async def stop_music():
    """
    停止播放音乐  

    :return: 是否停止播放
    """
    if SoundObj.value["object"]:
        SoundObj.value["object"].stop()
        SoundObj.value["object"] = None
        return json.dumps({"result": f"已停止播放"}, ensure_ascii=False)
    else:
        return json.dumps({"result": f"停止无效: user没有点歌，所以并没有音乐在播放哦。"}, ensure_ascii=False)




if __name__ == "__main__":
    # 以标准 I/O 方式运行 MCP 服务器
    mcp.run(transport='stdio')

