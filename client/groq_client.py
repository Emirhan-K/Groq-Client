# Groq Dynamic Client - Ana istemci sınıfı
# Kullanıcının tek noktadan erişim sağlayacağı ana istemci sınıfıdır.

from typing import Optional
from api.api_client import APIClient
from handlers.text_generation import TextGenerationHandler
from handlers.speech_to_text import SpeechToTextHandler
from core.model_registry import ModelRegistry
from core.token_counter import TokenCounter
from core.rate_limit_handler import RateLimitHandler
from core.queue_manager import QueueManager
from exceptions.errors import (
    GroqAPIError, ClientError, ClientInitializationError, ValidationError,
    ConfigurationError, InvalidModel, TokenLimitExceeded
)


class GroqClient:
    """Groq API ile etkileşim için ana istemci sınıfı"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.groq.com"):
        """
        GroqClient'ı başlatır
        
        Args:
            api_key: Groq API anahtarı
            base_url: API base URL'i (varsayılan: https://api.groq.com)
            
        Raises:
            ValidationError: Geçersiz parametreler
            ConfigurationError: Yapılandırma hatası
            ClientInitializationError: Başlatma hatası
        """
        if not api_key or not api_key.strip():
            raise ValidationError("api_key", "API key is required and cannot be empty")
        
        if not base_url or not base_url.strip():
            raise ValidationError("base_url", "Base URL is required and cannot be empty")
        
        try:
            # API istemcisini oluştur
            self.api_client = APIClient(api_key, base_url)
            
            # Core bileşenleri oluştur
            self.model_registry = ModelRegistry(api_key=api_key)
            self.rate_limit_handler = RateLimitHandler()
            self.token_counter = TokenCounter(
                model_registry=self.model_registry,
                rate_limit_handler=self.rate_limit_handler
            )
            self.queue_manager = QueueManager(self.rate_limit_handler)
            
            # Handler'ları oluştur
            self._text_handler = TextGenerationHandler(
                api_client=self.api_client,
                model_registry=self.model_registry,
                token_counter=self.token_counter,
                rate_limit_handler=self.rate_limit_handler
            )
            
            self._speech_handler = SpeechToTextHandler(
                api_client=self.api_client,
                model_registry=self.model_registry,
                rate_limit_handler=self.rate_limit_handler
            )
        except Exception as e:
            raise ClientInitializationError(f"Failed to initialize GroqClient: {str(e)}")
    
    @property
    def text(self) -> TextGenerationHandler:
        """
        Text generation handler'ına erişim
        
        Returns:
            TextGenerationHandler instance
        """
        return self._text_handler
    
    @property
    def speech(self) -> SpeechToTextHandler:
        """
        Speech-to-text handler'ına erişim
        
        Returns:
            SpeechToTextHandler instance
        """
        return self._speech_handler
    
    def get_available_models(self, model_type: Optional[str] = None) -> list:
        """
        Kullanılabilir modelleri listeler
        
        Args:
            model_type: Model tipi filtresi ('chat' veya 'stt')
            
        Returns:
            Model adları listesi
            
        Raises:
            ValidationError: Geçersiz model tipi
            ClientError: Model listesi alma hatası
        """
        try:
            return self.model_registry.list_models(model_type)
        except Exception as e:
            raise ClientError(f"Failed to get available models: {str(e)}")
    
    def get_model_info(self, model: str) -> dict:
        """
        Model bilgilerini döndürür
        
        Args:
            model: Model adı
            
        Returns:
            Model bilgileri
            
        Raises:
            ValidationError: Geçersiz model adı
            InvalidModel: Model bulunamadığında
            ClientError: Model bilgisi alma hatası
        """
        if not model:
            raise ValidationError("model", "Model name cannot be empty")
            
        try:
            return self.model_registry.get_model_info(model)
        except Exception as e:
            if isinstance(e, (ValidationError, InvalidModel)):
                raise
            raise ClientError(f"Failed to get model info: {str(e)}")
    
    def is_model_supported(self, model: str) -> bool:
        """
        Model'in desteklenip desteklenmediğini kontrol eder
        
        Args:
            model: Model adı
            
        Returns:
            True: Destekleniyor, False: Desteklenmiyor
            
        Raises:
            ValidationError: Geçersiz model adı
            ClientError: Model kontrol hatası
        """
        if not model:
            raise ValidationError("model", "Model name cannot be empty")
            
        try:
            return self.model_registry.is_model_supported(model)
        except Exception as e:
            raise ClientError(f"Failed to check model support: {str(e)}")
    
    def count_tokens(self, text: str, model: str) -> int:
        """
        Metnin token sayısını hesaplar
        
        Args:
            text: Hesaplanacak metin
            model: Model adı
            
        Returns:
            Token sayısı
            
        Raises:
            ValidationError: Geçersiz parametreler
            InvalidModel: Model bulunamadığında
            ClientError: Token sayım hatası
        """
        if not text:
            raise ValidationError("text", "Text cannot be empty")
            
        if not model:
            raise ValidationError("model", "Model name cannot be empty")
            
        try:
            return self.token_counter.count_tokens(text, model)
        except Exception as e:
            if isinstance(e, (ValidationError, InvalidModel)):
                raise
            raise ClientError(f"Failed to count tokens: {str(e)}")
    
    def count_message_tokens(self, messages: list, model: str) -> int:
        """
        Mesaj listesinin token sayısını hesaplar
        
        Args:
            messages: Mesaj listesi
            model: Model adı
            
        Returns:
            Token sayısı
            
        Raises:
            ValidationError: Geçersiz parametreler
            InvalidModel: Model bulunamadığında
            ClientError: Token sayım hatası
        """
        if not messages:
            raise ValidationError("messages", "Messages list cannot be empty")
            
        if not model:
            raise ValidationError("model", "Model name cannot be empty")
            
        try:
            return self.token_counter.count_message_tokens(messages, model)
        except Exception as e:
            if isinstance(e, (ValidationError, InvalidModel)):
                raise
            raise ClientError(f"Failed to count message tokens: {str(e)}")
    
    def get_rate_limit_status(self) -> dict:
        """
        Rate limit durumunu döndürür
        
        Returns:
            Rate limit durum bilgileri
            
        Raises:
            ClientError: Rate limit durumu alma hatası
        """
        try:
            return self.rate_limit_handler.get_status()
        except Exception as e:
            raise ClientError(f"Failed to get rate limit status: {str(e)}")
    
    def get_queue_status(self) -> dict:
        """
        İstek sırası durumunu döndürür
        
        Returns:
            Sıra durum bilgileri
            
        Raises:
            ClientError: Sıra durumu alma hatası
        """
        try:
            return self.queue_manager.get_queue_status()
        except Exception as e:
            raise ClientError(f"Failed to get queue status: {str(e)}")
    
    def get_usage_info(self, messages: list, model: str, max_tokens: int = 0) -> dict:
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
            ClientError: Kullanım bilgisi alma hatası
        """
        if not messages:
            raise ValidationError("messages", "Messages list cannot be empty")
            
        if not model:
            raise ValidationError("model", "Model name cannot be empty")
            
        if max_tokens < 0:
            raise ValidationError("max_tokens", "Max tokens cannot be negative")
            
        try:
            return self.token_counter.get_token_usage_info(messages, model, max_tokens)
        except Exception as e:
            if isinstance(e, (ValidationError, InvalidModel)):
                raise
            raise ClientError(f"Failed to get usage info: {str(e)}")
    
    def enqueue_request(self, request_func, *args, priority: str = "normal", 
                       tokens_required: int = 0, max_retries: int = 3, **kwargs) -> str:
        """
        İsteği sıraya alır
        
        Args:
            request_func: Çalıştırılacak fonksiyon
            *args: Fonksiyon argümanları
            priority: Öncelik seviyesi
            tokens_required: Gereken token sayısı
            max_retries: Maksimum yeniden deneme sayısı
            **kwargs: Fonksiyon keyword argümanları
            
        Returns:
            İstek ID'si
            
        Raises:
            ValidationError: Geçersiz parametreler
            ClientError: Sıraya alma hatası
        """
        if not callable(request_func):
            raise ValidationError("request_func", "Request function must be callable")
            
        if tokens_required < 0:
            raise ValidationError("tokens_required", "Tokens required cannot be negative")
            
        if max_retries < 0:
            raise ValidationError("max_retries", "Max retries cannot be negative")
            
        try:
            return self.queue_manager.enqueue(
                request_func, *args, 
                priority=priority, 
                tokens_required=tokens_required, 
                max_retries=max_retries, 
                **kwargs
            )
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ClientError(f"Failed to enqueue request: {str(e)}")
    
    def process_queue(self) -> None:
        """
        İstek sırasını işler
        
        Raises:
            ClientError: Sıra işleme hatası
        """
        try:
            self.queue_manager.process_queue()
        except Exception as e:
            raise ClientError(f"Failed to process queue: {str(e)}")
    
    def clear_queue(self, priority: Optional[str] = None) -> None:
        """
        İstek sırasını temizler
        
        Args:
            priority: Temizlenecek öncelik seviyesi (opsiyonel)
            
        Raises:
            ValidationError: Geçersiz öncelik seviyesi
            ClientError: Sıra temizleme hatası
        """
        try:
            self.queue_manager.clear_queue(priority)
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ClientError(f"Failed to clear queue: {str(e)}")
    
    def stop_queue_processing(self) -> None:
        """
        Sıra işlemeyi durdurur
        
        Raises:
            ClientError: Sıra durdurma hatası
        """
        try:
            self.queue_manager.stop_processing()
        except Exception as e:
            raise ClientError(f"Failed to stop queue processing: {str(e)}")
    
    def close(self) -> None:
        """
        İstemciyi kapatır ve kaynakları temizler
        
        Raises:
            ClientError: Kapatma hatası
        """
        try:
            # API istemcisini kapat
            if hasattr(self, 'api_client'):
                self.api_client.close()
            
            # Sıra işlemeyi durdur
            if hasattr(self, 'queue_manager'):
                self.queue_manager.stop_processing()
        except Exception as e:
            raise ClientError(f"Failed to close client: {str(e)}")
    
    def __enter__(self):
        """Context manager desteği"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager desteği"""
        self.close()
    
    def __del__(self):
        """Destructor"""
        try:
            self.close()
        except:
            pass  # Destructor'da hata fırlatma 