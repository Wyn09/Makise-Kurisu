from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
from qwen_vl_utils import process_vision_info
import torch
from PIL import Image
from torchvision import transforms
from io import BytesIO
import asyncio

class Img2TextModel:
    def __init__(self, quantization="8bit"):
    
        model_path = r"pretrained_models\Qwen\Qwen2.5-VL-3B-Instruct"
        #配置8-bit量化参数
        if quantization == "4bit":
            self.quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quantization_type="nf4",  # 使用NormalFloat4量化
                bnb_4bit_use_double_quantization=True,  # 启用双重量化节省显存
                bnb_4bit_compute_dtype=torch.bfloat16
            )
        elif quantization == "8bit":
            self.quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0
            )
        # 加载量化后的模型
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_path,
            quantization_config=self.quantization_config,
            device_map="auto",                # 自动分配GPU/CPU
            torch_dtype=torch.float16,         # 混合精度计算（显存优化）
            # attn_implementation="flash_attention_2",  # 启用Flash Attention加速
            trust_remote_code=True           # 信任远程代码（Qwen模型需要）
        )

        self.processor = AutoProcessor.from_pretrained(model_path)

    async def img2text(self, input_path, user_inputs="", max_new_tokens=256, target_width=800, target_height=600):
    
        # 打开图像
        with Image.open(input_path) as img:
            original_width, original_height = img.size
            if (original_width * original_height) > (target_width * target_height):
                # 计算等比例尺寸
                if target_width and not target_height:  # 按宽度缩放
                    ratio = target_width / original_width
                    target_height = int(original_height * ratio)
                elif target_height and not target_width:  # 按高度缩放
                    ratio = target_height / original_height
                    target_width = int(original_width * ratio)
                else:  # 按最大边限制
                    ratio = min(target_width/original_width, target_height/original_height)
                    target_width = int(original_width * ratio)
                    target_height = int(original_height * ratio)
                
                img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                # 将图像数据存入内存字节流
            
            buffer = BytesIO()
            img.save(buffer, format="PNG")  # 保持与原图相同格式

        # ===================
            messages = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "image",
                            "image": Image.open(buffer) ,
                        },
                        {"type": "text", "text": "详细描述用户在干嘛"},
                    ],
                }
            ]
            if user_inputs != "":
                messages.extend([{"role": "user", "content": user_inputs}])

            # Preparation for inference
            text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to("cuda")

            # Inference: Generation of the output
            generated_ids = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
            generated_ids_trimmed = [
                out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )
            return output_text[0].replace("\n","")


if __name__ == "__main__":
    img_path = r"E:\VsCode-Python\Experiment\练习\QwenVL使用\data\imgs\2.png"
    # get model and processor
    model = Img2TextModel("8bit")
    # recognize img
    ans = asyncio.run(model.img2text(img_path))
    print(ans)