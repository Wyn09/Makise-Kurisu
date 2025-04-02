import asyncio
from interaction_webui_config import get_constant

REMOVE_PATH, CHARACTER, REF_AUDIO_TEXT, WEIGHTS_MODEL_PATH, REF_LANGUAGE_OPTIONS, LANGUAGE_OPTIONS, CUT_METHOD_OPTIONS = get_constant()

async def set_weights(page, character_str: str):
    """
    设置 #component-5这个下拉框的值为 character_str对应的权重文件路径
    """
    # 1) 点击下拉区域，展开选项
    await page.click("#component-5 .secondary-wrap")

    # 2) 等待下拉容器出现
    await page.wait_for_selector("ul.options[role='listbox']", state="visible")

    # 3) 根据 aria-label 匹配 <li>
    # 设置GPT-weights
    selector_gpt = f"li[role='option'][aria-label='{WEIGHTS_MODEL_PATH[character_str][0]}']"
    await page.click(selector_gpt)

    # 给前端一点时间刷新UI
    await asyncio.sleep(0.5)

    """
    设置 #component-6这个下拉框的值为 character_str对应的权重文件路径
    """
    # 1) 点击下拉区域，展开选项
    await page.click("#component-6 .secondary-wrap")

    # 2) 等待下拉容器出现
    await page.wait_for_selector("ul.options[role='listbox']", state="visible")

    selector_sovits = f"li[role='option'][aria-label='{WEIGHTS_MODEL_PATH[character_str][1]}']"
    await page.click(selector_sovits)

    # 给前端一点时间刷新UI
    await asyncio.sleep(0.5)

async def set_ref_language(page, language_str: str):
    """
    设置 #component-19 这个下拉框的值为 language_str
    """

    # 1) 点击下拉区域，展开选项
    await page.click("#component-19 .secondary-wrap")

    # 2) 等待下拉容器出现
    await page.wait_for_selector("ul.options[role='listbox']", state="visible")

    # 3) 根据 aria-label 匹配 <li>
    selector = f"li[role='option'][aria-label='{language_str}']"
    await page.click(selector)

    # 给前端一点时间刷新UI
    await asyncio.sleep(1)



async def set_language(page, language_str: str, chatmodel=None):
    """
    设置 #component-31 这个下拉框的值为 language_str
    """
    # 1) 点击下拉区域，展开选项
    await page.click("#component-31 .secondary-wrap")

    # 2) 等待下拉容器出现
    await page.wait_for_selector("ul.options[role='listbox']", state="visible")

    # 3) 根据 aria-label 匹配 <li>
    selector = f"li[role='option'][aria-label='{language_str}']"
    await page.click(selector)

    if chatmodel is not None:
        chatmodel.set_model_language(language_str)

    # 给前端一点时间刷新UI
    await asyncio.sleep(1)


async def set_cut_method(page, method_str: str):
    """
    设置 #component-32 这个下拉框的值为 method_str
    """
    # 1) 点击下拉区域，展开选项
    await page.click("#component-32 .secondary-wrap")

    # 2) 等待下拉容器出现
    await page.wait_for_selector("ul.options[role='listbox']", state="visible")

    # 3) 根据 aria-label 匹配 <li>
    selector = f"li[role='option'][aria-label='{method_str}']"
    await page.click(selector)

    # 给前端一点时间刷新UI
    await asyncio.sleep(0.5)

async def set_top_k(page, top_k: float):
    """
    设置 #component-40 这个横向拉拽组件 (range slider + number input) 的值。
    前端有两个元素：
      - <input type="number" data-testid="number-input" aria-label="number input for top_k">
      - <input type="range" id="range_id_2" ... aria-label="range slider for top_k">
    一般直接填写数字输入框就能同步 slider。
    """
    # 确保 top_k 在 1~100 范围内
    top_k = max(1, min(100, top_k))

    # 方式一：填写数字输入框
    await page.fill("input[aria-label='number input for top_k']", str(top_k))

    # 如果需要也可以同时填 range slider (通常不需要)
    # await page.fill("input[aria-label='range slider for top_k']", str(top_k))

    # 给前端一点时间同步
    await asyncio.sleep(0.5)

async def set_top_p(page, top_p: int):
    """
    设置 #component-41 这个横向拉拽组件 (range slider + number input) 的值。
    前端有两个元素：
      - <input type="number" data-testid="number-input" aria-label="number input for top_p">
      - <input type="range" id="range_id_2" ... aria-label="range slider for top_p">
    一般直接填写数字输入框就能同步 slider。
    """
    # 确保 top_p 在 0~1 范围内
    top_p = max(0, min(1, top_p))

    # 方式一：填写数字输入框
    await page.fill("input[aria-label='number input for top_p']", str(top_p))

    # 如果需要也可以同时填 range slider (通常不需要)
    # await page.fill("input[aria-label='range slider for top_p']", str(top_p))

    # 给前端一点时间同步
    await asyncio.sleep(0.5)


async def set_temperature(page, temperature: float):
    """
    设置 #component-40 这个横向拉拽组件 (range slider + number input) 的值。
    前端有两个元素：
      - <input type="number" data-testid="number-input" aria-label="number input for temperature">
      - <input type="range" id="range_id_2" ... aria-label="range slider for temperature">
    一般直接填写数字输入框就能同步 slider。
    """
    # 确保 temperature 在 0~1 范围内
    temperature = max(0, min(1, temperature))

    # 方式一：填写数字输入框
    await page.fill("input[aria-label='number input for temperature']", str(temperature))

    # 如果需要也可以同时填 range slider (通常不需要)
    # await page.fill("input[aria-label='range slider for temperature']", str(temperature))

    # 给前端一点时间同步
    await asyncio.sleep(0.5)