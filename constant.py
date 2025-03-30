"""
    r"D:\GPT-SoVITS-v3lora-20250228\GPT-SoVITS-v3lora-20250228\GPT-SoVITS-v3lora-20250228\TEMP\gradio"
    设置None在不小心点了y可以不删除任何文件
"""
REMOVE_PATH = None

CHARACTER = [
    "2B",
    "DMC3-Vergil",
    "DMC4-Vergil",
    "DMC5-Vergil",
    "Makise Kurisu"
]

# 列表第一个是参考音频文件路径，第二个是参考音频文本
REF_AUDIO_TEXT = {
    "2B": [r"character\Nier\2B\疑问\疑问.wav", "何か忘れ物でもしたの?  そこで補給してきたらどう?"],
    "DMC3-Vergil": [r"character\Vergil\DMC3-Vergil\平淡\平淡.wav", "You shall die. How boring."],
    "DMC4-Vergil": [r"character\Vergil\DMC4-Vergil\平淡\平淡.wav", "You think you stand a chance?"],
    "DMC5-Vergil": [r"character\Vergil\DMC5-Vergil\平淡\平淡.wav", "Fine. I suppose this is how you wish to die."],
    "Makise Kurisu": [r"character\Makise Kurisu\平淡\crs_0160.wav", "研究所のメンバーに迎えてくれるっていうこと? でも、私…8月中にアメリカに帰る予定なんですけど"]
}

# 第一个是GPT-weights，第二个是SoVITS-weights
# 这里指定的路径是GPT-SoVITS文件夹下的。如果没有权重，可以在本文件夹下找到复制到GPT-SoVITS下
WEIGHTS_MODEL_PATH = {
    "2B": [r"GPT_weights_v3/Nier-2B-e40.ckpt", r"SoVITS_weights_v3/Nier-2B_e3_s75_l128.pth"],
    "DMC3-Vergil": [r"GPT_weights_v3/DMC3-Vergil-e40.ckpt", r"SoVITS_weights_v3/DMC3-Vergil_e3_s99_l128.pth"],
    "DMC4-Vergil": [r"GPT_weights_v3/DMC4-Vergil-e40.ckpt", r"SoVITS_weights_v3/DMC4-Vergil_e3_s96_l128.pth"],
    "DMC5-Vergil": [r"GPT_weights_v3/DMC5-Vergil-e40.ckpt", r"SoVITS_weights_v3/DMC5-Vergil_e3_s105_l128.pth"],
    "Makise Kurisu": [r"GPT_weights_v3/SteinsGate-Kurisu-e45.ckpt", r"SoVITS_weights_v3/SteinsGate-Kurisu_e3_s729_l128.pth"]
}


REF_LANGUAGE_OPTIONS = [
    "中文",      # 1
    "英文",      # 2
    "日文",      # 3
    "粤语",      # 4
    "中英混合",  # 5
    "日英混合",  # 6
    "多语种混合"  # 7
]

LANGUAGE_OPTIONS = [
    "中文",      # 1
    "英文",      # 2
    "日文",      # 3
    "粤语",      # 4
    "中英混合",  # 5
    "日英混合",  # 6
    "多语种混合"  # 7
]
CUT_METHOD_OPTIONS = [
    "不切",            # 1
    "凑四句一切",       # 2
    "凑50字一切",       # 3
    "按中文句号。切",   # 4
    "按英文句号.切",    # 5
    "按标点符号切"      # 6
    # 如果还有别的切分方式，可以继续加
]

def get_constant():
    return REMOVE_PATH, CHARACTER, REF_AUDIO_TEXT, WEIGHTS_MODEL_PATH, REF_LANGUAGE_OPTIONS, LANGUAGE_OPTIONS, CUT_METHOD_OPTIONS