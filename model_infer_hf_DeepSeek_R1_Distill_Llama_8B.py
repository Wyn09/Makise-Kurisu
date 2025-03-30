from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig
import torch
from peft import PeftModel
from baidu_translate import translate
"""
使用封装的ChatModel类
"""

class ChatModel:
    def __init__(self):
        self.language = "中文"
        self.system_prompt = ""
        self.sys_prompt_dic = {
            "中文": r"./system_prompts/Kurisu_sys_prompt_ZH.txt",
            "粤语": r"./system_prompts/Kurisu_sys_prompt_ZH.txt",
            "英文": r"./system_prompts/Kurisu_sys_prompt_EN.txt",
            "日文": r"./system_prompts/Kurisu_sys_prompt_JP.txt"
        }

        # 基础模型路径
        base_model = r"pretrained_models\DeepSeek-R1-Distill-Llama-8B"
        # LoRA权重路径
        lora_path = r"models weights\chat_model\DeepSeek-R1-8B-Distill\lora\train_2025-03-13-08-58-23"
        
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",  # 使用NormalFloat4量化
            bnb_4bit_use_double_quant=True,  # 启用双重量化节省显存
            bnb_4bit_compute_dtype=torch.bfloat16
        )

        # 初始化基础模型（修改模型加载方式）
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model,
            quantization_config=quant_config,  # 应用4-bit量化配置
            device_map="auto",
            torch_dtype=torch.bfloat16,
            # token=True  # 若使用私有模型需验证
        )

        # # 应用LoRA适配器
        self.model = PeftModel.from_pretrained(self.model, lora_path)
        self.model = self.model.merge_and_unload()  # 合并LoRA权重到基础模型

        self.tokenizer = AutoTokenizer.from_pretrained(base_model)
        # 生成参数配置（对应原SamplingParams）
        self.generation_config = GenerationConfig(
            temperature=1.2,
            top_k=20,
            top_p=0.8,
            max_new_tokens=1024,
            repetition_penalty=1.2,
            pad_token_id=self.tokenizer.eos_token_id,
            do_sample=True
        )
        
    def chat(self, history = []):
            query = input("\n🤗 >>: ")
            if query.lower() == "exit":
                return history, "exit"
            if self.language not in ["中文", "粤语"]:
                query = translate(query, self.language)
                history, answer = self.chat_with_history(query, history)
            else:
                history, answer = self.chat_with_history(query, history)
            return history, answer
    def chat_with_history(self, query, history=[]):
        def build_multiturn_prompt( history, query):
            # 系统提示仅出现在首轮对话前
            prompt = f"<｜begin▁of▁sentence｜>{self.system_prompt}"
            # 历史对话处理
            for idx, (user_msg, assistant_msg) in enumerate(history):
                prompt += f"<｜User｜>{user_msg}"
                prompt += f"<｜Assistant｜>{assistant_msg}<｜end▁of▁sentence｜>"
            prompt += f"<｜User｜>{query}"  
            prompt += "<｜Assistant｜><think>"  
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
        answer = "<think>" + self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).replace("\n\n", "\n")
        # 因为有think，不能把think填入历史
        history.append((query, answer.split("</think>")[1].strip()))
        return history, answer

    def set_model_language(self, language="中文"):
        self.language = language
        # 读取角色信息
        with open(self.sys_prompt_dic[language], "r", encoding="utf-8") as f:
            self.system_prompt = "".join(f.readlines())


if __name__ == "__main__":
    """
    对外调用示例
    """
    model = ChatModel()
    history = []
    while 1:
        model.set_model_language("中文")
        history, text = model.chat(history)
        if text.lower() == "exit":
            break
        print(text)
    print("history: \n", history)