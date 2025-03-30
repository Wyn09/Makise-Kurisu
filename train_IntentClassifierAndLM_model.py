import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM

base_model = r"E:\VsCode-Python\pretrained_models\Qwen\Qwen2.5-3B-Instruct"
QwenModel = AutoModelForCausalLM.from_pretrained(base_model)
tokenizer = AutoTokenizer.from_pretrained(base_model)


class IntentClassifierAndLMModel(QwenModel.__class__):

    def __init__(self, num_classes=1):
        self.num_classes = num_classes
        self.classifier = nn.Linear(2048, num_classes)

    def forward(self, **kwargs):
        with torch.no_grad():
            super().forward(**kwargs)
    pass



if __name__ == "__main__":

    for param in QwenModel.parameters():
        param.requires_grad_ = False

    pass