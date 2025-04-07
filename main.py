import asyncio
from aioconsole import ainput
from qwen_vl_3B_Instruct import Img2TextModel
from model_hf_Qwen2d5 import ChatModel as LocalChatModel
from model_from_api import APIChatModel
from model_intent import IntentModel
import os
import time
from config import *
from multi_function import *


# chatModel = LocalChatModel(
#     base_model=ChatModelConfig.base_model, 
#     lora_path=ChatModelConfig.lora_path, 
#     quantization=ChatModelConfig.quantization, 
#     system_prompt=ChatModelConfig.system_prompt,
#     temperature=ChatModelConfig.temperature,
#     top_k=ChatModelConfig.top_k,
#     top_p=ChatModelConfig.top_p,
#     max_new_tokens=ChatModelConfig.max_new_tokens,
#     repetition_penalty=ChatModelConfig.repetition_penalty
# )

chatModel = APIChatModel(
    base_model=APIChatModelConfig.base_model, 
    api_key=APIChatModelConfig.api_key,
    base_url=APIChatModelConfig.base_url,
    system_prompt=APIChatModelConfig.system_prompt,
    temperature=APIChatModelConfig.temperature,
    top_p=APIChatModelConfig.top_p,
    max_new_tokens=APIChatModelConfig.max_new_tokens,
    repetition_penalty=APIChatModelConfig.repetition_penalty,
    role=APIChatModelConfig.role
)
img2textModel = Img2TextModel(Img2TextModelConfig.quantization)
intentModel = IntentModel()
chatModel.set_model_language(TTSModelConfig.text_language)


async def recognize_screenshot(
    chatModel,
    img2textModel
):
    loop = asyncio.get_running_loop()
    asyncio.create_task(
        chatWithImg_sleep_correction(
            chatModel,
            img2textModel,
            loop
        )
    )

async def read_user_inputs(
    chatModel,
    img2textModel,
    intentModel
):
    loop = asyncio.get_running_loop()
    while True:
        user_input = await ainput("🤗 >> ")
        user_input = user_input.strip().lower()
        if user_input in ["quit", "exit"]:
            print("\nExiting... ", end="")
            for x in "😱🐾🐾🐾":
                print(x, end=" ")
                time.sleep(0.5)
            # 当检测到退出命令时，结束进程
            # print(ChatModelResponse.outputs["chat_history"])
            os._exit(0)
        else:
            print(f"🤓 : {user_input}")
        
            asyncio.create_task(
                handle_user_inputs(
                    chatModel, 
                    img2textModel, 
                    intentModel, 
                    user_input, 
                    loop
                )
            )


async def main():
    
    print(f"\ninit time: {asyncio.get_running_loop().time()}")

    await asyncio.gather(
         recognize_screenshot(chatModel, img2textModel),
         read_user_inputs(chatModel, img2textModel, intentModel)
    )

if __name__ == "__main__":
    asyncio.run(main())

    pass