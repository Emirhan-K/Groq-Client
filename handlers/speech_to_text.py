# Ses dosyalarından yazı üretir (STT)

import os
import mimetypes
from pathlib import Path
from typing import Union, Dict, Any, Optional
from api.api_client import APIClient
from api.endpoints import STT_ENDPOINT
from core.model_registry import ModelRegistry
from core.rate_limit_handler import RateLimitHandler
from exceptions.errors import (
    InvalidModel, GroqAPIError, SpeechToTextError, AudioFileError,
    UnsupportedFormatError, FileSizeError, FileError, ValidationError
)


class SpeechToTextHandler:
    """Ses dosyalarından yazı üreten handler"""
    
    def __init__(self, api_client: APIClient, model_registry: Optional[ModelRegistry] = None,
                 rate_limit_handler: Optional[RateLimitHandler] = None, plan: str = "free"):
        """
        SpeechToTextHandler'ı başlatır
        
        Args:
            api_client: API istemcisi
            model_registry: Model registry (opsiyonel)
            rate_limit_handler: Rate limit handler (opsiyonel)
            plan: API planı ("free" veya "developer")
            
        Raises:
            SpeechToTextError: Başlatma hatası
        """
        try:
            self.api_client = api_client
            self.rate_limit_handler = rate_limit_handler or RateLimitHandler()
            self.model_registry = model_registry or ModelRegistry()
            
            # Plan bazlı dosya boyutu limitleri
            self.plan = plan.lower()
            if self.plan == "developer":
                self.max_file_size = 100 * 1024 * 1024  # 100 MB
            else:
                self.max_file_size = 25 * 1024 * 1024   # 25 MB (free plan)
            
            # Desteklenen ses dosyası formatları
            self.supported_formats = {
                '.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm', '.ogg', '.flac'
            }
        except Exception as e:
            raise SpeechToTextError("unknown", "unknown", f"Failed to initialize SpeechToTextHandler: {str(e)}")
    
    def transcribe(self, file: Union[str, Path], model: str, **kwargs) -> Dict[str, Any]:
        """
        Temel transkripsiyon fonksiyonu
        """
        # Dosya yolunu Path objesine çevir
        file_path = Path(file)
        # Dosya varlığını kontrol et
        if not file_path.exists():
            raise FileError(str(file_path), f"Audio file not found: {file_path}")
        if not file_path.is_file():
            raise FileError(str(file_path), f"Path is not a file: {file_path}")
        # Dosya formatını kontrol et
        self._validate_audio_file(file_path)
        # Model'i doğrula
        if not self.model_registry.is_model_supported(model):
            raise InvalidModel(model, f"Model '{model}' is not supported")
        # Model tipini kontrol et
        model_type = self.model_registry.get_type(model)
        if model_type != "stt":
            raise InvalidModel(model, f"Model '{model}' is not a speech-to-text model")
        # Rate limit kontrolü
        self._check_rate_limits(file_path)
        # Multipart form data hazırla
        try:
            with open(file_path, 'rb') as audio_file:
                files = {
                    'file': (
                        file_path.name,
                        audio_file,
                        self._get_mime_type(file_path)
                    )
                }
                data = {
                    'model': model
                }
                valid_params = {
                    'language', 'prompt', 'response_format', 'temperature'
                }
                for key, value in kwargs.items():
                    if key in valid_params and value is not None:
                        data[key] = str(value)
                response = self.api_client.post_multipart(
                    STT_ENDPOINT,
                    data=data,
                    files=files
                )
            # Rate limit bilgilerini güncelle
            if '_headers' in response:
                self.rate_limit_handler.update_from_headers(response['_headers'])
            return response
        except GroqAPIError as e:
            if hasattr(e, 'response') and hasattr(e.response, 'headers'):
                self.rate_limit_handler.update_from_headers(dict(e.response.headers))
            raise
        except Exception as e:
            raise SpeechToTextError(model, str(file_path), f"Transcription failed: {str(e)}")
    
    def _validate_audio_file(self, file_path: Path) -> None:
        """
        Ses dosyasını doğrular
        
        Args:
            file_path: Dosya yolu
            
        Raises:
            UnsupportedFormatError: Desteklenmeyen format
            FileSizeError: Dosya boyutu hatası
            AudioFileError: Ses dosyası hatası
        """
        # Dosya uzantısını kontrol et
        file_extension = file_path.suffix.lower()
        
        if file_extension not in self.supported_formats:
            raise UnsupportedFormatError(
                str(file_path), 
                file_extension, 
                list(self.supported_formats)
            )
        
        # Dosya boyutunu kontrol et
        try:
            file_size = file_path.stat().st_size
        except OSError as e:
            raise AudioFileError(str(file_path), f"Cannot get file size: {str(e)}")
            
        if file_size > self.max_file_size:
            raise FileSizeError(str(file_path), file_size, self.max_file_size)
        
        # Minimum süre kontrolü (0.01 saniye)
        estimated_duration = self._estimate_audio_duration(file_path)
        if estimated_duration < 0.01:
            raise AudioFileError(str(file_path), f"Audio file too short: {estimated_duration}s (minimum: 0.01s)")
        
        # Dosya okunabilir mi kontrol et
        if not os.access(file_path, os.R_OK):
            raise AudioFileError(str(file_path), f"Cannot read file: {file_path}")
    
    def _check_rate_limits(self, file_path: Path) -> None:
        """
        Rate limit kontrolü yapar
        
        Args:
            file_path: Ses dosyası yolu
            
        Raises:
            SpeechToTextError: Rate limit kontrol hatası
        """
        try:
            # Ses süresini hesapla (yaklaşık)
            audio_seconds = self._estimate_audio_duration(file_path)
            
            # STT için audio seconds ve request kontrolü
            if not self.rate_limit_handler.can_proceed(
                audio_seconds=audio_seconds,
                requests=1
            ):
                self.rate_limit_handler.wait_if_needed()
        except Exception as e:
            raise SpeechToTextError("unknown", "unknown", f"Failed to check rate limits: {str(e)}")
    
    def _estimate_audio_duration(self, file_path: Path) -> int:
        """
        Dosya boyutuna göre ses süresini tahmin eder
        
        Args:
            file_path: Ses dosyası yolu
            
        Returns:
            Tahmini ses süresi (saniye)
        """
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            
            # Yaklaşık hesaplama: 1MB ses ≈ 30-60 saniye (format'a göre değişir)
            # Ortalama: 1MB = 45 saniye
            estimated_seconds = int(file_size_mb * 45)
            
            # Minimum ve maksimum sınırlar
            return max(1, min(estimated_seconds, 3600))  # 1 saniye - 1 saat
            
        except Exception:
            # Hata durumunda varsayılan değer
            return 30
    
    def _prepare_multipart_data(self, file_path: Path, model: str, **kwargs) -> tuple:
        """
        (Kullanılmıyor) - Eski fonksiyon, backward compatibility için bırakılabilir.
        """
        raise NotImplementedError("_prepare_multipart_data artık kullanılmıyor. Lütfen transcribe fonksiyonunu kullanın.")
    
    def _get_mime_type(self, file_path: Path) -> str:
        """
        Dosya için MIME tipini döndürür
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            MIME tipi
        """
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        if mime_type is None:
            # Varsayılan MIME tipleri
            mime_map = {
                '.mp3': 'audio/mpeg',
                '.mp4': 'audio/mp4',
                '.mpeg': 'audio/mpeg',
                '.mpga': 'audio/mpeg',
                '.m4a': 'audio/mp4',
                '.wav': 'audio/wav',
                '.webm': 'audio/webm',
                '.ogg': 'audio/ogg',
                '.flac': 'audio/flac'
            }
            mime_type = mime_map.get(file_path.suffix.lower(), 'audio/mpeg')
        
        return mime_type
    
    def transcribe_with_prompt(self, file: Union[str, Path], model: str, 
                              prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Prompt ile ses dosyasını yazıya çevirir
        
        Args:
            file: Ses dosyası yolu
            model: Kullanılacak model adı
            prompt: Transkripsiyon için prompt
            **kwargs: Ek parametreler
            
        Returns:
            API yanıtı
            
        Raises:
            ValidationError: Geçersiz parametreler
            FileError: Dosya hatası
            AudioFileError: Ses dosyası hatası
            UnsupportedFormatError: Desteklenmeyen format
            FileSizeError: Dosya boyutu hatası
            InvalidModel: Model bulunamadığında
            SpeechToTextError: STT hatası
            GroqAPIError: API hatası durumunda
        """
        if not prompt:
            raise ValidationError("prompt", "Prompt cannot be empty")
            
        kwargs['prompt'] = prompt
        return self.transcribe(file, model, **kwargs)
    
    def transcribe_with_language(self, file: Union[str, Path], model: str, 
                                language: str, **kwargs) -> Dict[str, Any]:
        """
        Belirli dil ile ses dosyasını yazıya çevirir
        
        Args:
            file: Ses dosyası yolu
            model: Kullanılacak model adı
            language: Dil kodu (örn: 'tr', 'en', 'es')
            **kwargs: Ek parametreler
            
        Returns:
            API yanıtı
            
        Raises:
            ValidationError: Geçersiz parametreler
            FileError: Dosya hatası
            AudioFileError: Ses dosyası hatası
            UnsupportedFormatError: Desteklenmeyen format
            FileSizeError: Dosya boyutu hatası
            InvalidModel: Model bulunamadığında
            SpeechToTextError: STT hatası
            GroqAPIError: API hatası durumunda
        """
        if not language:
            raise ValidationError("language", "Language cannot be empty")
            
        kwargs['language'] = language
        return self.transcribe(file, model, **kwargs)
    
    def transcribe_json(self, file: Union[str, Path], model: str, **kwargs) -> Dict[str, Any]:
        """
        JSON formatında transkripsiyon yapar
        
        Args:
            file: Ses dosyası yolu
            model: Kullanılacak model adı
            **kwargs: Ek parametreler
            
        Returns:
            API yanıtı
            
        Raises:
            ValidationError: Geçersiz parametreler
            FileError: Dosya hatası
            AudioFileError: Ses dosyası hatası
            UnsupportedFormatError: Desteklenmeyen format
            FileSizeError: Dosya boyutu hatası
            InvalidModel: Model bulunamadığında
            SpeechToTextError: STT hatası
            GroqAPIError: API hatası durumunda
        """
        kwargs['response_format'] = 'json'
        return self.transcribe(file, model, **kwargs)
    
    def transcribe_verbose(self, file: Union[str, Path], model: str, **kwargs) -> Dict[str, Any]:
        """
        Detaylı transkripsiyon yapar (timestamp'ler ile)
        
        Args:
            file: Ses dosyası yolu
            model: Kullanılacak model adı
            **kwargs: Ek parametreler
            
        Returns:
            API yanıtı
            
        Raises:
            ValidationError: Geçersiz parametreler
            FileError: Dosya hatası
            AudioFileError: Ses dosyası hatası
            UnsupportedFormatError: Desteklenmeyen format
            FileSizeError: Dosya boyutu hatası
            InvalidModel: Model bulunamadığında
            SpeechToTextError: STT hatası
            GroqAPIError: API hatası durumunda
        """
        kwargs['response_format'] = 'verbose_json'
        return self.transcribe(file, model, **kwargs)
    
    def get_supported_formats(self) -> set:
        """
        Desteklenen ses dosyası formatlarını döndürür
        
        Returns:
            Desteklenen formatlar set'i
        """
        return self.supported_formats.copy()
    
    def validate_file_format(self, file_path: Union[str, Path]) -> bool:
        """
        Dosya formatının desteklenip desteklenmediğini kontrol eder
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            True: Format destekleniyor, False: Desteklenmiyor
        """
        file_path = Path(file_path)
        return file_path.suffix.lower() in self.supported_formats
    
    def get_plan_info(self) -> Dict[str, Any]:
        """
        Mevcut plan bilgilerini döndürür
        
        Returns:
            Plan bilgileri
        """
        return {
            'plan': self.plan,
            'max_file_size_mb': self.max_file_size / (1024 * 1024),
            'max_file_size_bytes': self.max_file_size,
            'supported_formats': list(self.supported_formats),
            'min_duration_seconds': 0.01
        }
    
    def check_file_compatibility(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Dosyanın uyumluluğunu kontrol eder
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            Uyumluluk bilgileri
        """
        file_path = Path(file_path)
        
        try:
            file_size = file_path.stat().st_size
            estimated_duration = self._estimate_audio_duration(file_path)
            format_supported = file_path.suffix.lower() in self.supported_formats
            
            return {
                'file_path': str(file_path),
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'estimated_duration_seconds': estimated_duration,
                'format_supported': format_supported,
                'format': file_path.suffix.lower(),
                'size_within_limit': file_size <= self.max_file_size,
                'duration_within_limit': estimated_duration >= 0.01,
                'compatible': (
                    format_supported and 
                    file_size <= self.max_file_size and 
                    estimated_duration >= 0.01
                ),
                'plan_limit_mb': self.max_file_size / (1024 * 1024)
            }
        except Exception as e:
            return {
                'file_path': str(file_path),
                'error': str(e),
                'compatible': False
            } 