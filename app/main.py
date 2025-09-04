from fastapi import FastAPI, Request
from app.model_loader import load_phi2_pipeline

app = FastAPI()
generator = load_phi2_pipeline()

@app.post("/generate")
async def generate_text(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    response = generator(prompt, max_new_tokens=300)
    return {"response": response[0]["generated_text"]}