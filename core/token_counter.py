# Prompt ve mesajların token sayısını hesaplar

import tiktoken
import time
from typing import List, Dict, Any, Optional
from core.model_registry import ModelRegistry
from core.rate_limit_handler import RateLimitHandler
from exceptions.errors import (
    InvalidModel, TokenCounterError, EncodingError, ValidationError, 
    MessageFormatError, TokenLimitExceeded, RateLimitExceeded
)


class TokenCounter:
    """Prompt ve mesajların token sayısını hesaplayan sınıf"""
    
    def __init__(self, model_registry: Optional[ModelRegistry] = None, 
                 rate_limit_handler: Optional[RateLimitHandler] = None):
        """
        TokenCounter'ı başlatır
        
        Args:
            model_registry: Model registry (opsiyonel)
            rate_limit_handler: Rate limit handler (opsiyonel)
            
        Raises:
            TokenCounterError: Başlatma hatası
        """
        try:
            self.model_registry = model_registry or ModelRegistry()
            self.rate_limit_handler = rate_limit_handler
            self._encoders = {}
            self._model_to_encoding = {
                # Llama modelleri için cl100k_base encoding
                "llama3-8b-8192": "cl100k_base",
                "llama3-70b-8192": "cl100k_base",
                "llama3.1-8b-8192": "cl100k_base",
                "llama3.1-70b-8192": "cl100k_base",
                "llama3.1-405b-8192": "cl100k_base",
                
                # Mixtral için cl100k_base encoding
                "mixtral-8x7b-32768": "cl100k_base",
                
                # Gemma modelleri için cl100k_base encoding
                "gemma2-9b-it": "cl100k_base",
                "gemma2-27b-it": "cl100k_base",
                
                # Whisper için cl100k_base encoding (STT ama yine de encoding gerekebilir)
                "whisper-large-v3": "cl100k_base"
            }
            
            # Token kullanım geçmişi için
            self._usage_history = []
            self._total_tokens_used = 0
            
        except Exception as e:
            raise TokenCounterError(f"Failed to initialize TokenCounter: {str(e)}")
    
    def _get_encoder(self, model: str) -> tiktoken.Encoding:
        """
        Model için uygun encoder'ı döndürür
        
        Args:
            model: Model adı
            
        Returns:
            tiktoken.Encoding objesi
            
        Raises:
            EncodingError: Encoding hatası
        """
        if model not in self._encoders:
            # Model için encoding tipini belirle
            encoding_name = self._model_to_encoding.get(model, "cl100k_base")
            
            try:
                self._encoders[model] = tiktoken.get_encoding(encoding_name)
            except KeyError as e:
                raise EncodingError(model, encoding_name, f"Encoding '{encoding_name}' not found")
            except Exception as e:
                raise EncodingError(model, encoding_name, f"Failed to get encoding: {str(e)}")
        
        return self._encoders[model]
    
    def count_tokens(self, prompt: str, model: str) -> int:
        """
        Tek bir prompt'un token sayısını hesaplar
        
        Args:
            prompt: Hesaplanacak prompt
            model: Model adı
            
        Returns:
            Token sayısı
            
        Raises:
            ValidationError: Geçersiz prompt
            InvalidModel: Model bulunamadığında
            EncodingError: Encoding hatası
        """
        if not isinstance(prompt, str):
            raise ValidationError("prompt", "Prompt must be a string")
        
        if not prompt:
            raise ValidationError("prompt", "Prompt cannot be empty")
        
        # Model'in desteklenip desteklenmediğini kontrol et
        if not self.model_registry.is_model_supported(model):
            raise InvalidModel(model, f"Model '{model}' is not supported")
        
        # STT modelleri için token sayımı yapılmaz
        model_type = self.model_registry.get_type(model)
        if model_type == "stt":
            return 0
        
        # Encoder'ı al ve token sayısını hesapla
        try:
            encoder = self._get_encoder(model)
            tokens = encoder.encode(prompt)
            return len(tokens)
        except Exception as e:
            raise EncodingError(model, "unknown", f"Failed to count tokens: {str(e)}")
    
    def count_message_tokens(self, messages: List[Dict[str, Any]], model: str) -> int:
        """
        Mesaj listesinin toplam token sayısını hesaplar
        
        Args:
            messages: Mesaj listesi [{"role": "...", "content": "..."}, ...]
            model: Model adı
            
        Returns:
            Toplam token sayısı
            
        Raises:
            ValidationError: Geçersiz mesaj listesi
            InvalidModel: Model bulunamadığında
            MessageFormatError: Geçersiz mesaj formatı
            EncodingError: Encoding hatası
        """
        if not isinstance(messages, list):
            raise ValidationError("messages", "Messages must be a list")
        
        if not messages:
            raise ValidationError("messages", "Messages list cannot be empty")
        
        # Model'in desteklenip desteklenmediğini kontrol et
        if not self.model_registry.is_model_supported(model):
            raise InvalidModel(model, f"Model '{model}' is not supported")
        
        # STT modelleri için token sayımı yapılmaz
        model_type = self.model_registry.get_type(model)
        if model_type == "stt":
            return 0
        
        # Encoder'ı al
        try:
            encoder = self._get_encoder(model)
        except Exception as e:
            raise EncodingError(model, "unknown", f"Failed to get encoder: {str(e)}")
            
        total_tokens = 0
        
        for i, message in enumerate(messages):
            if not isinstance(message, dict):
                raise MessageFormatError(i, f"Message at index {i} must be a dictionary")
            
            # Mesaj formatını kontrol et
            if "role" not in message or "content" not in message:
                raise MessageFormatError(i, f"Message at index {i} must contain 'role' and 'content' fields")
            
            role = message["role"]
            content = message["content"]
            
            if not isinstance(content, str):
                raise MessageFormatError(i, f"Message content at index {i} must be a string")
            
            if not isinstance(role, str):
                raise MessageFormatError(i, f"Message role at index {i} must be a string")
            
            # Role ve content'i birleştir (ChatGPT formatı)
            # Her mesaj için: <|im_start|>role\ncontent<|im_end|>
            formatted_message = f"<|im_start|>{role}\n{content}<|im_end|>"
            
            # Token sayısını hesapla
            try:
                tokens = encoder.encode(formatted_message)
                total_tokens += len(tokens)
            except Exception as e:
                raise EncodingError(model, "unknown", f"Failed to encode message at index {i}: {str(e)}")
        
        # Son mesajdan sonra assistant'ın yanıtı için ek token
        if messages and messages[-1].get("role") != "assistant":
            # Assistant yanıtı için ek token
            try:
                assistant_token = encoder.encode("<|im_start|>assistant\n")
                total_tokens += len(assistant_token)
            except Exception as e:
                raise EncodingError(model, "unknown", f"Failed to encode assistant token: {str(e)}")
        
        return total_tokens
    
    def estimate_tokens(self, text: str, model: str) -> int:
        """
        Metni token sayısına çevirir (yaklaşık hesaplama)
        
        Args:
            text: Hesaplanacak metin
            model: Model adı
            
        Returns:
            Yaklaşık token sayısı
            
        Raises:
            ValidationError: Geçersiz metin
        """
        if not isinstance(text, str):
            raise ValidationError("text", "Text must be a string")
        
        # Basit yaklaşım: 1 token ≈ 4 karakter (İngilizce için)
        # Türkçe için biraz daha fazla olabilir
        return len(text) // 3  # Daha muhafazakar tahmin
    
    def validate_token_limit(self, messages: List[Dict[str, Any]], model: str, max_tokens: int = None) -> bool:
        """
        Token limitini aşıp aşmadığını kontrol eder
        
        Args:
            messages: Mesaj listesi
            model: Model adı
            max_tokens: Maksimum token sayısı (opsiyonel)
            
        Returns:
            True: Limit aşılmamış, False: Limit aşılmış
            
        Raises:
            ValidationError: Geçersiz parametreler
            InvalidModel: Model bulunamadığında
            TokenLimitExceeded: Token limiti aşıldığında
        """
        if not self.model_registry.is_model_supported(model):
            raise InvalidModel(model, f"Model '{model}' is not supported")
        
        # Model'in maksimum token sayısını al
        if max_tokens is None:
            max_tokens = self.model_registry.get_max_tokens(model)
            if max_tokens is None:
                return True  # Limit bilgisi yoksa izin ver
        
        if max_tokens is not None and max_tokens < 0:
            raise ValidationError("max_tokens", "Max tokens cannot be negative")
        
        # Mevcut token sayısını hesapla
        try:
            current_tokens = self.count_message_tokens(messages, model)
        except Exception as e:
            raise TokenCounterError(f"Failed to count message tokens: {str(e)}")
        
        if max_tokens is not None and current_tokens > max_tokens:
            raise TokenLimitExceeded(current_tokens, max_tokens)
        
        return True
    
    def get_token_usage_info(self, messages: List[Dict[str, Any]], model: str, max_tokens: int = None) -> Dict[str, Any]:
        """
        Token kullanım bilgilerini döndürür
        
        Args:
            messages: Mesaj listesi
            model: Model adı
            max_tokens: Maksimum token sayısı (opsiyonel)
            
        Returns:
            Token kullanım bilgileri
            
        Raises:
            ValidationError: Geçersiz parametreler
            InvalidModel: Model bulunamadığında
            TokenCounterError: Token sayım hatası
        """
        if not self.model_registry.is_model_supported(model):
            raise InvalidModel(model, f"Model '{model}' is not supported")
        
        # Model'in maksimum token sayısını al
        if max_tokens is None:
            max_tokens = self.model_registry.get_max_tokens(model)
        
        # Mevcut token sayısını hesapla
        try:
            current_tokens = self.count_message_tokens(messages, model)
        except Exception as e:
            raise TokenCounterError(f"Failed to count message tokens: {str(e)}")
        
        info = {
            'current_tokens': current_tokens,
            'max_tokens': max_tokens,
            'model': model
        }
        
        if max_tokens is not None:
            info['remaining_tokens'] = max_tokens - current_tokens
            info['usage_percentage'] = (current_tokens / max_tokens) * 100
            info['within_limit'] = current_tokens <= max_tokens
        
        return info 
    
    def track_token_usage(self, messages: List[Dict[str, Any]], model: str, request_id: str = None) -> Dict[str, Any]:
        """
        Token kullanımını kaydeder ve geçmişe ekler
        
        Args:
            messages: Mesaj listesi
            model: Model adı
            request_id: İstek ID'si (opsiyonel)
            
        Returns:
            Kaydedilen token kullanım bilgileri
            
        Raises:
            TokenCounterError: Token sayım hatası
        """
        try:
            # Token sayısını hesapla
            token_count = self.count_message_tokens(messages, model)
            
            # Kullanım kaydı oluştur
            usage_record = {
                'timestamp': time.time(),
                'model': model,
                'token_count': token_count,
                'request_id': request_id,
                'message_count': len(messages)
            }
            
            # Geçmişe ekle
            self._usage_history.append(usage_record)
            
            # Toplam token sayısını güncelle
            self._total_tokens_used += token_count
            
            return usage_record
            
        except Exception as e:
            raise TokenCounterError(f"Failed to track token usage: {str(e)}")
    
    def get_usage_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Token kullanım geçmişini döndürür
        
        Args:
            limit: Döndürülecek kayıt sayısı (varsayılan: 100)
            
        Returns:
            Token kullanım geçmişi
        """
        return self._usage_history[-limit:] if limit > 0 else self._usage_history
    
    def get_total_tokens_used(self) -> int:
        """
        Toplam kullanılan token sayısını döndürür
        
        Returns:
            Toplam token sayısı
        """
        return self._total_tokens_used
    
    def clear_usage_history(self) -> None:
        """
        Token kullanım geçmişini temizler
        """
        self._usage_history.clear()
        self._total_tokens_used = 0
    
    def validate_request_with_rate_limit(self, 
                                       messages: List[Dict[str, Any]], 
                                       model: str, 
                                       max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        Token limitini ve rate limitini birlikte kontrol eder
        
        Args:
            messages: Mesaj listesi
            model: Model adı
            max_tokens: Maksimum token sayısı (opsiyonel)
            
        Returns:
            Validasyon sonuçları
            
        Raises:
            ValidationError: Geçersiz parametreler
            TokenLimitExceeded: Token limiti aşıldığında
            RateLimitExceeded: Rate limit aşıldığında
        """
        # Token sayısını hesapla
        token_count = self.count_message_tokens(messages, model)
        
        # Token limitini kontrol et
        self.validate_token_limit(messages, model, max_tokens)
        
        # Rate limit kontrolü (eğer rate limiter varsa)
        if self.rate_limit_handler:
            if not self.rate_limit_handler.can_proceed(token_count, 1):
                status = self.rate_limit_handler.get_status()
                raise RateLimitExceeded(
                    f"API rate limit exceeded. "
                    f"Requests: {status['request_remaining']}/{status['request_limit']}, "
                    f"Tokens: {status['token_remaining']}/{status['token_limit']}",
                    "API_RATE_LIMIT_EXCEEDED"
                )
        
        return {
            'token_count': token_count,
            'model': model,
            'can_proceed': True,
            'rate_limit_status': self.rate_limit_handler.get_status() if self.rate_limit_handler else None
        }
    
    def record_usage_with_rate_limit(self, 
                                   messages: List[Dict[str, Any]], 
                                   model: str,
                                   request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Token kullanımını kaydeder
        
        Args:
            messages: Mesaj listesi
            model: Model adı
            request_id: İstek ID'si (opsiyonel)
            
        Returns:
            Kaydedilen kullanım bilgileri
        """
        # Token sayısını hesapla
        token_count = self.count_message_tokens(messages, model)
        
        # Token kullanımını kaydet
        token_usage = self.track_token_usage(messages, model, request_id)
        
        return {
            'token_usage': token_usage,
            'token_count': token_count,
            'model': model,
            'timestamp': time.time(),
            'rate_limit_status': self.rate_limit_handler.get_status() if self.rate_limit_handler else None
        }
    
    def can_proceed_with_rate_limit(self, 
                                  messages: List[Dict[str, Any]], 
                                  model: str,
                                  max_tokens: Optional[int] = None) -> bool:
        """
        Token limitini ve rate limitini kontrol eder
        
        Args:
            messages: Mesaj listesi
            model: Model adı
            max_tokens: Maksimum token sayısı (opsiyonel)
            
        Returns:
            True: İstek yapılabilir, False: Limit aşılmış
        """
        try:
            self.validate_request_with_rate_limit(messages, model, max_tokens)
            return True
        except (TokenLimitExceeded, RateLimitExceeded, ValidationError):
            return False
    
    def get_comprehensive_status(self, model: str) -> Dict[str, Any]:
        """
        Model için kapsamlı durum raporu döndürür
        
        Args:
            model: Model adı
            
        Returns:
            Kapsamlı durum bilgileri
        """
        status = {
            'model': model,
            'current_time': time.time()
        }
        
        # Token bilgilerini güvenli şekilde al
        try:
            status['token_info'] = self.get_token_usage_info([], model)
        except Exception:
            # Boş mesaj listesi için varsayılan değerler
            status['token_info'] = {
                'current_tokens': 0,
                'max_tokens': self.model_registry.get_max_tokens(model) if self.model_registry else None,
                'model': model,
                'remaining_tokens': None,
                'usage_percentage': 0,
                'within_limit': True
            }
        
        # Rate limiter durumu (eğer varsa)
        if self.rate_limit_handler:
            status['rate_limit_status'] = self.rate_limit_handler.get_status()
        
        return status
    
    def get_all_models_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Tüm modellerin durumunu döndürür
        
        Returns:
            Tüm modellerin durum bilgileri
        """
        status = {}
        
        # Tüm desteklenen modeller için durum
        for model in self._model_to_encoding:
            status[model] = self.get_comprehensive_status(model)
        
        return status
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        Genel kullanım istatistiklerini döndürür
        
        Returns:
            Kullanım istatistikleri
        """
        stats = {
            'token_counter_stats': {
                'total_requests': len(self._usage_history),
                'total_tokens': self._total_tokens_used,
                'average_tokens_per_request': self._total_tokens_used / len(self._usage_history) if self._usage_history else 0,
                'usage_history': self._usage_history[-10:]  # Son 10 kayıt
            }
        }
        
        # Rate limiter istatistikleri (eğer varsa)
        if self.rate_limit_handler:
            stats['rate_limit_status'] = self.rate_limit_handler.get_status()
        
        return stats
    
    def reset_all_usage(self) -> None:
        """
        Tüm kullanım verilerini sıfırlar
        """
        self.clear_usage_history()
        
        # Rate limiter'ı da sıfırla (eğer varsa)
        if self.rate_limit_handler:
            self.rate_limit_handler.reset()
    
    def reset_model_usage(self, model: str) -> None:
        """
        Belirli model'in kullanımını sıfırlar
        
        Args:
            model: Model adı
        """
        # Token counter'ı sıfırla
        self.clear_usage_history()
        
        # Rate limiter'ı sıfırla (eğer varsa)
        if self.rate_limit_handler:
            self.rate_limit_handler.reset() 