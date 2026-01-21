#!/bin/bash

echo "========================================"
echo "   Git 协同同步管理工具"
echo "   跨端代码同步利器"
echo "========================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装 Python 3.8+"
    exit 1
fi

# 检查依赖是否安装
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "[提示] 首次运行，正在安装依赖..."
    python3 -m pip install streamlit -i https://pypi.tuna.tsinghua.edu.cn/simple
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败，请检查网络连接"
        exit 1
    fi
fi

# 启动应用
echo "[启动] 正在启动 Git 同步工具..."
echo ""
python3 sync.py
