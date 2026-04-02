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
    """生成专业简洁的AI解析，一两句话点明本质"""
    stem = question.get('stem', '')
    answer = question.get('answer', '')
    analysis = question.get('analysis', '')
    knowledge_tags = question.get('knowledge_tags', [])

    # 判断题目类型和特征
    is_calculation = any(word in stem for word in ['计算', '等于', '为', '%', '比例', '收益率', '价格', '现值', '终值'])
    is_year_question = any(word in stem for word in ['年', '月', '日', '期限'])
    is_definition = any(word in stem for word in ['是指', '定义', '概念', '含义'])
    is_regulation = any(word in stem for word in ['规定', '要求', '应当', '必须', '禁止', '不得'])
    is_penalty = any(word in stem for word in ['处罚', '罚款', '警告', '撤销', '吊销'])

    result = []

    # 计算题：给出核心公式和逻辑
    if is_calculation:
        if any(word in stem for word in ['收益率', '利率', '回报', '收益']):
            result.append('收益率 = 收益 / 本金。这是金融学最基础的收益计算逻辑，记住分子分母关系即可。')
        elif any(word in stem for word in ['现值', '终值', '贴现']):
            result.append('货币时间价值原理：今天的1元 > 明天的1元。现值计算本质是未来现金流按利率折现。')
        elif any(word in stem for word in ['价格', '估值', '价值']):
            result.append('资产价格 = 未来现金流现值之和。这是估值的核心逻辑，选 %s。' % answer)
        else:
            result.append('计算题关键是识别已知条件和所求变量，套用对应公式即可。答案 %s。' % answer)

    # 年限类：监管逻辑解释
    elif is_year_question:
        if '5年' in stem or '五年' in stem:
            result.append('5年是行政处罚的基准刑期，类似于刑法中的"量刑起点"，适用于一般性违规。')
        elif '10年' in stem or '十年' in stem:
            result.append('10年对应严重失信行为，与刑事犯罪相衔接，体现"过罚相当"的监管原则。')
        elif '终身' in stem or '终生' in stem:
            result.append('终身禁入是行业清退机制，适用于情节特别严重、不再适合从事证券业务的情形。')
        else:
            result.append('监管期限设置遵循过罚相当原则，违规严重程度与时间长度成正比。')

    # 处罚类：区分处罚层级
    elif is_penalty:
        if '罚款' in stem:
            result.append('罚款属于财产罚，与警告（申诫罚）、资格罚（禁入）形成阶梯式处罚体系。')
        elif '警告' in stem:
            result.append('警告是最轻的监管措施，属于申诫罚，通常作为前置程序或轻微违规的处理。')
        elif '撤销' in stem or '吊销' in stem:
            result.append('资格罚是最严厉的措施之一，直接剥夺从业资格，适用于重大违规或失信行为。')
        else:
            result.append('行政处罚遵循从轻则原则，根据违规性质、情节、后果综合判定。')

    # 法规规定类：法律术语解释
    elif is_regulation:
        if '应当' in stem:
            result.append('"应当"在法律语境中等同于"必须"，是强制性规范，违反即构成违规。')
        elif '禁止' in stem or '不得' in stem:
            result.append('禁止性规范设定行为红线，属于效力性强制规定，触碰即产生法律责任。')
        elif '可以' in stem:
            result.append('"可以"是授权性规范，赋予主体选择权，做或不做均在允许范围内。')
        else:
            result.append('法律规范的逻辑结构：假定条件 + 行为模式 + 法律后果。理解这个框架即可解题。')

    # 基本概念类：核心定义
    elif is_definition:
        result.append('概念题考查对特定术语的准确理解。这类题目没有推理空间，准确记忆定义原文即可。')

    # 其他情况：提取原解析的核心
    elif analysis and len(analysis) > 10:
        # 尝试提取关键逻辑
        clean_analysis = analysis.replace('\n', ' ').strip()
        # 取前两句话
        sentences = clean_analysis.split('。')
        if len(sentences) >= 2:
            summary = sentences[0] + '。' + sentences[1] + '。'
        else:
            summary = clean_analysis[:150]
        if len(summary) > 150:
            summary = summary[:150] + '...'
        result.append(summary)

    # 兜底
    else:
        tags_str = '、'.join(knowledge_tags[:2]) if knowledge_tags else '相关法规或概念'
        result.append('题目涉及%s，答案为 %s。建议结合监管实践理解记忆。' % (tags_str, answer))

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
