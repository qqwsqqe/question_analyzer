"""PDF生成器 - 生成排序后的题目PDF"""

import os
from datetime import datetime
from typing import List, Dict
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class PDFGenerator:
    """题目PDF生成器"""

    def __init__(self, output_path: str):
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        self.story = []
        self.styles = getSampleStyleSheet()

        # 尝试注册中文字体
        self._register_chinese_font()

    def _register_chinese_font(self):
        """注册中文字体"""
        font_paths = [
            'C:/Windows/Fonts/simhei.ttf',  # 黑体
            'C:/Windows/Fonts/simsun.ttc',  # 宋体
            'C:/Windows/Fonts/msyh.ttc',    # 微软雅黑
            'C:/Windows/Fonts/simkai.ttf',  # 楷体
        ]

        self.chinese_font = 'Helvetica'
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font_name = os.path.basename(font_path).split('.')[0]
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    self.chinese_font = font_name
                    print(f"成功加载字体: {font_name}")
                    break
                except Exception as e:
                    print(f"字体加载失败: {font_path}, {e}")
                    continue

        # 创建自定义样式
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontName=self.chinese_font,
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=30
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontName=self.chinese_font,
            fontSize=14,
            spaceAfter=12
        )

        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=11,
            leading=18,
            spaceAfter=6
        )

        self.option_style = ParagraphStyle(
            'OptionStyle',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            leading=16,
            leftIndent=20
        )

    def add_title(self, title: str):
        """添加标题"""
        self.story.append(Paragraph(title, self.title_style))
        self.story.append(Spacer(1, 20))

    def add_summary(self, freq: Dict[str, int], total_questions: int):
        """添加统计摘要"""
        self.story.append(Paragraph("一、知识点出场率统计", self.heading_style))
        self.story.append(Spacer(1, 10))

        # 创建表格数据
        data = [['排名', '知识点', '出场次数', '占比']]
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)

        for i, (knowledge, count) in enumerate(sorted_freq, 1):
            percentage = f"{(count / total_questions) * 100:.1f}%"
            data.append([str(i), knowledge, str(count), percentage])

        # 创建表格
        table = Table(data, colWidths=[40, 200, 80, 60])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), self.chinese_font),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 20))

        # 添加说明
        summary_text = f"共分析 {total_questions} 道题目，识别出 {len(freq)} 个知识点。"
        self.story.append(Paragraph(summary_text, self.normal_style))
        self.story.append(PageBreak())

    def add_questions(self, questions: List):
        """添加题目列表"""
        self.story.append(Paragraph("二、题目列表（按知识点出场率排序）", self.heading_style))
        self.story.append(Spacer(1, 10))

        for i, q in enumerate(questions, 1):
            # 题目编号和知识点
            tags_text = " | ".join(q.knowledge_tags) if q.knowledge_tags else "未分类"
            header = f"题目 {i} (原题号: {q.number})  [知识点: {tags_text}]"
            self.story.append(Paragraph(header, self.heading_style))

            # 题干
            stem_text = self._escape_html(q.stem)
            self.story.append(Paragraph(stem_text, self.normal_style))

            # 选项
            for opt_label in ['A', 'B', 'C', 'D']:
                if opt_label in q.options:
                    opt_text = self._escape_html(q.options[opt_label])
                    option_line = f"&nbsp;&nbsp;&nbsp;&nbsp;{opt_label}. {opt_text}"
                    self.story.append(Paragraph(option_line, self.option_style))

            # 答案和解析
            if q.answer:
                answer_text = f"<b>答案：</b>{q.answer}"
                self.story.append(Paragraph(answer_text, self.normal_style))

            if q.analysis:
                analysis_text = f"<b>解析：</b>{self._escape_html(q.analysis)}"
                self.story.append(Paragraph(analysis_text, self.normal_style))

            self.story.append(Spacer(1, 15))

            # 每10题分页，避免过长
            if i % 10 == 0 and i < len(questions):
                self.story.append(PageBreak())

    def _escape_html(self, text: str) -> str:
        """转义HTML特殊字符"""
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        return text

    def save(self):
        """保存PDF"""
        self.doc.build(self.story)
        print(f"PDF已生成: {self.output_path}")
