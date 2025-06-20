# Groq API'den dönen gerçek rate limit header'larını işler

import time
import threading
import re
from typing import Dict, Any, Optional
from exceptions.errors import (
    RateLimitExceeded, ValidationError, ConfigurationError, ThreadingError, LockError
)


class RateLimitHandler:
    """Groq API rate limit yönetimi için handler sınıfı"""
    
    def __init__(self):
        """RateLimitHandler'ı başlatır"""
        try:
            self.lock = threading.Lock()
        except Exception as e:
            raise ThreadingError(f"Failed to create lock: {str(e)}")
            
        # Rate limit durumu
        self.request_limit = 0
        self.request_remaining = 0
        self.request_reset_time = 0
        self.token_limit = 0
        self.token_remaining = 0
        self.token_reset_time = 0
        # STT için audio seconds limitleri
        self.audio_seconds_limit = 0
        self.audio_seconds_remaining = 0
        self.audio_seconds_reset_time = 0
        self.last_update = 0
    
    def _parse_time_string(self, time_str: str) -> float:
        """
        Groq'un zaman formatını parse eder (örn: "6s", "60ms")
        
        Args:
            time_str: Zaman string'i
            
        Returns:
            Saniye cinsinden süre
        """
        if not time_str:
            return 0.0
        
        # Regex ile sayı ve birimi ayır
        match = re.match(r'(\d+(?:\.\d+)?)([a-zA-Z]+)', time_str)
        if not match:
            return 0.0
        
        value = float(match.group(1))
        unit = match.group(2).lower()
        
        # Birime göre saniyeye çevir
        if unit == 's':
            return value
        elif unit == 'ms':
            return value / 1000.0
        elif unit == 'm':
            return value * 60.0
        elif unit == 'h':
            return value * 3600.0
        else:
            return 0.0
    
    def update_from_headers(self, headers: dict) -> None:
        """
        Response header'larından rate limit bilgilerini günceller
        
        Args:
            headers: API response header'ları
            
        Raises:
            ValidationError: Geçersiz header formatı
            LockError: Lock edinme hatası
        """
        if not headers:
            raise ValidationError("headers", "Headers cannot be empty")
            
        try:
            with self.lock:
                # Limit değişikliklerini tespit et
                old_request_limit = self.request_limit
                old_token_limit = self.token_limit
                
                # Groq'un gerçek header'larını işle
                if 'x-ratelimit-limit-requests' in headers:
                    try:
                        self.request_limit = int(headers['x-ratelimit-limit-requests'])
                    except (ValueError, TypeError) as e:
                        raise ValidationError("x-ratelimit-limit-requests", f"Invalid request limit value: {headers['x-ratelimit-limit-requests']}")
                
                if 'x-ratelimit-remaining-requests' in headers:
                    try:
                        self.request_remaining = int(headers['x-ratelimit-remaining-requests'])
                    except (ValueError, TypeError) as e:
                        raise ValidationError("x-ratelimit-remaining-requests", f"Invalid remaining requests value: {headers['x-ratelimit-remaining-requests']}")
                
                if 'x-ratelimit-reset-requests' in headers:
                    try:
                        reset_time_str = headers['x-ratelimit-reset-requests']
                        reset_seconds = self._parse_time_string(reset_time_str)
                        self.request_reset_time = time.time() + reset_seconds
                    except Exception as e:
                        raise ValidationError("x-ratelimit-reset-requests", f"Invalid reset time value: {headers['x-ratelimit-reset-requests']}")
                
                # Token limitleri
                if 'x-ratelimit-limit-tokens' in headers:
                    try:
                        self.token_limit = int(headers['x-ratelimit-limit-tokens'])
                    except (ValueError, TypeError) as e:
                        raise ValidationError("x-ratelimit-limit-tokens", f"Invalid token limit value: {headers['x-ratelimit-limit-tokens']}")
                
                if 'x-ratelimit-remaining-tokens' in headers:
                    try:
                        self.token_remaining = int(headers['x-ratelimit-remaining-tokens'])
                    except (ValueError, TypeError) as e:
                        raise ValidationError("x-ratelimit-remaining-tokens", f"Invalid remaining tokens value: {headers['x-ratelimit-remaining-tokens']}")
                
                if 'x-ratelimit-reset-tokens' in headers:
                    try:
                        reset_time_str = headers['x-ratelimit-reset-tokens']
                        reset_seconds = self._parse_time_string(reset_time_str)
                        self.token_reset_time = time.time() + reset_seconds
                    except Exception as e:
                        raise ValidationError("x-ratelimit-reset-tokens", f"Invalid token reset time value: {headers['x-ratelimit-reset-tokens']}")
                
                # STT Audio Seconds limitleri
                if 'x-ratelimit-limit-audio-seconds' in headers:
                    try:
                        self.audio_seconds_limit = int(headers['x-ratelimit-limit-audio-seconds'])
                    except (ValueError, TypeError) as e:
                        raise ValidationError("x-ratelimit-limit-audio-seconds", f"Invalid audio seconds limit value: {headers['x-ratelimit-limit-audio-seconds']}")
                
                if 'x-ratelimit-remaining-audio-seconds' in headers:
                    try:
                        self.audio_seconds_remaining = int(headers['x-ratelimit-remaining-audio-seconds'])
                    except (ValueError, TypeError) as e:
                        raise ValidationError("x-ratelimit-remaining-audio-seconds", f"Invalid remaining audio seconds value: {headers['x-ratelimit-remaining-audio-seconds']}")
                
                if 'x-ratelimit-reset-audio-seconds' in headers:
                    try:
                        reset_time_str = headers['x-ratelimit-reset-audio-seconds']
                        reset_seconds = self._parse_time_string(reset_time_str)
                        self.audio_seconds_reset_time = time.time() + reset_seconds
                    except Exception as e:
                        raise ValidationError("x-ratelimit-reset-audio-seconds", f"Invalid audio seconds reset time value: {headers['x-ratelimit-reset-audio-seconds']}")
                
                self.last_update = time.time()
                
                # Limit değişikliklerini kontrol et
                request_limit_changed = old_request_limit != self.request_limit
                token_limit_changed = old_token_limit != self.token_limit
                
                if request_limit_changed or token_limit_changed:
                    # Limit değişikliği tespit edildi - log veya callback ile bildir
                    self._on_limits_changed(
                        request_limit_changed=request_limit_changed,
                        old_request_limit=old_request_limit,
                        new_request_limit=self.request_limit,
                        token_limit_changed=token_limit_changed,
                        old_token_limit=old_token_limit,
                        new_token_limit=self.token_limit
                    )
                    
        except Exception as e:
            raise LockError(f"Failed to acquire lock: {str(e)}")
    
    def _on_limits_changed(self, **kwargs) -> None:
        """
        Limit değişikliklerinde çağrılır (override edilebilir)
        
        Args:
            **kwargs: Değişiklik detayları
        """
        # Bu metod alt sınıflar tarafından override edilebilir
        # Örneğin: logging, monitoring, callback'ler için
        pass
    
    def can_proceed(self, tokens: int = 0, requests: int = 1, audio_seconds: int = 0) -> bool:
        """
        Belirtilen token, request ve audio seconds için istek yapılıp yapılamayacağını kontrol eder
        
        Args:
            tokens: İstek için gereken token sayısı (varsayılan: 0)
            requests: İstek sayısı (varsayılan: 1)
            audio_seconds: İstek için gereken ses süresi (STT için, varsayılan: 0)
            
        Returns:
            True: İstek yapılabilir, False: Rate limit aşılmış
            
        Raises:
            ValidationError: Geçersiz token/request/audio_seconds sayısı
            LockError: Lock edinme hatası
        """
        if tokens < 0:
            raise ValidationError("tokens", "Token count cannot be negative")
        if requests < 0:
            raise ValidationError("requests", "Request count cannot be negative")
        if audio_seconds < 0:
            raise ValidationError("audio_seconds", "Audio seconds cannot be negative")
            
        try:
            with self.lock:
                current_time = time.time()
                
                # Reset zamanları kontrol et
                if self.request_reset_time > 0 and current_time >= self.request_reset_time:
                    self.request_remaining = self.request_limit
                    self.request_reset_time = 0
                
                if self.token_reset_time > 0 and current_time >= self.token_reset_time:
                    self.token_remaining = self.token_limit
                    self.token_reset_time = 0
                
                if self.audio_seconds_reset_time > 0 and current_time >= self.audio_seconds_reset_time:
                    self.audio_seconds_remaining = self.audio_seconds_limit
                    self.audio_seconds_reset_time = 0
                
                # Request limit kontrolü
                if self.request_limit > 0:
                    if self.request_remaining < requests:
                        return False
                
                # Token limit kontrolü
                if self.token_limit > 0:
                    if self.token_remaining < tokens:
                        return False
                
                # Audio seconds limit kontrolü (STT için)
                if self.audio_seconds_limit > 0:
                    if self.audio_seconds_remaining < audio_seconds:
                        return False
                
                return True
                
        except Exception as e:
            raise LockError(f"Failed to acquire lock: {str(e)}")
    
    def wait_if_needed(self) -> None:
        """
        Rate limit aşılmışsa gerekli süre kadar bekler
        
        Raises:
            RateLimitExceeded: Rate limit aşılmış ve bekleme süresi çok uzunsa
            LockError: Lock edinme hatası
        """
        wait_time = 0
        
        try:
            with self.lock:
                current_time = time.time()
                
                # Bekleme süresi hesapla
                # Request reset kontrolü
                if self.request_reset_time > 0 and current_time < self.request_reset_time:
                    wait_time = max(wait_time, self.request_reset_time - current_time)
                
                # Token reset kontrolü
                if self.token_reset_time > 0 and current_time < self.token_reset_time:
                    wait_time = max(wait_time, self.token_reset_time - current_time)
                
                # Audio seconds reset kontrolü
                if self.audio_seconds_reset_time > 0 and current_time < self.audio_seconds_reset_time:
                    wait_time = max(wait_time, self.audio_seconds_reset_time - current_time)
                
                # Varsayılan bekleme süresi
                if wait_time == 0:
                    wait_time = 60
                
                # Çok uzun bekleme süreleri için hata fırlat
                if wait_time > 300:  # 5 dakikadan fazla
                    raise RateLimitExceeded(
                        f"Rate limit exceeded. Wait time: {wait_time} seconds",
                        "RATE_LIMIT_WAIT_TOO_LONG",
                        wait_time
                    )
                    
        except Exception as e:
            raise LockError(f"Failed to acquire lock: {str(e)}")
        
        # Lock dışında bekleme yap
        if wait_time > 0:
            time.sleep(wait_time)
            
            # Bekleme sonrası limitleri güncelle
            try:
                with self.lock:
                    current_time = time.time()
                    
                    if self.request_reset_time > 0 and current_time >= self.request_reset_time:
                        self.request_remaining = self.request_limit
                        self.request_reset_time = 0
                    
                    if self.token_reset_time > 0 and current_time >= self.token_reset_time:
                        self.token_remaining = self.token_limit
                        self.token_reset_time = 0
                        
                    if self.audio_seconds_reset_time > 0 and current_time >= self.audio_seconds_reset_time:
                        self.audio_seconds_remaining = self.audio_seconds_limit
                        self.audio_seconds_reset_time = 0
                        
            except Exception as e:
                raise LockError(f"Failed to acquire lock after wait: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Mevcut rate limit durumunu döndürür
        
        Returns:
            Rate limit durum bilgileri
            
        Raises:
            LockError: Lock edinme hatası
        """
        try:
            with self.lock:
                current_time = time.time()
                
                # Reset zamanlarını kontrol et ve güncelle
                if self.request_reset_time > 0 and current_time >= self.request_reset_time:
                    self.request_remaining = self.request_limit
                    self.request_reset_time = 0
                
                if self.token_reset_time > 0 and current_time >= self.token_reset_time:
                    self.token_remaining = self.token_limit
                    self.token_reset_time = 0
                
                if self.audio_seconds_reset_time > 0 and current_time >= self.audio_seconds_reset_time:
                    self.audio_seconds_remaining = self.audio_seconds_limit
                    self.audio_seconds_reset_time = 0
                
                return {
                    'request_limit': self.request_limit,
                    'request_remaining': self.request_remaining,
                    'request_reset_time': self.request_reset_time,
                    'token_limit': self.token_limit,
                    'token_remaining': self.token_remaining,
                    'token_reset_time': self.token_reset_time,
                    'audio_seconds_limit': self.audio_seconds_limit,
                    'audio_seconds_remaining': self.audio_seconds_remaining,
                    'audio_seconds_reset_time': self.audio_seconds_reset_time,
                    'last_update': self.last_update,
                    'current_time': current_time,
                    'has_rate_limit_info': self._has_rate_limit_info(),
                    'time_since_update': current_time - self.last_update if self.last_update > 0 else 0
                }
        except Exception as e:
            raise LockError(f"Failed to acquire lock: {str(e)}")
    
    def _has_rate_limit_info(self) -> bool:
        """
        API'den rate limit bilgisi alınıp alınmadığını kontrol eder
        
        Returns:
            True: Rate limit bilgisi mevcut, False: Henüz bilgi alınmamış
        """
        return (self.request_limit > 0 or self.token_limit > 0 or 
                self.last_update > 0)
    
    def needs_refresh(self) -> bool:
        """
        Rate limit bilgilerinin yenilenmesi gerekip gerekmediğini kontrol eder
        
        Returns:
            True: Yenileme gerekli, False: Mevcut bilgiler yeterli
        """
        # Eğer hiç rate limit bilgisi yoksa yenileme gerekli
        if not self._has_rate_limit_info():
            return True
            
        # Reset zamanları yaklaşıyorsa yenile
        current_time = time.time()
        
        # Request reset'i 30 saniye içindeyse yenile
        if (self.request_reset_time > 0 and 
            self.request_reset_time - current_time < 30):
            return True
            
        # Token reset'i 60 saniye içindeyse yenile
        if (self.token_reset_time > 0 and 
            self.token_reset_time - current_time < 60):
            return True
            
        # Son güncelleme 10 dakikadan eskiyse yenile
        if self.last_update > 0 and current_time - self.last_update > 600:
            return True
            
        return False
    
    def refresh_if_needed(self, api_callback=None) -> bool:
        """
        Gerekirse rate limit bilgilerini yeniler
        
        Args:
            api_callback: API çağrısı yapacak callback fonksiyon (opsiyonel)
            
        Returns:
            True: Yenileme yapıldı, False: Yenileme gerekli değildi
            
        Raises:
            ConfigurationError: API callback sağlanmamışsa
        """
        if not self.needs_refresh():
            return False
            
        # API callback sağlanmışsa yenileme yap
        if api_callback:
            try:
                # API çağrısı yap ve header'ları al
                response = api_callback()
                if response and 'headers' in response:
                    self.update_from_headers(response['headers'])
                    return True
            except Exception as e:
                # Yenileme başarısız olsa bile devam et
                print(f"⚠️ Rate limit yenileme başarısız: {e}")
                return False
        else:
            # API callback yoksa sadece reset zamanlarını kontrol et
            try:
                with self.lock:
                    current_time = time.time()
                    
                    # Reset zamanlarını kontrol et (remaining değerlerini değiştirme)
                    if self.request_reset_time > 0 and current_time >= self.request_reset_time:
                        # Reset zamanı geçmiş, sadece reset zamanını sıfırla
                        self.request_reset_time = 0
                    
                    if self.token_reset_time > 0 and current_time >= self.token_reset_time:
                        # Reset zamanı geçmiş, sadece reset zamanını sıfırla
                        self.token_reset_time = 0
                        
                    self.last_update = current_time
                    return True
                    
            except Exception as e:
                raise LockError(f"Failed to refresh rate limits: {str(e)}")
        
        return False
    
    def force_refresh(self, api_callback) -> bool:
        """
        Rate limit bilgilerini zorla yeniler
        
        Args:
            api_callback: API çağrısı yapacak callback fonksiyon
            
        Returns:
            True: Yenileme başarılı, False: Yenileme başarısız
            
        Raises:
            ConfigurationError: API callback sağlanmamışsa
        """
        if not api_callback:
            raise ConfigurationError("api_callback", "API callback function is required for force refresh")
            
        try:
            # API çağrısı yap ve header'ları al
            response = api_callback()
            if response and 'headers' in response:
                self.update_from_headers(response['headers'])
                return True
            else:
                return False
        except Exception as e:
            print(f"❌ Force refresh başarısız: {e}")
            return False
    
    def get_status_summary(self) -> Dict[str, Any]:
        """
        Rate limit durumunun özet bilgilerini döndürür
        
        Returns:
            Özet durum bilgileri
        """
        status = self.get_status()
        
        summary = {
            'has_info': status['has_rate_limit_info'],
            'needs_refresh': self.needs_refresh(),
            'can_make_requests': status['request_remaining'] > 0 if status['has_rate_limit_info'] else True,
            'can_use_tokens': status['token_remaining'] > 0 if status['has_rate_limit_info'] else True,
            'request_usage_percent': 0,
            'token_usage_percent': 0
        }
        
        # Kullanım yüzdelerini hesapla
        if status['request_limit'] > 0:
            summary['request_usage_percent'] = round(
                ((status['request_limit'] - status['request_remaining']) / status['request_limit']) * 100, 1
            )
            
        if status['token_limit'] > 0:
            summary['token_usage_percent'] = round(
                ((status['token_limit'] - status['token_remaining']) / status['token_limit']) * 100, 1
            )
            
        return summary
    
    def has_limits_changed(self, new_headers: dict) -> bool:
        """
        Yeni header'larla limitlerin değişip değişmediğini kontrol eder
        
        Args:
            new_headers: Yeni API response header'ları
            
        Returns:
            True: Limitler değişmiş, False: Limitler aynı
            
        Raises:
            ValidationError: Geçersiz header formatı
        """
        if not new_headers:
            return False
            
        try:
            # Mevcut limitlerle karşılaştır
            new_request_limit = int(new_headers.get('x-ratelimit-limit-requests', 0))
            new_token_limit = int(new_headers.get('x-ratelimit-limit-tokens', 0))
            
            return (new_request_limit != self.request_limit or 
                    new_token_limit != self.token_limit)
                    
        except (ValueError, TypeError) as e:
            raise ValidationError("new_headers", f"Invalid header values: {str(e)}")
    
    def reset(self) -> None:
        """
        Rate limit durumunu sıfırlar (test amaçlı)
        
        Raises:
            LockError: Lock edinme hatası
        """
        try:
            with self.lock:
                self.request_limit = 0
                self.request_remaining = 0
                self.request_reset_time = 0
                self.token_limit = 0
                self.token_remaining = 0
                self.token_reset_time = 0
                self.audio_seconds_limit = 0
                self.audio_seconds_remaining = 0
                self.audio_seconds_reset_time = 0
                self.last_update = 0
        except Exception as e:
            raise LockError(f"Failed to acquire lock: {str(e)}") 