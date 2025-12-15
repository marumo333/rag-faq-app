import logging
import re
from typing import List, Optional
from uuid import UUID, uuid4

from domain.entities.chunk import Chunk


logger = logging.getLogger(__name__)

class ChunkSplitter:
    """テキストをチャンクに分割するドメインサービス"""
    
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100
    ):
        """
        Args:
            chunk_size: 目標チャンクサイズ（文字数）
            chunk_overlap: チャンク間のオーバーラップ（文字数）
            min_chunk_size: 最小チャンクサイズ（これより小さいチャンクは破棄）
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.logger = logger
    
    def split(self, document_id: UUID, text: str) -> List[Chunk]:
        """
        テキストをチャンクに分割
        
        Args:
            document_id: ドキュメントID
            text: 分割対象のテキスト
            
        Returns:
            List[Chunk]: 分割されたチャンクのリスト
        """
        if not text or not text.strip():
            self.logger.warning("Empty text provided for chunking")
            return []
        
        # セクション単位で分割（見出しベース）
        sections = self._split_by_sections(text)
        
        # 各セクションをさらに細かく分割
        chunks = []
        for section_title, section_text in sections:
            section_chunks = self._split_text(
                document_id=document_id,
                text=section_text,
                section=section_title,
                start_index=len(chunks)
            )
            chunks.extend(section_chunks)
        
        self.logger.info(f"Created {len(chunks)} chunks from text ({len(text)} chars)")
        return chunks
    
    def _split_by_sections(self, text: str) -> List[tuple[Optional[str], str]]:
        """
        見出しベースでセクションに分割
        
        Returns:
            List[(section_title, section_text)]
        """
        # 見出しパターン（# 見出し、## 見出し、第1章、など）
        heading_patterns = [
            r'^#+\s+(.+)$',           # Markdown見出し
            r'^第[0-9一二三四五六七八九十百]+章\s*(.*)$',  # 第N章
            r'^[0-9]+\.\s+(.+)$',     # 1. 見出し
            r'^【(.+)】$',             # 【見出し】
        ]
        
        combined_pattern = '|'.join(f'({p})' for p in heading_patterns)
        
        lines = text.split('\n')
        sections = []
        current_section = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                current_text.append('')
                continue
            
            # 見出しマッチング
            is_heading = False
            for pattern in heading_patterns:
                match = re.match(pattern, line)
                if match:
                    # 前のセクションを保存
                    if current_text:
                        sections.append((current_section, '\n'.join(current_text)))
                    
                    # 新しいセクション開始
                    current_section = line
                    current_text = []
                    is_heading = True
                    break
            
            if not is_heading:
                current_text.append(line)
        
        # 最後のセクション
        if current_text:
            sections.append((current_section, '\n'.join(current_text)))
        
        # セクションが1つもない場合は全体を1セクションとする
        if not sections:
            sections = [(None, text)]
        
        return sections
    
    def _split_text(
        self,
        document_id: UUID,
        text: str,
        section: Optional[str],
        start_index: int
    ) -> List[Chunk]:
        """
        テキストをチャンクサイズに基づいて分割
        
        Args:
            document_id: ドキュメントID
            text: 分割対象テキスト
            section: セクション名
            start_index: チャンクインデックスの開始番号
            
        Returns:
            List[Chunk]: チャンクのリスト
        """
        chunks = []
        
        # 段落で分割
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        current_chunk_text = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            # 段落が大きすぎる場合は文単位で分割
            if para_length > self.chunk_size:
                # 現在のチャンクを保存
                if current_chunk_text:
                    chunks.append(self._create_chunk(
                        document_id,
                        '\n\n'.join(current_chunk_text),
                        section,
                        start_index + len(chunks)
                    ))
                    current_chunk_text = []
                    current_length = 0
                
                # 大きな段落を文単位で分割
                sentence_chunks = self._split_large_paragraph(para)
                for sent_chunk in sentence_chunks:
                    chunks.append(self._create_chunk(
                        document_id,
                        sent_chunk,
                        section,
                        start_index + len(chunks)
                    ))
            
            # チャンクサイズを超える場合
            elif current_length + para_length > self.chunk_size:
                # 現在のチャンクを保存
                if current_chunk_text:
                    chunks.append(self._create_chunk(
                        document_id,
                        '\n\n'.join(current_chunk_text),
                        section,
                        start_index + len(chunks)
                    ))
                
                # 新しいチャンク開始（オーバーラップ考慮）
                if self.chunk_overlap > 0 and current_chunk_text:
                    # 最後の段落を次のチャンクに含める
                    current_chunk_text = [current_chunk_text[-1], para]
                    current_length = len(current_chunk_text[-2]) + para_length
                else:
                    current_chunk_text = [para]
                    current_length = para_length
            else:
                # チャンクに追加
                current_chunk_text.append(para)
                current_length += para_length
        
        # 残りのチャンク
        if current_chunk_text:
            chunk_text = '\n\n'.join(current_chunk_text)
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append(self._create_chunk(
                    document_id,
                    chunk_text,
                    section,
                    start_index + len(chunks)
                ))
        
        return chunks
    
    def _split_large_paragraph(self, text: str) -> List[str]:
        """大きな段落を文単位で分割"""
        sentences = re.split(r'([。！？\n])', text)
        
        chunks = []
        current = []
        current_length = 0
        
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]
            else:
                sentence = sentences[i]
            
            if current_length + len(sentence) > self.chunk_size and current:
                chunks.append(''.join(current))
                current = [sentence]
                current_length = len(sentence)
            else:
                current.append(sentence)
                current_length += len(sentence)
        
        if current:
            chunks.append(''.join(current))
        
        return chunks
    
    def _create_chunk(
        self,
        document_id: UUID,
        content: str,
        section: Optional[str],
        position: int
    ) -> Chunk:
        """Chunkエンティティを作成"""
        return Chunk(
            id=uuid4(),
            document_id=document_id,
            content=content.strip(),
            section=section,
            position=position
        )