from fastapi import FastAPI
from app.routers import scenario, categorize, feedback
from dotenv import load_dotenv
from app.routers.llm_router import router as llm_router
from app.routers.scenario_router import router as scenario_router


load_dotenv()

app = FastAPI(title="Financial Assistant Engine", version="1.0")

# Register routers
app.include_router(scenario.router, tags=["Scenario Simulation"])
app.include_router(categorize.router, tags=["Transaction Categorization"])
app.include_router(feedback.router, tags=["User Feedback"])
app.include_router(llm_router)
app.include_router(scenario_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "model": "Mistral-7B-Q4", "engine": "llama.cpp"}


@app.get("/ping")
async def ping():
    return {"status": "Server D is alive"}

from fastapi import Request

@app.post("/infer")
async def infer(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")

    # TODO: Replace with actual LLM inference logic
    response = {
        "recommendations": "Mock recommendation",
        "tax_implications": "Mock tax advice",
        "cash_flow_projection": {"month": "Mock projection"}
    }

    return {
        "response": response,
        "confidence": 0.95,
        "source_model": "server-d-llm"
    }