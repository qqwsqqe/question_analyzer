"""
投资顾问考试题目识别与知识点统计程序

功能：
1. 自动提取PDF和Word中的题目
2. 自动归纳知识点
3. 统计各知识点出场率
4. 按出场率排序生成PDF

使用方法：
    python main.py <文件路径或目录> [选项]

示例：
    python main.py "C:/考试题目/"
    python main.py "C:/考试题目/2024年真题.pdf" --ocr
    python main.py "C:/考试题目/" --output "D:/输出/"
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extractors import PDFExtractor, WordExtractor
from parsers import QuestionParser
from analyzer import KnowledgeAnalyzer
from pdf_generator import PDFGenerator
from config import OUTPUT_DIR, OUTPUT_FILENAME


def scan_files(input_path: str) -> List[str]:
    """
    扫描输入路径，返回所有支持的文件列表

    Args:
        input_path: 文件或目录路径

    Returns:
        文件路径列表
    """
    input_path = Path(input_path)
    files = []

    if input_path.is_file():
        if input_path.suffix.lower() in ['.pdf', '.docx']:
            files.append(str(input_path))
    elif input_path.is_dir():
        for ext in ['*.pdf', '*.docx', '*.PDF', '*.DOCX']:
            files.extend([str(f) for f in input_path.glob(ext)])

    return sorted(files)


def process_file(file_path: str, use_ocr: bool = False) -> str:
    """
    处理单个文件，提取文本

    Args:
        file_path: 文件路径
        use_ocr: 是否使用OCR

    Returns:
        提取的文本
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    print(f"\n正在处理: {file_path.name}")

    try:
        if suffix == '.pdf':
            extractor = PDFExtractor(use_ocr=use_ocr)
            text = extractor.extract(file_path)
        elif suffix == '.docx':
            extractor = WordExtractor()
            text = extractor.extract(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")

        print(f"  [OK] 提取了 {len(text)} 个字符")
        return text

    except Exception as e:
        print(f"  [ERR] 处理失败: {e}")
        return ""


def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(
        description='投资顾问考试题目识别与知识点统计程序',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python main.py "C:/考试题目/"
  python main.py "C:/考试题目/2024年真题.pdf" --ocr
  python main.py "C:/考试题目/" --output "D:/输出/"
        '''
    )

    parser.add_argument('input', help='输入文件或目录路径')
    parser.add_argument('--output', '-o', default=OUTPUT_DIR,
                       help=f'输出目录 (默认: {OUTPUT_DIR})')
    parser.add_argument('--ocr', action='store_true',
                       help='启用OCR识别（用于扫描版PDF）')
    parser.add_argument('--name', '-n', default=OUTPUT_FILENAME,
                       help=f'输出文件名 (默认: {OUTPUT_FILENAME})')

    args = parser.parse_args()

    # 检查输入路径
    if not os.path.exists(args.input):
        print(f"错误: 路径不存在 - {args.input}")
        sys.exit(1)

    # 扫描文件
    files = scan_files(args.input)
    if not files:
        print(f"未找到支持的文件 (.pdf 或 .docx)")
        sys.exit(1)

    print(f"=" * 60)
    print(f"投资顾问考试题目识别与知识点统计程序")
    print(f"=" * 60)
    print(f"找到 {len(files)} 个文件:")
    for f in files:
        print(f"  - {Path(f).name}")

    # 提取文本
    print(f"\n[1/4] 正在提取文本...")
    all_texts = []
    for file_path in files:
        text = process_file(file_path, use_ocr=args.ocr)
        if text:
            all_texts.append(text)

    if not all_texts:
        print("\n错误: 未能从文件中提取到文本")
        sys.exit(1)

    # 解析题目
    print(f"\n[2/4] 正在解析题目...")
    parser = QuestionParser()
    all_questions = []

    for text in all_texts:
        questions = parser.parse(text)
        all_questions.extend(questions)

    print(f"  [OK] 共解析出 {len(all_questions)} 道题目")

    if not all_questions:
        print("\n错误: 未能识别到题目，请检查文件格式")
        sys.exit(1)

    # 知识点分析
    print(f"\n[3/4] 正在分析知识点...")
    analyzer = KnowledgeAnalyzer()
    sorted_questions, freq = analyzer.get_sorted_questions(all_questions)

    # 打印统计报告
    report = analyzer.generate_report(freq, len(all_questions))
    print("\n" + report)

    # 生成PDF
    print(f"\n[4/4] 正在生成PDF...")

    # 确保输出目录存在
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / args.name

    generator = PDFGenerator(str(output_path))
    generator.add_title("投资顾问考试题目汇总\n（按知识点出场率排序）")
    generator.add_summary(freq, len(all_questions))
    generator.add_questions(sorted_questions)
    generator.save()

    print(f"\n" + "=" * 60)
    print(f"[OK] 处理完成!")
    print(f"  输入文件: {len(files)} 个")
    print(f"  识别题目: {len(all_questions)} 道")
    print(f"  知识点数: {len(freq)} 个")
    print(f"  输出文件: {output_path}")
    print(f"=" * 60)


if __name__ == '__main__':
    main()
