"""OCR引擎 - 用于扫描版PDF识别"""

import io
import logging
from PIL import Image
from typing import Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCREngine:
    """OCR识别引擎"""

    def __init__(self, lang: str = 'ch'):
        """
        初始化OCR引擎

        Args:
            lang: 语言，默认中文(ch)
        """
        self.lang = lang
        self.ocr = None
        self._init_ocr()

    def _init_ocr(self):
        """初始化PaddleOCR"""
        try:
            from paddleocr import PaddleOCR

            logger.info("正在初始化PaddleOCR引擎...")
            self.ocr = PaddleOCR(
                use_angle_cls=True,  # 方向分类
                lang=self.lang,
                show_log=False,
                use_gpu=False,  # CPU运行
            )
            logger.info("PaddleOCR初始化完成")

        except ImportError:
            logger.error("请先安装PaddleOCR: pip install paddleocr paddlepaddle")
            raise

    def recognize(self, image_data: Union[bytes, str]) -> str:
        """
        识别图片中的文字

        Args:
            image_data: 图片数据(bytes)或图片路径

        Returns:
            识别的文字
        """
        if self.ocr is None:
            return ""

        try:
            # 如果是bytes，保存为临时文件
            if isinstance(image_data, bytes):
                img = Image.open(io.BytesIO(image_data))
                temp_path = "_temp_ocr.png"
                img.save(temp_path)
                image_path = temp_path
            else:
                image_path = image_data

            # OCR识别
            result = self.ocr.ocr(image_path, cls=True)

            # 清理临时文件
            if isinstance(image_data, bytes):
                import os
                try:
                    os.remove(temp_path)
                except:
                    pass

            # 提取文字
            texts = []
            if result and result[0]:
                for line in result[0]:
                    if line:
                        texts.append(line[1][0])  # text content

            return '\n'.join(texts)

        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return ""

    def recognize_file(self, image_path: str) -> str:
        """
        识别图片文件中的文字

        Args:
            image_path: 图片文件路径

        Returns:
            识别的文字
        """
        return self.recognize(image_path)
