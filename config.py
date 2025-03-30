import os
import threading
import asyncio


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


class TTSModelConfig:
    # "中文", "英文", "日文", "中英混合", "日英混合", "多语种混合"
    text_language = "日英混合"
    cut_punc = "。"
    top_k = 20
    top_p = 0.8
    temperature = 1.0
    speed = 1.0
    
API_MODEL_SYSTEM_PROMPT = f"用{TTSModelConfig.text_language}对话。根据用户正在做的事情，你需要根据提供的信息以第一人称对用户进行调侃，禁止非对话描述，如'(突然脸红)'"    
LOCAL_MODEL_SYSTEM_PROMPT = f"根据用户正在做的事情，你需要根据提供的信息以第一人称对用户进行调侃，不要输出讲话人称呼。对话要符合角色性格。"


class Img2TextModelConfig:
    screenshot_folder_path = r"data\screenshot"
    init_sleep_time = 5
    quantization = "4bit" 
    max_new_tokens = 256
    state = ScreenshotState()
    freeze_time = 12

class ChatModelConfig:
    base_model = r"../../pretrained_models/Qwen/Qwen2.5-3B-Instruct"
    lora_path = None
    quantization = "8bit" 
    system_prompt = LOCAL_MODEL_SYSTEM_PROMPT
    temperature=1.0
    top_k=20
    top_p=0.8
    max_new_tokens=80
    repetition_penalty=1.2

class APIChatModelConfig:
    base_model = "deepseek-chat"
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_API_KEY_URL")
    system_prompt = API_MODEL_SYSTEM_PROMPT
    temperature = 1.0
    top_p = 0.7
    max_new_tokens = 160
    repetition_penalty = 1.2
    role = "kurisu"



