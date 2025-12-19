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
        model: str = "models/gemini-2.5-flash-lite",
        system_instruction: Optional[str] = None
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
        base_system = system_instruction or self._get_default_system_prompt()
        self.system_instruction = base_system
        self.model_name = model
        self.model = genai.GenerativeModel(
            model=model,
            system_instruction=base_system
        )
        self.logger = logger
    
    def generate_answer(
        self,
        question: str,
        context_chunks: List[dict]
    ) -> dict:
        """
        質問に対してコンテキストを使用して回答を生成
        
        Args:
            question: ユーザーの質問
            context_chunks: 検索されたチャンクのリスト
            
        Returns:
            dict: 回答テキストと使用したチャンク情報
        """
        try:
            # コンテキストの整形
            formatted_context = self._format_context(context_chunks)
            
            # プロンプトの構築
            prompt = self._build_prompt(
                context=formatted_context,
                question=question
            )
            tokens_info = self.model.count_tokens(prompt)
            input_tokens = tokens_info.total_tokens
            self.logger.info(f"Estimated Input Tokens: {input_tokens}")
            self.logger.info(f"Generating answer for question: '{question}'")
            self.logger.debug(f"Using {len(context_chunks)} context chunks")
            
            # Gemini APIで回答生成
            response = self.model.generate_content(prompt)
            
            answer_text = response.text
            
            self.logger.info(f"Answer generated: {len(answer_text)} characters")
            
            return {
                "answer": answer_text,
                "model": self.model_name,
                "chunks_used": len(context_chunks),
                "input_tokens": input_tokens
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
    
    def _format_context(self, chunks: List[dict], max_chars: int = 8000) -> str:
        """
        チャンクリストをコンテキスト文字列に整形
        
        重複や矛盾を抑制するために：
        - 類似度の高い順にソート済み
        - セクション情報を含める
        - チャンクIDを参照として保持
        """
        if not chunks:
            return "関連情報が見つかりませんでした。"
        
        context_parts:list[str] = []
        seen_content: set[str] = set()
        current_len = 0
        
        for i, chunk in enumerate(chunks, start=1):
            content = chunk.get('content', '').strip()
        
            # 空または重複チェック
            if not content or content in seen_content:
                continue
            
            seen_content.add(content)
            
            # セクション情報
            section = chunk.get('metadata', {}).get('section') or '情報なし'
            part = f"[参考情報 {i}] (セクション: {section})\n{content}"
            
            #追加後の長さを計算
            additional = len(part) + (2 if context_parts else 0) # 改行文を加味

            # 文字数制限を超える場合は切り捨て
            if current_len + additional > max_chars:
                break
            
            context_parts.append(part)
            current_len += additional

        return "\n\n".join(context_parts) if context_parts else "関連情報が見つかりませんでした。"
        
    
    def _build_prompt(
        self,
        context: str,
        question: str
    ) -> str:
        """完全なプロンプトを構築"""
        return f"""{self.system_instruction}

【コンテキスト情報】
{context}

【質問】
{question}

【回答】
"""