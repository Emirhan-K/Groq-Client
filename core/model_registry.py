# Kullanılabilir modellerin tiplerini ve limitlerini dinamik olarak Groq API'sinden alır

import requests
import time
from typing import Dict, Optional, List
from exceptions.errors import (
    InvalidModel, ModelRegistryError, ValidationError, ConfigurationError
)


class ModelRegistry:
    """Groq modellerinin bilgilerini dinamik olarak API'den alan registry sınıfı"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.groq.com/openai/v1"):
        """
        ModelRegistry'yi başlatır
        
        Args:
            api_key: Groq API key (opsiyonel)
            base_url: API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self._models: Dict[str, Dict] = {}
        self._last_fetch = 0
        self._fetch_interval = 3600  # 1 saat cache
        
        # Eğer API key varsa hemen modelleri al
        if self.api_key:
            self._fetch_models()
    
    def _fetch_models(self) -> None:
        """
        Groq API'sinden model bilgilerini alır
        
        Raises:
            ConfigurationError: API key yoksa
        """
        if not self.api_key:
            return  # API key yoksa sessizce çık
        
        # Cache kontrolü
        current_time = time.time()
        if current_time - self._last_fetch < self._fetch_interval:
            return  # Cache hala geçerli
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.base_url}/models", headers=headers)
            
            if response.status_code == 200:
                models_data = response.json()
                
                # API response'unu parse et
                self._models.clear()
                for model in models_data.get("data", []):
                    model_id = model.get("id")
                    if model_id and model.get("active", False):
                        # Sadece STT ve chat modellerini al
                        model_type = self._determine_model_type(model_id)
                        if model_type in ["chat", "stt"]:
                            # Model bilgilerini kaydet
                            self._models[model_id] = {
                                "type": model_type,
                                "max_tokens": model.get("context_window"),
                                "max_completion_tokens": model.get("max_completion_tokens"),
                                "owned_by": model.get("owned_by", ""),
                                "created": model.get("created"),
                                "active": model.get("active", True)
                            }
                
                self._last_fetch = current_time
                
        except Exception as e:
            # Hata durumunda sessizce devam et
            print(f"⚠️ Model registry fetch error: {e}")
    
    def _determine_model_type(self, model_id: str) -> str:
        """
        Model ID'sine göre model tipini belirler
        
        Args:
            model_id: Model ID'si
            
        Returns:
            Model tipi ('chat' veya 'stt')
        """
        model_id_lower = model_id.lower()
        
        # STT modelleri
        if "whisper" in model_id_lower:
            return "stt"
        
        # Chat modelleri (varsayılan)
        return "chat"
    
    def refresh_models(self) -> None:
        """
        Model listesini zorla yeniler
        """
        self._last_fetch = 0  # Cache'i sıfırla
        self._fetch_models()
    
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
        """
        if not model or not isinstance(model, str):
            raise ValidationError("model", "Model name must be a non-empty string")
        
        # Modelleri güncelle (gerekirse)
        if self.api_key:
            self._fetch_models()
            
        if model not in self._models:
            raise InvalidModel(model, f"Model '{model}' not found in registry")
        
        return self._models[model].copy()
    
    def get_type(self, model: str) -> str:
        """
        Model tipini döndürür
        
        Args:
            model: Model adı
            
        Returns:
            Model tipi ('chat' veya 'stt')
            
        Raises:
            ValidationError: Geçersiz model adı
            InvalidModel: Model bulunamadığında
        """
        model_info = self.get_model_info(model)
        return model_info["type"]
    
    def list_models(self, model_type: Optional[str] = None) -> List[str]:
        """
        Kayıtlı modelleri listeler
        
        Args:
            model_type: Filtreleme için model tipi (opsiyonel)
            
        Returns:
            Model adları listesi
            
        Raises:
            ValidationError: Geçersiz model tipi
        """
        # Modelleri güncelle (gerekirse)
        if self.api_key:
            self._fetch_models()
        
        if model_type is not None:
            if model_type not in ["chat", "stt"]:
                raise ValidationError("model_type", "Model type must be 'chat' or 'stt'")
            
            return [
                model for model, info in self._models.items() 
                if info["type"] == model_type
            ]
        
        return list(self._models.keys())
    
    def is_model_supported(self, model: str) -> bool:
        """
        Model'in desteklenip desteklenmediğini kontrol eder
        
        Args:
            model: Model adı
            
        Returns:
            True: Model destekleniyor, False: Desteklenmiyor
            
        Raises:
            ValidationError: Geçersiz model adı
        """
        if not model or not isinstance(model, str):
            raise ValidationError("model", "Model name must be a non-empty string")
        
        # Modelleri güncelle (gerekirse)
        if self.api_key:
            self._fetch_models()
            
        return model in self._models
    
    def get_max_tokens(self, model: str) -> Optional[int]:
        """
        Model'in maksimum token sayısını döndürür
        
        Args:
            model: Model adı
            
        Returns:
            Maksimum token sayısı (None: STT modelleri için)
            
        Raises:
            ValidationError: Geçersiz model adı
            InvalidModel: Model bulunamadığında
        """
        model_info = self.get_model_info(model)
        return model_info.get("max_tokens")
    
    def get_max_completion_tokens(self, model: str) -> Optional[int]:
        """
        Model'in maksimum completion token sayısını döndürür
        
        Args:
            model: Model adı
            
        Returns:
            Maksimum completion token sayısı
            
        Raises:
            ValidationError: Geçersiz model adı
            InvalidModel: Model bulunamadığında
        """
        model_info = self.get_model_info(model)
        return model_info.get("max_completion_tokens")
    
    def get_context_length(self, model: str) -> Optional[int]:
        """
        Model'in context length'ini döndürür (max_tokens ile aynı)
        
        Args:
            model: Model adı
            
        Returns:
            Context length (None: STT modelleri için)
            
        Raises:
            ValidationError: Geçersiz model adı
            InvalidModel: Model bulunamadığında
        """
        return self.get_max_tokens(model)
    
    def get_cache_info(self) -> Dict[str, any]:
        """
        Cache bilgilerini döndürür
        
        Returns:
            Cache bilgileri
        """
        return {
            "last_fetch": self._last_fetch,
            "fetch_interval": self._fetch_interval,
            "models_count": len(self._models),
            "cache_age": time.time() - self._last_fetch if self._last_fetch > 0 else None,
            "has_api_key": bool(self.api_key)
        }
    
    def get_models_summary(self) -> Dict[str, any]:
        """
        Model listesinin özetini döndürür
        
        Returns:
            Model özeti
        """
        if self.api_key:
            self._fetch_models()
        
        chat_models = self.list_models("chat")
        stt_models = self.list_models("stt")
        
        return {
            "total_models": len(self._models),
            "chat_models": len(chat_models),
            "stt_models": len(stt_models),
            "chat_model_list": chat_models,
            "stt_model_list": stt_models,
            "cache_info": self.get_cache_info()
        } 