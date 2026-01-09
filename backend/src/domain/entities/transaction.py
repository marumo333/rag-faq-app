from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from enum import Enum


class TransactionType(Enum):
    """トランザクション種別"""
    SUBSCRIPTION = "subscription"
    TICKET = "ticket"


class TransactionStatus(Enum):
    """トランザクションステータス"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Transaction:
    """トランザクションエンティティ"""
    
    id: UUID
    user_id: UUID
    stripe_session_id: str
    stripe_customer_id: Optional[str]
    transaction_type: TransactionType
    status: TransactionStatus
    amount: int  # 金額（円）
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    def complete(self) -> None:
        """トランザクションを完了にする"""
        self.status = TransactionStatus.COMPLETED
        self.updated_at = datetime.now()
    
    def fail(self, error_message: str) -> None:
        """トランザクションを失敗にする"""
        self.status = TransactionStatus.FAILED
        self.metadata["error_message"] = error_message
        self.updated_at = datetime.now()
    
    def is_completed(self) -> bool:
        """完了しているか"""
        return self.status == TransactionStatus.COMPLETED
    
    def is_pending(self) -> bool:
        """保留中か"""
        return self.status == TransactionStatus.PENDING
    
    @classmethod
    def create_pending(
        cls,
        user_id: UUID,
        stripe_session_id: str,
        transaction_type: TransactionType,
        amount: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'Transaction':
        """保留中のトランザクションを作成"""
        from uuid import uuid4
        
        return cls(
            id=uuid4(),
            user_id=user_id,
            stripe_session_id=stripe_session_id,
            stripe_customer_id=None,
            transaction_type=transaction_type,
            status=TransactionStatus.PENDING,
            amount=amount,
            metadata=metadata or {},
            created_at=datetime.now(),
            updated_at=None
        )