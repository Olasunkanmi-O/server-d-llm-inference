from fastapi import APIRouter, HTTPException
from app.schemas import FeedbackRequest, FeedbackResponse
from app.db.pool import get_pool

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/")
async def ping():
    return {"status": "feedback router active"}



@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(payload: FeedbackRequest):
    pool = await get_pool()

    async with pool.acquire() as conn:
        convo = await conn.fetchrow("""
            SELECT id FROM conversation_logs WHERE id = $1 AND user_id = $2
        """, payload.conversation_id, payload.user_id)

        if not convo:
            raise HTTPException(status_code=404, detail="Conversation not found")

        await conn.execute("""
            INSERT INTO conversation_feedback (user_id, conversation_id, feedback_text, rating)
            VALUES ($1, $2, $3, $4)
        """, payload.user_id, payload.conversation_id, payload.feedback_text, payload.rating)

    return FeedbackResponse(status="success", message="Feedback submitted")