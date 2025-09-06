from fastapi import APIRouter, Request, Query
from llama_cpp import Llama
from dotenv import load_dotenv
import os
import time
import logging


load_dotenv()
router = APIRouter(prefix="/llm", tags=["LLM Inference"])
model_path = os.getenv("LLM_MODEL_PATH")
context_window = int(os.getenv("LLM_CONTEXT_WINDOW", "4096"))
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load model path from environment or fallback
DEFAULT_MODEL_PATH = os.getenv(
    "LLM_MODEL_PATH",
    "/home/ubuntu/server-d-llm-inference/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf"
)

# Load model with large context
llm = Llama(model_path=DEFAULT_MODEL_PATH, n_ctx=32768)
model_name = llm.metadata.get("general.name", "unknown-model")
context_window = llm.context_params.n_ctx

print(f" Loaded model: {model_name}")
print(f" Context window: {context_window} tokens")
print(" Server D is live and ready for inference.")

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "model": model_name,
        "context_window": context_window,
        "engine": "llama.cpp"
    }

@router.get("/ping")
async def ping():
    return {"status": "Server D is alive"}





@router.post("/infer")
async def infer_llm(request: Request, model_override: str = Query(None)):
    start_time = time.time()
    data = await request.json()
    prompt = data.get("prompt", "")
    caller = data.get("caller", "unknown")

    if not prompt:
        return {"error": "No prompt provided."}

    logging.info(f" Inference triggered by: {caller}")
    logging.info(f" Prompt received: {prompt[:60]}...")
    logging.info(f"Received scenario payload: {data}")

    # Model selection
    model_load_start = time.time()
    try:
        llm_instance = Llama(model_path=model_override, n_ctx=32768) if model_override else llm
    except Exception as e:
        logging.error(f" Model load failed: {str(e)}")
        return {"response": "Model load failed", "error": str(e), "source_model": model_override}
    logging.info(f" Model loaded in {time.time() - model_load_start:.2f}s")

    model_name = llm_instance.metadata.get("general.name", "unknown-model")

    # Prompt construction
    structured_prompt = f"""
You are a financial assistant. Analyze the following scenario and provide:
- Recommendations
- Tax implications
- Cash flow projection for next month

Scenario: {prompt}

Response:
"""

    # Tokenization
    token_start = time.time()
    prompt_tokens = llm_instance.tokenize(structured_prompt.encode("utf-8"), add_bos=True, special=True)
    prompt_length = len(prompt_tokens)
    logging.info(f" Tokenization took {time.time() - token_start:.2f}s ({prompt_length} tokens)")

    # Token budgeting
    buffer = 500
    available_output = llm_instance.context_params.n_ctx - prompt_length - buffer
    max_tokens = max(128, min(available_output, 1024))
    logging.info(f" Max tokens allocated: {max_tokens}")

    # Inference
    infer_start = time.time()
    output = llm_instance(structured_prompt, max_tokens=max_tokens, stop=["</s>"])
    logging.info(f" Inference took {time.time() - infer_start:.2f}s")

    # Parsing
    parse_start = time.time()
    choices = output.get("choices", [])
    generated_text = choices[0].get("text", "").strip() if choices and isinstance(choices[0], dict) else ""
    logging.info(f" Parsing took {time.time() - parse_start:.2f}s")

    # Final response
    total_time = time.time() - start_time
    logging.info(f" Total request time: {total_time:.2f}s")

    if not generated_text:
        logging.warning(" Empty response from model")
        return {
            "response": "Unable to generate scenario.",
            "confidence": None,
            "source_model": model_name,
            "error": "Empty response from model"
        }

    return {
        "response": {
            "recommendations": generated_text,
            "tax_implications": "To be extracted",
            "cash_flow_projection": {"next_month": "To be estimated"}
        },
        "confidence": 0.87,
        "source_model": model_name
    }