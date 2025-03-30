"""
语音识别
"""
import os
import time
from playwright.sync_api import sync_playwright

FOLDER_PATH = r"D:\GPT-SoVITS-v3lora-20250228\GPT-SoVITS-v3lora-20250228\GPT-SoVITS-v3lora-20250228\output\slicer_opt"
WEBSITE_URL = "https://products.aspose.ai/total/zh/speech-to-text/"
SUPPORTED_EXT = ['.mp3', '.wav', '.m4a', '.webm', '.mp4', '.mpeg']

COUNT = 1

def process_audio_files(save_path):
    global COUNT
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        results = {}
        
        # 初始访问
        page.goto(WEBSITE_URL)
        # time.sleep(3)  # 确保完全加载
        with open(save_path, "a", encoding="utf-8") as f:
            for filename in os.listdir(FOLDER_PATH):
                if not any(filename.lower().endswith(ext) for ext in SUPPORTED_EXT):
                    continue

                file_path = os.path.join(FOLDER_PATH, filename)
                
                try:
                    # 上传文件
                    with page.expect_file_chooser() as fc_info:
                        page.click('label.file-upload-label')  # 模拟真实点击
                    file_chooser = fc_info.value
                    file_chooser.set_files(file_path)

                    # 直接等待处理完成（关键修改部分）
                    # time.sleep(10)  # 根据测试调整等待时长
                    # 随便点个
                    page.click('#cke_20')
                    # 点击p
                    page.click('#cke_elementspath_7_1')
                    # 点击复制按钮
                    page.click('#cke_13')
                    # 获取剪贴板内容（核心代码）
                    copied_text = page.evaluate('''() => {
                        return navigator.clipboard.readText()
                            .then(text => text)
                            .catch(err => `ERROR: ${err.message}`);
                    }''')  # 
                    COUNT += 1
                    print(f"✅ Count: {COUNT}, 读取到内容: {copied_text}")
                    # 写入前把光标移动到下一行的开始
                    f.write(f"✅ Count: {COUNT}, 读取到内容: {copied_text}\n")
                    results[filename] = copied_text
                    
                    # time.sleep(10)

                    # 重置操作
                    page.click('#lnkStartAgain')
                    # page.wait_for_selector('body.cke_editable p:empty', timeout=30000)
                    # time.sleep(1)

                except Exception as e:
                    print(f"❌ 处理 {filename} 失败：{str(e)}")
                    COUNT += 1
                    print("已处理完个数: ", COUNT)
                    results[filename] = "ERROR: " + str(e)
                    # 恢复页面状态
                    page.goto(WEBSITE_URL)
                    # time.sleep(2)

        context.close()
        return results

if __name__ == "__main__":
    save_path = r"speech_text.txt"
    recognition_results = process_audio_files(save_path)

    
    # with open(save_path, "w", encoding="utf-8") as f:
    #     for filename, text in recognition_results.items():
    #         f.write(f"【{filename}】\n{text}\n{'='*50}\n")