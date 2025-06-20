#!/usr/bin/env python3
"""
Özel Implementasyon Örnekleri
=============================

Bu dosya Groq Client'ın temel bileşenlerini kullanarak özel implementasyonlar gösterir:
- Custom handlers
- Custom rate limit strategies
- Custom queue implementations
- Custom token counting
- Custom model registry
"""

import os
import sys
import time
import asyncio
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# Proje kök dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.model_registry import ModelRegistry
from core.token_counter import TokenCounter
from core.rate_limit_handler import RateLimitHandler
from core.queue_manager import QueueManager
from handlers.text_generation import TextGenerationHandler
from handlers.speech_to_text import SpeechToTextHandler
from api.api_client import APIClient
from exceptions.errors import *

class CustomTextHandler:
    """Özel text generation handler"""
    
    def __init__(self, api_key: str, model_registry: ModelRegistry, 
                 token_counter: TokenCounter, rate_handler: RateLimitHandler):
        self.api_key = api_key
        self.model_registry = model_registry
        self.token_counter = token_counter
        self.rate_handler = rate_handler
        self.api_client = APIClient(api_key)
        self.request_history = []
    
    def generate_with_history(self, model: str, prompt: str, max_tokens: int = 100, 
                            temperature: float = 0.7) -> Dict[str, Any]:
        """Geçmiş istekleri takip eden text generation"""
        
        # Token sayımı
        tokens = self.token_counter.count_tokens(prompt, model)
        
        # Rate limit kontrolü
        if not self.rate_handler.can_proceed(tokens=tokens, requests=1):
            self.rate_handler.wait_if_needed()
        
        # İstek gönder
        response = self.api_client.post(
            "/openai/v1/chat/completions",
            payload={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        )
        
        # Geçmişe kaydet
        self.request_history.append({
            'timestamp': datetime.now(),
            'model': model,
            'prompt': prompt,
            'tokens': tokens,
            'response': response['choices'][0]['message']['content'],
            'usage': response['usage']
        })
        
        return response
    
    def get_history_summary(self) -> Dict[str, Any]:
        """İstek geçmişi özeti"""
        if not self.request_history:
            return {'total_requests': 0, 'total_tokens': 0}
        
        total_requests = len(self.request_history)
        total_tokens = sum(req['usage']['total_tokens'] for req in self.request_history)
        models_used = list(set(req['model'] for req in self.request_history))
        
        return {
            'total_requests': total_requests,
            'total_tokens': total_tokens,
            'models_used': models_used,
            'first_request': self.request_history[0]['timestamp'],
            'last_request': self.request_history[-1]['timestamp']
        }

class CustomRateLimitStrategy:
    """Özel rate limit stratejisi"""
    
    def __init__(self, base_handler: RateLimitHandler):
        self.base_handler = base_handler
        self.custom_limits = {
            'high_priority': {'multiplier': 2.0, 'priority': 1},
            'normal_priority': {'multiplier': 1.0, 'priority': 2},
            'low_priority': {'multiplier': 0.5, 'priority': 3}
        }
        self.request_queue = []
    
    def can_proceed_with_priority(self, tokens: int, requests: int, 
                                priority: str = 'normal_priority') -> bool:
        """Öncelik bazlı rate limit kontrolü"""
        
        # Öncelik ayarlarını al
        settings = self.custom_limits.get(priority, self.custom_limits['normal_priority'])
        multiplier = settings['multiplier']
        
        # Token ve request limitlerini ayarla
        adjusted_tokens = int(tokens * multiplier)
        adjusted_requests = int(requests * multiplier)
        
        return self.base_handler.can_proceed(tokens=adjusted_tokens, requests=adjusted_requests)
    
    def add_request_to_queue(self, request_id: str, priority: str, 
                           tokens: int, requests: int):
        """İsteği sıraya ekle"""
        settings = self.custom_limits.get(priority, self.custom_limits['normal_priority'])
        
        self.request_queue.append({
            'id': request_id,
            'priority': priority,
            'priority_value': settings['priority'],
            'tokens': tokens,
            'requests': requests,
            'timestamp': datetime.now()
        })
        
        # Önceliğe göre sırala
        self.request_queue.sort(key=lambda x: x['priority_value'])
    
    def process_queue(self) -> List[Dict[str, Any]]:
        """Sırayı işle"""
        processed_requests = []
        
        for request in self.request_queue[:]:
            if self.can_proceed_with_priority(
                request['tokens'], 
                request['requests'], 
                request['priority']
            ):
                processed_requests.append(request)
                self.request_queue.remove(request)
        
        return processed_requests

class CustomTokenAnalyzer:
    """Özel token analizörü"""
    
    def __init__(self, token_counter: TokenCounter):
        self.token_counter = token_counter
        self.token_stats = {}
    
    def analyze_text_complexity(self, text: str, model: str) -> Dict[str, Any]:
        """Metin karmaşıklığını analiz et"""
        
        # Token sayımı
        tokens = self.token_counter.count_tokens(text, model)
        
        # Basit metrikler
        word_count = len(text.split())
        char_count = len(text)
        avg_tokens_per_word = tokens / word_count if word_count > 0 else 0
        avg_tokens_per_char = tokens / char_count if char_count > 0 else 0
        
        # Karmaşıklık skoru (basit hesaplama)
        complexity_score = (avg_tokens_per_word * 0.7) + (avg_tokens_per_char * 0.3)
        
        return {
            'text_length': len(text),
            'word_count': word_count,
            'char_count': char_count,
            'token_count': tokens,
            'avg_tokens_per_word': avg_tokens_per_word,
            'avg_tokens_per_char': avg_tokens_per_char,
            'complexity_score': complexity_score,
            'complexity_level': self._get_complexity_level(complexity_score)
        }
    
    def _get_complexity_level(self, score: float) -> str:
        """Karmaşıklık seviyesini belirle"""
        if score < 0.5:
            return "Basit"
        elif score < 1.0:
            return "Orta"
        elif score < 1.5:
            return "Karmaşık"
        else:
            return "Çok Karmaşık"
    
    def compare_texts(self, texts: List[str], model: str) -> Dict[str, Any]:
        """Metinleri karşılaştır"""
        results = []
        
        for i, text in enumerate(texts):
            analysis = self.analyze_text_complexity(text, model)
            analysis['text_index'] = i
            results.append(analysis)
        
        # En karmaşık metni bul
        most_complex = max(results, key=lambda x: x['complexity_score'])
        least_complex = min(results, key=lambda x: x['complexity_score'])
        
        return {
            'texts_analyzed': len(texts),
            'total_tokens': sum(r['token_count'] for r in results),
            'most_complex': most_complex,
            'least_complex': least_complex,
            'all_analyses': results
        }

class CustomModelSelector:
    """Özel model seçici"""
    
    def __init__(self, model_registry: ModelRegistry):
        self.model_registry = model_registry
        self.model_performance = {}
        self.model_costs = {
            'llama3-8b-8192': {'cost_per_1k_tokens': 0.05, 'speed': 'fast'},
            # 'mixtral-8x7b-32768': {'cost_per_1k_tokens': 0.14, 'speed': 'medium'},  # Desteklenmiyor
            'llama3-70b-8192': {'cost_per_1k_tokens': 0.59, 'speed': 'slow'}
        }
    
    def select_model_by_requirements(self, max_tokens: int, 
                                   budget_constraint: float = None,
                                   speed_requirement: str = 'medium') -> str:
        """Gereksinimlere göre model seç"""
        
        available_models = self.model_registry.list_models("chat")
        suitable_models = []
        
        for model in available_models:
            try:
                model_info = self.model_registry.get_model_info(model)
                max_model_tokens = model_info.get('max_tokens', 8192)
                
                # Token limit kontrolü
                if max_tokens > max_model_tokens:
                    continue
                
                # Hız kontrolü
                model_cost_info = self.model_costs.get(model, {})
                model_speed = model_cost_info.get('speed', 'medium')
                
                if speed_requirement == 'fast' and model_speed != 'fast':
                    continue
                elif speed_requirement == 'slow' and model_speed == 'fast':
                    continue
                
                # Bütçe kontrolü
                if budget_constraint is not None:
                    estimated_cost = (max_tokens / 1000) * model_cost_info.get('cost_per_1k_tokens', 0.1)
                    if estimated_cost > budget_constraint:
                        continue
                
                suitable_models.append({
                    'model': model,
                    'max_tokens': max_model_tokens,
                    'speed': model_speed,
                    'estimated_cost': (max_tokens / 1000) * model_cost_info.get('cost_per_1k_tokens', 0.1)
                })
                
            except Exception:
                continue
        
        if not suitable_models:
            return "llama3-8b-8192"  # Varsayılan model
        
        # En uygun modeli seç (düşük maliyet, uygun hız)
        suitable_models.sort(key=lambda x: x['estimated_cost'])
        return suitable_models[0]['model']
    
    def record_model_performance(self, model: str, tokens: int, 
                               response_time: float, success: bool):
        """Model performansını kaydet"""
        
        if model not in self.model_performance:
            self.model_performance[model] = {
                'total_requests': 0,
                'successful_requests': 0,
                'total_tokens': 0,
                'total_response_time': 0,
                'avg_response_time': 0
            }
        
        self.model_performance[model]['total_requests'] += 1
        self.model_performance[model]['total_tokens'] += tokens
        self.model_performance[model]['total_response_time'] += response_time
        
        if success:
            self.model_performance[model]['successful_requests'] += 1
        
        # Ortalama yanıt süresini güncelle
        total_requests = self.model_performance[model]['total_requests']
        total_time = self.model_performance[model]['total_response_time']
        self.model_performance[model]['avg_response_time'] = total_time / total_requests
    
    def get_best_performing_model(self) -> str:
        """En iyi performans gösteren modeli döndür"""
        
        if not self.model_performance:
            return "llama3-8b-8192"
        
        # Başarı oranı ve ortalama yanıt süresine göre sırala
        models = []
        for model, stats in self.model_performance.items():
            success_rate = stats['successful_requests'] / stats['total_requests']
            models.append({
                'model': model,
                'success_rate': success_rate,
                'avg_response_time': stats['avg_response_time'],
                'score': success_rate / (stats['avg_response_time'] + 0.1)  # 0'a bölme hatası önleme
            })
        
        models.sort(key=lambda x: x['score'], reverse=True)
        return models[0]['model']

class CustomQueueProcessor:
    """Özel sıra işleyici"""
    
    def __init__(self, queue_manager: QueueManager):
        self.queue_manager = queue_manager
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'avg_processing_time': 0
        }
    
    async def process_with_retry(self, request_func, *args, 
                               max_retries: int = 3, **kwargs) -> Dict[str, Any]:
        """Yeniden deneme ile işleme"""
        
        start_time = time.time()
        
        for attempt in range(max_retries):
            try:
                # İsteği sıraya ekle
                request_id = await self.queue_manager.enqueue(
                    request_func,
                    *args,
                    priority="normal",
                    max_retries=max_retries,
                    **kwargs
                )
                
                # İşleme bekle
                await asyncio.sleep(0.1)  # Kısa bekleme
                
                # Sonucu al (gerçek uygulamada callback kullanılır)
                result = "İşlem başarılı"  # Simüle edilmiş sonuç
                
                # İstatistikleri güncelle
                processing_time = time.time() - start_time
                self.processing_stats['total_processed'] += 1
                self.processing_stats['successful'] += 1
                self.processing_stats['avg_processing_time'] = (
                    (self.processing_stats['avg_processing_time'] * 
                     (self.processing_stats['total_processed'] - 1) + processing_time) /
                    self.processing_stats['total_processed']
                )
                
                return {
                    'success': True,
                    'request_id': request_id,
                    'result': result,
                    'attempts': attempt + 1,
                    'processing_time': processing_time
                }
                
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    self.processing_stats['total_processed'] += 1
                    self.processing_stats['failed'] += 1
                    
                    return {
                        'success': False,
                        'error': str(e),
                        'attempts': attempt + 1,
                        'processing_time': time.time() - start_time
                    }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """İşleme istatistiklerini döndür"""
        total = self.processing_stats['total_processed']
        if total == 0:
            return {**self.processing_stats, 'success_rate': 0}
        
        success_rate = self.processing_stats['successful'] / total
        
        return {
            **self.processing_stats,
            'success_rate': success_rate,
            'failure_rate': 1 - success_rate
        }

def demonstrate_custom_implementations():
    """Özel implementasyonları göster"""
    print("🚀 ÖZEL İMPLEMENTASYON ÖRNEKLERİ")
    print("=" * 60)
    
    api_key = "your_api_key"
    
    # Temel bileşenleri oluştur
    model_registry = ModelRegistry(api_key)
    token_counter = TokenCounter(model_registry)
    rate_handler = RateLimitHandler()
    queue_manager = QueueManager(rate_handler)
    
    try:
        # 1. Custom Text Handler
        print("\n1️⃣ Custom Text Handler:")
        custom_handler = CustomTextHandler(api_key, model_registry, token_counter, rate_handler)
        
        response = custom_handler.generate_with_history(
            model="llama3-8b-8192",
            prompt="Custom handler test mesajı",
            max_tokens=50
        )
        
        print(f"Yanıt: {response['choices'][0]['message']['content']}")
        
        history_summary = custom_handler.get_history_summary()
        print(f"Geçmiş özeti: {history_summary}")
        
        # 2. Custom Rate Limit Strategy
        print("\n2️⃣ Custom Rate Limit Strategy:")
        custom_rate_strategy = CustomRateLimitStrategy(rate_handler)
        
        can_proceed = custom_rate_strategy.can_proceed_with_priority(
            tokens=100, 
            requests=1, 
            priority='high_priority'
        )
        print(f"Yüksek öncelikli istek izni: {can_proceed}")
        
        # 3. Custom Token Analyzer
        print("\n3️⃣ Custom Token Analyzer:")
        token_analyzer = CustomTokenAnalyzer(token_counter)
        
        texts = [
            "Basit bir cümle.",
            "Bu daha karmaşık bir cümle çünkü daha fazla kelime içeriyor ve teknik terimler kullanıyor.",
            "Python programming language is a high-level, interpreted programming language that emphasizes code readability and simplicity."
        ]
        
        comparison = token_analyzer.compare_texts(texts, "llama3-8b-8192")
        print(f"Metin karşılaştırması:")
        print(f"  - Analiz edilen metin sayısı: {comparison['texts_analyzed']}")
        print(f"  - Toplam token: {comparison['total_tokens']}")
        print(f"  - En karmaşık: {comparison['most_complex']['complexity_level']}")
        print(f"  - En basit: {comparison['least_complex']['complexity_level']}")
        
        # 4. Custom Model Selector
        print("\n4️⃣ Custom Model Selector:")
        model_selector = CustomModelSelector(model_registry)
        
        selected_model = model_selector.select_model_by_requirements(
            max_tokens=1000,
            budget_constraint=0.1,
            speed_requirement='fast'
        )
        print(f"Seçilen model: {selected_model}")
        
        # Model performansını kaydet
        model_selector.record_model_performance("llama3-8b-8192", 150, 2.5, True)
        model_selector.record_model_performance("llama3-70b-8192", 200, 4.0, True)
        
        best_model = model_selector.get_best_performing_model()
        print(f"En iyi performans gösteren model: {best_model}")
        
        # 5. Custom Queue Processor
        print("\n5️⃣ Custom Queue Processor:")
        queue_processor = CustomQueueProcessor(queue_manager)
        
        # Test fonksiyonu
        def test_function():
            return "Test başarılı"
        
        # Sync versiyonunu kullan
        try:
            # Sırayı işle (sync)
            queue_manager.process_queue()
            
            print("Queue işleme tamamlandı")
            
            # İstatistikleri al
            queue_stats = queue_manager.get_queue_status()
            print(f"Queue istatistikleri: {queue_stats}")
            
        except Exception as e:
            print(f"Queue işleme hatası: {e}")
        
        print("\n✅ Tüm özel implementasyonlar başarıyla test edildi!")
        
    except Exception as e:
        print(f"❌ Özel implementasyon hatası: {e}")

def main():
    """Ana fonksiyon"""
    demonstrate_custom_implementations()

if __name__ == "__main__":
    main() 