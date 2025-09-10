from typing import List, Optional
from pydantic import BaseModel
from app.schemas.transaction import Transaction
from app.schemas.hypothetical_change import HypotheticalChange



class HypotheticalChange(BaseModel):
    description: str
    amount: float
    category: Optional[str] = "uncategorized"


class ScenarioRequest(BaseModel):
    user_id: int
    request: List[Transaction]  # <-- updated from str to list of Transaction
    session_id: Optional[str] = None
    scenario_type: Optional[str] = "general"
    timeframe_days: Optional[int] = 180
    aggregation_days: Optional[int] = 365
    hypothetical_changes: Optional[List[HypotheticalChange]] = []


class CashFlowProjection(BaseModel):
    initial_impact: float
    estimated_tax_savings: Optional[float] = None
    net_effect: Optional[float] = None

class Scenario(BaseModel):
    recommendations: str
    tax_implications: str
    cash_flow_projection: CashFlowProjection

class ScenarioResponse(BaseModel):
    status: str  # e.g., "success" or "failed"
    scenario: Scenario
    confidence: Optional[float] = None
    scenario_type: Optional[str] = "general"
    session_id: Optional[str] = None

