import os
import threading
import asyncio
import glob


class TTSModelConfig:
    # "中文", "英文", "日文", "中英混合", "日英混合"
    text_language = "日英混合"
    cut_punc = "。."
    top_k = 15
    top_p = 0.9
    temperature = 1.0
    speed = 1.0

class FunctionThread(threading.Thread):
    def __init__(self, target, args=()):
        super().__init__()
        self.target = target
        self.args = args
        self.result = None  # 存储返回值的属性

    def run(self):
        self.result = self.target(*self.args)  # 执行目标函数并存储结果

    def get_result(self):
        self.join()  # 确保线程执行完毕
        return self.result
    
class ScreenshotState:
    def __init__(self):
        # 记录任务的下次计划执行时间
        self.next_run_time = None
        # 跟踪当前的睡眠任务以便取消
        self.current_sleep = None
        # 确保对共享状态的原子操作
        self.lock = asyncio.Lock()

    
API_MODEL_SYSTEM_PROMPT = f"用{TTSModelConfig.text_language[0]}文对话。根据用户正在做的事情，你需要根据提供的信息以第一人称对用户进行调侃，禁止输出如括号里动作和心里描写的文本。"    
LOCAL_MODEL_SYSTEM_PROMPT = f"根据用户正在做的事情，你需要根据提供的信息以第一人称对用户进行调侃，不要输出讲话人称呼。对话要符合角色性格。"


class Img2TextModelConfig:
    screenshot_folder_path = r"data\screenshot"
    init_sleep_time = 5
    quantization = "4bit" 
    max_new_tokens = 256
    state = ScreenshotState()
    freeze_time = 18
    model = []  

class LocalChatModelConfig:
    base_model = r"../../pretrained_models/Qwen/Qwen2.5-3B-Instruct"
    lora_path = None
    quantization = "8bit" 
    system_prompt = LOCAL_MODEL_SYSTEM_PROMPT
    temperature = 1.0
    top_k = 20
    top_p = 0.8
    max_new_tokens = 80
    repetition_penalty = 1.2
    model = []

class APIChatModelConfig:
    base_model = "deepseek-chat"  # GLM-4-Flash, deepseek-chat
    api_key = os.getenv("DEEPSEEK_API_KEY")    # ZHIPU_API_KEY, DEEPSEEK_API_KEY
    base_url = os.getenv("DEEPSEEK_API_KEY_URL")   # ZHIPU_API_KEY_URL, DEEPSEEK_API_KEY_URL
    system_prompt = API_MODEL_SYSTEM_PROMPT
    temperature = 1.0
    top_p = 0.7
    max_new_tokens = 160
    repetition_penalty = 1.4
    role = "kurisu"
    mdoel = []


class SoundObj:
    value = {"object": None}
        

class ChatModelResponse:
    outputs = {
        "response": "", 
        "translated_response": "",
        "chat_history": []
    }
    
    chat_history_length = 10




MUSIC_FILE_FOLDER = r"./music/*"
FILE_PATHS = glob.glob(MUSIC_FILE_FOLDER)
# 提取纯文件名（不带后缀）
filenames = [
    os.path.splitext(os.path.basename(path))[0]  # 分割路径并去除扩展名
    for path in FILE_PATHS
]
MUSIC_REPOSITORY = {i: n for i, n in enumerate(filenames)}
