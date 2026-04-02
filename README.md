# 投资顾问考试题目识别与知识点统计程序

## 功能介绍

这个程序可以自动识别PDF和Word文件中的考试题目，自动归纳知识点，统计各知识点的出场率，并按出场率排序生成PDF报告。

## 主要功能

1. **多格式支持**：支持纯文本PDF、扫描版PDF（需OCR）、Word文档（.docx）
2. **智能识别**：自动提取题号、题干、选项、答案
3. **知识点归纳**：使用TF-IDF算法自动提取高频关键词作为知识点
4. **出场率统计**：统计各知识点在题目中的出现频率
5. **智能排序**：将高频知识点的题目排在前面，方便重点复习

## 安装方法

### 方式1：使用批处理文件（推荐）

双击运行 `run.bat`，按提示输入题目文件路径即可。

### 方式2：手动安装

```bash
# 1. 进入项目目录
cd "D:\claude program\question_analyzer"

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行程序
python main.py "你的题目文件路径"
```

## 使用方法

### 基本用法

```bash
# 处理单个文件
python main.py "C:/考试题目/2024年真题.pdf"

# 处理整个目录
python main.py "C:/考试题目/"

# 启用OCR（扫描版PDF需要）
python main.py "C:/考试题目/扫描版.pdf" --ocr

# 指定输出目录
python main.py "C:/考试题目/" --output "D:/输出报告/"
```

### 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `input` | 输入文件或目录（必需） | `"C:/题目/"` |
| `--output, -o` | 输出目录 | `--output "D:/输出/"` |
| `--ocr` | 启用OCR识别 | `--ocr` |
| `--name, -n` | 输出文件名 | `--name "我的题目.pdf"` |

## 输出文件

程序会生成一个PDF文件，包含：

1. **统计摘要页**：展示各知识点的出场率排名
2. **排序题目列表**：按知识点出场率排序的题目，每道题都标注了所属知识点

## 项目结构

```
question_analyzer/
├── main.py                 # 主程序入口
├── config.py               # 配置文件
├── requirements.txt        # 依赖列表
├── run.bat                 # Windows一键运行脚本
├── extractors/             # 文件提取模块
│   ├── pdf_extractor.py    # PDF提取
│   ├── word_extractor.py   # Word提取
│   └── ocr_engine.py       # OCR引擎
├── parsers/                # 题目解析模块
│   └── question_parser.py  # 题目解析器
├── analyzer/               # 知识点分析模块
│   └── knowledge_analyzer.py
├── output/                 # 输出目录（自动生成）
└── README.md               # 本文件
```

## 注意事项

1. **扫描版PDF**：如果是图片扫描的PDF，请加上 `--ocr` 参数启用OCR识别
2. **中文字体**：程序会自动尝试加载Windows系统字体，确保PDF正常显示中文
3. **首次运行**：首次运行时会自动下载OCR模型（约100MB），请保持网络畅通

## 依赖库

- `pdfplumber`：PDF文本提取
- `PyMuPDF`：PDF处理
- `python-docx`：Word文档读取
- `paddleocr` / `paddlepaddle`：OCR识别
- `reportlab`：PDF生成
- `jieba`：中文分词
- `scikit-learn`：TF-IDF分析
- `pandas` / `numpy`：数据处理

## 问题排查

### 字体显示问题

如果生成的PDF中文显示为方框，请检查：
- Windows系统是否有中文字体（如宋体、黑体）
- 字体文件路径是否正确

### OCR识别问题

如果扫描版PDF识别效果不佳：
- 确保PDF图片清晰度足够
- 尝试调整PDF的分辨率

### 题目解析问题

如果题目识别不准确：
- 检查题目格式是否标准（题号、选项格式）
- 可以在 `config.py` 中调整正则表达式模式

## 许可证

MIT License
