"""
投资顾问考试题目分析Web应用
"""

import os
import sys
import uuid
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extractors import PDFExtractor, WordExtractor
from parsers import QuestionParser
from analyzer import KnowledgeAnalyzer
from analyzer.memory_trick_generator import MemoryTrickGenerator
from pdf_generator_memory import MemoryPDFGenerator

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB限制


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """分析上传的多个文件"""
    if 'files' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400

    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': '文件名为空'}), 400

    # 过滤有效文件
    valid_files = [f for f in files if f.filename and allowed_file(f.filename)]
    if not valid_files:
        return jsonify({'error': '只支持PDF和Word文件'}), 400

    try:
        filepaths = []
        for file in valid_files:
            # 保存上传的文件
            unique_id = str(uuid.uuid4())[:8]
            filename = secure_filename(f"{unique_id}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            filepaths.append(filepath)

        # 处理所有文件
        result = process_files(filepaths)

        # 清理临时文件
        for filepath in filepaths:
            if os.path.exists(filepath):
                os.remove(filepath)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """生成PDF报告"""
    data = request.json
    if not data or 'questions' not in data:
        return jsonify({'error': '没有题目数据'}), 400

    try:
        # 生成PDF
        unique_id = str(uuid.uuid4())[:8]
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f'report_{unique_id}.pdf')

        # 转换JSON数据为Question对象
        from parsers.question_parser import Question
        questions = []
        for q_data in data['questions']:
            q = Question()
            q.number = q_data.get('number', 0)
            q.stem = q_data.get('stem', '')
            q.options = q_data.get('options', {})
            q.answer = q_data.get('answer', '')
            q.knowledge_tags = q_data.get('knowledge_tags', [])
            questions.append(q)

        # 统计知识点
        knowledge_count = {}
        for q in questions:
            for tag in q.knowledge_tags:
                knowledge_count[tag] = knowledge_count.get(tag, 0) + 1

        # 生成PDF
        generator = MemoryPDFGenerator(pdf_path)
        generator.generate_full_report(questions, knowledge_count)
        generator.save()

        return send_file(pdf_path, as_attachment=True, download_name='急救记忆手册.pdf')

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-analyze', methods=['POST'])
def ai_analyze():
    """AI 智能分析单道题目"""
    data = request.json
    if not data or 'question' not in data:
        return jsonify({'error': '没有题目数据'}), 400

    try:
        question = data['question']
        analysis = generate_ai_analysis(question)
        return jsonify({'analysis': analysis})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generate_ai_analysis(question):
    """生成简洁有趣的AI解析，一两句话说清楚"""
    stem = question.get('stem', '')
    options = question.get('options', {})
    answer = question.get('answer', '')
    analysis = question.get('analysis', '')
    knowledge_tags = question.get('knowledge_tags', [])

    # 判断题目类型和特征
    is_calculation = any(word in stem for word in ['计算', '等于', '为', '%', '比例', '收益率', '价格'])
    is_year_question = any(word in stem for word in ['年', '月', '日', '期限', '时间'])
    is_definition = any(word in stem for word in ['是指', '定义', '概念', '含义', '所谓'])
    is_regulation = any(word in stem for word in ['规定', '要求', '应当', '必须', '禁止', '不得'])

    result = []

    # 计算题：给出计算过程
    if is_calculation and any(word in stem for word in ['收益率', '利率', '回报']):
        result.append(f'💡 计算题：收益率 = 收益 / 本金 × 100%。记住这个公式就行。')
        result.append(f'答案 {answer}。')
    elif is_calculation and '价格' in stem:
        result.append(f'💡 价格计算题：通常涉及供需关系或贴现计算。')
        result.append(f'这题选 {answer}，具体看题干给的数据套公式。')

    # 年限类：口诀记忆
    elif is_year_question and ('5年' in stem or '五年' in stem):
        result.append(f'💡 类比：就像大学毕业后再读个博士，5年时间让你彻底长记性。')
        result.append(f'个人违规处罚一般5年禁入，选 {answer}。')
    elif is_year_question and ('10年' in stem or '十年' in stem):
        result.append(f'💡 类比：刑事犯罪 = 严重失信，相当于金融界的"有期徒刑"，10年起步。')
        result.append(f'选 {answer}。')
    elif is_year_question and ('终身' in stem or '终生' in stem):
        result.append(f'💡 类比：就像被拉入航空公司黑名单，这辈子别想再飞了。')
        result.append(f'特别严重就是终身禁入，选 {answer}。')

    # 基本概念类：幽默处理
    elif is_definition:
        jokes = [
            f'🤷 没解释，背吧。这就像问"为什么1+1=2"，定义就是定义。',
            f'📚 基础概念，建议直接背下来。考试不会问"为什么"，只问"是什么"。',
            f'😅 这种题就是考记忆力，理解不了就先记住，选 {answer}。'
        ]
        import random
        result.append(random.choice(jokes))

    # 法规规定类
    elif is_regulation:
        if '应当' in stem:
            result.append(f'💡 "应当" = 必须做，不做就违法。这就像红绿灯，红灯应当停。')
        elif '禁止' in stem or '不得' in stem:
            result.append(f'💡 禁止就是红线，碰了就要受罚。选 {answer}。')
        else:
            result.append(f'💡 法规题没有太多道理可讲，记住"是什么"就行。选 {answer}。')

    # 其他情况：提取原解析的核心
    elif analysis:
        # 提取原解析的关键信息，简化成一两句
        clean_analysis = analysis.replace('。', ' ').replace('\n', ' ').strip()
        if len(clean_analysis) > 100:
            clean_analysis = clean_analysis[:100] + '...'
        result.append(f'💡 {clean_analysis}')
        result.append(f'简单说就是选 {answer}。')

    # 完全不知道说什么
    else:
        funny_responses = [
            f'🤷 这题我也没啥好解释的，选 {answer} 就对了。',
            f'📚 记住它，考试用得上。答案是 {answer}。',
            f'😎 有时候生活不需要解释，就像这题，选 {answer} 就行。',
            f'💡 这个知识点就像你爸妈的电话号码，记住比理解更重要。答案是 {answer}。'
        ]
        import random
        result.append(random.choice(funny_responses))

    return '\n'.join(result)


def process_files(filepaths):
    """处理多个文件，合并分析"""
    all_questions = []
    file_count = 0

    for filepath in filepaths:
        filepath = Path(filepath)
        suffix = filepath.suffix.lower()

        # 提取文本
        if suffix == '.pdf':
            extractor = PDFExtractor(use_ocr=False)
            text = extractor.extract(filepath)
        elif suffix == '.docx':
            extractor = WordExtractor()
            text = extractor.extract(filepath)
        else:
            continue

        if not text:
            continue

        # 解析题目
        parser = QuestionParser()
        questions = parser.parse(text)

        if questions:
            all_questions.extend(questions)
            file_count += 1

    if not all_questions:
        raise ValueError('未能从文件中识别到题目，请检查文件格式')

    # 知识点分析（合并所有文件）
    analyzer = KnowledgeAnalyzer()
    sorted_questions, freq = analyzer.get_sorted_questions(all_questions)

    # 生成统计报告
    stats_summary = MemoryTrickGenerator.generate_statistics_summary(sorted_questions)

    # 为每道题生成记忆口诀
    questions_with_memory = []
    for q in sorted_questions:
        memory = MemoryTrickGenerator.generate(q)
        questions_with_memory.append({
            'number': q.number,
            'stem': q.stem,
            'options': q.options,
            'answer': q.answer,
            'analysis': q.analysis,
            'knowledge_tags': q.knowledge_tags,
            'memory': memory
        })

    # 知识点优先级
    knowledge_priority = []
    sorted_knowledge = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    total = len(all_questions)
    for knowledge, count in sorted_knowledge:
        knowledge_priority.append({
            'name': knowledge,
            'count': count,
            'percentage': f"{count/total*100:.1f}%"
        })

    return {
        'total_questions': len(all_questions),
        'knowledge_count': len(freq),
        'file_count': file_count,
        'statistics': stats_summary,
        'knowledge_priority': knowledge_priority,
        'questions': questions_with_memory
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
