import logging
from pathlib import Path
from typing import Optional
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


class PDFExtractor:
    """PDFからテキストを抽出するクラス"""
    
    def __init__(self):
        self.logger = logger
    
    def extract_text(self, file_path: str) -> str:
        """
        PDFファイルからテキストを抽出
        
        Args:
            file_path: PDFファイルのパス
            
        Returns:
            str: 抽出されたテキスト
            
        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: PDF読み込みエラー
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            self.logger.info(f"Extracting text from PDF: {file_path}")
            
            reader = PdfReader(str(path))
            
            # 全ページからテキスト抽出
            text_parts = []
            for page_num, page in enumerate(reader.pages, start=1):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_parts.append(page_text)
                        self.logger.debug(f"Extracted {len(page_text)} chars from page {page_num}")
                except Exception as e:
                    self.logger.warning(f"Failed to extract text from page {page_num}: {e}")
                    continue
            
            full_text = "\n\n".join(text_parts)
            self.logger.info(f"Total extracted: {len(full_text)} characters from {len(text_parts)} pages")
            
            return full_text
            
        except FileNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"PDF extraction failed: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def get_page_count(self, file_path: str) -> int:
        """PDFのページ数を取得"""
        try:
            reader = PdfReader(str(file_path))
            return len(reader.pages)
        except Exception as e:
            self.logger.error(f"Failed to get page count: {e}")
            return 0