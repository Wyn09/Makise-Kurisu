import asyncio
from config import *
from multi_function import *
from baidu_translate import translate
from text2audio import synthesize_and_play
from screen_grap import screenshot
import os


async def get_random_sleep_time(response, alpha=5):
    min_sleep_time = len(response) / alpha
    time_size = min_sleep_time ** 0.5
    sleep_time = np.random.randint(min_sleep_time, min_sleep_time + time_size)
    return sleep_time


async def random_sleep_with_response(response, alpha=5):
    sleep_time = await get_random_sleep_time(response, alpha)
    await asyncio.sleep(sleep_time)



async def chatWithTTS(
        chatModel,
        text,
        text_language=TTSModelConfig.text_language,
        cut_punc=TTSModelConfig.cut_punc,
        top_k=TTSModelConfig.top_k,
        top_p=TTSModelConfig.top_p,
        temperature=TTSModelConfig.temperature,
        speed=TTSModelConfig.speed
):

    ChatModelResponse.outputs["chat_history"], ChatModelResponse.outputs["response"] = \
    await chatModel.chat_with_history(text, ChatModelResponse.outputs["chat_history"])
    await synthesize_and_play(
        ChatModelResponse.outputs["response"],     
        text_language=text_language,
        cut_punc=cut_punc,
        top_k=top_k,
        top_p=top_p,
        temperature=temperature,
        speed=speed,
    )
    print(f"\nResponse:\n\t{ChatModelResponse.outputs["response"]}")
    # print(f"Length of chat_history:\t{int(len(ChatModelResponse.outputs["chat_history"]) // 2)}\n")

    # 如果是本地部署的Model，并且不是中文或者粤语，那么就调用翻译API
    if chatModel.language not in ["中文", "粤语", "中英混合"]:
        ChatModelResponse.outputs["translated_response"] = await translate(ChatModelResponse.outputs["response"].replace("\n", ""))
        print(f"\n\t({ChatModelResponse.outputs["translated_response"]})")

    if len(ChatModelResponse.outputs["chat_history"]) >= ChatModelResponse.chat_history_length * 2:
            ChatModelResponse.outputs["chat_history"] = ChatModelResponse.outputs["chat_history"][-ChatModelResponse.chat_history_length * 2:]




async def chatWithImg(
    chatModel,
    img2textModel,
    user_inputs="",
    screenshot_folder_path=Img2TextModelConfig.screenshot_folder_path, 
    max_new_tokens=Img2TextModelConfig.max_new_tokens,
    
):
    print("*" * 80)
    img_file_path = screenshot(screenshot_folder_path)
    # print("截图已保存在: ", img_file_path)
    text_of_img = await img2textModel.img2text(img_file_path, user_inputs=user_inputs, max_new_tokens=max_new_tokens)
    # print(f"\nText Of Img:\n\t{text_of_img}")
    await chatWithTTS(chatModel, text_of_img + user_inputs)

    # print(f"Length of chat_history:\t{len(ChatModelResponse.outputs["chat_history"])}\n")

    # 删除抓取的图片
    os.remove(img_file_path)



async def delay_screenshot_time_or_not(loop, state=Img2TextModelConfig.state, freeze_time=Img2TextModelConfig.freeze_time):
        current_time = loop.time()
        desired_next_run = current_time + freeze_time  # freeze_time 保护期
        try:
            async with state.lock:
            # 如果指定的执行时间比真实执行时间要晚，那么就赋值为指定的执行时间
                if desired_next_run > state.next_run_time:  # 需要延长计划
                    state.next_run_time = desired_next_run
                    if state.current_sleep and not state.current_sleep.done():
                        state.current_sleep.cancel()  # 打碎旧闹钟
            print(f"\nstate.next_run_time: ", state.next_run_time)
            
        except Exception as e:
             pass