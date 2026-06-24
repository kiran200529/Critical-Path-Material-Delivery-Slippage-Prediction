from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.schemas.schemas import CopilotRequest, CopilotResponse
from backend.services.ai_service import ask_procurement_copilot
from backend.api.dependencies.auth import get_current_user
from typing import Any

router = APIRouter(prefix="/copilot", tags=["AI Procurement Copilot"])

@router.post("/chat", response_model=CopilotResponse, status_code=status.HTTP_200_OK)
def chat_with_copilot(
    request: CopilotRequest,
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Interacts with the AI Procurement Copilot.
    Uses prediction histories, supplier metrics, and project health context to answer questions.
    """
    res = ask_procurement_copilot(db, request.question)
    return res
