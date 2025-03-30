import asyncio
from playwright.async_api import async_playwright
import base64
import io
import os
import sounddevice as sd
import soundfile as sf
import shutil
from constant import get_constant
from preset import setup_reference
from model_hf_Qwen2d5 import ChatModel
from baidu_translate import translate

REMOVE_PATH, CHARACTER, REF_AUDIO_TEXT, WEIGHTS_MODEL_PATH, REF_LANGUAGE_OPTIONS, LANGUAGE_OPTIONS, CUT_METHOD_OPTIONS = get_constant()

async def synthesize_once(page, user_text, old_src):
    """
    1) 填写「需要合成的文本」（#component-28 textarea）
    2) 点击「合成语音」按钮 (#component-47)
    3) 等待 <audio> 元素出现
    4) 获取其 src (可能是 data: 或 blob:) 并返回
    """
    print(f"(看我狠狠地！😤🤯😤🤯... 🐾🐾🐾)")
    await page.fill("#component-28 textarea", user_text)

    # 点击合成按钮
    await page.click("#component-47")

    while True:
        try:
            # 这里给 5 分钟超时
            await page.wait_for_selector("#component-48 audio", state="attached", timeout=300000)
        except:
            print("超过5分钟，语音合成仍未完成，放弃。")
            return None, old_src

        audio_src = await page.get_attribute("#component-48 audio", "src")
        if audio_src != old_src:
            # 说明出现了新的音频
            old_src = audio_src
            return audio_src, old_src

async def blob_to_base64(page, blob_url: str) -> str:
    """
    在浏览器里fetch(blobUrl)，得到ArrayBuffer后再转base64。
    返回的base64不带 'data:audio/wav;base64,' 前缀
    """
    js_code = f"""
    async () => {{
        const resp = await fetch("{blob_url}");
        const ab = await resp.arrayBuffer();
        const bytes = new Uint8Array(ab);
        let binary = '';
        for (let i = 0; i < bytes.length; i++) {{
            binary += String.fromCharCode(bytes[i]);
        }}
        return btoa(binary);
    }}
    """
    b64_data = await page.evaluate(js_code)
    return b64_data

async def main():
    history = []
    model = ChatModel()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("http://localhost:9872/") 

        # === 1) 预先设置(只做一次) ===
        await setup_reference(page, True)

        old_src = ""

        # === 2) 循环让用户输入要合成的文本 ===
        history = []
        while True:

            # 返回值是聊天记录和刚刚生成的对话
            history, text = model.chat(history)
            
            if text.lower() == "exit":
                break

            # 调用合成
            text = text.replace("\n", " ")
            audio_src, old_src = await synthesize_once(page, text, old_src)
            if not audio_src:
                print("未获取到音频src!")
                continue
            masked_audio_src = "***" + audio_src.split("-")[-1]
            
            text_translated = translate(text, "中文")
            text += "\n" + "(" + text_translated + ")"
            print(text)
            
            # print("音频 src =>", masked_audio_src)
            
            # 区分 data:audio/wav;base64 与 blob:
            if audio_src.startswith("data:audio/wav;base64,"):
                prefix = "data:audio/wav;base64,"
                b64_data = audio_src[len(prefix):]
                wav_bytes = base64.b64decode(b64_data)
            elif audio_src.startswith("blob:"):
                b64_data = await blob_to_base64(page, audio_src)
                wav_bytes = base64.b64decode(b64_data)
            else:
                print("音频不是 data:audio/wav;base64 也不是 blob:，无法处理！")
                continue

            # 解码并播放
            try:
                data, samplerate = sf.read(io.BytesIO(wav_bytes))
                # print(f"采样率: {samplerate}, shape={data.shape}")
                sd.play(data, samplerate=samplerate)
                sd.wait()
            except Exception as e:
                print("音频解码失败:", e)

        await browser.close()

    text = input("是否删除已生成音频的文件?(y/n) 🤔\n")
    while True:
        try:
            if text.lower() == "y":
                shutil.rmtree(REMOVE_PATH)
                os.makedirs(REMOVE_PATH)
                return
            elif text.lower() == "n":
                return
            else:
                print("无效输入，重新输入。")
        except Exception as e:
            print("路径格式错误:", e)
            return

if __name__ == "__main__":
    asyncio.run(main())
