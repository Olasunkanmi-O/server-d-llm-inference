

from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
from llama_cpp import Llama
from dotenv import load_dotenv
import os
import time
import logging

load_dotenv()
router = APIRouter(prefix="/llm", tags=["LLM Inference"])

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Environment config
DEFAULT_MODEL_PATH = os.getenv(
    "LLM_MODEL_PATH",
    "/home/ubuntu/server-d-llm-inference/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf"
)
DEFAULT_CONTEXT_WINDOW = int(os.getenv("LLM_CONTEXT_WINDOW", "32768"))

# Global model instance (lazy-loaded)
llm = None
model_name = "unknown-model"
context_window = DEFAULT_CONTEXT_WINDOW

try:
    llm = Llama(model_path=DEFAULT_MODEL_PATH, n_ctx=DEFAULT_CONTEXT_WINDOW)
    model_name = llm.metadata.get("general.name", "unknown-model")
    context_window = llm.context_params.n_ctx
    logging.info(f"Model loaded: {model_name} with context window {context_window}")
except Exception as e:
    logging.error(f"Model failed to load at startup: {str(e)}")
    llm = None

# Health check
@router.get("/health")
def health_check():
    return {
        "status": "ok" if llm else "model unavailable",
        "model": model_name,
        "context_window": context_window,
        "engine": "llama.cpp"
    }

@router.get("/")
async def ping():
    return {"status": "llm router active"}

# Inference route
@router.post("/infer")
async def infer_llm(request: Request, model_override: str = Query(None)):
    start_time = time.time()

    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        caller = data.get("caller", "unknown")

        if not prompt:
            return JSONResponse(status_code=400, content={"error": "No prompt provided."})

        logging.info(f"Inference triggered by: {caller}")
        logging.info(f"Prompt received: {prompt[:60]}...")

        # Load model (override or fallback)
        try:
            llm_instance = Llama(model_path=model_override, n_ctx=DEFAULT_CONTEXT_WINDOW) if model_override else llm
            if llm_instance is None:
                raise RuntimeError("Model not initialized")
        except Exception as e:
            logging.error(f"Model load failed: {str(e)}")
            return JSONResponse(status_code=500, content={"error": "Model load failed", "details": str(e)})

        model_used = llm_instance.metadata.get("general.name", "unknown-model")

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
        logging.info(f"Tokenization took {time.time() - token_start:.2f}s ({prompt_length} tokens)")

        # Token budgeting
        buffer = 500
        available_output = llm_instance.context_params.n_ctx - prompt_length - buffer
        max_tokens = max(128, min(available_output, 1024))
        logging.info(f"Max tokens allocated: {max_tokens}")

        # Inference
        infer_start = time.time()
        output = llm_instance(structured_prompt, max_tokens=max_tokens, stop=["</s>"])
        logging.info(f"Inference took {time.time() - infer_start:.2f}s")

        # Parsing
        parse_start = time.time()
        choices = output.get("choices", [])
        generated_text = choices[0].get("text", "").strip() if choices and isinstance(choices[0], dict) else ""
        logging.info(f"Parsing took {time.time() - parse_start:.2f}s")

        # Final response
        total_time = time.time() - start_time
        logging.info(f"Total request time: {total_time:.2f}s")

        if not generated_text:
            logging.warning("Empty response from model")
            return JSONResponse(status_code=200, content={
                "response": "Unable to generate scenario.",
                "confidence": None,
                "source_model": model_used,
                "error": "Empty response from model"
            })

        return {
            "response": {
                "recommendations": generated_text,
                "tax_implications": "To be extracted",
                "cash_flow_projection": {"next_month": "To be estimated"}
            },
            "confidence": 0.87,
            "source_model": model_used
        }

    except Exception as e:
        logging.error(f"LLM inference failed: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "LLM inference failed", "details": str(e)})