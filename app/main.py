# app/main.py

from fastapi import FastAPI
from dotenv import load_dotenv

# Import routers
from app.routers.llm_router import router as llm_router
from app.routers.scenario_router import router as scenario_router
from app.routers import scenario, categorize, feedback

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Financial Assistant Engine", version="1.0")

# Register routers with appropriate prefixes
app.include_router(llm_router, tags=["LLM Inference"])
app.include_router(scenario_router, prefix="/scenario", tags=["Scenario Simulation"])
app.include_router(categorize.router, prefix="/categorize", tags=["Transaction Categorization"])
app.include_router(feedback.router, prefix="/feedback", tags=["User Feedback"])

for route in app.routes:
    print(f" Registered route: {route.path}")