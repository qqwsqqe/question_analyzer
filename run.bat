@echo off
chcp 65001 >nul
echo ==========================================
echo 投资顾问考试题目识别与知识点统计程序
echo ==========================================
echo.

:: 设置Python路径（使用安装依赖的Python）
set PYTHON_PATH=D:\Program\Python\python.exe

:: 检查Python是否安装
%PYTHON_PATH% --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python: %PYTHON_PATH%
    echo 请修改run.bat中的PYTHON_PATH指向正确的Python路径
    pause
    exit /b 1
)

echo 使用Python: %PYTHON_PATH%
echo.

:: 运行程序
if "%~1"=="" (
    echo 使用方法: run.bat [文件或目录路径] [选项]
    echo.
    echo 示例:
    echo   run.bat "考试题目\2024真题.pdf"
    echo   run.bat "考试题目\" --ocr
    echo.
    set /p input_path="请输入题目文件或目录路径: "
    %PYTHON_PATH% main.py "%input_path%"
) else (
    %PYTHON_PATH% main.py %*
)

pause
