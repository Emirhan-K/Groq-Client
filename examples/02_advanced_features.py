#!/usr/bin/env python3
"""
Gelişmiş Özellikler Örnekleri
=============================

Bu dosya Groq Client'ın gelişmiş özelliklerini gösterir:
- Token counting
- Model registry
- Rate limiting
- Queue management
- Advanced text generation
"""

import os
import sys
import time
import asyncio
from typing import List, Dict, Any

# Proje kök dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.groq_client import GroqClient
from core.model_registry import ModelRegistry
from core.token_counter import TokenCounter
from core.rate_limit_handler import RateLimitHandler
from core.queue_manager import QueueManager
from handlers.text_generation import TextGenerationHandler
from handlers.speech_to_text import SpeechToTextHandler

def token_counting_examples():
    """Token counting örnekleri"""
    print("=" * 60)
    print("🔢 TOKEN COUNTING ÖRNEKLERİ")
    print("=" * 60)
    
    api_key = "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"
    client = GroqClient(api_key)
    
    try:
        # 1. Basit token sayımı
        print("\n1️⃣ Basit Token Sayımı:")
        text = "Merhaba dünya! Bu bir test metnidir."
        tokens = client.count_tokens(text, "llama3-8b-8192")
        print(f"Metin: '{text}'")
        print(f"Token sayısı: {tokens}")
        
        # 2. Uzun metin token sayımı
        print("\n2️⃣ Uzun Metin Token Sayımı:")
        long_text = """
        Python, Guido van Rossum tarafından 1991 yılında geliştirilen yüksek seviyeli, 
        genel amaçlı bir programlama dilidir. Python'un tasarım felsefesi, kodun 
        okunabilirliğini vurgular ve sözdizimi, programcıların daha az kod yazarak 
        kavramları ifade etmelerine olanak tanır. Python, nesne yönelimli, 
        yorumlanmış ve dinamik olarak yazılmış bir dildir.
        """
        tokens = client.count_tokens(long_text, "llama3-8b-8192")
        print(f"Uzun metin token sayısı: {tokens}")
        
        # 3. Mesaj token sayımı
        print("\n3️⃣ Mesaj Token Sayımı:")
        # Mesaj listesi yerine string kullan
        message_text = "Sen yardımcı bir AI'sın. Python nedir? Python, yüksek seviyeli bir programlama dilidir. Avantajları nelerdir?"
        
        message_tokens = client.count_tokens(message_text, "llama3-8b-8192")
        print(f"Mesaj metni token sayısı: {message_tokens}")
        
        # 4. Token limit kontrolü
        print("\n4️⃣ Token Limit Kontrolü:")
        model_info = client.get_model_info("llama3-8b-8192")
        max_tokens = model_info.get('max_tokens', 8192)
        
        print(f"Model: llama3-8b-8192")
        print(f"Maksimum token: {max_tokens}")
        print(f"Kullanılabilir token: {max_tokens - message_tokens}")
        
        # 5. Farklı modeller için token sayımı
        print("\n5️⃣ Farklı Modeller için Token Sayımı:")
        models = ["llama3-8b-8192"]  # Sadece çalışan model
        
        for model in models:
            try:
                tokens = client.count_tokens(text, model)
                print(f"{model}: {tokens} token")
            except Exception as e:
                print(f"{model}: Hata - {e}")
        
    except Exception as e:
        print(f"❌ Token Counting Hatası: {e}")
    finally:
        client.close()

def model_registry_examples():
    """Model registry örnekleri"""
    print("\n" + "=" * 60)
    print("📋 MODEL REGISTRY ÖRNEKLERİ")
    print("=" * 60)
    
    api_key = "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"
    client = GroqClient(api_key)
    
    try:
        # 1. Tüm modelleri listele
        print("\n1️⃣ Tüm Modeller:")
        all_models = client.get_available_models()
        print(f"Toplam model sayısı: {len(all_models)}")
        
        # 2. Chat modelleri
        print("\n2️⃣ Chat Modelleri:")
        chat_models = client.get_available_models("chat")
        print(f"Chat model sayısı: {len(chat_models)}")
        for model in chat_models[:5]:  # İlk 5 modeli göster
            print(f"  - {model}")
        
        # 3. STT modelleri
        print("\n3️⃣ STT Modelleri:")
        stt_models = client.get_available_models("stt")
        print(f"STT model sayısı: {len(stt_models)}")
        for model in stt_models:
            print(f"  - {model}")
        
        # 4. Model bilgileri
        print("\n4️⃣ Model Bilgileri:")
        for model_id in chat_models[:3]:  # İlk 3 chat modeli
            try:
                model_info = client.get_model_info(model_id)
                print(f"\n{model_id}:")
                print(f"  - Max Tokens: {model_info.get('max_tokens', 'N/A')}")
                print(f"  - Owner: {model_info.get('owner', 'N/A')}")
                print(f"  - Type: {model_info.get('type', 'N/A')}")
            except Exception as e:
                print(f"{model_id}: Hata - {e}")
        
        # 5. Model kategorileri
        print("\n5️⃣ Model Kategorileri:")
        categories = {}
        for model in all_models:
            try:
                info = client.get_model_info(model)
                category = info.get('type', 'unknown')
                if category not in categories:
                    categories[category] = []
                categories[category].append(model)
            except:
                pass
        
        for category, models in categories.items():
            print(f"{category}: {len(models)} model")
        
    except Exception as e:
        print(f"❌ Model Registry Hatası: {e}")
    finally:
        client.close()

def rate_limiting_examples():
    """Rate limiting örnekleri"""
    print("\n" + "=" * 60)
    print("⏱️ RATE LIMITING ÖRNEKLERİ")
    print("=" * 60)
    
    api_key = "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"
    client = GroqClient(api_key)
    
    try:
        # 1. Rate limit durumu
        print("\n1️⃣ Rate Limit Durumu:")
        status = client.get_rate_limit_status()
        print(f"Request Limit: {status['request_limit']}")
        print(f"Request Remaining: {status['request_remaining']}")
        print(f"Token Limit: {status['token_limit']}")
        print(f"Token Remaining: {status['token_remaining']}")
        print(f"Audio Seconds Limit: {status['audio_seconds_limit']}")
        print(f"Audio Seconds Remaining: {status['audio_seconds_remaining']}")
        
        # 2. Rate limit kontrolü
        print("\n2️⃣ Rate Limit Kontrolü:")
        can_proceed = client.rate_limit_handler.can_proceed(tokens=100, requests=1)
        print(f"100 token, 1 request için izin: {can_proceed}")
        
        # 3. Rate limit yenileme
        print("\n3️⃣ Rate Limit Yenileme:")
        needs_refresh = client.rate_limit_handler.needs_refresh()
        print(f"Yenileme gerekli: {needs_refresh}")
        
        # 4. Rate limit değişiklik tespiti
        print("\n4️⃣ Rate Limit Değişiklik Tespiti:")
        mock_headers = {
            'x-ratelimit-limit-requests': '200',
            'x-ratelimit-remaining-requests': '180',
            'x-ratelimit-reset-requests': str(int(time.time()) + 3600)
        }
        
        has_changed = client.rate_limit_handler.has_limits_changed(mock_headers)
        print(f"Limit değişikliği tespit edildi: {has_changed}")
        
        # 5. Rate limit özeti
        print("\n5️⃣ Rate Limit Özeti:")
        summary = client.rate_limit_handler.get_status_summary()
        print(f"Özet: {summary}")
        
    except Exception as e:
        print(f"❌ Rate Limiting Hatası: {e}")
    finally:
        client.close()

def queue_management_examples():
    """Queue management örnekleri"""
    print("\n" + "=" * 60)
    print("📋 QUEUE MANAGEMENT ÖRNEKLERİ")
    print("=" * 60)
    
    api_key = "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"
    
    try:
        # Queue manager'ı doğrudan kullan
        rate_handler = RateLimitHandler()
        queue_manager = QueueManager(rate_handler, max_queue_size=10)
        
        # 1. Queue durumu
        print("\n1️⃣ Queue Durumu:")
        status = queue_manager.get_queue_status()
        print(f"Toplam sıralanan: {status.get('total_queued', 0)}")
        print(f"Toplam işlenen: {status.get('total_processed', 0)}")
        print(f"Toplam başarısız: {status.get('total_failed', 0)}")
        print(f"Toplam yeniden deneme: {status.get('total_retries', 0)}")
        
        # 2. Queue kapasitesi
        print("\n2️⃣ Queue Kapasitesi:")
        print(f"Maksimum queue boyutu: {queue_manager.max_queue_size}")
        print(f"Şu anki queue boyutu: {queue_manager.get_queue_size()}")
        print(f"Queue dolu mu: {queue_manager.is_queue_full()}")
        
        # 3. Rate limit handler durumu
        print("\n3️⃣ Rate Limit Handler Durumu:")
        print(f"Rate limit handler aktif: {queue_manager.rate_limit_handler is not None}")
        
    except Exception as e:
        print(f"❌ Queue Management Hatası: {e}")

def advanced_text_generation():
    """Gelişmiş text generation örnekleri"""
    print("\n" + "=" * 60)
    print("🚀 GELİŞMİŞ TEXT GENERATION")
    print("=" * 60)
    
    api_key = "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"
    client = GroqClient(api_key)
    
    try:
        # 1. Function calling
        print("\n1️⃣ Function Calling:")
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Belirli bir şehir için hava durumu bilgisi alır",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "Şehir adı"
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
        
        response = client.text.generate(
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": "İstanbul'da hava nasıl?"}
            ],
            tools=tools,
            max_tokens=200
        )
        
        print("Function calling yanıtı:")
        print(response['choices'][0]['message'])
        
        # 2. JSON mode
        print("\n2️⃣ JSON Mode:")
        response = client.text.generate(
            model="llama3-8b-8192",
            prompt="Türkiye'nin 3 büyük şehrini JSON formatında listele:",
            response_format={"type": "json_object"},
            max_tokens=200
        )
        
        print("JSON mode yanıtı:")
        print(response['choices'][0]['message']['content'])
        
        # 3. Parallel requests
        print("\n3️⃣ Parallel Requests:")
        import concurrent.futures
        
        def make_request(prompt, model):
            try:
                response = client.text.generate(
                    model=model,
                    prompt=prompt,
                    max_tokens=100
                )
                return f"{model}: {response['choices'][0]['message']['content'][:50]}..."
            except Exception as e:
                return f"{model}: Hata - {e}"
        
        prompts = [
            "Python nedir?",
            "JavaScript nedir?",
            "Machine Learning nedir?"
        ]
        
        models = ["llama3-8b-8192"]  # Sadece çalışan model
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for prompt in prompts:
                for model in models:
                    future = executor.submit(make_request, prompt, model)
                    futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                print(result)
        
        # 4. Usage tracking
        print("\n4️⃣ Usage Tracking:")
        response = client.text.generate(
            model="llama3-8b-8192",
            prompt="Kısa bir hikaye anlat:",
            max_tokens=150
        )
        
        usage = response['usage']
        print(f"Prompt tokens: {usage['prompt_tokens']}")
        print(f"Completion tokens: {usage['completion_tokens']}")
        print(f"Total tokens: {usage['total_tokens']}")
        
        # 5. Error handling with retries
        print("\n5️⃣ Error Handling with Retries:")
        
        def retry_request(max_retries=3):
            for attempt in range(max_retries):
                try:
                    response = client.text.generate(
                        model="llama3-8b-8192",
                        prompt="Test mesajı",
                        max_tokens=50
                    )
                    print(f"✅ Başarılı (deneme {attempt + 1})")
                    return response
                except Exception as e:
                    print(f"❌ Deneme {attempt + 1} başarısız: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(1)  # 1 saniye bekle
                    else:
                        print("Maksimum deneme sayısına ulaşıldı")
                        raise
        
        try:
            retry_request()
        except Exception as e:
            print(f"Retry başarısız: {e}")
        
    except Exception as e:
        print(f"❌ Advanced Text Generation Hatası: {e}")
    finally:
        client.close()

def main():
    """Ana fonksiyon"""
    print("🚀 GROQ CLIENT - GELİŞMİŞ ÖZELLİKLER ÖRNEKLERİ")
    print("=" * 60)
    
    # Gelişmiş örnekler
    token_counting_examples()
    model_registry_examples()
    rate_limiting_examples()
    queue_management_examples()
    advanced_text_generation()
    
    print("\n" + "=" * 60)
    print("✅ GELİŞMİŞ ÖZELLİKLER ÖRNEKLERİ TAMAMLANDI")
    print("=" * 60)

if __name__ == "__main__":
    main() 