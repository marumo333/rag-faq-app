import logging
import os
from typing import Any, Dict, List, Optional, Tuple
import google.generativeai as genai  # type: ignore[import-untyped,attr-defined]
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
        
        # システムプロンプトの準備
        base_system = system_instruction or self._get_default_system_prompt()
        self.system_instruction = base_system
        self.model_name = model
        
        # GenerativeModelの初期化
        # ここで system_instruction を渡しているため、generate_content 時には不要です
        self.model = genai.GenerativeModel(
            model_name=model,
            system_instruction=base_system
        )
        self.logger = logger
    
    def generate_answer(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        質問に対してコンテキストを使用して回答を生成
        """
        try:
            # コンテキストの整形（実際に使用されたチャンク数を受け取る）
            formatted_context, used_count = self._format_context(context_chunks)
            
            # プロンプトの構築
            prompt = self._build_prompt(
                context=formatted_context,
                question=question
            )
            
            # トークン数の見積もり
            tokens_info = self.model.count_tokens(prompt)
            input_tokens = tokens_info.total_tokens
            
            self.logger.info(f"Estimated Input Tokens: {input_tokens}")
            self.logger.info(f"Generating answer for question: '{question}'")
            # 検索ヒット数と、実際にコンテキストに入った数を分けてログ出力
            self.logger.debug(f"Using {used_count} chunks (retrieved {len(context_chunks)})")
            
            # Gemini APIで回答生成
            response = self.model.generate_content(prompt)
            
            answer_text = response.text
            
            self.logger.info(f"Answer generated: {len(answer_text)} characters")
            
            return {
                "answer": answer_text,
                "model": self.model_name,
                "chunks_used": used_count, # 実際に使用された数（監査用）
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
    
    def _format_context(self, chunks: List[Dict[str, Any]], max_chars: int = 8000) -> Tuple[str, int]:
        """
        チャンクリストをコンテキスト文字列に整形（文字数制限で切り詰め）
        Returns:
            Tuple[str, int]: (整形済みテキスト, 使用したチャンク数)
        """
        if not chunks:
            return "関連情報が見つかりませんでした。", 0

        context_parts: List[str] = []
        seen_content: set[str] = set()
        current_len = 0
        used_count = 0

        for i, chunk in enumerate(chunks, start=1):
            content = chunk.get("content", "").strip()
            
            if not content or content in seen_content:
                continue

            seen_content.add(content)
            
            section = chunk.get("metadata", {}).get("section") or "情報なし"
            # ヘッダー部分を作成
            header = f"[参考情報 {i}] (セクション: {section})\n"
            
            # 追加に必要な基本文字数（前の要素との間の改行 \n\n を考慮）
            separator_len = 2 if context_parts else 0
            
            # このチャンクを追加したときの合計予想長
            estimated_len = current_len + separator_len + len(header) + len(content)

            if estimated_len <= max_chars:
                # 制限内ならそのまま追加
                part = f"{header}{content}"
                context_parts.append(part)
                current_len = estimated_len
                used_count += 1
            else:
                # 制限を超える場合：残り容量に合わせてコンテンツを切り詰める
                suffix = "...(省略)"
                
                # コンテンツ部分（サフィックス含む）に使える残り文字数を計算
                # max_chars - (現在長 + セパレータ + ヘッダー)
                available_for_content_block = max_chars - (current_len + separator_len + len(header))
                
                # サフィックス分を引いて、実際のコンテンツをスライスする長さを決定
                slice_len = available_for_content_block - len(suffix)
                
                if slice_len > 0:
                    # コンテンツを少しでも表示できる場合のみ追加
                    truncated_content = content[:slice_len] + suffix
                    part = f"{header}{truncated_content}"
                    context_parts.append(part)
                    used_count += 1
                    
                    self.logger.warning(
                        f"Chunk {i} truncated to fit context limit. "
                        f"(Used {slice_len} chars of content)"
                    )
                else:
                    # サフィックスすら入らない、あるいはコンテンツがほぼ入らない場合は諦める
                    self.logger.warning(f"Context full. Stopped before chunk {i}.")
                
                # 制限に達したので、これ以降のチャンクは処理せず終了
                break

        if not context_parts:
            # 万が一、検索結果はあるが制限が厳しすぎて1つも入らなかった場合
            return "関連情報は見つかりましたが、コンテキスト制限により内容を含められませんでした。", 0

        final_text = "\n\n".join(context_parts)
        return final_text, used_count
        
    
    def _build_prompt(
        self,
        context: str,
        question: str
    ) -> str:
        """
        ユーザープロンプトの構築
        ※System Instructionはモデル初期化時に設定済みのため、ここには含めない
        """
        return f"""以下の【コンテキスト情報】を使用して、【質問】に回答してください。

【コンテキスト情報】
{context}

【質問】
{question}
"""