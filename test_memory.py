"""
测试记忆口诀生成功能
"""

import sys
sys.path.insert(0, 'D:/claude program/question_analyzer')

from parsers import QuestionParser
from analyzer.memory_trick_generator import MemoryTrickGenerator


def test_memory_tricks():
    """测试记忆口诀生成"""

    # 创建测试题目
    test_questions = [
        {
            "number": 1,
            "stem": "投资组合理论中，分散投资的主要目的是降低哪种风险？",
            "options": {
                "A": "系统性风险",
                "B": "非系统性风险",
                "C": "市场风险",
                "D": "利率风险"
            },
            "answer": "B",
            "knowledge_tags": ["分散投资", "投资组合"]
        },
        {
            "number": 2,
            "stem": "某从业人员因内幕交易被处罚，市场禁入的期限通常是？",
            "options": {
                "A": "1年",
                "B": "3年",
                "C": "5年",
                "D": "终身"
            },
            "answer": "C",
            "knowledge_tags": ["监管法规", "处罚"]
        },
        {
            "number": 3,
            "stem": "一只股票的久期为5年，当市场利率上升1%时，该股票价格大约会如何变动？",
            "options": {
                "A": "上涨5%",
                "B": "下跌5%",
                "C": "上涨1%",
                "D": "下跌1%"
            },
            "answer": "B",
            "knowledge_tags": ["久期", "利率风险"]
        }
    ]

    print("=" * 60)
    print("测试记忆口诀生成功能")
    print("=" * 60)

    for q_data in test_questions:
        # 创建题目对象
        q = QuestionParser().parse(f"{q_data['number']}. {q_data['stem']}")[0]
        q.number = q_data['number']
        q.stem = q_data['stem']
        q.options = q_data['options']
        q.answer = q_data['answer']
        q.knowledge_tags = q_data['knowledge_tags']

        print(f"\n题目 {q.number}: {q.stem}")
        print(f"选项: A.{q.options['A']} B.{q.options['B']} C.{q.options['C']} D.{q.options['D']}")
        print(f"答案: {q.answer}")

        # 生成记忆口诀
        memory = MemoryTrickGenerator.generate(q)

        # 先显示答案
        answer_text = q.options.get(q.answer, "")
        print(f"\n【答案】{q.answer}. {answer_text}")

        print("\n生成的记忆口诀：")
        if memory.get('quick_trick'):
            print(f"[口诀] {memory['quick_trick']}")
        if memory.get('keyword_bind'):
            print(f"[提示] {memory['keyword_bind']}")
        if memory.get('full_story'):
            print(f"[逻辑] {memory['full_story']}")
        if memory.get('law_pattern'):
            print(f"[法规] {memory['law_pattern']}")
        if memory.get('calculation_trick'):
            print(f"[计算] {memory['calculation_trick']}")

        print("\n" + "-" * 60)

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    test_memory_tricks()
