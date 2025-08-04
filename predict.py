from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def predict(input):
    transcription = input['transcription']  # text from Whisper
    # Load base model + adapter
    base_model_name = "mistral-base-model-hf"
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    base_model = AutoModelForCausalLM.from_pretrained(base_model_name)
    model = PeftModel.from_pretrained(base_model, "./adapter_model")  # local path or repo
    
    model.eval()
    inputs = tokenizer(transcription, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=200)
    explanation = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return explanation
