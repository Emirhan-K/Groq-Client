# Groq API ile HTTP üzerinden iletişim kurar

import requests
import json
from typing import Dict, Any, Optional, Union
from exceptions.errors import (
    GroqAPIError, NetworkError, AuthenticationError, RequestTimeoutError,
    ValidationError, ConfigurationError
)


class APIClient:
    """Groq API ile HTTP üzerinden iletişim kuran istemci sınıfı"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.groq.com"):
        """
        APIClient'i başlatır
        
        Args:
            api_key: Groq API anahtarı
            base_url: API base URL'i (varsayılan: https://api.groq.com)
            
        Raises:
            ConfigurationError: API key eksikse
        """
        if not api_key:
            raise ConfigurationError("api_key", "API key is required")
            
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'User-Agent': 'Groq-Dynamic-Client/1.0'
        })
    
    def post(self, endpoint: str, payload: dict, headers: dict = None) -> Dict[str, Any]:
        """
        POST isteği gönderir
        
        Args:
            endpoint: API endpoint'i (örn: /v1/chat/completions)
            payload: Gönderilecek veri
            headers: Ek header'lar (opsiyonel)
            
        Returns:
            API yanıtı
            
        Raises:
            ValidationError: Geçersiz endpoint veya payload
            NetworkError: Ağ bağlantısı hatası
            AuthenticationError: Kimlik doğrulama hatası
            RequestTimeoutError: Zaman aşımı hatası
            GroqAPIError: Diğer API hataları
        """
        if not endpoint:
            raise ValidationError("endpoint", "Endpoint is required")
            
        if not payload:
            raise ValidationError("payload", "Payload is required")
            
        url = f"{self.base_url}{endpoint}"
        
        # Ek header'ları ekle
        request_headers = self.session.headers.copy()
        request_headers['Content-Type'] = 'application/json'
        if headers:
            request_headers.update(headers)
        
        try:
            response = self.session.post(
                url=url,
                json=payload,
                headers=request_headers,
                timeout=30
            )
            
            return self.handle_response(response)
            
        except requests.exceptions.Timeout as e:
            raise RequestTimeoutError(30, f"Request timeout: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"HTTP request failed: {str(e)}")
    
    def post_multipart(self, endpoint: str, data: dict, files: dict, headers: dict = None) -> Dict[str, Any]:
        """
        Multipart/form-data POST isteği gönderir
        
        Args:
            endpoint: API endpoint'i (örn: /v1/audio/transcriptions)
            data: Form data
            files: Dosya verileri
            headers: Ek header'lar (opsiyonel)
            
        Returns:
            API yanıtı
            
        Raises:
            ValidationError: Geçersiz endpoint veya dosya
            NetworkError: Ağ bağlantısı hatası
            AuthenticationError: Kimlik doğrulama hatası
            RequestTimeoutError: Zaman aşımı hatası
            GroqAPIError: Diğer API hataları
        """
        if not endpoint:
            raise ValidationError("endpoint", "Endpoint is required")
            
        if not files:
            raise ValidationError("files", "Files are required for multipart request")
            
        url = f"{self.base_url}{endpoint}"
        
        # Authorization header'ını ekle (Content-Type multipart olacak)
        request_headers = {
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'Groq-Dynamic-Client/1.0'
        }
        # Content-Type kesinlikle eklenmemeli!
        if headers:
            # Content-Type varsa kaldır
            headers.pop('Content-Type', None)
            request_headers.update(headers)
        
        try:
            response = self.session.post(
                url=url,
                data=data,
                files=files,
                headers=request_headers,
                timeout=60  # Dosya yükleme için daha uzun timeout
            )
            
            return self.handle_response(response)
            
        except requests.exceptions.Timeout as e:
            raise RequestTimeoutError(60, f"Multipart request timeout: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"HTTP multipart request failed: {str(e)}")
    
    def post_stream(self, endpoint: str, payload: dict, headers: dict = None):
        """
        Streaming POST isteği gönderir
        
        Args:
            endpoint: API endpoint'i (örn: /v1/chat/completions)
            payload: Gönderilecek veri
            headers: Ek header'lar (opsiyonel)
            
        Yields:
            Streaming yanıt chunk'ları
            
        Raises:
            ValidationError: Geçersiz endpoint veya payload
            NetworkError: Ağ bağlantısı hatası
            AuthenticationError: Kimlik doğrulama hatası
            RequestTimeoutError: Zaman aşımı hatası
            GroqAPIError: Diğer API hataları
        """
        if not endpoint:
            raise ValidationError("endpoint", "Endpoint is required")
            
        if not payload:
            raise ValidationError("payload", "Payload is required")
            
        url = f"{self.base_url}{endpoint}"
        
        # Ek header'ları ekle
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        try:
            response = self.session.post(
                url=url,
                json=payload,
                headers=request_headers,
                timeout=30,
                stream=True  # Streaming için
            )
            
            # HTTP durum kodunu kontrol et
            if not response.ok:
                error_message = f"API request failed with status {response.status_code}"
                response_data = None
                
                try:
                    response_data = response.json()
                    if 'error' in response_data:
                        error_message = response_data['error'].get('message', error_message)
                except json.JSONDecodeError:
                    error_message += f": {response.text}"
                
                # Durum koduna göre özel exception'lar
                if response.status_code in [401, 403]:
                    raise AuthenticationError(error_message)
                elif response.status_code == 400:
                    raise ValidationError("request", error_message)
                else:
                    raise GroqAPIError(error_message, f"HTTP_{response.status_code}", response_data)
            
            # Streaming yanıtı işle
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    
                    # Server-Sent Events formatı: "data: {...}"
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # "data: " kısmını çıkar
                        
                        if data_str == '[DONE]':
                            break  # Stream sonu
                        
                        try:
                            chunk_data = json.loads(data_str)
                            yield chunk_data
                        except json.JSONDecodeError:
                            # JSON parse hatası - chunk'ı atla
                            continue
                            
        except requests.exceptions.Timeout as e:
            raise RequestTimeoutError(30, f"Streaming request timeout: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            pass  # Streaming desteği kullanılmıyor, hata durumunda hiçbir şey yapma
    
    def extract_headers(self, response: requests.Response) -> Dict[str, str]:
        """
        Response header'larından önemli bilgileri çıkarır
        
        Args:
            response: requests.Response objesi
            
        Returns:
            Önemli header bilgileri
        """
        headers = {}
        
        # Groq API'nin gerçek rate limit header'ları
        rate_limit_headers = [
            'x-ratelimit-limit-requests',
            'x-ratelimit-remaining-requests',
            'x-ratelimit-reset-requests',
            'x-ratelimit-limit-tokens',
            'x-ratelimit-remaining-tokens',
            'x-ratelimit-reset-tokens',
            'x-ratelimit-limit-audio-seconds',
            'x-ratelimit-remaining-audio-seconds',
            'x-ratelimit-reset-audio-seconds'
        ]
        
        for header_name in rate_limit_headers:
            if header_name in response.headers:
                headers[header_name] = response.headers[header_name]
        
        # Diğer önemli header'lar
        important_headers = [
            'x-request-id',
            'x-groq-region',
            'content-type',
            'content-length',
            'retry-after'
        ]
        
        for header_name in important_headers:
            if header_name in response.headers:
                headers[header_name] = response.headers[header_name]
        
        return headers
    
    def close(self):
        """HTTP session'ını kapatır"""
        self.session.close()
    
    def __enter__(self):
        """Context manager desteği"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager desteği"""
        self.close()

    def handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        API yanıtını işler
        
        Args:
            response: requests.Response objesi
        
        Returns:
            İşlenmiş yanıt verisi
        
        Raises:
            AuthenticationError: 401/403 hataları
            ValidationError: 400 hataları
            GroqAPIError: Diğer API hataları
        """
        # HTTP durum kodunu kontrol et
        if not response.ok:
            error_message = f"API request failed with status {response.status_code}"
            response_data = None
            try:
                response_data = response.json()
                if 'error' in response_data:
                    error_message = response_data['error'].get('message', error_message)
            except json.JSONDecodeError:
                error_message += f": {response.text}"
            # Durum koduna göre özel exception'lar
            if response.status_code in [401, 403]:
                raise AuthenticationError(error_message)
            elif response.status_code == 400:
                raise ValidationError("request", error_message)
            else:
                raise GroqAPIError(error_message, f"HTTP_{response.status_code}", response_data)
        # Yanıtı JSON olarak parse et
        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
            raise GroqAPIError(f"Invalid JSON response: {str(e)}", "INVALID_JSON")
        # Header bilgilerini ekle
        response_data['_headers'] = self.extract_headers(response)
        return response_data 