from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def load_phi2_pipeline():
    model_id = "microsoft/phi-2"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)
    generator = pipeline("text-generation", model=model, tokenizer=tokenizer, device=-1)
    return generator