from typing import List, Optional, Dict, Any, cast
from uuid import UUID
from datetime import datetime
import json
from supabase import Client

from domain.entities.transaction import Transaction, TransactionType, TransactionStatus
from domain.repositories.transaction_repository import TransactionRepository


class SupabaseTransactionRepository(TransactionRepository):
    """Supabaseを使用したトランザクションリポジトリの実装"""
    
    def __init__(self, supabase_client: Client) -> None:
        self.client = supabase_client
    
    async def create(self, transaction: Transaction) -> Transaction:
        """トランザクションを作成"""
        self.client.table('transactions').insert({
            'id': str(transaction.id),
            'user_id': str(transaction.user_id),
            'stripe_session_id': transaction.stripe_session_id,
            'stripe_customer_id': transaction.stripe_customer_id,
            'transaction_type': transaction.transaction_type.value,
            'status': transaction.status.value,
            'amount': transaction.amount,
            'metadata': json.dumps(transaction.metadata) if transaction.metadata else '{}',
            'created_at': transaction.created_at.isoformat(),
            'updated_at': transaction.updated_at.isoformat() if transaction.updated_at else None,
        }).execute()
        
        return transaction
    
    async def get_by_id(self, transaction_id: UUID) -> Optional[Transaction]:
        """IDでトランザクションを取得"""
        response = self.client.table('transactions').select('*').eq('id', str(transaction_id)).execute()
        
        if not response.data:
            return None
        
        data = response.data[0]
        if not isinstance(data, dict):
            return None
        
        return self._map_to_transaction(cast(Dict[str, Any], data))
    
    async def get_by_stripe_session_id(self, stripe_session_id: str) -> Optional[Transaction]:
        """Stripe Session IDでトランザクションを取得"""
        response = self.client.table('transactions').select('*').eq(
            'stripe_session_id', stripe_session_id
        ).execute()
        
        if not response.data:
            return None
        
        data = response.data[0]
        if not isinstance(data, dict):
            return None
        
        return self._map_to_transaction(cast(Dict[str, Any], data))
    
    async def update(self, transaction: Transaction) -> Transaction:
        """トランザクションを更新"""
        self.client.table('transactions').update({
            'stripe_customer_id': transaction.stripe_customer_id,
            'status': transaction.status.value,
            'metadata': json.dumps(transaction.metadata) if transaction.metadata else '{}',
            'updated_at': datetime.now().isoformat(),
        }).eq('id', str(transaction.id)).execute()
        
        return transaction
    
    async def list_by_user(
        self, 
        user_id: UUID,
        status: Optional[TransactionStatus] = None,
        limit: int = 100
    ) -> List[Transaction]:
        """ユーザーのトランザクション一覧を取得"""
        query = self.client.table('transactions').select('*').eq('user_id', str(user_id))
        
        if status:
            query = query.eq('status', status.value)
        
        response = query.order('created_at', desc=True).limit(limit).execute()
        
        if not response.data:
            return []
        
        transactions = []
        for item in response.data:
            if isinstance(item, dict):
                transaction = self._map_to_transaction(cast(Dict[str, Any], item))
                if transaction:
                    transactions.append(transaction)
        
        return transactions
    
    async def update_status(
        self,
        transaction_id: UUID,
        status: TransactionStatus,
        metadata_update: Optional[dict] = None
    ) -> Transaction:
        """トランザクションのステータスを更新（アトミック操作）"""
        # 現在のトランザクションを取得
        transaction = await self.get_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction not found: {transaction_id}")
        
        # ステータスを更新
        transaction.status = status
        transaction.updated_at = datetime.now()
        
        # メタデータを更新（マージ）
        if metadata_update:
            transaction.metadata.update(metadata_update)
        
        # DBに保存
        await self.update(transaction)
        
        return transaction
    
    def _map_to_transaction(self, data: Dict[str, Any]) -> Optional[Transaction]:
        """辞書データをTransactionエンティティにマッピング"""
        try:
            # metadataをパース
            metadata = {}
            if data.get('metadata'):
                if isinstance(data['metadata'], str):
                    metadata = json.loads(data['metadata'])
                elif isinstance(data['metadata'], dict):
                    metadata = data['metadata']
            
            return Transaction(
                id=UUID(data['id']),
                user_id=UUID(data['user_id']),
                stripe_session_id=data['stripe_session_id'],
                stripe_customer_id=data.get('stripe_customer_id'),
                transaction_type=TransactionType(data['transaction_type']),
                status=TransactionStatus(data['status']),
                amount=data['amount'],
                metadata=metadata,
                created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data.get('updated_at') else None,
            )
        except (KeyError, ValueError) as e:
            print(f"Error mapping transaction data: {e}")
            return None