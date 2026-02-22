"""
Pydantic 模型定义 - OpenAI API 兼容格式
"""
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
import time


# ============ OpenAI 请求模型 ============

class ChatMessage(BaseModel):
    """聊天消息"""
    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionRequest(BaseModel):
    """聊天完成请求 - OpenAI 格式"""
    model: str = "llama3.1-8B"
    messages: List[ChatMessage]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    user: Optional[str] = None


# ============ OpenAI 响应模型 ============

class ChatCompletionChoice(BaseModel):
    """聊天完成选择"""
    index: int = 0
    message: ChatMessage
    finish_reason: Optional[str] = "stop"


class Usage(BaseModel):
    """Token 使用量"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponse(BaseModel):
    """聊天完成响应 - OpenAI 格式"""
    id: str = Field(default_factory=lambda: f"chatcmpl-{int(time.time())}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str = "llama3.1-8B"
    choices: List[ChatCompletionChoice]
    usage: Optional[Usage] = None


# ============ 流式响应模型 ============

class DeltaMessage(BaseModel):
    """增量消息（用于流式响应）"""
    role: Optional[str] = None
    content: Optional[str] = None


class StreamChoice(BaseModel):
    """流式选择"""
    index: int = 0
    delta: DeltaMessage
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    """聊天完成块（流式响应）"""
    id: str = Field(default_factory=lambda: f"chatcmpl-{int(time.time())}")
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str = "llama3.1-8B"
    choices: List[StreamChoice]


# ============ 模型列表响应 ============

class ModelInfo(BaseModel):
    """模型信息"""
    id: str
    object: str = "model"
    created: int
    owned_by: str


class ModelListResponse(BaseModel):
    """模型列表响应"""
    object: str = "list"
    data: List[ModelInfo]


# ============ ChatJimmy 请求模型 ============

class ChatOptions(BaseModel):
    """ChatJimmy 聊天选项"""
    selectedModel: str = "llama3.1-8B"
    systemPrompt: str = ""
    topK: int = 8
    temperature: Optional[float] = None
    topP: Optional[float] = None
    maxTokens: Optional[int] = None


class ChatJimmyRequest(BaseModel):
    """ChatJimmy API 请求格式"""
    messages: List[Dict[str, str]]
    chatOptions: ChatOptions
    attachment: Optional[Any] = None
