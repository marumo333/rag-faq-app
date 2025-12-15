import logging
import os
from typing import List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class GeminiGenerationClient:
    """Google Gemini APIを使用した回答生成クライアント"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "models/gemini-2.5-flash"
    ):
        """
        Args:
            api_key: Google API Key（省略時は環境変数から取得）
            model: 使用する生成モデル
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is required")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)
        self.logger = logger
    
    def generate_answer(
        self,
        question: str,
        context_chunks: List[dict],
        system_prompt: Optional[str] = None
    ) -> dict:
        """
        質問に対してコンテキストを使用して回答を生成
        
        Args:
            question: ユーザーの質問
            context_chunks: 検索されたチャンクのリスト
            system_prompt: システムプロンプト（省略時はデフォルト使用）
            
        Returns:
            dict: 回答テキストと使用したチャンク情報
        """
        try:
            # システムプロンプトの設定
            if system_prompt is None:
                system_prompt = self._get_default_system_prompt()
            
            # コンテキストの整形
            formatted_context = self._format_context(context_chunks)
            
            # プロンプトの構築
            prompt = self._build_prompt(
                system_prompt=system_prompt,
                context=formatted_context,
                question=question
            )
            
            self.logger.info(f"Generating answer for question: '{question}'")
            self.logger.debug(f"Using {len(context_chunks)} context chunks")
            
            # Gemini APIで回答生成
            response = self.model.generate_content(prompt)
            
            answer_text = response.text
            
            self.logger.info(f"Answer generated: {len(answer_text)} characters")
            
            return {
                "answer": answer_text,
                "model": self.model_name,
                "chunks_used": len(context_chunks)
            }
            
        except Exception as e:
            self.logger.error(f"Answer generation failed: {e}", exc_info=True)
            raise
    
    def _get_default_system_prompt(self) -> str:
        """デフォルトのシステムプロンプト"""
        return """あなたは親切で正確なFAQアシスタントです。

【役割】
- あなたはユーザーの質問に対して、提供されたコンテキスト情報のみを根拠として回答します。
- 回答は簡潔で分かりやすい日本語で記述してください。

【厳守事項】
- コンテキストに含まれていない情報を推測・補完してはいけません。
- 回答できない場合は、必ず次の文言をそのまま出力してください：
  「回答不能：提供されたコンテキストに該当情報がありません」

【引用ルール】
- 回答内の各主張には、使用した参考情報番号を必ず付与してください。
  例：「〇〇です。[参考情報1]」

【出力制約】
- 必要に応じて箇条書きを使用してください。
"""
    
    def _format_context(self, chunks: List[dict]) -> str:
        """
        チャンクリストをコンテキスト文字列に整形
        
        重複や矛盾を抑制するために：
        - 類似度の高い順にソート済み
        - セクション情報を含める
        - チャンクIDを参照として保持
        """
        if not chunks:
            return "関連情報が見つかりませんでした。"
        
        context_parts = []
        seen_content = set()
        
        for i, chunk in enumerate(chunks, start=1):
            content = chunk.get('content', '').strip()
            
            # 重複チェック（完全一致）
            if content in seen_content:
                continue
            
            seen_content.add(content)
            
            # セクション情報
            section = chunk.get('metadata', {}).get('section') or '情報なし'
            
            # フォーマット
            context_parts.append(
                f"[参考情報 {i}] (セクション: {section})\n{content}"
            )
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(
        self,
        system_prompt: str,
        context: str,
        question: str
    ) -> str:
        """完全なプロンプトを構築"""
        return f"""{system_prompt}

【コンテキスト情報】
{context}

【質問】
{question}

【回答】
"""