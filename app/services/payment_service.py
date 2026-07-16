import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from uuid import UUID
from decimal import Decimal
from datetime import datetime


from app.models.models import User, Account, Transaction
from app.config import settings


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def verify_signature(self, data: dict, signature: str) -> bool:
        """Проверка подписи вебхука"""
        sorted_keys = sorted(data.keys())

        signature_string = ""
        for key in sorted_keys:
            if key != "signature":
                signature_string += str(data[key])

        signature_string += settings.SECRET_KEY

        computed_signature = hashlib.sha256(
            signature_string.encode('utf-8')
        ).hexdigest()

        return computed_signature == signature

    async def process_webhook(
            self,
            transaction_id: UUID,
            user_id: int,
            account_id: int,
            amount: Decimal,
            signature: str
    ) -> Transaction:
        """Обработка вебхука"""

        webhook_data = {
            "transaction_id": str(transaction_id),
            "user_id": user_id,
            "account_id": account_id,
            "amount": float(amount)
        }

        if not self.verify_signature(webhook_data, signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )

        result = await self.db.execute(
            select(Transaction).where(
                Transaction.transaction_id == transaction_id
            )
        )
        existing_transaction = result.scalar_one_or_none()

        if existing_transaction:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Transaction already processed"
            )

        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        result = await self.db.execute(
            select(Account).where(Account.id == account_id)
        )
        account = result.scalar_one_or_none()

        if not account:
            account = Account(
                user_id=user_id,
                balance=0.00
            )
            self.db.add(account)
            await self.db.commit()
            await self.db.refresh(account)

        if account.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account does not belong to user"
            )

        transaction = Transaction(
            transaction_id=transaction_id,
            user_id=user_id,
            account_id=account.id,
            amount=amount,
            status="completed"
        )
        self.db.add(transaction)

        account.balance += amount
        account.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(transaction)

        return transaction