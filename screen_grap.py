import mss
import uuid
import time
import numpy as np
import os
import asyncio
def screenshot(folder_path=r"data\screenshot"):
    with mss.mss() as sct:
        # 获取主显示器参数
        monitor = sct.monitors[1]  # 0为所有显示器，1为主屏
        screenshot = sct.grab(monitor)
        
        # 保存为PNG
        file_name = "screenshot" + uuid.uuid4().hex + ".jpg"
        img_path = os.path.join(folder_path, file_name)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=img_path)
        return img_path
def random_screenshot(folder_path, min_sleep_time=2, time_size=5):
    sleep_time = np.random.randint(min_sleep_time, min_sleep_time + time_size)
    time.sleep(sleep_time)
    img_path = screenshot(folder_path)
    return img_path

if __name__ == "__main__":
    folder_path = r"data\screenshot"
    img_path = random_screenshot(folder_path)
    print(img_path)