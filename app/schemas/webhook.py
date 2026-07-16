from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal

class WebhookPayload(BaseModel):
    transaction_id: UUID
    user_id: int
    account_id: int
    amount: Decimal
    signature: str