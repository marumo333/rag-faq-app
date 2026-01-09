from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.quota import Quota


class QuotaRepository(ABC):
    """クォータリポジトリのインターフェース"""
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[Quota]:
        """ユーザーIDでクォータを取得"""
        pass
    
    @abstractmethod
    async def create(self, quota: Quota) -> Quota:
        """クォータを作成"""
        pass
    
    @abstractmethod
    async def update(self, quota: Quota) -> Quota:
        """クォータを更新"""
        pass
    
    @abstractmethod
    async def decrement_count(self, user_id: UUID) -> Quota:
        """利用回数を1減らす（アトミック操作）"""
        pass
    
    @abstractmethod
    async def reset_monthly_quotas(self) -> int:
        """月次リセット対象のクォータをリセット
        
        Returns:
            リセットした件数
        """
        pass
    
    @abstractmethod
    async def get_quotas_needing_reset(self) -> List[Quota]:
        """リセットが必要なクォータ一覧を取得"""
        pass
    
    @abstractmethod
    async def batch_reset(self, user_ids: List[UUID]) -> int:
        """複数ユーザーのクォータを一括リセット
        
        Args:
            user_ids: リセット対象のユーザーIDリスト
            
        Returns:
            リセットした件数
        """
        pass