from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
from qwen_vl_utils import process_vision_info
import torch
from PIL import Image
from torchvision import transforms
from io import BytesIO


class Img2TextModel:
    def __init__(self):
    
        model_path = r"E:\VsCode-Python\pretrained_models\Qwen\Qwen2.5-VL-7B-Instruct"
        #配置8-bit量化参数
        self.quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,                 # 启用4-bit量化
            # load_in_8bit=True,                # 启用8-bit量化
            llm_int8_threshold=6.0            # 异常值检测阈值（默认值）
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

    def img2text(self, input_path, target_width=800, target_height=500):
    
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
                        {"type": "text", "text": "描述用户在干嘛"},
                    ],
                }
            ]

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
            generated_ids = self.model.generate(**inputs, max_new_tokens=64)
            generated_ids_trimmed = [
                out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )
            return output_text


if __name__ == "__main__":
    img_path = r"E:\VsCode-Python\Experiment\练习\QwenVL使用\data\imgs\2.png"
    # get model and processor
    model = Img2TextModel()
    # recognize img
    ans = model.img2text(img_path)
    print(ans)