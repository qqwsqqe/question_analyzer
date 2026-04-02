# PythonAnywhere 部署指南

## 第一步：注册和登录

1. 访问 https://www.pythonanywhere.com/
2. 注册免费账户（免费版足够小项目使用）
3. 登录后进入 Dashboard

## 第二步：上传代码

### 方法1：通过 Git（推荐）

1. 打开 **Consoles** -> **Start a new console** -> **Bash**
2. 运行以下命令：

```bash
# 克隆你的代码仓库（或者先上传到 GitHub）
cd ~
git clone https://github.com/yourusername/question_analyzer.git
# 如果没有 GitHub，可以用 Files 页面上传 zip 文件并解压
```

### 方法2：直接上传文件

1. 进入 **Files** 标签
2. 点击 **Upload a file**
3. 上传整个项目文件夹（先压缩成 zip）
4. 在 Bash 控制台解压：`unzip question_analyzer.zip`

## 第三步：创建虚拟环境并安装依赖

在 Bash 控制台运行：

```bash
cd ~/question_analyzer

# 创建虚拟环境
python3.10 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 第四步：配置 Web 应用

1. 进入 **Web** 标签
2. 点击 **Add a new web app**
3. 选择 **Manual configuration** (包括虚拟环境配置)
4. 选择 **Python 3.10**

## 第五步：配置 WSGI 文件

1. 在 Web 标签页，找到 **Code** 部分下的 **WSGI configuration file**
2. 点击该文件链接，清空内容并粘贴以下代码：

```python
import sys
import os

# 添加项目路径
PROJECT_PATH = '/home/你的用户名/question_analyzer'
sys.path.insert(0, PROJECT_PATH)
os.chdir(PROJECT_PATH)

# 激活虚拟环境
activate_this = '/home/你的用户名/question_analyzer/venv/bin/activate_this.py'
exec(open(activate_this).read(), {'__file__': activate_this})

# 导入 Flask 应用
from web_app import app as application
```

**注意**：将 `你的用户名` 替换为你的 PythonAnywhere 用户名

## 第六步：配置静态文件（可选）

在 Web 标签页的 **Static files** 部分：
- URL: `/static/`
- Directory: `/home/你的用户名/question_analyzer/static/`

## 第七步：重启应用

1. 回到 **Web** 标签
2. 点击 **Reload** 按钮
3. 访问提供的网址（如 `你的用户名.pythonanywhere.com`）

## 常见问题

### 1. 502 Bad Gateway 错误
- 检查 WSGI 配置是否正确
- 确保虚拟环境路径正确
- 查看 Error log 排查问题

### 2. 依赖安装失败
- 某些包可能需要系统依赖，可以在 Bash 中运行：
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### 3. 中文显示问题
- PythonAnywhere 支持中文，但如果遇到问题，在代码开头添加：
```python
import sys
sys.setdefaultencoding('utf-8')
```

### 4. 免费版限制
- 每天有一次手动重启限制
- CPU 时间每天限制 100 秒（足够小型应用）
- 存储空间 512 MB

## 更新代码

以后更新代码时，只需：
1. 上传新代码（覆盖或重新 clone）
2. 在 Web 页面点击 **Reload**

## 绑定自定义域名（可选）

免费版不支持自定义域名，如需此功能，需升级到付费版（$5/月起）。
