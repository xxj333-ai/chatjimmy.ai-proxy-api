"""
ChatJimmy API 客户端
处理与 ChatJimmy.ai 的通信
"""
import httpx
import json
import re
from typing import AsyncGenerator, Tuple, Optional
from models import ChatJimmyRequest, ChatOptions
import config


class ChatJimmyClient:
    """ChatJimmy API 客户端"""
    
    def __init__(self):
        self.base_url = config.CHATJIMMY_API_URL
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Referer": "https://chatjimmy.ai/"
        }
    
    def convert_request(self, messages: list, model: str = None, temperature: float = None, top_p: float = None, max_tokens: int = None) -> ChatJimmyRequest:
        """
        将 OpenAI 格式的消息转换为 ChatJimmy 格式
        
        Args:
            messages: OpenAI 格式的消息列表
            model: 模型名称
            temperature: 控制输出随机性，翻译任务推荐 0.1-0.3
            top_p: 核采样参数
            max_tokens: 最大输出 token 数
            
        Returns:
            ChatJimmyRequest 对象
        """
        # 提取 system 消息作为 systemPrompt
        system_prompt = ""
        chat_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                chat_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # 增强系统提示词（如果启用）
        if config.ENHANCE_TRANSLATION and system_prompt:
            system_prompt = system_prompt + config.TRANSLATION_ENHANCEMENT_RULES
        
        return ChatJimmyRequest(
            messages=chat_messages,
            chatOptions=ChatOptions(
                selectedModel=model or config.CHATJIMMY_DEFAULT_MODEL,
                systemPrompt=system_prompt,
                topK=8,
                temperature=temperature,
                topP=top_p,
                maxTokens=max_tokens
            ),
            attachment=None
        )
    
    def parse_response(self, response_text: str) -> Tuple[str, dict]:
        """
        解析 ChatJimmy 响应
        
        Args:
            response_text: ChatJimmy 返回的原始文本
            
        Returns:
            (内容, 统计信息) 元组
        """
        # 解析 <|stats|> 标签中的统计信息
        stats = {}
        content = response_text
        
        stats_match = re.search(r'<\|stats\|>(.*?)<\|/stats\|>', response_text, re.DOTALL)
        if stats_match:
            try:
                stats = json.loads(stats_match.group(1))
                # 移除统计信息部分，获取纯内容
                content = response_text[:stats_match.start()].strip()
            except json.JSONDecodeError:
                pass
        
        return content, stats
    
    async def chat(self, messages: list, model: str = None, temperature: float = None, top_p: float = None, max_tokens: int = None) -> Tuple[str, dict]:
        """
        发送聊天请求（非流式）
        
        Args:
            messages: OpenAI 格式的消息列表
            model: 模型名称
            temperature: 控制输出随机性，翻译任务推荐 0.1-0.3
            top_p: 核采样参数
            max_tokens: 最大输出 token 数
            
        Returns:
            (内容, 统计信息) 元组
        """
        request = self.convert_request(messages, model, temperature, top_p, max_tokens)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.base_url,
                content=request.model_dump_json(),
                headers=self.headers
            )
            response.raise_for_status()
            
            response_text = response.text
            return self.parse_response(response_text)
    
    async def chat_stream(self, messages: list, model: str = None) -> AsyncGenerator[str, None]:
        """
        发送聊天请求（流式）
        
        由于 ChatJimmy API 本身返回的是完整响应，我们需要模拟流式输出
        以保持与 OpenAI 流式 API 的兼容性
        
        Args:
            messages: OpenAI 格式的消息列表
            model: 模型名称
            
        Yields:
            字符片段
        """
        content, stats = await self.chat(messages, model)
        
        # 逐字符 yield 以模拟流式输出
        for char in content:
            yield char


# 全局客户端实例
client = ChatJimmyClient()
