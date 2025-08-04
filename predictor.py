from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import torch
import os

m_token = os.environ.get("mistral_token")

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

base_model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2",
    token=m_token,
    quantization_config=quantization_config,
    device_map="auto",
    torch_dtype=torch.float16,
    use_safetensors=True,
    trust_remote_code=True
)

model = PeftModel.from_pretrained(base_model, "jwwylie1/f1-explainer-adapter")

tokenizer = AutoTokenizer.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2",
    token=m_token
)

def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt")

    # Move inputs to same device as model
    if torch.cuda.is_available():
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
    print(48)

    input_length = inputs['input_ids'].shape[1]
    
    print(49)
    response = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
    
    print(50)
    return response