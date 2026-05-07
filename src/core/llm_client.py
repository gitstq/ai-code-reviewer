#!/usr/bin/env python3
"""
LLM客户端 - 支持多种AI模型后端
"""

import os
import json
from typing import List, Dict, Any, Optional, Generator
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class LLMResponse:
    """LLM响应数据类"""
    content: str
    model: str
    usage: Dict[str, int]
    

class BaseLLMClient(ABC):
    """LLM客户端基类"""
    
    @abstractmethod
    def review_code(self, code: str, context: str = "") -> LLMResponse:
        """审查代码"""
        pass
    
    @abstractmethod
    def stream_review(self, code: str, context: str = "") -> Generator[str, None, None]:
        """流式审查代码"""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI客户端"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                pass
    
    def _build_prompt(self, code: str, context: str = "") -> str:
        """构建提示词"""
        prompt = f"""你是一个专业的代码审查助手。请对以下代码进行审查，并提供详细的改进建议。

审查维度：
1. 代码质量和可读性
2. 潜在的安全漏洞
3. 性能优化建议
4. 最佳实践遵循情况
5. 可维护性和扩展性

{context}

代码内容：
```
{code}
```

请以JSON格式返回审查结果：
{{
    "summary": "总体评价摘要",
    "issues": [
        {{
            "line": 行号,
            "severity": "critical/high/medium/low/info",
            "category": "security/quality/performance/style",
            "message": "问题描述",
            "suggestion": "改进建议"
        }}
    ],
    "recommendations": ["总体改进建议1", "总体改进建议2"]
}}
"""
        return prompt
    
    def review_code(self, code: str, context: str = "") -> LLMResponse:
        """审查代码"""
        if not self.client:
            raise RuntimeError("OpenAI客户端未初始化，请检查API密钥")
        
        prompt = self._build_prompt(code, context)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业的代码审查助手，擅长发现代码中的问题和改进点。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=self.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        )
    
    def stream_review(self, code: str, context: str = "") -> Generator[str, None, None]:
        """流式审查代码"""
        if not self.client:
            raise RuntimeError("OpenAI客户端未初始化，请检查API密钥")
        
        prompt = self._build_prompt(code, context)
        
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业的代码审查助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude客户端"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.client = None
        
        if self.api_key:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
            except ImportError:
                pass
    
    def _build_prompt(self, code: str, context: str = "") -> str:
        """构建提示词"""
        prompt = f"""请对以下代码进行专业审查：

{context}

代码：
```
{code}
```

请从以下维度分析：
1. 代码质量和可读性
2. 安全漏洞
3. 性能问题
4. 最佳实践
5. 可维护性

返回JSON格式的审查结果。"""
        return prompt
    
    def review_code(self, code: str, context: str = "") -> LLMResponse:
        """审查代码"""
        if not self.client:
            raise RuntimeError("Anthropic客户端未初始化，请检查API密钥")
        
        prompt = self._build_prompt(code, context)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        
        return LLMResponse(
            content=response.content[0].text,
            model=self.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
        )
    
    def stream_review(self, code: str, context: str = "") -> Generator[str, None, None]:
        """流式审查代码"""
        if not self.client:
            raise RuntimeError("Anthropic客户端未初始化，请检查API密钥")
        
        prompt = self._build_prompt(code, context)
        
        with self.client.messages.stream(
            model=self.model,
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ],
        ) as stream:
            for text in stream.text_stream:
                yield text


class OllamaClient(BaseLLMClient):
    """Ollama本地模型客户端"""
    
    def __init__(self, model: str = "codellama", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        self.client = None
        
        try:
            import ollama
            self.client = ollama
        except ImportError:
            pass
    
    def _build_prompt(self, code: str, context: str = "") -> str:
        """构建提示词"""
        prompt = f"""作为代码审查专家，请审查以下代码：

{context}

代码：
```
{code}
```

请指出：
1. 代码问题
2. 安全风险
3. 改进建议
4. 最佳实践建议"""
        return prompt
    
    def review_code(self, code: str, context: str = "") -> LLMResponse:
        """审查代码"""
        if not self.client:
            raise RuntimeError("Ollama客户端未初始化，请安装ollama库")
        
        prompt = self._build_prompt(code, context)
        
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        
        return LLMResponse(
            content=response['message']['content'],
            model=self.model,
            usage={}
        )
    
    def stream_review(self, code: str, context: str = "") -> Generator[str, None, None]:
        """流式审查代码"""
        if not self.client:
            raise RuntimeError("Ollama客户端未初始化")
        
        prompt = self._build_prompt(code, context)
        
        stream = self.client.chat(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            stream=True,
        )
        
        for chunk in stream:
            yield chunk['message']['content']


class DeepSeekClient(BaseLLMClient):
    """DeepSeek客户端"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model = model
        self.client = None
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.deepseek.com"
                )
            except ImportError:
                pass
    
    def _build_prompt(self, code: str, context: str = "") -> str:
        """构建提示词"""
        prompt = f"""请对以下代码进行专业审查：

{context}

代码：
```
{code}
```

请分析：
1. 代码质量
2. 安全问题
3. 性能优化
4. 最佳实践"""
        return prompt
    
    def review_code(self, code: str, context: str = "") -> LLMResponse:
        """审查代码"""
        if not self.client:
            raise RuntimeError("DeepSeek客户端未初始化")
        
        prompt = self._build_prompt(code, context)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是专业的代码审查助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=self.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        )
    
    def stream_review(self, code: str, context: str = "") -> Generator[str, None, None]:
        """流式审查代码"""
        if not self.client:
            raise RuntimeError("DeepSeek客户端未初始化")
        
        prompt = self._build_prompt(code, context)
        
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是专业的代码审查助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class LLMClientFactory:
    """LLM客户端工厂"""
    
    CLIENTS = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "ollama": OllamaClient,
        "deepseek": DeepSeekClient,
    }
    
    @classmethod
    def create(cls, provider: str, **kwargs) -> BaseLLMClient:
        """创建LLM客户端"""
        provider = provider.lower()
        if provider not in cls.CLIENTS:
            raise ValueError(f"不支持的LLM提供商: {provider}，支持的选项: {list(cls.CLIENTS.keys())}")
        
        return cls.CLIENTS[provider](**kwargs)
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """列出支持的提供商"""
        return list(cls.CLIENTS.keys())
    
    @classmethod
    def get_default_provider(cls) -> str:
        """获取默认提供商"""
        # 按优先级检查环境变量
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        elif os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        elif os.getenv("DEEPSEEK_API_KEY"):
            return "deepseek"
        else:
            return "ollama"
