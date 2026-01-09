from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.transaction import Transaction, TransactionStatus


class TransactionRepository(ABC):
    """トランザクションリポジトリのインターフェース"""
    
    @abstractmethod
    async def create(self, transaction: Transaction) -> Transaction:
        """トランザクションを作成"""
        pass
    
    @abstractmethod
    async def get_by_id(self, transaction_id: UUID) -> Optional[Transaction]:
        """IDでトランザクションを取得"""
        pass
    
    @abstractmethod
    async def get_by_stripe_session_id(
        self, 
        stripe_session_id: str
    ) -> Optional[Transaction]:
        """Stripe Session IDでトランザクションを取得"""
        pass
    
    @abstractmethod
    async def update(self, transaction: Transaction) -> Transaction:
        """トランザクションを更新"""
        pass
    
    @abstractmethod
    async def list_by_user(
        self, 
        user_id: UUID,
        status: Optional[TransactionStatus] = None,
        limit: int = 100
    ) -> List[Transaction]:
        """ユーザーのトランザクション一覧を取得
        
        Args:
            user_id: ユーザーID
            status: フィルタするステータス（Noneの場合は全て）
            limit: 取得件数上限
        """
        pass
    
    @abstractmethod
    async def update_status(
        self,
        transaction_id: UUID,
        status: TransactionStatus,
        metadata_update: Optional[dict] = None
    ) -> Transaction:
        """トランザクションのステータスを更新（アトミック操作）"""
        pass