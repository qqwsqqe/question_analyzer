# -*- coding: utf-8 -*-
"""
考前急救记忆口诀生成器

功能：为每道题目生成简洁、幽默、易记的记忆口诀
核心理念：不需要理解，只需要记住答案！
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import sys
sys.path.append('D:/claude program/question_analyzer')


@dataclass
class MemoryTemplate:
    """记忆模板"""
    keywords: List[str]
    answer_hint: str
    trick: str
    story: str
    option_tricks: Dict[str, str]


class MemoryTrickGenerator:
    """考前急救记忆口诀生成器"""

    # 投顾考试常见知识点记忆库
    KNOWLEDGE_MEMORY_BANK: Dict[str, MemoryTemplate] = {
        "分散投资": MemoryTemplate(
            keywords=["分散", "多样化", "组合"],
            answer_hint="非系统性风险",
            trick="分散只能防个别风险（非系统），不能防整体风险（系统）",
            story="分散投资 = 东边不亮西边亮。单个公司倒闭（非系统）不影响整体，但经济危机（系统）谁也跑不了。",
            option_tricks={"B": "非系统性 = 个别风险"}
        ),
        "系统性风险": MemoryTemplate(
            keywords=["系统性风险", "市场风险", "不可分散"],
            answer_hint="无法通过分散消除",
            trick="系统风险 = 影响整个市场，分散没用",
            story="系统性风险是整个市场的问题，就像台风来了，所有船都会摇晃，不管你买了多少条船。",
            option_tricks={}
        ),
        "股票": MemoryTemplate(
            keywords=["股票", "权益", "高风险高收益"],
            answer_hint="风险最高/收益最高",
            trick="股票 = 剩余索取权，亏完才是你的",
            story="股票是最后拿钱的人。公司破产先还债，再还优先股，最后才轮到普通股股东。所以风险最高。",
            option_tricks={}
        ),
        "债券": MemoryTemplate(
            keywords=["债券", "固定收益", "稳健"],
            answer_hint="风险低于股票",
            trick="债券 = 债权优先，固定收益",
            story="债券是债主关系。公司破产要先还债，利息固定。相比股票的不确定性，债券风险更低。",
            option_tricks={}
        ),
        "复利": MemoryTemplate(
            keywords=["复利", "利滚利", "时间价值"],
            answer_hint="时间越长效果越明显",
            trick="复利 = 利滚利，时间越长威力越大",
            story="复利是利息再生利息。时间越长，产生的利息越多，再生的利息也越多，呈指数增长。",
            option_tricks={}
        ),
        "技术分析": MemoryTemplate(
            keywords=["技术分析", "K线", "趋势", "图表"],
            answer_hint="基于历史价格和成交量",
            trick="技术分析 = 只看价格走势，不看公司好坏",
            story="技术分析假设价格已包含所有信息。通过历史价格和成交量预测未来走势，不涉及公司基本面分析。",
            option_tricks={}
        ),
        "基本面分析": MemoryTemplate(
            keywords=["基本面", "财务报表", "盈利能力", "估值"],
            answer_hint="分析公司内在价值",
            trick="基本面 = 看公司真实经营状况",
            story="基本面分析通过财务报表、行业地位、盈利能力等，评估公司内在价值，判断股价是否合理。",
            option_tricks={}
        ),
        "GDP": MemoryTemplate(
            keywords=["GDP", "国内生产总值", "经济增长"],
            answer_hint="衡量经济总规模",
            trick="GDP = 总的，一个国家总的家底",
            story="GDP就像你全家一年赚的钱的总和。中国GDP第二，就是全家总收入全球排第二！",
            option_tricks={}
        ),
        "CPI": MemoryTemplate(
            keywords=["CPI", "消费者价格指数", "通货膨胀"],
            answer_hint="衡量通胀水平",
            trick="CPI = Consumer，买东西变贵了多少",
            story="CPI就像你买菜的小票。去年100块买一车，今年只能买半车，CPI涨了！",
            option_tricks={}
        ),
        "期货": MemoryTemplate(
            keywords=["期货", "保证金", "杠杆", "合约"],
            answer_hint="杠杆高/风险大",
            trick="期货 = 保证金交易，杠杆放大盈亏",
            story="期货只需交5-10%保证金就能交易全额合约。10倍杠杆意味着价格涨1%你就赚/亏10%，风险放大。",
            option_tricks={}
        ),
        "期权": MemoryTemplate(
            keywords=["期权", "权利金", "行权", "看涨看跌"],
            answer_hint="权利而非义务",
            trick="期权 = 花钱买选择权，可买可不买",
            story="期权买方支付权利金获得选择权：行情有利就行权，不利就放弃，最大损失就是权利金。",
            option_tricks={}
        ),
        "适当性管理": MemoryTemplate(
            keywords=["适当性", "风险匹配", "合格投资者"],
            answer_hint="把合适的产品卖给合适的人",
            trick="适当性 = 风险承受能力与产品匹配",
            story="适当性要求根据客户的风险承受能力、投资经验等，推荐相匹配的产品，避免低风险客户买高风险产品。",
            option_tricks={}
        ),
        "信息披露": MemoryTemplate(
            keywords=["信息披露", "公开透明", "虚假陈述"],
            answer_hint="真实准确完整及时",
            trick="信息披露 = 上市公司必须公开重要信息",
            story="信息披露制度要求上市公司及时公开影响股价的重大信息，确保所有投资者公平获取信息。",
            option_tricks={}
        ),
        "风险对冲": MemoryTemplate(
            keywords=["风险对冲", "对冲风险", "自我对冲", "市场对冲"],
            answer_hint="自我对冲和市场对冲",
            trick="对冲分两种：自己玩（自我）和出去玩（市场）",
            story="风险对冲分两类：自我对冲（用自己资产对冲）和市场对冲（用市场工具如期货期权对冲）。",
            option_tricks={}
        ),
        "久期": MemoryTemplate(
            keywords=["久期", "duration", "利率敏感"],
            answer_hint="利率变动1%时价格变动的百分比",
            trick="久期就是利率敏感度，久期5年=利率变1%，价格变5%",
            story="久期衡量债券对利率的敏感程度。久期5年意味着利率上升1%，债券价格大约下跌5%。",
            option_tricks={}
        ),
        "夏普比率": MemoryTemplate(
            keywords=["夏普比率", "sharpe", "风险调整后收益"],
            answer_hint="超额收益/标准差",
            trick="夏普比率 = (收益-无风险利率)/波动，越高越好",
            story="夏普比率衡量每承担一份风险获得多少超额收益。分子是超额收益，分母是风险（标准差）。",
            option_tricks={}
        ),
        "贝塔系数": MemoryTemplate(
            keywords=["贝塔", "beta", "系统风险", "β系数"],
            answer_hint="衡量系统风险相对于市场的倍数",
            trick="β=1跟市场一样，β>1比市场波动大，β<1比市场稳",
            story="贝塔系数衡量股票相对于市场的波动程度。β=1.5意味着市场涨10%，这只股票涨15%。",
            option_tricks={}
        ),
        " VaR": MemoryTemplate(
            keywords=["VaR", "风险价值", "最大可能损失"],
            answer_hint="给定置信水平下的最大可能损失",
            trick="VaR = 在正常情况下的最坏损失",
            story="VaR（风险价值）表示在一定置信水平（如95%）下，资产组合在未来特定时间内的最大可能损失。",
            option_tricks={}
        ),
    }

    # 注：选项位置记忆已移除，因为机考选项随机排列

    # 数字记忆口诀
    NUMBER_TRICKS: Dict[str, str] = {
        "80%": "八霸天下，80%就是控制线",
        "50%": "五无中间，50%是分界线",
        "30%": "三散开，30%分散投资线",
        "20%": "二爱风险，20%是警戒线",
        "5%": "我（5）要举牌，5%披露线",
        "3%": "散（3）户线，3%是小股东",
    }

    # 法律法规年限统计规律
    LAW_YEAR_PATTERNS: Dict[str, Dict] = {
        "5年": {
            "keywords": ["从业人员", "处罚", "禁入", "市场禁入", "资格取消"],
            "trick": "从业人员犯事 = 5年禁赛，像足球红牌罚下5场",
            "pattern": "涉及个人从业资格处罚，一般是5年"
        },
        "10年": {
            "keywords": ["严重违法", "犯罪", "刑事", "欺诈", "内幕交易", "操纵市场"],
            "trick": "刑事犯罪级别 = 10年，像坐牢10年",
            "pattern": "涉及刑事犯罪、严重欺诈，一般是10年"
        },
        "3年": {
            "keywords": ["一般违规", "警告", "罚款", "记录"],
            "trick": "一般违规 = 3年观察期，像试用期3年",
            "pattern": "一般性违规记录，通常是3年"
        },
        "终身": {
            "keywords": ["特别严重", "巨额", "系统性造假", "恶意"],
            "trick": "特别严重 = 终身ban，像游戏开挂永久封号",
            "pattern": "情节特别严重，终身禁入"
        }
    }

    # 计算题数字凑答案规律
    CALCULATION_TRICKS: List[Dict] = [
        {
            "name": "夏普比率速算",
            "keywords": ["夏普", "sharpe", "超额收益", "标准差"],
            "trick": "夏普 = (收益-无风险)/波动，分子分母题干里找",
            "method": "找题干里最大的收益数字，减去最小的利率，除以波动率"
        },
        {
            "name": "久期近似计算",
            "keywords": ["久期", "duration", "利率变动", "价格变动"],
            "trick": "价格变动约等于 -久期乘利率变动，负号别忘！",
            "method": "看到久期和利率变动，直接相乘再加负号"
        },
        {
            "name": "杠杆倍数速算",
            "keywords": ["杠杆", "保证金", "维持担保比例"],
            "trick": "杠杆 = 1/保证金比例，20%保证金=5倍杠杆",
            "method": "用100除以保证金百分比，就是杠杆倍数"
        },
        {
            "name": "分红除权计算",
            "keywords": ["除权", "除息", "分红", "派息"],
            "trick": "除权价 = 原价 - 每股分红，简单直接减",
            "method": "股价减去每股分红金额"
        },
        {
            "name": "收益率计算",
            "keywords": ["收益率", "return", "收益/成本"],
            "trick": "收益率 = (卖-买)/买，记住分母是买入价",
            "method": "(卖出价-买入价)/买入价，或者收益/本金"
        }
    ]

    @classmethod
    def generate(cls, question) -> Dict[str, str]:
        """为题目生成记忆口诀"""
        result = {
            'quick_trick': '',
            'full_story': '',
            'keyword_bind': '',
            'law_pattern': '',
            'calculation_trick': ''
        }

        # 1. 匹配知识点模板
        matched_template = cls._match_knowledge_template(question)
        if matched_template:
            result['quick_trick'] = matched_template.trick
            result['full_story'] = matched_template.story

        # 2. 生成简单提示
        result['keyword_bind'] = cls._generate_simple_hint(question)

        # 3. 检查是否有数字需要特殊记忆
        number_trick = cls._check_number_trick(question)
        if number_trick:
            if result['quick_trick']:
                result['quick_trick'] += f" | 数字口诀：{number_trick}"
            else:
                result['quick_trick'] = f"数字口诀：{number_trick}"

        # 4. 分析法律法规统计规律
        law_pattern = cls.analyze_law_pattern(question)
        if law_pattern:
            result['law_pattern'] = law_pattern

        # 5. 分析计算题凑数技巧
        calculation_trick = cls.analyze_calculation_trick(question)
        if calculation_trick:
            result['calculation_trick'] = calculation_trick

        return result

    @classmethod
    def _match_knowledge_template(cls, question) -> Optional[MemoryTemplate]:
        """匹配知识点模板 - 优先匹配题干，避免被选项干扰"""
        # 优先只使用题干进行匹配
        stem_text = question.stem
        # 其次使用选项
        options_text = ' '.join(question.options.values())

        best_match = None
        best_score = 0

        for knowledge, template in cls.KNOWLEDGE_MEMORY_BANK.items():
            # 计算题干匹配分数（权重更高）
            stem_score = 0
            stem_matches = []
            for keyword in template.keywords:
                if cls._is_whole_word_match(keyword, stem_text):
                    stem_score += len(keyword) * 2  # 题干匹配权重×2
                    stem_matches.append(keyword)

            # 计算选项匹配分数
            option_score = 0
            for keyword in template.keywords:
                if cls._is_whole_word_match(keyword, options_text):
                    option_score += len(keyword)

            total_score = stem_score + option_score
            total_matches = len(stem_matches)

            # 只有在题干匹配到关键词时才考虑该模板
            if total_matches >= 1:
                if total_score > best_score:
                    best_score = total_score
                    best_match = template

        return best_match

    @classmethod
    def _is_whole_word_match(cls, keyword: str, text: str) -> bool:
        """检查关键词是否是整词匹配，避免子串误匹配"""
        # 特殊处理：如果关键词是"系统性风险"，要避免匹配"非系统性风险"
        if keyword == "系统性风险":
            # 只匹配"系统性风险"，不匹配"非系统性风险"
            idx = text.find(keyword)
            while idx != -1:
                # 检查前面是否有"非"字
                if idx == 0 or text[idx-1] != '非':
                    return True
                # 继续查找下一个匹配
                idx = text.find(keyword, idx + 1)
            return False

        # 其他关键词使用普通匹配
        return keyword in text

    @classmethod
    def _generate_simple_hint(cls, question) -> str:
        """生成通俗易懂的答案解释"""
        answer_text = question.options.get(question.answer, "")
        if not answer_text:
            return ""

        question_text = question.stem

        # 1. 定义类题目
        if "是指" in question_text or "是（" in question_text:
            return f"简单说就是：{answer_text[:15]}..."

        # 2. 目的/作用类
        if "目的" in question_text or "作用" in question_text or "为了" in question_text:
            return f"为什么要这样？因为{answer_text[:15]}..."

        # 3. 方法/方式类
        if "方法" in question_text or "方式" in question_text:
            return f"做法很简单：{answer_text[:15]}..."

        # 4. 数字/年限类 - 解释为什么是这个数字
        numbers = re.findall(r'(\d+)[年%]', answer_text)
        if numbers:
            num = numbers[0]
            if "年" in answer_text:
                explanations = {
                    "3": "3年是观察期，相当于试用期",
                    "5": "5年处罚是行业惯例，像足球红牌禁赛",
                    "10": "10年对应刑事犯罪，像坐牢10年",
                }
                return explanations.get(num, f"记住是{num}年")
            if "%" in answer_text:
                return f"记住比例是{num}%"

        # 5. 默认解释 - 基于答案内容给出最简明的解释
        if len(answer_text) <= 15:
            return f"答案：{answer_text}"
        else:
            return f"答案要点：{answer_text[:15]}..."

    @classmethod
    def _check_number_trick(cls, question) -> Optional[str]:
        """检查答案中是否有需要特殊记忆的数字"""
        # 只检查答案中的数字，而不是题干
        answer_text = question.options.get(question.answer, "")
        if not answer_text:
            return None

        # 检查答案中是否有特定数字
        for number, trick in cls.NUMBER_TRICKS.items():
            if number in answer_text:
                return trick

        # 检查百分比
        percentages = re.findall(r'(\d+)%', answer_text)
        if percentages:
            pct = percentages[0]
            if pct in ['80', '50', '30', '20']:
                return cls.NUMBER_TRICKS.get(f"{pct}%", "")

        return None

    @classmethod
    def analyze_law_pattern(cls, question) -> Optional[str]:
        """分析法律法规题目的年限规律"""
        question_text = f"{question.stem} {' '.join(question.options.values())}"

        law_keywords = ["处罚", "禁入", "违规", "违法", "监管", "证监会", "年限", "期限"]
        if not any(kw in question_text for kw in law_keywords):
            return None

        for year, pattern in cls.LAW_YEAR_PATTERNS.items():
            for keyword in pattern["keywords"]:
                if keyword in question_text:
                    return f"法规统计：{pattern['pattern']} | 口诀：{pattern['trick']}"

        return None

    @classmethod
    def analyze_calculation_trick(cls, question) -> Optional[str]:
        """分析计算题的凑数技巧"""
        question_text = f"{question.stem} {' '.join(question.options.values())}"

        numbers = re.findall(r'\d+\.?\d*', question_text)
        if len(numbers) < 2:
            return None

        for calc in cls.CALCULATION_TRICKS:
            for keyword in calc["keywords"]:
                if keyword in question_text.lower():
                    return f"{calc['name']}：{calc['method']} | 口诀：{calc['trick']}"

        return cls._generate_generic_calculation_trick(numbers, question)

    @classmethod
    def _generate_generic_calculation_trick(cls, numbers: List[str], question) -> Optional[str]:
        """通用计算题凑数技巧"""
        try:
            nums = [float(n) for n in numbers[:4]]

            if len(nums) >= 2:
                add = nums[0] + nums[1]
                sub = abs(nums[0] - nums[1])

                for opt_label, opt_text in question.options.items():
                    opt_nums = re.findall(r'\d+\.?\d*', opt_text)
                    if opt_nums:
                        opt_val = float(opt_nums[0])

                        if abs(opt_val - add) < 0.01:
                            return f"数字凑答案：{nums[0]} + {nums[1]} = {opt_val}"
                        elif abs(opt_val - sub) < 0.01:
                            return f"数字凑答案：|{nums[0]} - {nums[1]}| = {opt_val}"

        except (ValueError, ZeroDivisionError):
            pass

        return None

    @classmethod
    def generate_batch_statistics(cls, questions: List) -> Dict:
        """批量分析题目，生成统计规律汇总"""
        stats = {
            "law_years": {},
            "calculation_types": [],
            "option_distribution": {"A": 0, "B": 0, "C": 0, "D": 0}
        }

        for q in questions:
            if q.answer in stats["option_distribution"]:
                stats["option_distribution"][q.answer] += 1

            law_pattern = cls.analyze_law_pattern(q)
            if law_pattern:
                year_match = re.search(r'(\d+)年', law_pattern)
                if year_match:
                    year = year_match.group(1) + "年"
                    stats["law_years"][year] = stats["law_years"].get(year, 0) + 1

            calc_pattern = cls.analyze_calculation_trick(q)
            if calc_pattern:
                calc_type = calc_pattern.split("：")[0]
                if calc_type not in stats["calculation_types"]:
                    stats["calculation_types"].append(calc_type)

        return stats

    @classmethod
    def generate_statistics_summary(cls, questions: List) -> str:
        """生成统计规律汇总报告"""
        stats = cls.generate_batch_statistics(questions)

        # 统计知识点出现概率
        knowledge_count = {}
        for q in questions:
            for tag in q.knowledge_tags:
                knowledge_count[tag] = knowledge_count.get(tag, 0) + 1

        sorted_knowledge = sorted(knowledge_count.items(), key=lambda x: x[1], reverse=True)

        lines = [
            "=" * 60,
            "考前统计秘籍（按出现概率排序）",
            "=" * 60,
            "",
            "【高频知识点 TOP 10】",
            "优先复习这些知识点，效率最高："
        ]

        for i, (knowledge, count) in enumerate(sorted_knowledge[:10], 1):
            pct = count / len(questions) * 100 if questions else 0
            lines.append(f"  {i}. {knowledge}：{count}题 ({pct:.1f}%)")

        lines.extend(["", "【知识点优先级划分】"])
        high_freq = [k for k, c in sorted_knowledge if c/len(questions)*100 >= 10]
        mid_freq = [k for k, c in sorted_knowledge if 5 <= c/len(questions)*100 < 10]
        low_freq = [k for k, c in sorted_knowledge if c/len(questions)*100 < 5]

        lines.append(f"  第一梯队（概率>=10%）：{len(high_freq)}个知识点")
        if high_freq:
            lines.append(f"    包含：{'、'.join(high_freq[:5])}{'...' if len(high_freq) > 5 else ''}")
        lines.append(f"  第二梯队（概率5-10%）：{len(mid_freq)}个知识点")
        lines.append(f"  第三梯队（概率<5%）：{len(low_freq)}个知识点")

        lines.extend(["", "【法规年限速记】"])
        if stats["law_years"]:
            for year, count in sorted(stats["law_years"].items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {year}出现{count}次")
        else:
            lines.append("  暂无法规类题目")

        lines.extend(["", "【计算题类型】"])
        if stats["calculation_types"]:
            for calc_type in stats["calculation_types"][:5]:
                lines.append(f"  - {calc_type}")
        else:
            lines.append("  暂无计算类题目")

        lines.extend([
            "",
            "=" * 60,
            "蒙题技巧（实在不会时参考）：",
            "  1. 绝对化的选项（一定、必须、永远）往往是错的",
            "  2. 两个选项意思相反 → 答案在其中之一",
            "  3. 数字题看尾数：尾数0、5的选项优先验证",
            "  4. 多选题宁少勿多，不确定的不选",
            "  5. 法规题：个人处罚5年，刑事犯罪10年，特别严重终身",
            "  6. 计算题：看题干数字，试试加减乘除组合",
            "=" * 60
        ])

        return "\n".join(lines)

