import requests
import hashlib
import random
import os

# 禁用系统代理
os.environ['NO_PROXY'] = 'fanyi-api.baidu.com'

APP_ID = "20250311002299349"  # 替换为实际值
SECRET_KEY = "wg0VK7qUFnyv1tBCE7ca"  # 替换为实际值
LANGUAGE_DICT = {
    "中文": "zh",
    "英文": "en",
    "日文": "jp",
    "粤语": "zh"
}


def baidu_translate(text, appid, secret_key, tgt_language):
    url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    salt = str(random.randint(10000, 99999))
    sign = hashlib.md5(f"{appid}{text}{salt}{secret_key}".encode()).hexdigest()

    params = {
        "q": text,
        "from": "auto",
        "to": LANGUAGE_DICT[tgt_language],
        "appid": appid,
        "salt": salt,
        "sign": sign
    }
    
    try:
        # 添加重试逻辑
        session = requests.Session()
        session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
        response = session.post(url, data=params, timeout=10)
        return response.json()
    except Exception as e:
        print(f"最终请求失败：{str(e)}")
        return None

def translate(text, tgt_language="中文"):
    translated_text = baidu_translate(text, APP_ID, SECRET_KEY, tgt_language)
    return translated_text["trans_result"][0]["dst"]


if __name__ == "__main__":
    text = translate("你好", "日文")
    print(text)