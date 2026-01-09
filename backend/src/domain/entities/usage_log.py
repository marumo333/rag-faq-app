from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum


class ActionType(Enum):
    """アクション種別"""
    FAQ_ANSWER = "faq_answer"
    DOCUMENT_UPLOAD = "document_upload"


@dataclass
class UsageLog:
    """利用ログエンティティ"""
    
    id: UUID
    user_id: UUID
    action_type: ActionType
    resource_id: Optional[UUID]  # 関連リソースID（回答ID、ドキュメントIDなど）
    created_at: datetime
    
    @classmethod
    def create(
        cls,
        user_id: UUID,
        action_type: ActionType,
        resource_id: Optional[UUID] = None
    ) -> 'UsageLog':
        """新規利用ログを作成"""
        from uuid import uuid4
        
        return cls(
            id=uuid4(),
            user_id=user_id,
            action_type=action_type,
            resource_id=resource_id,
            created_at=datetime.now()
        )