import asyncio
from interaction_webui_config import get_constant
from set_component import set_weights, set_cut_method, set_language, set_ref_language, set_temperature, set_top_k, set_top_p

REMOVE_PATH, CHARACTER, REF_AUDIO_TEXT, WEIGHTS_MODEL_PATH, REF_LANGUAGE_OPTIONS, LANGUAGE_OPTIONS, CUT_METHOD_OPTIONS = get_constant()

async def setup_reference(page, chatmodel=None):
    """
    只执行一次：
      1) 设置「参考文本」和「参考音频」。
      2) 选择「合成语种」。
      3) 选择「切分方法」。
      4) 设置 top_k。
    """

    print("\n选择角色 😍 ：")
    for i, character in enumerate(CHARACTER, start=1):
        print(f"{i}. {character}")
    while True:
        try:
            character_choice = int(input("请选择角色："))
            if 1 <= character_choice <= len(CHARACTER):
                break
            else:
                print("超出范围，请重新输入。")
        except ValueError:
            print("无效输入，请输入数字。")
    character_str = CHARACTER[character_choice - 1]
    print(f"✅ 你选择了 😉 ：{character_str}")
    # 调用 set_weights 设置角色模型权重
    await set_weights(page, character_str)
    

    print("\nLoading...🤓🤓🤓...\n")
    await page.set_input_files("input[data-testid='file-upload']", REF_AUDIO_TEXT[character_str][0])
    await page.fill("#component-15 textarea", REF_AUDIO_TEXT[character_str][1])
    await asyncio.sleep(3)
    print("Preset Completed! 😤👌")


    # === 1) 选择参考音频语种 ===
    print("\n输入参考音频语种 😇 ：")
    for i, lang in enumerate(REF_LANGUAGE_OPTIONS, start=1):
        print(f"  {i}. {lang}")
    while True:
        try:
            lang_choice = int(input("请选择参考音频语种："))
            if 1 <= lang_choice <= len(REF_LANGUAGE_OPTIONS):
                break
            else:
                print("超出范围，请重新输入。")
        except ValueError:
            print("无效输入，请输入数字。")

    language_str = LANGUAGE_OPTIONS[lang_choice - 1]
    print(f"✅ 你选择了 😘 ：{language_str}")

    # 调用 set_ref_language 设置语种
    await set_ref_language(page, language_str)

    # === 2) 选择合成语种 ===
    print("\n可选语种 😜 ：")
    for i, lang in enumerate(LANGUAGE_OPTIONS, start=1):
        print(f"  {i}. {lang}")
    while True:
        try:
            lang_choice = int(input("请选择合成语种："))
            if 1 <= lang_choice <= len(LANGUAGE_OPTIONS):
                break
            else:
                print("超出范围，请重新输入。")
        except ValueError:
            print("无效输入，请输入数字。")

    language_str = LANGUAGE_OPTIONS[lang_choice - 1]
    print(f"✅ 你选择了 😘 ：{language_str}")

    # 调用 set_language 设置语种
    await set_language(page, language_str, chatmodel)

    # === 3) 选择切分方法 ===
    print("\n可选切分方法 😨🔪 ：")
    for i, method in enumerate(CUT_METHOD_OPTIONS, start=1):
        print(f"  {i}. {method}")
    while True:
        try:
            method_choice = int(input("请选择切分方法(输入数字 1~{} )：".format(len(CUT_METHOD_OPTIONS))))
            if 1 <= method_choice <= len(CUT_METHOD_OPTIONS):
                break
            else:
                print("超出范围，请重新输入。")
        except ValueError:
            print("无效输入，请输入数字。")

    method_str = CUT_METHOD_OPTIONS[method_choice - 1]
    print(f"✅ 你选择了切分方法 😱 ：{method_str}")

    # 调用 set_cut_method 设置切分方式
    await set_cut_method(page, method_str)

    # === 4) 设置 top_k ===
    while True:
        try:
            top_k = int(input("\n请输入 top_k (1~100) 😏 ："))
            if 1 <= top_k <= 100:
                break
            else:
                print("超出范围，请重新输入。")
        except ValueError:
            print("无效输入，请输入数字。")

    print(f"✅ 你选择了 🤯 top_k = {top_k}")
    await set_top_k(page, top_k)

    # === 5) 设置 top_p ===
    while True:
        try:
            top_p = float(input("\n请输入 top_p (0~1) 🤤 ："))
            if 0 <= top_p <= 1:
                break
            else:
                print("超出范围，请重新输入。")
        except ValueError:
            print("无效输入，请输入数字。")

    print(f"✅ 你选择了 🤪 top_p = {top_p}")
    await set_top_p(page, top_p)


    # === 6) 设置 temperature ===
    while True:
        try:
            temperature = float(input("\n请输入 temperature (0~1) 🥵 ："))
            if 0 <= temperature <= 1:
                break
            else:
                print("超出范围，请重新输入。")
        except ValueError:
            print("无效输入，请输入数字。")

    print(f"✅ 你选择了 😵 temperature = {temperature}")
    await set_temperature(page, temperature)