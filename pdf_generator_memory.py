"""
考前急救记忆口诀PDF生成器

功能：生成带记忆口诀、统计规律的PDF，按知识点出现概率排序
核心理念：不需要理解，只需要记住答案！
"""

import os
from typing import List, Dict
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER

from analyzer.memory_trick_generator import MemoryTrickGenerator


class MemoryPDFGenerator:
    """考前急救记忆口诀PDF生成器"""

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
            fontSize=20,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#1a1a2e')
        )

        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=colors.HexColor('#4a4a4a')
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontName=self.chinese_font,
            fontSize=14,
            spaceAfter=10,
            textColor=colors.HexColor('#16213e'),
            borderPadding=5
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

        # 记忆口诀专用样式
        self.trick_box_style = ParagraphStyle(
            'TrickBox',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            leading=16,
            leftIndent=10,
            rightIndent=10,
            spaceAfter=8,
            textColor=colors.HexColor('#2c3e50')
        )

        self.answer_highlight_style = ParagraphStyle(
            'AnswerHighlight',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=12,
            leading=20,
            textColor=colors.HexColor('#e74c3c'),
            spaceAfter=6
        )

        self.statistics_style = ParagraphStyle(
            'Statistics',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            leading=16,
            leftIndent=15,
            textColor=colors.HexColor('#27ae60')
        )

    def add_title(self, title: str):
        """添加标题"""
        self.story.append(Paragraph(title, self.title_style))
        self.story.append(Paragraph("急救记忆版 - 按考点概率排序", self.subtitle_style))
        self.story.append(Spacer(1, 20))

    def add_statistics_summary(self, questions: List):
        """添加统计规律汇总"""
        self.story.append(Paragraph("考前必看统计秘籍", self.heading_style))
        self.story.append(Spacer(1, 10))

        # 生成统计汇总
        stats_text = MemoryTrickGenerator.generate_statistics_summary(questions)

        # 分行添加到PDF
        for line in stats_text.split('\n'):
            if line.strip():
                if line.startswith('='):
                    self.story.append(Spacer(1, 10))
                elif line.startswith('【'):
                    self.story.append(Paragraph(line, self.heading_style))
                elif line.startswith('  '):
                    self.story.append(Paragraph(line, self.statistics_style))
                else:
                    self.story.append(Paragraph(line, self.normal_style))

        self.story.append(PageBreak())

    def add_memory_guide(self):
        """添加记忆方法指导"""
        self.story.append(Paragraph("记忆口诀使用指南", self.heading_style))
        self.story.append(Spacer(1, 10))

        guide_content = [
            ("快速口诀", "看到题目第一时间想起的关键词联想，1秒内唤起记忆"),
            ("完整故事", "荒诞夸张的联想故事，帮助深度记忆复杂知识点"),
            ("法规统计", "法律法规类题目的统计规律，什么情况下选几年"),
            ("计算技巧", "计算题的凑数方法，题干数字怎么组合出答案"),
            ("概率重点", "按知识点出现概率排序，优先复习高频考点"),
        ]

        for title, desc in guide_content:
            text = f"<b>{title}</b>：{desc}"
            self.story.append(Paragraph(text, self.normal_style))

        tips = [
            "",
            "记忆要诀：",
            "1. 先看口诀，再看题目，形成条件反射",
            "2. 把口诀读出声，听觉记忆更深刻",
            "3. 按知识点出现概率排序，优先复习高频考点",
            "4. 实在不会的题，用统计规律辅助判断",
        ]

        for tip in tips:
            if tip:
                self.story.append(Paragraph(tip, self.normal_style))

        self.story.append(PageBreak())

    def add_knowledge_priority(self, questions: List):
        """添加知识点优先级排序（按出现概率）"""
        self.story.append(Paragraph("知识点优先级（按出现概率排序）", self.heading_style))
        self.story.append(Spacer(1, 10))

        # 统计各知识点出现次数
        knowledge_count = {}
        for q in questions:
            for tag in q.knowledge_tags:
                knowledge_count[tag] = knowledge_count.get(tag, 0) + 1

        # 按出现次数排序
        sorted_knowledge = sorted(knowledge_count.items(), key=lambda x: x[1], reverse=True)

        # 添加概率统计表格
        table_data = [['知识点', '出现次数', '占比']]
        total_questions = len(questions)

        for knowledge, count in sorted_knowledge[:15]:  # 显示前15个
            percentage = f"{count/total_questions*100:.1f}%"
            table_data.append([knowledge, str(count), percentage])

        table = Table(table_data, colWidths=[200, 80, 80])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 15))

        # 添加复习建议
        self.story.append(Paragraph("复习建议", self.heading_style))
        suggestions = [
            "第一梯队（概率>10%）：必须掌握，反复记忆口诀",
            "第二梯队（概率5-10%）：尽量掌握，理解关键词",
            "第三梯队（概率<5%）：有印象即可，实在不会可放弃",
        ]
        for suggestion in suggestions:
            self.story.append(Paragraph(suggestion, self.normal_style))

        self.story.append(PageBreak())

    def add_questions_with_tricks(self, questions: List):
        """添加带记忆口诀的题目列表"""
        self.story.append(Paragraph("题目+记忆口诀（按出现概率排序）", self.heading_style))
        self.story.append(Spacer(1, 10))

        for i, q in enumerate(questions, 1):
            # 生成记忆口诀
            memory = MemoryTrickGenerator.generate(q)

            # 题目编号和知识点
            tags_text = " | ".join(q.knowledge_tags[:3]) if q.knowledge_tags else "未分类"
            header = f"题目 {i} (原题号: {q.number})  [知识点: {tags_text}]"
            self.story.append(Paragraph(header, self.heading_style))

            # 题干
            stem_text = self._escape_html(q.stem)
            self.story.append(Paragraph(stem_text, self.normal_style))

            # 选项（全部显示，答案高亮）
            for opt_label in ['A', 'B', 'C', 'D']:
                if opt_label in q.options:
                    opt_text = self._escape_html(q.options[opt_label])
                    if opt_label == q.answer:
                        # 正确答案高亮
                        option_line = f"<b>【答案】{opt_label}. {opt_text}</b>"
                        self.story.append(Paragraph(option_line, self.answer_highlight_style))
                    else:
                        option_line = f"&nbsp;&nbsp;&nbsp;&nbsp;{opt_label}. {opt_text}"
                        self.story.append(Paragraph(option_line, self.option_style))

            # 分隔线效果
            self.story.append(Spacer(1, 5))

            # ========== 记忆口诀区域 ==========
            trick_parts = []

            # 1. 快速口诀
            if memory.get('quick_trick'):
                trick_parts.append(f"<b>[口诀]</b> {memory['quick_trick']}")

            # 2. 简单提示
            if memory.get('keyword_bind'):
                trick_parts.append(f"<b>[记]</b> {memory['keyword_bind']}")

            # 3. 完整故事/解释
            if memory.get('full_story'):
                story = memory['full_story'].replace('\n', '<br/>')
                trick_parts.append(f"<b>[逻辑]</b> {story}")

            # 4. 法规统计
            if memory.get('law_pattern'):
                law = memory['law_pattern'].replace('\n', '<br/>')
                trick_parts.append(f"<b>[法规]</b> {law}")

            # 5. 计算技巧
            if memory.get('calculation_trick'):
                calc = memory['calculation_trick'].replace('\n', '<br/>')
                trick_parts.append(f"<b>[计算]</b> {calc}")

            # 如果有记忆口诀，添加带背景色的区域
            if trick_parts:
                trick_text = "<br/>".join(trick_parts)
                # 使用表格创建带背景色的区域
                trick_data = [[Paragraph(trick_text, self.trick_box_style)]]
                trick_table = Table(trick_data, colWidths=[440])
                trick_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff9e6')),
                    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#f39c12')),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                self.story.append(trick_table)

            self.story.append(Spacer(1, 20))

            # 每5题分页，保持节奏
            if i % 5 == 0 and i < len(questions):
                self.story.append(PageBreak())

    def add_emergency_cheat_sheet(self, questions: List):
        """添加急救速查表（最后一页）"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("考前急救速查表", self.heading_style))
        self.story.append(Spacer(1, 10))

        # 高频知识点速记
        self.story.append(Paragraph("高频知识点速记", self.heading_style))

        # 统计各知识点出现次数
        knowledge_count = {}
        for q in questions:
            for tag in q.knowledge_tags:
                knowledge_count[tag] = knowledge_count.get(tag, 0) + 1

        # 取前10个高频知识点
        top_knowledge = sorted(knowledge_count.items(), key=lambda x: x[1], reverse=True)[:10]

        for i, (knowledge, count) in enumerate(top_knowledge, 1):
            # 找到该知识点的记忆口诀
            sample_q = next((q for q in questions if knowledge in q.knowledge_tags), None)
            if sample_q:
                memory = MemoryTrickGenerator.generate(sample_q)
                trick = memory.get('quick_trick', '')[:50]  # 取前50字
                text = f"{i}. <b>{knowledge}</b> ({count}题)<br/>&nbsp;&nbsp;{trick}..."
                self.story.append(Paragraph(text, self.normal_style))
                self.story.append(Spacer(1, 5))

        self.story.append(Spacer(1, 15))

        # 终极蒙题技巧
        self.story.append(Paragraph("终极蒙题技巧（实在不会时用）", self.heading_style))
        cheat_tips = [
            "• 选项中有绝对词（一定、必须、永远、不可能）→ 大概率错",
            "• 两个选项意思相反 → 答案在其中之一",
            "• 选项长度三长一短 → 选最短；三短一长 → 选最长",
            "• 数字题看尾数：尾数0、5的选项优先验证",
            "• 实在不会选B或C（统计显示出现率约30%）",
            "• 多选题宁少勿多，不确定的不选",
            "• 法规题：个人处罚5年，刑事犯罪10年，特别严重终身",
            "• 计算题：看题干数字，试试加减乘除组合",
        ]
        for tip in cheat_tips:
            self.story.append(Paragraph(tip, self.normal_style))

    def _escape_html(self, text: str) -> str:
        """转义HTML特殊字符"""
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        return text

    def generate_full_report(self, questions: List, freq: Dict[str, int]):
        """生成完整的急救记忆报告"""
        # 1. 标题
        self.add_title("投资顾问考试急救记忆手册")

        # 2. 统计秘籍
        self.add_statistics_summary(questions)

        # 3. 使用指南
        self.add_memory_guide()

        # 4. 知识点优先级
        self.add_knowledge_priority(questions)

        # 5. 题目+口诀（主体内容）
        self.add_questions_with_tricks(questions)

        # 6. 急救速查表
        self.add_emergency_cheat_sheet(questions)

    def save(self):
        """保存PDF"""
        self.doc.build(self.story)
        print(f"急救记忆版PDF已生成: {self.output_path}")
