#!/bin/bash

# ChatJimmy API Proxy 启动脚本

echo "正在启动 ChatJimmy API Proxy..."

# 检查虚拟环境
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "已激活虚拟环境"
fi

# 启动服务
python main.py
