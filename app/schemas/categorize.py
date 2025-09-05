from pydantic import BaseModel, Field
from typing import Annotated
from datetime import date
from typing import List, Optional

class TransactionUpdate(BaseModel):
    id: int
    description: str
    amount: float
    date: Annotated[date | None, Field(default=None)]  # ✅ Pydantic v2-compatible
    category: str = "Uncategorized"
    needs_review: bool = True
    confidence: float = 0.0

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "description": "Tesco",
                "amount": -45.0,
                "date": "2025-08-01",
                "category": "Uncategorized",
                "needs_review": True,
                "confidence": 0.0
            }
        }



class CategorizeResponse(BaseModel):
    status: str
    transactions: List[TransactionUpdate]
    low_confidence_count: int