from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class AccountBase(BaseModel):
    balance: Decimal

class AccountResponse(AccountBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True