"""
PythonAnywhere 配置文件

使用说明：
1. 在 PythonAnywhere 创建账户 (pythonanywhere.com)
2. 进入 Dashboard -> Web -> Add a new web app
3. 选择 Manual configuration -> Python 3.10
4. 在 Files 中上传项目代码到 /home/你的用户名/ 目录
5. 修改此文件中的路径
6. 在 Web 标签页的 WSGI 配置文件中导入此配置
"""

import sys
import os

# 添加项目路径（修改为你的用户名）
PROJECT_PATH = '/home/yourusername/question_analyzer'
sys.path.insert(0, PROJECT_PATH)
os.chdir(PROJECT_PATH)

# 导入 Flask 应用
from web_app import app as application

# PythonAnywhere 配置
if __name__ == '__main__':
    application.run()
