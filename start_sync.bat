@echo off
chcp 65001 >nul
title Git 同步工具

echo ========================================
echo    Git 协同同步管理工具
echo    跨端代码同步利器
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查依赖是否安装
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [提示] 首次运行，正在安装依赖...
    python -m pip install streamlit -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
)

:: 启动应用
echo [启动] 正在启动 Git 同步工具...
echo.
python sync.py

pause
