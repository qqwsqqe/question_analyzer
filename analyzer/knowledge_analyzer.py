"""知识点分析器 - 自动归纳知识点并统计出场率"""

import re
import jieba
import jieba.analyse
from collections import Counter
from typing import List, Dict, Tuple, Set
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

import sys
sys.path.append('D:/claude program/question_analyzer')
from config import STOP_WORDS, KNOWLEDGE_CONFIG


class KnowledgeAnalyzer:
    """知识点分析器"""

    def __init__(self):
        self.config = KNOWLEDGE_CONFIG
        self.stop_words = STOP_WORDS
        self.knowledge_keywords = []  # 提取的知识点关键词
        self.question_knowledge_map = {}  # 题目-知识点映射

    def analyze(self, questions: List) -> Dict[str, int]:
        """
        分析题目并提取知识点

        Args:
            questions: 题目对象列表

        Returns:
            知识点-频率字典
        """
        if not questions:
            return {}

        # 准备文本数据
        texts = []
        for q in questions:
            # 合并题干和所有选项作为分析文本
            text = q.stem + ' ' + ' '.join(q.options.values())
            texts.append(text)

        # 使用TF-IDF提取关键词
        self.knowledge_keywords = self._extract_keywords_tfidf(texts)

        # 为每道题分配知识点标签
        for i, question in enumerate(questions):
            question_text = texts[i]
            tags = self._assign_knowledge_tags(question_text)
            question.knowledge_tags = tags

        # 统计知识点出场率
        knowledge_freq = self._calculate_frequency(questions)

        return knowledge_freq

    def _extract_keywords_tfidf(self, texts: List[str]) -> List[Tuple[str, float]]:
        """
        使用TF-IDF提取关键词

        Args:
            texts: 文本列表

        Returns:
            (关键词, 权重)列表
        """
        # 预处理文本：分词并去除停用词
        processed_texts = []
        for text in texts:
            words = self._segment_and_filter(text)
            processed_texts.append(' '.join(words))

        # 使用TF-IDF
        try:
            vectorizer = TfidfVectorizer(
                max_features=100,
                ngram_range=self.config['ngram_range'],
                min_df=self.config['min_freq'],
                stop_words=list(self.stop_words)
            )

            tfidf_matrix = vectorizer.fit_transform(processed_texts)
            feature_names = vectorizer.get_feature_names_out()

            # 计算每个词的平均TF-IDF值
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)

            # 排序并取前K个
            keywords = [(feature_names[i], mean_scores[i])
                       for i in range(len(feature_names))]
            keywords.sort(key=lambda x: x[1], reverse=True)

            return keywords[:self.config['top_k']]

        except Exception as e:
            print(f"TF-IDF提取失败: {e}")
            # 降级方案：使用简单词频
            return self._extract_keywords_by_frequency(processed_texts)

    def _extract_keywords_by_frequency(self, texts: List[str]) -> List[Tuple[str, float]]:
        """基于词频提取关键词（降级方案）"""
        word_freq = Counter()

        for text in texts:
            words = text.split()
            for word in words:
                if len(word) > 1 and word not in self.stop_words:
                    word_freq[word] += 1

        # 过滤低频词
        min_freq = self.config['min_freq']
        filtered = [(word, freq) for word, freq in word_freq.items() if freq >= min_freq]

        # 按频率排序
        filtered.sort(key=lambda x: x[1], reverse=True)

        return filtered[:self.config['top_k']]

    # 投顾考试官方大纲四大模块知识点体系
    KNOWLEDGE_CATEGORIES = {
        # 第一部分：业务监管
        '业务监管': [
            '资格管理', '执业资格', '后续培训', '主要职责',
            '工作规程', '合规管理', '风控机制', '留痕管理',
            '禁止性行为', '职业操守', '法律责任', '监管措施',
            '静默期', '客户回访', '投诉处理',
        ],
        # 第二部分：专业基础
        '专业基础': [
            '生命周期理论', '货币时间价值', '现值', '终值', '年金',
            '资本资产定价', 'CAPM', '证券市场线',
            '证券组合', '可行域', '有效边界', '最优组合',
            '资产配置', '战略配置', '战术配置',
            '有效市场', '弱式有效', '半强式有效', '强式有效',
            '行为金融', '过度自信', '心理账户', '羊群效应', '损失厌恶',
        ],
        # 第三部分：专业技能 - 客户分析
        '客户分析': [
            '定量信息', '定性信息', '财务信息',
            '资产负债表', '现金流量表',
            '风险偏好', '风险承受能力', '风险特征',
            '投资需求', '投资目标', '理财目标',
        ],
        # 第三部分：专业技能 - 证券分析
        '证券分析': [
            '宏观分析', '行业分析', '公司分析',
            '偿债能力', '盈利能力', '营运能力', '成长能力',
            '杜邦分析', '分红派息', '财务报表',
            '绝对估值', '股息贴现', '股利增长',
            '相对估值', '市盈率', '市净率',
            '技术分析', 'K线', '趋势线', '支撑阻力',
            '移动平均线', 'MACD', 'RSI', '道氏理论',
        ],
        # 第三部分：专业技能 - 风险管理
        '风险管理': [
            '信用风险', '客户评级', '债项评级', '风险限额',
            '市场风险', '久期', '风险价值', 'VaR', '压力测试',
            '流动性风险', '流动性比率', '缺口分析',
            '风险对冲', '自我对冲', '市场对冲',
        ],
        # 第四部分：专项业务
        '投资组合': [
            '股票组合', '消极策略', '指数策略', '积极策略',
            '债券组合', '水平分析', '债券互换', '骑乘收益率',
            '免疫策略', '久期匹配',
            '衍生工具', '对冲策略', '对冲比率', '风险敞口',
            '套利策略', '期现套利', '跨期套利',
        ],
        '理财规划': [
            '现金管理', '消费管理', '债务管理', '应急资金',
            '保险规划', '寿险', '财险',
            '税收规划', '个人所得税',
            '教育规划', '教育金', '退休规划', '养老金',
            '遗产规划', '投资规划',
        ],
        # 投资工具
        '投资工具': [
            '股票', '债券', '基金', '公募基金', '私募基金',
            '衍生品', '期货', '期权', '互换',
            '货币市场', '资本市场', '一级市场', '二级市场',
        ],
        # 法律法规
        '法律法规': [
            '适当性', '投资者适当性', '风险匹配',
            '信息披露', '内幕交易', '操纵市场', '虚假陈述',
            '市场禁入', '执业规范',
        ],
    }

    # 合并为词典
    CORE_TERMS = {}
    for category, terms in KNOWLEDGE_CATEGORIES.items():
        for term in terms:
            CORE_TERMS[term] = 1000

    # 无意义词汇过滤 - 题干干扰词
    MEANINGLESS_WORDS = {
        '选择题', '单选题', '多选题', '不定项', '不定', '答案', '解析', '题目',
        '选项', '正确', '错误', '说法', '下列', '以下', '关于', '有关',
        '根据', '以上', '所述', '一项', '属于', '不属于', '主要', '需要',
        '包括', '包含', '各种', '有关', '一定', '必须', '应当', '不得',
        '可能', '应该', '可以', '符合', '违反', '规定', '按照', '依据',
        '一', '二', '三', '四', '五', '个', '种', '类', '项',
        'A', 'B', 'C', 'D', 'AB', 'AC', 'AD', 'BC', 'BD', 'CD',
        'ABC', 'ABD', 'ACD', 'BCD', 'ABCD',
        '投资', '投资者', '证券投资', '证券业', '金融服务',
    }

    def _segment_and_filter(self, text: str) -> List[str]:
        """分词并过滤 - 使用专业术语库"""
        # 添加自定义词典（投资顾问相关词汇）
        for term in self.CORE_TERMS.keys():
            jieba.add_word(term, freq=self.CORE_TERMS[term])

        # 分词
        words = jieba.lcut(text)

        # 过滤
        filtered = []
        for word in words:
            word = word.strip()
            # 优先保留专业术语
            if word in self.CORE_TERMS:
                filtered.append(word)
                continue

            # 过滤条件
            if (len(word) > 1 and
                word not in self.stop_words and
                word not in self.MEANINGLESS_WORDS and
                not word.isdigit() and
                not re.match(r'^[A-D]$', word) and
                not re.match(r'^[一二三四五六七八九十]+$', word)):
                filtered.append(word)

        return filtered

    def _assign_knowledge_tags(self, question_text: str, top_n: int = 3) -> List[str]:
        """
        为题目分配知识点标签

        Args:
            question_text: 题目文本
            top_n: 最多分配的标签数

        Returns:
            知识点标签列表
        """
        if not self.knowledge_keywords:
            return []

        # 分词
        words = set(self._segment_and_filter(question_text))

        # 匹配知识点关键词
        matched = []
        for keyword, weight in self.knowledge_keywords:
            # 检查关键词是否在文本中
            if keyword in question_text or any(kw in words for kw in keyword.split()):
                matched.append((keyword, weight))

        # 按权重排序，取前N个
        matched.sort(key=lambda x: x[1], reverse=True)

        return [tag for tag, _ in matched[:top_n]]

    def _calculate_frequency(self, questions: List) -> Dict[str, int]:
        """计算知识点出场率"""
        freq = Counter()

        for q in questions:
            for tag in q.knowledge_tags:
                freq[tag] += 1

        return dict(freq)

    def get_sorted_questions(self, questions: List) -> Tuple[List, Dict[str, int]]:
        """
        按知识点出场率排序题目

        Args:
            questions: 题目列表

        Returns:
            (排序后的题目列表, 知识点频率字典)
        """
        # 分析知识点
        freq = self.analyze(questions)

        # 为每个知识点计算总权重
        def get_question_priority(q):
            priority = 0
            for tag in q.knowledge_tags:
                priority += freq.get(tag, 0)
            return -priority  # 负值用于降序排序

        # 排序
        sorted_questions = sorted(questions, key=get_question_priority)

        return sorted_questions, freq

    def generate_report(self, freq: Dict[str, int], total_questions: int) -> str:
        """
        生成统计报告

        Args:
            freq: 知识点频率字典
            total_questions: 总题数

        Returns:
            报告文本
        """
        lines = ["=" * 50]
        lines.append("知识点出场率统计报告")
        lines.append("=" * 50)
        lines.append(f"总题数: {total_questions}")
        lines.append("")

        # 排序
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)

        lines.append("知识点排名（按出场率）：")
        lines.append("-" * 50)

        for i, (knowledge, count) in enumerate(sorted_freq, 1):
            percentage = (count / total_questions) * 100
            lines.append(f"{i:2d}. {knowledge:20s} {count:3d}题 ({percentage:5.1f}%)")

        lines.append("=" * 50)

        return '\n'.join(lines)
