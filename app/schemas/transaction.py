from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class TransactionBase(BaseModel):
    transaction_id: UUID
    amount: Decimal
    status: str = "completed"

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    account_id: int
    created_at: datetime

    class Config:
        from_attributes = True