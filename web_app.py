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
