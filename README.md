# ChatJimmy API 代理服务

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

为沉浸式翻译浏览器插件提供 OpenAI 兼容的 API 接口，利用 ChatJimmy.ai 的高速推理能力（约 16,000-18,000 tokens/s）。

## ✨ 功能特性

- 🚀 **OpenAI 兼容 API** - 无缝对接沉浸式翻译等支持 OpenAI API 的应用
- ⚡ **流式响应支持** - 支持 SSE 流式输出，实时返回翻译结果
- 🔐 **API Key 验证** - 支持多 API Key 配置与验证
- 🎯 **翻译质量增强** - 内置翻译优化规则，提升翻译质量
- ⚙️ **灵活配置** - 支持环境变量配置，易于部署

## 📦 快速开始

### 前置要求

- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/xxj333-ai/chatjimmy.ai-proxy-api
cd chatjimmy-api-proxy
```

2. **创建虚拟环境（推荐）**

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows
# .venv\Scripts\activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **配置环境变量（可选）**

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置
vim .env  # 或使用其他编辑器
```

5. **启动服务**

```bash
# 方式一：直接启动
python main.py

# 方式二：使用启动脚本（自动激活虚拟环境）
./start.sh

# 方式三：指定端口
PORT=8001 python main.py
```

服务将在 `http://localhost:8000` 启动（默认端口）。

## 🔧 配置沉浸式翻译

在沉浸式翻译插件设置中配置：

| 配置项 | 值 |
|--------|-----|
| API 地址 | `http://localhost:8000/v1/chat/completions` |
| API Key | `sk-chatjimmy-local-dev-key` |
| 模型 | `llama3.1-8B` |

### 支持的模型

- `llama3.1-8B`（默认）
- `llama3.2-3B`
- 其他 ChatJimmy.ai 支持的模型

## 📖 API 文档

### POST /v1/chat/completions

聊天完成端点，完全兼容 OpenAI API 格式。

**请求示例：**

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-chatjimmy-local-dev-key" \
  -d '{
    "model": "llama3.1-8B",
    "messages": [
      {"role": "user", "content": "Translate to Chinese: Hello, world!"}
    ],
    "stream": false
  }'
```

**响应示例：**

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "llama3.1-8B",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "你好，世界！"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 5,
    "total_tokens": 15
  }
}
```

### GET /v1/models

返回可用模型列表。

**请求示例：**

```bash
curl http://localhost:8000/v1/models \
  -H "Authorization: Bearer sk-chatjimmy-local-dev-key"
```

## ⚙️ 配置选项

### 环境变量

创建 `.env` 文件或直接设置环境变量：

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `HOST` | 服务监听地址 | `0.0.0.0` |
| `PORT` | 服务端口 | `8000` |
| `API_KEYS` | API 密钥（多个用逗号分隔） | `sk-chatjimmy-local-dev-key` |
| `ENHANCE_TRANSLATION` | 是否启用翻译增强 | `true` |
| `STREAM_CHUNK_SIZE` | 流式响应块大小（字符数） | `5` |

### 配置示例

```env
# 服务配置
HOST=0.0.0.0
PORT=8000

# API Keys（多个用逗号分隔）
API_KEYS=sk-your-key-1,sk-your-key-2

# 翻译增强
ENHANCE_TRANSLATION=true
STREAM_CHUNK_SIZE=5
```

## 📁 项目结构

```
chatjimmy-api-proxy/
├── main.py              # FastAPI 主应用
├── config.py            # 配置管理
├── models.py            # Pydantic 数据模型
├── chatjimmy_client.py  # ChatJimmy API 客户端
├── requirements.txt     # Python 依赖
├── start.sh             # 启动脚本
├── .env.example         # 环境变量模板
├── .gitignore           # Git 忽略规则
├── LICENSE              # MIT 许可证
└── README.md            # 项目文档
```

## 🔍 故障排除

### 服务无法启动

检查端口是否被占用：
```bash
# macOS/Linux
lsof -i :8000

# 终止占用进程
kill -9 $(lsof -t -i:8000)
```

### API 请求失败

1. 确认服务正在运行：访问 `http://localhost:8000/v1/models`
2. 检查 API Key 是否正确
3. 查看控制台错误日志

### 翻译质量问题

- 确保 `ENHANCE_TRANSLATION=true` 已启用
- 尝试调整 `temperature` 参数（默认 0.3）

## ⚠️ 注意事项

1. **仅供个人学习使用**：请遵守 ChatJimmy.ai 的服务条款
2. **速率限制**：ChatJimmy.ai 可能有隐式速率限制
3. **服务稳定性**：这是非官方 API 代理，可能会变更
4. **Token 限制**：页面显示 6144 tokens 限制

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [ChatJimmy.ai](https://chatjimmy.ai/) - 提供免费的 LLM 推理服务
- [沉浸式翻译](https://immersivetranslate.com/) - 优秀的浏览器翻译插件
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
