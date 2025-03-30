from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig
import torch
from peft import PeftModel
from baidu_translate import translate
"""
使用封装的ChatModel类
"""

class ChatModel:
    def __init__(self, 
        base_model=r"pretrained_models\Qwen\Qwen2.5-0.5B-Instruct",    # 基础模型路径
        lora_path=r"models weights\chat_model\Qwen2.5-0.5B-Instruct\lora\train_2025-03-10-15-22-21",     # LoRA权重路径
        quantization=None, 
        system_prompt="",
        temperature=1.0,
        top_k=20,
        top_p=0.8,
        max_new_tokens=128,
        repetition_penalty=1.2,
        role="kurisu"
    ):
        self.language = "中文"
        self.system_prompt = system_prompt
        self.role = role
        self.sys_prompt_dic = {
            "kurisu": {
                "中文": r"./system_prompts/Kurisu_sys_prompt_ZH.txt",
                "粤语": r"./system_prompts/Kurisu_sys_prompt_ZH.txt",
                "英文": r"./system_prompts/Kurisu_sys_prompt_EN.txt",
                "日文": r"./system_prompts/Kurisu_sys_prompt_JP.txt",
                "中英混合": r"./system_prompts/Kurisu_sys_prompt_ZH.txt",
                "日英混合": r"./system_prompts/Kurisu_sys_prompt_JP.txt",
                "多语种混合": r"./system_prompts/Kurisu_sys_prompt_ZH.txt"
            },
            "2b":{
                "中文": r"./system_prompts/2B_sys_prompt_ZH.txt",
                "粤语": r"./system_prompts/2B_sys_prompt_ZH.txt",
                "英文": r"./system_prompts/2B_sys_prompt_EN.txt",
                "日文": r"./system_prompts/2B_sys_prompt_JP.txt",
                "中英混合": r"./system_prompts/Kurisu_sys_prompt_ZH.txt",
                "日英混合": r"./system_prompts/Kurisu_sys_prompt_JP.txt",
                "多语种混合": r"./system_prompts/Kurisu_sys_prompt_ZH.txt"
            }
        }
        
        if quantization == "4bit":
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quantization_type="nf4",  # 使用NormalFloat4量化
                bnb_4bit_use_double_quantization=True,  # 启用双重量化节省显存
                bnb_4bit_compute_dtype=torch.bfloat16
            )
        elif quantization == "8bit":
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True
            )

        # 初始化基础模型（修改模型加载方式）
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model,
            quantization_config=quantization_config if quantization is not None else None,  # 应用量化配置
            device_map="auto",
            torch_dtype=torch.bfloat16,
            # token=True  # 若使用私有模型需验证
        )

        if lora_path is not None:
            # # 应用LoRA适配器
            self.model = PeftModel.from_pretrained(self.model, lora_path)
            self.model = self.model.merge_and_unload()  # 合并LoRA权重到基础模型

        self.tokenizer = AutoTokenizer.from_pretrained(base_model)
        # 生成参数配置（对应原SamplingParams）
        self.generation_config = GenerationConfig(
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            max_new_tokens=max_new_tokens,
            repetition_penalty=repetition_penalty,
            pad_token_id=self.tokenizer.eos_token_id,
            do_sample=True
        )
        
    def chat(self, history = []):
            query = input("\n🤗 >>: ")
            if query.lower() == "exit":
                return history, "exit"
            if self.language not in ["中文", "粤语"]:
                query = translate(query, self.language)
                history, answer = self.chat_with_history(query, history, True)
            else:
                history, answer = self.chat_with_history(query, history, True)
            return history, answer
    def chat_with_history(self, query, history=[], through_chat=False):
        if self.language not in ["中文", "粤语"] and not through_chat:
            query = translate(query, self.language)
        def build_multiturn_prompt(history, query):
            """构建含历史对话的prompt（保持原格式）"""
            prompt = f"<|im_start|>system\n{self.system_prompt}<|im_end|>\n"
            for user_msg, assistant_msg in history:
                prompt += f"<|im_start|>user\n{user_msg}<|im_end|>\n"
                prompt += f"<|im_start|>assistant\n{assistant_msg}<|im_end|>\n"
            prompt += f"<|im_start|>user\n{query}<|im_end|>\n"
            prompt += "<|im_start|>assistant\n"
            return prompt

        # 构建prompt并编码
        prompt = build_multiturn_prompt(history, query)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        # 生成响应
        outputs = self.model.generate(
            **inputs,
            generation_config=self.generation_config,
        )
        
        # 解码并提取新生成的文本
        answer = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).replace("\n\n", "\n")
        # 因为有think，不能把think填入历史
        history.append((query, answer.strip()))
        return history, answer

    def set_model_language(self, language="中文"):
        self.language = language
        if self.language not in ["中文", "粤语"]:
                self.system_prompt = translate(self.system_prompt, self.language)
        # 读取角色信息
        with open(self.sys_prompt_dic[self.role][language], "r", encoding="utf-8") as f:
            self.system_prompt += "".join(f.readlines())


if __name__ == "__main__":
    """
    对外调用示例
    """
    system_prompt = "根据用户正在做的事情，你需要根据提供的信息以第一人称对用户进行调侃，不要输出讲话人称呼。对话要符合角色性格。"
    base_model = r"E:\VsCode-Python\pretrained_models\Qwen\Qwen2.5-3B-Instruct"
    lora_path = None
    quantization = "4bit"
    model = ChatModel(
        base_model=base_model, 
        lora_path=lora_path, 
        quantization=quantization, 
        system_prompt=system_prompt
    )
    history = []
    while 1:
        model.set_model_language("日文")
        history, text = model.chat(history)
        if text.lower() == "exit":
            break
        print(text)
    print("history: \n", history)