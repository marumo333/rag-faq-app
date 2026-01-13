from typing import List, Optional, Dict, Any, cast
from uuid import UUID
from datetime import datetime, date
from calendar import monthrange
from supabase import Client

from domain.entities.usage_log import UsageLog, ActionType


class SupabaseUsageLogRepository:
    """Supabaseを使用した利用ログリポジトリの実装"""
    
    def __init__(self, supabase_client: Client) -> None:
        self.client = supabase_client
    
    async def log_usage(
        self, 
        user_id: UUID, 
        action_type: ActionType, 
        resource_id: Optional[UUID] = None
    ) -> UsageLog:
        """利用ログを記録"""
        usage_log = UsageLog.create(
            user_id=user_id,
            action_type=action_type,
            resource_id=resource_id
        )
        
        self.client.table('usage_logs').insert({
            'id': str(usage_log.id),
            'user_id': str(usage_log.user_id),
            'action_type': usage_log.action_type.value,
            'resource_id': str(usage_log.resource_id) if usage_log.resource_id else None,
            'created_at': usage_log.created_at.isoformat(),
        }).execute()
        
        return usage_log
    
    async def get_monthly_count(
        self, 
        user_id: UUID, 
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> int:
        """指定月の利用回数を取得
        
        Args:
            user_id: ユーザーID
            year: 年（Noneの場合は当年）
            month: 月（Noneの場合は当月）
            
        Returns:
            利用回数
        """
        # デフォルトは当月
        if year is None or month is None:
            now = datetime.now()
            year = year or now.year
            month = month or now.month
        
        # 月の開始日と終了日を計算
        start_date = datetime(year, month, 1)
        last_day = monthrange(year, month)[1]
        end_date = datetime(year, month, last_day, 23, 59, 59, 999999)
        
        response = self.client.table('usage_logs').select('id', count='exact').eq(
            'user_id', str(user_id)
        ).gte(
            'created_at', start_date.isoformat()
        ).lte(
            'created_at', end_date.isoformat()
        ).execute()
        
        return response.count if response.count else 0
    
    async def get_recent_logs(
        self,
        user_id: UUID,
        action_type: Optional[ActionType] = None,
        limit: int = 100
    ) -> List[UsageLog]:
        """最近の利用ログを取得
        
        Args:
            user_id: ユーザーID
            action_type: フィルタするアクション種別（Noneの場合は全て）
            limit: 取得件数上限
            
        Returns:
            利用ログリスト
        """
        query = self.client.table('usage_logs').select('*').eq('user_id', str(user_id))
        
        if action_type:
            query = query.eq('action_type', action_type.value)
        
        response = query.order('created_at', desc=True).limit(limit).execute()
        
        if not response.data:
            return []
        
        logs = []
        for item in response.data:
            if isinstance(item, dict):
                log = self._map_to_usage_log(cast(Dict[str, Any], item))
                if log:
                    logs.append(log)
        
        return logs
    
    def _map_to_usage_log(self, data: Dict[str, Any]) -> Optional[UsageLog]:
        """辞書データをUsageLogエンティティにマッピング"""
        try:
            return UsageLog(
                id=UUID(data['id']),
                user_id=UUID(data['user_id']),
                action_type=ActionType(data['action_type']),
                resource_id=UUID(data['resource_id']) if data.get('resource_id') else None,
                created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
            )
        except (KeyError, ValueError) as e:
            print(f"Error mapping usage log data: {e}")
            return None