from fastapi import APIRouter
from app.schemas import CategorizeResponse, TransactionUpdate
from app.services.categorize import categorize_transactions

router = APIRouter()

@router.post("/categorize", response_model=CategorizeResponse)
async def categorize_route(transactions: list[TransactionUpdate]):
    categorized = await categorize_transactions([tx.dict() for tx in transactions])
    low_conf = sum(1 for tx in categorized if tx["needs_review"])
    return CategorizeResponse(
        status="success",
        transactions=categorized,
        low_confidence_count=low_conf
    )