# app/schemas/hypothetical_change.py
from pydantic import BaseModel

class HypotheticalChange(BaseModel):
    description: str
    amount: float
    tax_category: str
