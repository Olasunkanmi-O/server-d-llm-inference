from fastapi import FastAPI
from app.routers import scenario, categorize, feedback

app = FastAPI(title="Financial Assistant Engine", version="1.0")

# Register routers
app.include_router(scenario.router, tags=["Scenario Simulation"])
app.include_router(categorize.router, tags=["Transaction Categorization"])
app.include_router(feedback.router, tags=["User Feedback"])

@app.get("/health")
def health_check():
    return {"status": "ok", "model": "Mistral-7B-Q4", "engine": "llama.cpp"}