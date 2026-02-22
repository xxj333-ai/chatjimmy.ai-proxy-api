"""
ChatJimmy API 代理服务 - 主应用
提供 OpenAI 兼容的 API 接口
"""
import json
import time
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import config
from models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatMessage,
    Usage,
    ChatCompletionChunk,
    StreamChoice,
    DeltaMessage,
    ModelListResponse,
    ModelInfo
)
from chatjimmy_client import client as chatjimmy_client

# 创建 FastAPI 应用
app = FastAPI(
    title="ChatJimmy API Proxy",
    description="OpenAI 兼容的 ChatJimmy.ai API 代理服务",
    version="1.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_api_key(authorization: Optional[str] = None) -> bool:
    """
    验证 API Key
    
    Args:
        authorization: Authorization 头
        
    Returns:
        验证是否通过
    """
    if not config.API_KEYS or config.API_KEYS == [""]:
        # 未配置 API Key，允许所有请求
        return True
    
    if not authorization:
        return False
    
    # 支持 Bearer token 格式
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization
    
    return token in config.API_KEYS


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "ChatJimmy API Proxy",
        "status": "running",
        "endpoints": {
            "chat": "/v1/chat/completions",
            "models": "/v1/models"
        }
    }


@app.get("/v1/models")
async def list_models(authorization: Optional[str] = Header(None)):
    """
    列出可用模型
    
    沉浸式翻译需要此端点
    """
    if not verify_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return ModelListResponse(
        data=[ModelInfo(**model) for model in config.AVAILABLE_MODELS]
    )


@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    authorization: Optional[str] = Header(None)
):
    """
    聊天完成端点 - OpenAI 兼容
    
    支持流式和非流式响应
    """
    if not verify_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # 转换消息格式
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    model = request.model
    
    if request.stream:
        # 流式响应
        return StreamingResponse(
            generate_stream_response(messages, model, request.temperature, request.top_p, request.max_tokens),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    else:
        # 非流式响应
        content, stats = await chatjimmy_client.chat(
            messages, 
            model, 
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens
        )
        
        # 构建 OpenAI 格式响应
        response = ChatCompletionResponse(
            model=model,
            choices=[
                ChatCompletionChoice(
                    message=ChatMessage(role="assistant", content=content),
                    finish_reason="stop"
                )
            ],
            usage=Usage(
                prompt_tokens=stats.get("prefill_tokens", 0),
                completion_tokens=stats.get("decode_tokens", 0),
                total_tokens=stats.get("total_tokens", 0)
            )
        )
        
        return response


async def generate_stream_response(messages: list, model: str, temperature: float = None, top_p: float = None, max_tokens: int = None):
    """
    生成流式响应
    
    Args:
        messages: 消息列表
        model: 模型名称
        temperature: 控制输出随机性，翻译任务推荐 0.1-0.3
        top_p: 核采样参数
        max_tokens: 最大输出 token 数
        
    Yields:
        SSE 格式的数据
    """
    chat_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    created = int(time.time())
    
    try:
        # 发送初始角色信息
        initial_chunk = ChatCompletionChunk(
            id=chat_id,
            created=created,
            model=model,
            choices=[
                StreamChoice(
                    delta=DeltaMessage(role="assistant"),
                    finish_reason=None
                )
            ]
        )
        yield f"data: {initial_chunk.model_dump_json()}\n\n"
        
        # 获取完整响应，然后批量发送
        content, stats = await chatjimmy_client.chat(
            messages, 
            model, 
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
        
        # 批量发送内容（优化速度）
        chunk_size = config.STREAM_CHUNK_SIZE
        for i in range(0, len(content), chunk_size):
            text_chunk = content[i:i+chunk_size]
            chunk = ChatCompletionChunk(
                id=chat_id,
                created=created,
                model=model,
                choices=[
                    StreamChoice(
                        delta=DeltaMessage(content=text_chunk),
                        finish_reason=None
                    )
                ]
            )
            yield f"data: {chunk.model_dump_json()}\n\n"
        
        # 发送结束标记
        final_chunk = ChatCompletionChunk(
            id=chat_id,
            created=created,
            model=model,
            choices=[
                StreamChoice(
                    delta=DeltaMessage(),
                    finish_reason="stop"
                )
            ]
        )
        yield f"data: {final_chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        # 发送错误信息
        error_data = {"error": {"message": str(e), "type": "internal_error"}}
        yield f"data: {json.dumps(error_data)}\n\n"


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": str(exc),
                "type": "internal_error"
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           ChatJimmy API Proxy Service                        ║
╠══════════════════════════════════════════════════════════════╣
║  API Address: http://{config.HOST}:{config.PORT}                       ║
║  Chat Endpoint: http://localhost:{config.PORT}/v1/chat/completions  ║
║  Models Endpoint: http://localhost:{config.PORT}/v1/models          ║
║  API Key: {config.API_KEYS[0][:20]}...                             ║
╚══════════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host=config.HOST, port=config.PORT)
