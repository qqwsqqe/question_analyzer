"""PDF文件提取器"""

import re
try:
    import fitz  # PyMuPDF
except ImportError:
    import pymupdf as fitz
import pdfplumber
from pathlib import Path
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFExtractor:
    """PDF文本提取器，支持纯文本和扫描版PDF"""

    def __init__(self, use_ocr: bool = True):
        self.use_ocr = use_ocr
        self.ocr_engine = None

        if use_ocr:
            try:
                from .ocr_engine import OCREngine
                self.ocr_engine = OCREngine()
            except Exception as e:
                logger.warning(f"OCR引擎初始化失败: {e}")

    def extract(self, file_path: str) -> str:
        """
        提取PDF文本内容

        Args:
            file_path: PDF文件路径

        Returns:
            提取的文本内容
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 先尝试用pdfplumber提取纯文本
        text = self._extract_with_pdfplumber(file_path)

        # 如果提取的文本太少，可能是扫描版，尝试OCR
        if len(text.strip()) < 100 and self.ocr_engine:
            logger.info("文本内容较少，尝试OCR识别...")
            text = self._extract_with_ocr(file_path)

        return text

    def _extract_with_pdfplumber(self, file_path: Path) -> str:
        """使用pdfplumber提取文本"""
        text_parts = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
        except Exception as e:
            logger.error(f"pdfplumber提取失败: {e}")

        return '\n\n'.join(text_parts)

    def _extract_with_pymupdf(self, file_path: Path) -> str:
        """使用PyMuPDF提取文本（备用方案）"""
        text_parts = []

        try:
            doc = fitz.open(file_path)
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
        except Exception as e:
            logger.error(f"PyMuPDF提取失败: {e}")

        return '\n\n'.join(text_parts)

    def _extract_with_ocr(self, file_path: Path) -> str:
        """使用OCR提取扫描版PDF"""
        if not self.ocr_engine:
            return ""

        text_parts = []

        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                # 将页面转换为图片
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2倍分辨率
                img_data = pix.tobytes("png")

                # OCR识别
                page_text = self.ocr_engine.recognize(img_data)
                text_parts.append(page_text)

                logger.info(f"OCR完成第 {page_num + 1}/{len(doc)} 页")

            doc.close()
        except Exception as e:
            logger.error(f"OCR提取失败: {e}")

        return '\n\n'.join(text_parts)

    def is_scanned_pdf(self, file_path: str, sample_pages: int = 3) -> bool:
        """
        检测PDF是否为扫描版

        Args:
            file_path: PDF文件路径
            sample_pages: 采样页数

        Returns:
            True如果是扫描版
        """
        file_path = Path(file_path)

        try:
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                check_pages = min(sample_pages, total_pages)

                total_text_len = 0
                for i in range(check_pages):
                    text = pdf.pages[i].extract_text() or ""
                    total_text_len += len(text.strip())

                avg_text_len = total_text_len / check_pages

                # 平均每页少于50个字符认为是扫描版
                return avg_text_len < 50

        except Exception as e:
            logger.error(f"检测失败: {e}")
            return False
