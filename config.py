"""
配置文件 - ChatJimmy API 代理服务
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 服务配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# API Key 配置（用于验证客户端请求）
# 可以设置多个 API Key，用逗号分隔
API_KEYS = os.getenv("API_KEYS", "sk-chatjimmy-local-dev-key").split(",")

# ChatJimmy.ai API 配置
CHATJIMMY_API_URL = "https://chatjimmy.ai/api/chat"
CHATJIMMY_DEFAULT_MODEL = "llama3.1-8B"

# 可用模型列表
AVAILABLE_MODELS = [
    {
        "id": "llama3.1-8B",
        "object": "model",
        "created": 1700000000,
        "owned_by": "chatjimmy"
    }
]

# 默认聊天选项
DEFAULT_CHAT_OPTIONS = {
    "selectedModel": CHATJIMMY_DEFAULT_MODEL,
    "systemPrompt": "",
    "topK": 8
}

# 翻译增强配置
ENHANCE_TRANSLATION = os.getenv("ENHANCE_TRANSLATION", "true").lower() == "true"

# 增强的翻译规则（注入到系统提示词中）
TRANSLATION_ENHANCEMENT_RULES = """

## 附加翻译规则（代理服务增强）
1. 使用常用词汇，避免生僻字和古语表达
2. 保持正式、专业的翻译风格
3. 严格保持原文的段落格式，每个段落独立翻译
4. 段落之间用空行分隔，不要合并段落
5. 常见词汇翻译规范：
   - "men and women" 翻译为"男女"，不要翻译为"男男女女"
   - "reckless" 翻译为"鲁莽"，不要使用生僻词如"莽撊"
6. 避免重复用词，如"各种各样"应简化为"各种"
7. 保持译文简洁流畅，避免冗余表达"""

# 流式响应配置
STREAM_CHUNK_SIZE = int(os.getenv("STREAM_CHUNK_SIZE", "5"))  # 每次发送的字符数
