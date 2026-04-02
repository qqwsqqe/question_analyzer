"""题目解析器"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from config import QUESTION_PATTERNS


@dataclass
class Question:
    """题目数据类"""
    number: int = 0                          # 题号
    stem: str = ""                           # 题干
    options: Dict[str, str] = field(default_factory=dict)  # 选项 {A: "选项内容", ...}
    answer: str = ""                         # 答案
    analysis: str = ""                       # 解析
    knowledge_tags: List[str] = field(default_factory=list)  # 知识点标签
    original_text: str = ""                  # 原始文本

    def __str__(self) -> str:
        lines = [f"第{self.number}题: {self.stem}"]
        for opt, text in self.options.items():
            lines.append(f"  {opt}. {text}")
        if self.answer:
            lines.append(f"  答案: {self.answer}")
        if self.knowledge_tags:
            lines.append(f"  知识点: {', '.join(self.knowledge_tags)}")
        return '\n'.join(lines)


class QuestionParser:
    """题目解析器"""

    def __init__(self):
        self.patterns = QUESTION_PATTERNS
        self._compile_patterns()

    def _compile_patterns(self):
        """编译正则表达式"""
        self.number_pattern = re.compile(self.patterns['question_number'], re.MULTILINE)
        self.option_pattern = re.compile(self.patterns['option'])
        self.answer_pattern = re.compile(self.patterns['answer'])
        self.analysis_pattern = re.compile(self.patterns['analysis'])

    def parse(self, text: str) -> List[Question]:
        """
        解析文本中的题目

        Args:
            text: 原始文本

        Returns:
            题目列表
        """
        # 清理文本
        text = self._clean_text(text)

        # 分割题目块
        question_blocks = self._split_questions(text)

        # 解析每个题目
        questions = []
        for block in question_blocks:
            question = self._parse_single_question(block)
            if question.stem:  # 只保留有题干的题目
                questions.append(question)

        return questions

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 统一换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 过滤广告信息
        # 1. 押题/微信号/联系方式类广告
        text = re.sub(r'更多押题\+v[：:]\s*\w+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'押题[微信]*[：:]\s*\w+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'v[：:]\s*[a-zA-Z0-9_]+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'vx[：:]\s*\w+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'微信[号]*[：:]\s*\w+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'qq[：:]\s*\d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\d{3,}[^\n]*押题[^\n]*', '', text, flags=re.IGNORECASE)
        # 2. 去除行尾残留的数字（广告后面的数字如"24"）
        text = re.sub(r'\s+\d{1,3}\s*$', '', text, flags=re.MULTILINE)
        # 3. 去除行首的干扰数字
        text = re.sub(r'^\s*\d{1,2}\s+', '', text, flags=re.MULTILINE)

        # 4. 移除多余的空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 移除特殊字符
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', text)
        return text.strip()

    def _split_questions(self, text: str) -> List[str]:
        """
        将文本分割成题目块
        通过题号来分割
        """
        # 查找所有题号位置
        matches = list(self.number_pattern.finditer(text))

        if not matches:
            return [text]

        blocks = []
        for i, match in enumerate(matches):
            start = match.start()
            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(text)
            blocks.append(text[start:end].strip())

        return blocks

    def _parse_single_question(self, block: str) -> Question:
        """解析单个题目块"""
        question = Question(original_text=block)

        # 提取题号
        number_match = self.number_pattern.search(block)
        if number_match:
            question.number = int(number_match.group(1))

        # 提取答案（在清理前提取）
        answer_match = self.answer_pattern.search(block)
        if answer_match:
            question.answer = answer_match.group(1).strip()

        # 提取解析
        analysis_match = self.analysis_pattern.search(block)
        if analysis_match:
            question.analysis = analysis_match.group(1).strip()

        # 移除答案和解析部分，便于提取题干和选项
        clean_block = block
        if answer_match:
            clean_block = clean_block[:answer_match.start()] + clean_block[answer_match.end():]
        if analysis_match:
            clean_block = re.sub(self.patterns['analysis'], '', clean_block, flags=re.MULTILINE)

        # 提取选项
        options = {}
        option_matches = list(self.option_pattern.finditer(clean_block))

        # 找到第一个选项的位置
        first_option_pos = option_matches[0].start() if option_matches else len(clean_block)

        for match in option_matches:
            opt_label = match.group(1)
            opt_text = match.group(2).strip()
            options[opt_label] = opt_text

        question.options = options

        # 提取题干
        # 题干在题号之后、第一个选项之前
        stem_text = clean_block
        if number_match:
            stem_text = stem_text[number_match.end():]
        if option_matches:
            stem_text = stem_text[:first_option_pos - number_match.end() if number_match else first_option_pos]

        # 清理题干
        stem_text = stem_text.strip()
        # 移除选项行
        for opt_label in ['A', 'B', 'C', 'D']:
            stem_text = re.sub(rf'{opt_label}[\.、\.\)].*?(?=\n|$)', '', stem_text)

        question.stem = stem_text.strip()

        return question

    def batch_parse(self, texts: List[str]) -> List[Question]:
        """
        批量解析多个文本

        Args:
            texts: 文本列表

        Returns:
            合并后的题目列表
        """
        all_questions = []
        for text in texts:
            questions = self.parse(text)
            all_questions.extend(questions)

        # 按题号排序
        all_questions.sort(key=lambda q: q.number)

        return all_questions
