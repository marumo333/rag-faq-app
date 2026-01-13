from typing import List, Optional, Dict, Any, cast
from uuid import UUID
from datetime import datetime
from supabase import Client

from domain.entities.quota import Quota, PlanType
from domain.repositories.quota_repository import QuotaRepository


class SupabaseQuotaRepository(QuotaRepository):
    """Supabaseを使用したクォータリポジトリの実装"""
    
    def __init__(self, supabase_client: Client) -> None:
        self.client = supabase_client
    
    async def get_by_user_id(self, user_id: UUID) -> Optional[Quota]:
        """ユーザーIDでクォータを取得"""
        response = self.client.table('user_quotas').select('*').eq('user_id', str(user_id)).execute()
        
        if not response.data:
            return None
        
        data = response.data[0]
        if not isinstance(data, dict):
            return None
        
        return self._map_to_quota(cast(Dict[str, Any], data))
    
    async def create(self, quota: Quota) -> Quota:
        """クォータを作成"""
        self.client.table('user_quotas').insert({
            'id': str(quota.id),
            'user_id': str(quota.user_id),
            'plan_type': quota.plan_type.value,
            'remaining_count': quota.remaining_count,
            'reset_date': quota.reset_date.isoformat(),
            'created_at': quota.created_at.isoformat(),
            'updated_at': quota.updated_at.isoformat() if quota.updated_at else None,
        }).execute()
        
        return quota
    
    async def update(self, quota: Quota) -> Quota:
        """クォータを更新"""
        self.client.table('user_quotas').update({
            'plan_type': quota.plan_type.value,
            'remaining_count': quota.remaining_count,
            'reset_date': quota.reset_date.isoformat(),
            'updated_at': datetime.now().isoformat(),
        }).eq('user_id', str(quota.user_id)).execute()
        
        return quota
    
    async def decrement_count(self, user_id: UUID) -> Quota:
        """利用回数を1減らす（アトミック操作）"""
        # まず現在のクォータを取得
        quota = await self.get_by_user_id(user_id)
        if not quota:
            raise ValueError(f"Quota not found for user_id: {user_id}")
        
        # リセットが必要な場合はリセット
        if quota.is_reset_needed():
            quota.reset()
            await self.update(quota)
        
        # カウントをデクリメント（アトミック操作のためRPCを使用）
        self.client.rpc(
            'decrement_quota_count',
            {'p_user_id': str(user_id)}
        ).execute()
        
        # 更新後のクォータを取得して返す
        updated_quota = await self.get_by_user_id(user_id)
        if not updated_quota:
            raise ValueError(f"Failed to get updated quota for user_id: {user_id}")
        
        return updated_quota
    
    async def reset_monthly_quotas(self) -> int:
        """月次リセット対象のクォータをリセット"""
        # リセットが必要なクォータを取得
        quotas = await self.get_quotas_needing_reset()
        
        reset_count = 0
        for quota in quotas:
            quota.reset()
            await self.update(quota)
            reset_count += 1
        
        return reset_count
    
    async def get_quotas_needing_reset(self) -> List[Quota]:
        """リセットが必要なクォータ一覧を取得"""
        now = datetime.now()
        response = self.client.table('user_quotas').select('*').lte('reset_date', now.isoformat()).execute()
        
        if not response.data:
            return []
        
        quotas = []
        for item in response.data:
            if isinstance(item, dict):
                quota = self._map_to_quota(cast(Dict[str, Any], item))
                if quota:
                    quotas.append(quota)
        
        return quotas
    
    async def batch_reset(self, user_ids: List[UUID]) -> int:
        """複数ユーザーのクォータを一括リセット"""
        reset_count = 0
        
        for user_id in user_ids:
            quota = await self.get_by_user_id(user_id)
            if quota:
                quota.reset()
                await self.update(quota)
                reset_count += 1
        
        return reset_count
    
    def _map_to_quota(self, data: Dict[str, Any]) -> Optional[Quota]:
        """辞書データをQuotaエンティティにマッピング"""
        try:
            return Quota(
                id=UUID(data['id']),
                user_id=UUID(data['user_id']),
                plan_type=PlanType(data['plan_type']),
                remaining_count=data['remaining_count'],
                reset_date=datetime.fromisoformat(data['reset_date'].replace('Z', '+00:00')),
                created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data.get('updated_at') else None,
            )
        except (KeyError, ValueError) as e:
            print(f"Error mapping quota data: {e}")
            return None