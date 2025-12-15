import logging
import os
from typing import List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class GeminiEmbeddingClient:
    """Google Gemini API を使用した埋め込み生成クライアント"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "models/embedding-001"):
        """
        Args:
            api_key: Google API Key（省略時は環境変数から取得）
            model: 使用する埋め込みモデル
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is required")
        
        genai.configure(api_key=self.api_key)
        self.model = model
        self.logger = logger
        
        # Gemini embedding-001 の次元数
        self.dimension = 768
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        単一テキストの埋め込みを生成
        
        Args:
            text: 埋め込み対象のテキスト
            
        Returns:
            List[float]: 埋め込みベクトル（768次元）
        """
        try:
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
            
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            
            embedding = result['embedding']
            
            if len(embedding) != self.dimension:
                raise ValueError(
                    f"Expected {self.dimension} dimensions, got {len(embedding)}"
                )
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"Embedding generation failed: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        複数テキストの埋め込みを一括生成
        
        Args:
            texts: 埋め込み対象のテキストリスト
            
        Returns:
            List[List[float]]: 埋め込みベクトルのリスト
        """
        try:
            if not texts:
                return []
            
            # 空テキストをフィルタ
            valid_texts = [t for t in texts if t and t.strip()]
            
            if not valid_texts:
                self.logger.warning("No valid texts provided for batch embedding")
                return []
            
            self.logger.info(f"Generating embeddings for {len(valid_texts)} texts")
            
            # 1つずつ生成（Geminiはバッチ生成APIがないため）
            embeddings = []
            for i, text in enumerate(valid_texts):
                try:
                    embedding = self.generate_embedding(text)
                    embeddings.append(embedding)
                    
                    if (i + 1) % 10 == 0:
                        self.logger.info(f"Generated {i + 1}/{len(valid_texts)} embeddings")
                        
                except Exception as e:
                    self.logger.error(f"Failed to generate embedding for text {i}: {e}")
                    # エラー時は0ベクトルで埋める（または例外を再送出）
                    raise
            
            self.logger.info(f"Successfully generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            self.logger.error(f"Batch embedding generation failed: {e}")
            raise
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        検索クエリの埋め込みを生成
        
        Args:
            query: 検索クエリテキスト
            
        Returns:
            List[float]: 埋め込みベクトル
        """
        try:
            result = genai.embed_content(
                model=self.model,
                content=query,
                task_type="retrieval_query"  # クエリ用のタスクタイプ
            )
            
            return result['embedding']
            
        except Exception as e:
            self.logger.error(f"Query embedding generation failed: {e}")
            raise