# Chat ve text modelleri ile tamamlamalar (completions) oluşturur

from typing import Dict, Any, List, Optional, Union
from api.api_client import APIClient
from api.endpoints import TEXT_COMPLETION_ENDPOINT
from core.model_registry import ModelRegistry
from core.token_counter import TokenCounter
from core.rate_limit_handler import RateLimitHandler
from exceptions.errors import (
    InvalidModel, TokenLimitExceeded, GroqAPIError, TextGenerationError,
    ValidationError, MessageFormatError, RateLimitExceeded
)


class TextGenerationHandler:
    """Chat ve text modelleri ile tamamlamalar oluşturan handler"""
    
    def __init__(self, api_client: APIClient, model_registry: Optional[ModelRegistry] = None,
                 token_counter: Optional[TokenCounter] = None, rate_limit_handler: Optional[RateLimitHandler] = None):
        """
        TextGenerationHandler'ı başlatır
        
        Args:
            api_client: API istemcisi
            model_registry: Model registry (opsiyonel)
            token_counter: Token counter (opsiyonel)
            rate_limit_handler: Rate limit handler (opsiyonel)
            
        Raises:
            TextGenerationError: Başlatma hatası
        """
        try:
            self.api_client = api_client
            self.rate_limit_handler = rate_limit_handler or RateLimitHandler()
            self.model_registry = model_registry or ModelRegistry()
            self.token_counter = token_counter or TokenCounter(
                model_registry=self.model_registry,
                rate_limit_handler=self.rate_limit_handler
            )
        except Exception as e:
            raise TextGenerationError("unknown", f"Failed to initialize TextGenerationHandler: {str(e)}")
    
    def generate(self, model: str, prompt: str = None, messages: List[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Text tamamlaması oluşturur
        
        Args:
            model: Kullanılacak model adı
            prompt: Tek satırlık prompt (completion modelleri için)
            messages: Mesaj listesi (chat modelleri için)
            **kwargs: Ek parametreler (temperature, max_tokens, vb.)
            
        Returns:
            API yanıtı
            
        Raises:
            ValidationError: Geçersiz parametreler
            InvalidModel: Model bulunamadığında
            TokenLimitExceeded: Token limiti aşıldığında
            TextGenerationError: Text generation hatası
            GroqAPIError: API hatası durumunda
        """
        # Model'i doğrula
        if not self.model_registry.is_model_supported(model):
            raise InvalidModel(model, f"Model '{model}' is not supported")
        
        # Model tipini al
        model_type = self.model_registry.get_type(model)
        
        if model_type != "chat":
            raise InvalidModel(model, f"Model '{model}' is not a chat model")
        
        # Parametreleri doğrula
        if prompt is None and messages is None:
            raise ValidationError("input", "Either 'prompt' or 'messages' must be provided")
        
        if prompt is not None and messages is not None:
            raise ValidationError("input", "Cannot provide both 'prompt' and 'messages'")
        
        # Mesaj formatını hazırla
        if prompt is not None:
            # Prompt'u mesaj formatına çevir
            messages = [{"role": "user", "content": prompt}]
        
        # Mesaj formatını doğrula
        self._validate_messages(messages)
        
        # Token sayısını kontrol et
        self._check_token_limits(messages, model, kwargs.get('max_tokens', 0))
        
        # Rate limit kontrolü
        self._check_rate_limits(messages, model)
        
        # API isteği için payload hazırla
        payload = self._prepare_payload(model, messages, **kwargs)
        
        # API isteği gönder
        try:
            response = self.api_client.post(TEXT_COMPLETION_ENDPOINT, payload)
            
            # Rate limit bilgilerini güncelle
            if '_headers' in response:
                self.rate_limit_handler.update_from_headers(response['_headers'])
            
            return response
            
        except GroqAPIError as e:
            # API hatası durumunda rate limit bilgilerini güncelle
            if hasattr(e, 'response') and hasattr(e.response, 'headers'):
                self.rate_limit_handler.update_from_headers(dict(e.response.headers))
            raise
        except Exception as e:
            raise TextGenerationError(model, f"Text generation failed: {str(e)}")
    
    def _validate_messages(self, messages: List[Dict[str, str]]) -> None:
        """
        Mesaj formatını doğrular
        
        Args:
            messages: Mesaj listesi
            
        Raises:
            ValidationError: Geçersiz mesaj listesi
            MessageFormatError: Geçersiz mesaj formatı
        """
        if not isinstance(messages, list):
            raise ValidationError("messages", "Messages must be a list")
        
        if not messages:
            raise ValidationError("messages", "Messages list cannot be empty")
        
        valid_roles = {"system", "user", "assistant"}
        
        for i, message in enumerate(messages):
            if not isinstance(message, dict):
                raise MessageFormatError(i, f"Message at index {i} must be a dictionary")
            
            if "role" not in message or "content" not in message:
                raise MessageFormatError(i, f"Message at index {i} must contain 'role' and 'content' fields")
            
            role = message["role"]
            content = message["content"]
            
            if role not in valid_roles:
                raise MessageFormatError(i, f"Message at index {i} has invalid role: {role}")
            
            if not isinstance(content, str):
                raise MessageFormatError(i, f"Message content at index {i} must be a string")
            
            if not content.strip():
                raise MessageFormatError(i, f"Message content at index {i} cannot be empty")
    
    def _check_token_limits(self, messages: List[Dict[str, str]], model: str, max_tokens: int) -> None:
        """
        Token limitlerini kontrol eder
        
        Args:
            messages: Mesaj listesi
            model: Model adı
            max_tokens: Maksimum token sayısı
            
        Raises:
            TokenLimitExceeded: Token limiti aşıldığında
            TextGenerationError: Token sayım hatası
        """
        try:
            # Mevcut mesajların token sayısını hesapla
            current_tokens = self.token_counter.count_message_tokens(messages, model)
            
            # Model'in maksimum token sayısını al
            model_max_tokens = self.model_registry.get_max_tokens(model)
            
            if model_max_tokens is None:
                return  # Limit bilgisi yoksa kontrol etme
            
            # Toplam token sayısını hesapla (mevcut + yeni)
            total_tokens = current_tokens + max_tokens
            
            if total_tokens > model_max_tokens:
                raise TokenLimitExceeded(
                    requested_tokens=total_tokens,
                    max_tokens=model_max_tokens,
                    message=f"Token limit exceeded. Current: {current_tokens}, Requested: {max_tokens}, Max: {model_max_tokens}"
                )
        except Exception as e:
            if isinstance(e, TokenLimitExceeded):
                raise
            raise TextGenerationError(model, f"Failed to check token limits: {str(e)}")
    
    def _check_rate_limits(self, messages: List[Dict[str, str]], model: str) -> None:
        """
        Rate limit kontrolü yapar
        
        Args:
            messages: Mesaj listesi
            model: Model adı
            
        Raises:
            TextGenerationError: Rate limit kontrol hatası
        """
        try:
            # Mesajların token sayısını hesapla
            tokens_required = self.token_counter.count_message_tokens(messages, model)
            
            # Rate limit kontrolü
            if not self.rate_limit_handler.can_proceed(tokens_required):
                self.rate_limit_handler.wait_if_needed()
        except Exception as e:
            raise TextGenerationError(model, f"Failed to check rate limits: {str(e)}")
    
    def _prepare_payload(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        API isteği için payload hazırlar
        
        Args:
            model: Model adı
            messages: Mesaj listesi
            **kwargs: Ek parametreler
            
        Returns:
            API payload'ı
        """
        payload = {
            "model": model,
            "messages": messages
        }
        
        # Ek parametreleri ekle
        valid_params = {
            'temperature', 'max_tokens', 'top_p', 'top_k', 'n', 'stream',
            'stop', 'presence_penalty', 'frequency_penalty', 'logit_bias',
            'user', 'response_format', 'seed', 'tools', 'tool_choice'
        }
        
        for key, value in kwargs.items():
            if key in valid_params:
                payload[key] = value
        
        return payload
    
    def generate_stream(self, model: str, prompt: str = None, messages: List[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Streaming text tamamlaması oluşturur
        
        Args:
            model: Kullanılacak model adı
            prompt: Tek satırlık prompt
            messages: Mesaj listesi
            **kwargs: Ek parametreler
            
        Returns:
            Streaming API yanıtı
            
        Raises:
            ValidationError: Geçersiz parametreler
            InvalidModel: Model bulunamadığında
            TokenLimitExceeded: Token limiti aşıldığında
            TextGenerationError: Text generation hatası
            GroqAPIError: API hatası durumunda
        """
        # Streaming için stream=True ekle
        kwargs['stream'] = True
        return self.generate(model, prompt, messages, **kwargs)
    
    def generate_with_tools(self, model: str, messages: List[Dict[str, str]], 
                           tools: List[Dict[str, Any]], tool_choice: str = "auto", **kwargs) -> Dict[str, Any]:
        """
        Tool kullanarak text tamamlaması oluşturur
        
        Args:
            model: Kullanılacak model adı
            messages: Mesaj listesi
            tools: Tool listesi
            tool_choice: Tool seçim stratejisi
            **kwargs: Ek parametreler
            
        Returns:
            API yanıtı
            
        Raises:
            ValidationError: Geçersiz parametreler
            InvalidModel: Model bulunamadığında
            TokenLimitExceeded: Token limiti aşıldığında
            TextGenerationError: Text generation hatası
            GroqAPIError: API hatası durumunda
        """
        if not isinstance(tools, list):
            raise ValidationError("tools", "Tools must be a list")
        
        if not tools:
            raise ValidationError("tools", "Tools list cannot be empty")
        
        # Tool parametrelerini ekle
        kwargs['tools'] = tools
        kwargs['tool_choice'] = tool_choice
        
        return self.generate(model, messages=messages, **kwargs)
    
    def get_usage_info(self, messages: List[Dict[str, str]], model: str, max_tokens: int = 0) -> Dict[str, Any]:
        """
        Token kullanım bilgilerini döndürür
        
        Args:
            messages: Mesaj listesi
            model: Model adı
            max_tokens: Maksimum token sayısı
            
        Returns:
            Token kullanım bilgileri
            
        Raises:
            ValidationError: Geçersiz parametreler
            InvalidModel: Model bulunamadığında
            TextGenerationError: Token sayım hatası
        """
        if not self.model_registry.is_model_supported(model):
            raise InvalidModel(model, f"Model '{model}' is not supported")
        
        try:
            return self.token_counter.get_token_usage_info(messages, model, max_tokens)
        except Exception as e:
            raise TextGenerationError(model, f"Failed to get usage info: {str(e)}") 