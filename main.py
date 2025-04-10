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
#     base_model=LocalChatModelConfig.base_model, 
#     lora_path=LocalChatModelConfig.lora_path, 
#     quantization=LocalChatModelConfig.quantization, 
#     system_prompt=LocalChatModelConfig.system_prompt,
#     temperature=LocalChatModelConfig.temperature,
#     top_k=LocalChatModelConfig.top_k,
#     top_p=LocalChatModelConfig.top_p,
#     max_new_tokens=LocalChatModelConfig.max_new_tokens,
#     repetition_penalty=LocalChatModelConfig.repetition_penalty
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
ChatModelResponse.outputs["chat_history"].append({"role": "system", "content": chatModel.system_prompt})

APIChatModelConfig.mdoel.append(chatModel)
Img2TextModelConfig.model.append(img2textModel)




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
    try:
        loop = asyncio.get_running_loop()
        while True:
            user_input = await ainput("🤗 >> ")
            user_input = user_input.strip()
            if user_input.lower() in ["quit", "exit"]:
                print("\nExiting... ", end="")
                for x in "😱🐾🐾🐾":
                    print(x, end=" ")
                    time.sleep(0.5)

                await chatModel.cleanup()
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

    except Exception as e:
        # print(e)
        pass


async def main():
    try:
        await chatModel.post_init()
        print(f"\ninit time: {asyncio.get_running_loop().time()}")
        
        await asyncio.gather(
             recognize_screenshot(chatModel, img2textModel),
            read_user_inputs(chatModel, img2textModel, intentModel)
        )
    except asyncio.CancelledError as e:
        print(e)
    finally:
        await chatModel.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Unhandled exception: {e}")

    pass