from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum


class PlanType(Enum):
    """プラン種別"""
    FREE = "free"
    STANDARD = "standard"


class QuotaExceededException(Exception):
    """クォータ超過例外"""
    def __init__(self, message: str = "利用回数の上限に達しました"):
        self.message = message
        super().__init__(self.message)


@dataclass
class Quota:
    """クォータエンティティ"""
    
    id: UUID
    user_id: UUID
    plan_type: PlanType
    remaining_count: int
    reset_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # プランごとの上限値
    PLAN_LIMITS = {
        PlanType.FREE: 3,
        PlanType.STANDARD: 15
    }
    
    def can_use(self) -> bool:
        """利用可能かチェック"""
        # リセットが必要な場合は、リセット後に判定
        if self.is_reset_needed():
            return True
        return self.remaining_count > 0
    
    def is_reset_needed(self) -> bool:
        """リセットが必要かチェック"""
        return datetime.now() >= self.reset_date
    
    def consume(self) -> None:
        """クォータを1消費"""
        if not self.can_use():
            raise QuotaExceededException()
        
        # リセットが必要な場合は先にリセット
        if self.is_reset_needed():
            self.reset()
        
        self.remaining_count -= 1
        self.updated_at = datetime.now()
    
    def reset(self) -> None:
        """月次リセット"""
        self.remaining_count = self.PLAN_LIMITS[self.plan_type]
        # 次回リセット日を1ヶ月後に設定
        self.reset_date = self._calculate_next_reset_date()
        self.updated_at = datetime.now()
    
    def _calculate_next_reset_date(self) -> datetime:
        """次回リセット日を計算"""
        # 現在の日時から1ヶ月後の同日同時刻
        current = datetime.now()
        
        # 月末処理を考慮
        if current.month == 12:
            next_month = 1
            next_year = current.year + 1
        else:
            next_month = current.month + 1
            next_year = current.year
        
        # 日付が存在しない場合（例：1月31日→2月31日）は月末に
        try:
            next_reset = current.replace(year=next_year, month=next_month)
        except ValueError:
            # 月末の最終日に設定
            import calendar
            last_day = calendar.monthrange(next_year, next_month)[1]
            next_reset = current.replace(
                year=next_year, 
                month=next_month, 
                day=last_day
            )
        
        return next_reset
    
    def upgrade_plan(self, new_plan: PlanType) -> None:
        """プランをアップグレード"""
        old_plan = self.plan_type
        self.plan_type = new_plan
        
        # プランアップグレード時は即座に新しい上限値を適用
        if new_plan == PlanType.STANDARD and old_plan == PlanType.FREE:
            # Freeから Standardへのアップグレード
            # 残り回数を新プランの上限値に設定
            self.remaining_count = self.PLAN_LIMITS[new_plan]
            self.reset_date = self._calculate_next_reset_date()
        
        self.updated_at = datetime.now()
    
    def add_tickets(self, count: int) -> None:
        """チケットを追加（回数追加）"""
        if count <= 0:
            raise ValueError("追加するチケット数は1以上である必要があります")
        
        self.remaining_count += count
        self.updated_at = datetime.now()
    
    @classmethod
    def create_new(cls, user_id: UUID, plan_type: PlanType = PlanType.FREE) -> 'Quota':
        """新規クォータを作成"""
        from uuid import uuid4
        
        now = datetime.now()
        quota = cls(
            id=uuid4(),
            user_id=user_id,
            plan_type=plan_type,
            remaining_count=cls.PLAN_LIMITS[plan_type],
            reset_date=now,  # 一時的に現在時刻を設定
            created_at=now,
            updated_at=None
        )
        # 正しい次回リセット日を設定
        quota.reset_date = quota._calculate_next_reset_date()
        return quota