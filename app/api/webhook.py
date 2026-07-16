from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import uuid4
import hashlib

from app.database import get_db
from app.schemas.webhook import WebhookPayload
from app.schemas.transaction import TransactionResponse
from app.services.payment_service import PaymentService
from app.core.dependencies import get_current_admin
from app.models.models import Admin
from app.config import settings

router = APIRouter(prefix="/api/webhook", tags=["webhook"])


class SignatureRequest(BaseModel):
    user_id: int
    account_id: int
    amount: float


class SignatureResponse(BaseModel):
    transaction_id: str
    signature: str
    payload: dict


@router.post("/generate-signature", response_model=SignatureResponse)
async def generate_signature(
    request: SignatureRequest,
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Генерация тестовой подписи для вебхука (только для админов!)
    """
    transaction_id = str(uuid4())

    data = {
        "account_id": request.account_id,
        "amount": request.amount,
        "transaction_id": transaction_id,
        "user_id": request.user_id
    }

    sorted_keys = sorted(data.keys())

    signature_string = ""
    for key in sorted_keys:
        signature_string += str(data[key])

    signature_string += settings.SECRET_KEY

    signature = hashlib.sha256(
        signature_string.encode('utf-8')
    ).hexdigest()

    return SignatureResponse(
        transaction_id=transaction_id,
        signature=signature,
        payload={
            "transaction_id": transaction_id,
            "user_id": request.user_id,
            "account_id": request.account_id,
            "amount": request.amount,
            "signature": signature
        }
    )


@router.post("/payment", response_model=TransactionResponse)
async def payment_webhook(
        payload: WebhookPayload,
        db: AsyncSession = Depends(get_db)
):
    """
    Обработка вебхука от платежной системы
    """
    service = PaymentService(db)

    transaction = await service.process_webhook(
        transaction_id=payload.transaction_id,
        user_id=payload.user_id,
        account_id=payload.account_id,
        amount=payload.amount,
        signature=payload.signature
    )

    return transaction