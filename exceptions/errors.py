# Uygulamaya özgü hata sınıflarını içerir 

from typing import Optional, Dict, Any


class GroqAPIError(Exception):
    """Groq API ile ilgili genel hatalar için temel sınıf"""
    
    def __init__(self, message: str, code: str = None, response: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.response = response
        super().__init__(self.message)


class RateLimitExceeded(GroqAPIError):
    """Rate limit aşıldığında fırlatılan hata"""
    
    def __init__(self, message: str = "Rate limit exceeded", code: str = "RATE_LIMIT_EXCEEDED", 
                 wait_time: Optional[float] = None):
        super().__init__(message, code)
        self.wait_time = wait_time


class InvalidModel(GroqAPIError):
    """Geçersiz model kullanıldığında fırlatılan hata"""
    
    def __init__(self, model: str, message: str = None, code: str = "INVALID_MODEL"):
        if message is None:
            message = f"Invalid model: {model}"
        super().__init__(message, code)
        self.model = model


class TokenLimitExceeded(GroqAPIError):
    """Token limiti aşıldığında fırlatılan hata"""
    
    def __init__(self, requested_tokens: int, max_tokens: int, message: str = None, code: str = "TOKEN_LIMIT_EXCEEDED"):
        if message is None:
            message = f"Token limit exceeded. Requested: {requested_tokens}, Max: {max_tokens}"
        super().__init__(message, code)
        self.requested_tokens = requested_tokens
        self.max_tokens = max_tokens


class ConfigurationError(GroqAPIError):
    """Yapılandırma hatası"""
    
    def __init__(self, key: str, message: str = None, code: str = "CONFIGURATION_ERROR"):
        if message is None:
            message = f"Configuration error for key: {key}"
        super().__init__(message, code)
        self.key = key


class FileError(GroqAPIError):
    """Dosya işlemleri ile ilgili hatalar"""
    
    def __init__(self, file_path: str, message: str = None, code: str = "FILE_ERROR"):
        if message is None:
            message = f"File error: {file_path}"
        super().__init__(message, code)
        self.file_path = file_path


class AudioFileError(FileError):
    """Ses dosyası ile ilgili hatalar"""
    
    def __init__(self, file_path: str, message: str = None, code: str = "AUDIO_FILE_ERROR"):
        if message is None:
            message = f"Audio file error: {file_path}"
        super().__init__(file_path, message, code)


class UnsupportedFormatError(AudioFileError):
    """Desteklenmeyen dosya formatı hatası"""
    
    def __init__(self, file_path: str, format: str, supported_formats: list, code: str = "UNSUPPORTED_FORMAT"):
        message = f"Unsupported audio format: {format}. Supported formats: {', '.join(supported_formats)}"
        super().__init__(file_path, message, code)
        self.format = format
        self.supported_formats = supported_formats


class FileSizeError(AudioFileError):
    """Dosya boyutu hatası"""
    
    def __init__(self, file_path: str, file_size: int, max_size: int, code: str = "FILE_SIZE_ERROR"):
        message = f"File too large: {file_size / (1024*1024):.2f}MB. Maximum size: {max_size / (1024*1024)}MB"
        super().__init__(file_path, message, code)
        self.file_size = file_size
        self.max_size = max_size


class QueueError(GroqAPIError):
    """İstek sırası ile ilgili hatalar"""
    
    def __init__(self, message: str, code: str = "QUEUE_ERROR"):
        super().__init__(message, code)


class QueueFullError(QueueError):
    """Sıra dolu hatası"""
    
    def __init__(self, queue_size: int, max_size: int, code: str = "QUEUE_FULL_ERROR"):
        message = f"Queue is full. Current size: {queue_size}, Max size: {max_size}"
        super().__init__(message, code)
        self.queue_size = queue_size
        self.max_size = max_size


class RequestTimeoutError(GroqAPIError):
    """İstek zaman aşımı hatası"""
    
    def __init__(self, timeout: float, message: str = None, code: str = "REQUEST_TIMEOUT_ERROR"):
        if message is None:
            message = f"Request timeout after {timeout} seconds"
        super().__init__(message, code)
        self.timeout = timeout


class NetworkError(GroqAPIError):
    """Ağ bağlantısı hatası"""
    
    def __init__(self, message: str = "Network connection error", code: str = "NETWORK_ERROR"):
        super().__init__(message, code)


class AuthenticationError(GroqAPIError):
    """Kimlik doğrulama hatası"""
    
    def __init__(self, message: str = "Authentication failed", code: str = "AUTHENTICATION_ERROR"):
        super().__init__(message, code)


class ValidationError(GroqAPIError):
    """Veri doğrulama hatası"""
    
    def __init__(self, field: str, message: str = None, code: str = "VALIDATION_ERROR"):
        if message is None:
            message = f"Validation error for field: {field}"
        super().__init__(message, code)
        self.field = field


class MessageFormatError(ValidationError):
    """Mesaj formatı hatası"""
    
    def __init__(self, message_index: int, message: str = None, code: str = "MESSAGE_FORMAT_ERROR"):
        if message is None:
            message = f"Invalid message format at index: {message_index}"
        super().__init__("message", message, code)
        self.message_index = message_index


class MetricsError(GroqAPIError):
    """Metrik işlemleri hatası"""
    
    def __init__(self, message: str, code: str = "METRICS_ERROR"):
        super().__init__(message, code)


class ExportError(MetricsError):
    """Metrik dışa aktarma hatası"""
    
    def __init__(self, format: str, message: str = None, code: str = "EXPORT_ERROR"):
        if message is None:
            message = f"Failed to export metrics in format: {format}"
        super().__init__(message, code)
        self.format = format


class ModelRegistryError(GroqAPIError):
    """Model registry hatası"""
    
    def __init__(self, message: str, code: str = "MODEL_REGISTRY_ERROR"):
        super().__init__(message, code)


class TokenCounterError(GroqAPIError):
    """Token sayacı hatası"""
    
    def __init__(self, message: str, code: str = "TOKEN_COUNTER_ERROR"):
        super().__init__(message, code)


class EncodingError(TokenCounterError):
    """Encoding hatası"""
    
    def __init__(self, model: str, encoding: str, message: str = None, code: str = "ENCODING_ERROR"):
        if message is None:
            message = f"Encoding error for model {model}: {encoding}"
        super().__init__(message, code)
        self.model = model
        self.encoding = encoding


class HandlerError(GroqAPIError):
    """Handler hatası"""
    
    def __init__(self, handler_type: str, message: str, code: str = "HANDLER_ERROR"):
        super().__init__(message, code)
        self.handler_type = handler_type


class TextGenerationError(HandlerError):
    """Text generation hatası"""
    
    def __init__(self, model: str, message: str = None, code: str = "TEXT_GENERATION_ERROR"):
        if message is None:
            message = f"Text generation error for model: {model}"
        super().__init__("text_generation", message, code)
        self.model = model


class SpeechToTextError(HandlerError):
    """Speech-to-text hatası"""
    
    def __init__(self, model: str, file_path: str, message: str = None, code: str = "SPEECH_TO_TEXT_ERROR"):
        if message is None:
            message = f"Speech-to-text error for model {model}, file {file_path}"
        super().__init__("speech_to_text", message, code)
        self.model = model
        self.file_path = file_path


class ClientError(GroqAPIError):
    """İstemci hatası"""
    
    def __init__(self, message: str, code: str = "CLIENT_ERROR"):
        super().__init__(message, code)


class ClientInitializationError(ClientError):
    """İstemci başlatma hatası"""
    
    def __init__(self, message: str = "Failed to initialize client", code: str = "CLIENT_INITIALIZATION_ERROR"):
        super().__init__(message, code)


class ThreadingError(GroqAPIError):
    """Threading hatası"""
    
    def __init__(self, message: str, code: str = "THREADING_ERROR"):
        super().__init__(message, code)


class LockError(ThreadingError):
    """Lock hatası"""
    
    def __init__(self, message: str = "Failed to acquire lock", code: str = "LOCK_ERROR"):
        super().__init__(message, code)


class RetryError(GroqAPIError):
    """Yeniden deneme hatası"""
    
    def __init__(self, max_retries: int, last_error: Exception, code: str = "RETRY_ERROR"):
        message = f"Max retries ({max_retries}) exceeded. Last error: {str(last_error)}"
        super().__init__(message, code)
        self.max_retries = max_retries
        self.last_error = last_error 