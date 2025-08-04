import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig
import os

class Predictor:
    def __init__(self):
        base_model_id = "mistralai/Mistral-7B-v0.1"
        adapter_path = "adapter_model" 
        config = PeftConfig.from_pretrained(adapter_path)
        self.tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)
        base_model = AutoModelForCausalLM.from_pretrained(
            config.base_model_name_or_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.model = PeftModel.from_pretrained(base_model, adapter_path)
        self.model.eval()

    def predict(self, prompt: str) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

