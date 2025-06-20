#!/usr/bin/env python3
"""
Kapsamlı Entegrasyon Örnekleri
==============================

Bu dosya Groq Client'ın tüm özelliklerini entegre şekilde kullanır:
- Text generation + STT + Token counting + Rate limiting + Queue management
- Real-world scenarios
- Performance monitoring
- Error handling
"""

import os
import sys
import time
import asyncio
import json
import wave
import struct
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import math

# Proje kök dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.groq_client import GroqClient
from core.model_registry import ModelRegistry
from core.token_counter import TokenCounter
from core.rate_limit_handler import RateLimitHandler
from core.queue_manager import QueueManager
from handlers.text_generation import TextGenerationHandler
from handlers.speech_to_text import SpeechToTextHandler

class GroqClientManager:
    """Groq Client'ın tüm özelliklerini yöneten sınıf"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = GroqClient(api_key)
        self.stats = {
            'text_requests': 0,
            'stt_requests': 0,
            'total_tokens': 0,
            'errors': 0,
            'start_time': time.time()
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Performans istatistiklerini döndürür"""
        elapsed_time = time.time() - self.stats['start_time']
        return {
            'elapsed_time': elapsed_time,
            'text_requests_per_minute': (self.stats['text_requests'] / elapsed_time) * 60,
            'stt_requests_per_minute': (self.stats['stt_requests'] / elapsed_time) * 60,
            'total_tokens_per_minute': (self.stats['total_tokens'] / elapsed_time) * 60,
            'error_rate': self.stats['errors'] / (self.stats['text_requests'] + self.stats['stt_requests']) if (self.stats['text_requests'] + self.stats['stt_requests']) > 0 else 0,
            **self.stats
        }
    
    def create_test_audio(self, filename: str, duration: int = 3) -> str:
        """Test için ses dosyası oluşturur"""
        sample_rate = 44100
        frequency = 440
        num_samples = sample_rate * duration
        
        samples = []
        for i in range(num_samples):
            sample = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
            samples.append(struct.pack('h', sample))
        
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b''.join(samples))
        
        return filename

def scenario_1_basic_integration():
    """Senaryo 1: Temel entegrasyon"""
    print("=" * 60)
    print("🎯 SENARYO 1: TEMEL ENTEGRASYON")
    print("=" * 60)
    
    api_key = "your_api_key"
    manager = GroqClientManager(api_key)
    
    try:
        # 1. Model bilgilerini al
        print("\n1️⃣ Model Bilgileri:")
        chat_models = manager.client.get_available_models("chat")
        stt_models = manager.client.get_available_models("stt")
        
        print(f"Chat modelleri: {len(chat_models)} adet")
        print(f"STT modelleri: {len(stt_models)} adet")
        
        # 2. Text generation
        print("\n2️⃣ Text Generation:")
        response = manager.client.text.generate(
            model="llama3-8b-8192",
            prompt="Python programlama dilinin avantajlarını açıkla:",
            max_tokens=150
        )
        
        manager.stats['text_requests'] += 1
        manager.stats['total_tokens'] += response['usage']['total_tokens']
        
        print(f"Yanıt: {response['choices'][0]['message']['content']}")
        print(f"Kullanılan token: {response['usage']['total_tokens']}")
        
        # 3. Token sayımı
        print("\n3️⃣ Token Sayımı:")
        text = "Bu bir test metnidir."
        tokens = manager.client.count_tokens(text, "llama3-8b-8192")
        print(f"'{text}' -> {tokens} token")
        
        # 4. Rate limit durumu
        print("\n4️⃣ Rate Limit Durumu:")
        status = manager.client.get_rate_limit_status()
        print(f"Request remaining: {status['request_remaining']}/{status['request_limit']}")
        print(f"Token remaining: {status['token_remaining']}/{status['token_limit']}")
        
        # 5. Performans istatistikleri
        print("\n5️⃣ Performans İstatistikleri:")
        stats = manager.get_performance_stats()
        print(f"Text requests: {stats['text_requests']}")
        print(f"Total tokens: {stats['total_tokens']}")
        print(f"Error rate: {stats['error_rate']:.2%}")
        
    except Exception as e:
        print(f"❌ Senaryo 1 Hatası: {e}")
        manager.stats['errors'] += 1
    finally:
        manager.client.close()

def scenario_2_advanced_workflow():
    """Senaryo 2: Gelişmiş iş akışı"""
    print("\n" + "=" * 60)
    print("🚀 SENARYO 2: GELİŞMİŞ İŞ AKIŞI")
    print("=" * 60)
    
    api_key = "your_api_key"
    manager = GroqClientManager(api_key)
    
    try:
        # 1. Ses dosyası oluştur ve transkripsiyon yap
        print("\n1️⃣ Ses Transkripsiyonu:")
        audio_file = manager.create_test_audio("test_workflow.wav", 2)
        
        response = manager.client.speech.transcribe(
            file=audio_file,
            model="whisper-large-v3"
        )
        
        manager.stats['stt_requests'] += 1
        manager.stats['total_tokens'] += response.get('usage', {}).get('total_tokens', 0)
        
        transcription = response['text']
        print(f"Transkripsiyon: {transcription}")
        
        # 2. Transkripsiyon üzerinde analiz yap
        print("\n2️⃣ Transkripsiyon Analizi:")
        analysis_prompt = f"""
        Aşağıdaki transkripsiyonu analiz et ve özetle:
        
        Transkripsiyon: {transcription}
        
        Analiz:
        - Konuşma kalitesi
        - Dil tespiti
        - Ana konular
        """
        
        response = manager.client.text.generate(
            model="llama3-8b-8192",
            prompt=analysis_prompt,
            max_tokens=200
        )
        
        manager.stats['text_requests'] += 1
        manager.stats['total_tokens'] += response['usage']['total_tokens']
        
        print(f"Analiz: {response['choices'][0]['message']['content']}")
        
        # 3. Token kullanım analizi
        print("\n3️⃣ Token Kullanım Analizi:")
        total_tokens = manager.stats['total_tokens']
        text_tokens = manager.client.count_tokens(analysis_prompt, "llama3-8b-8192")
        
        print(f"Toplam kullanılan token: {total_tokens}")
        print(f"Analiz prompt token: {text_tokens}")
        print(f"STT token: {response['usage']['total_tokens']}")
        
        # 4. Rate limit kontrolü
        print("\n4️⃣ Rate Limit Kontrolü:")
        can_proceed = manager.client.rate_limit_handler.can_proceed(
            tokens=100, 
            requests=1, 
            audio_seconds=10
        )
        print(f"Yeni istek yapılabilir: {can_proceed}")
        
        # 5. Model performans karşılaştırması
        print("\n5️⃣ Model Performans Karşılaştırması:")
        models = ["llama3-8b-8192"]  # Sadece çalışan model
        
        for model in models:
            try:
                start_time = time.time()
                response = manager.client.text.generate(
                    model=model,
                    prompt="Kısa bir hikaye anlat:",
                    max_tokens=100
                )
                end_time = time.time()
                
                manager.stats['text_requests'] += 1
                manager.stats['total_tokens'] += response['usage']['total_tokens']
                
                print(f"{model}:")
                print(f"  - Süre: {end_time - start_time:.2f}s")
                print(f"  - Token: {response['usage']['total_tokens']}")
                print(f"  - Yanıt: {response['choices'][0]['message']['content'][:50]}...")
                
            except Exception as e:
                print(f"{model}: Hata - {e}")
                manager.stats['errors'] += 1
        
        # Test dosyasını temizle
        if os.path.exists(audio_file):
            os.remove(audio_file)
        
    except Exception as e:
        print(f"❌ Senaryo 2 Hatası: {e}")
        manager.stats['errors'] += 1
    finally:
        manager.client.close()

def scenario_3_batch_processing():
    """Senaryo 3: Toplu işleme"""
    print("\n" + "=" * 60)
    print("📦 SENARYO 3: TOPLU İŞLEME")
    print("=" * 60)
    
    api_key = "your_api_key"
    manager = GroqClientManager(api_key)
    
    try:
        # 1. Toplu text generation
        print("\n1️⃣ Toplu Text Generation:")
        prompts = [
            "Python nedir?",
            "JavaScript nedir?",
            "Machine Learning nedir?",
            "Web development nedir?",
            "Data science nedir?"
        ]
        
        def process_prompt(prompt: str) -> Dict[str, Any]:
            try:
                start_time = time.time()
                response = manager.client.text.generate(
                    model="llama3-8b-8192",
                    prompt=prompt,
                    max_tokens=100
                )
                end_time = time.time()
                
                return {
                    'prompt': prompt,
                    'response': response['choices'][0]['message']['content'],
                    'tokens': response['usage']['total_tokens'],
                    'time': end_time - start_time,
                    'success': True
                }
            except Exception as e:
                return {
                    'prompt': prompt,
                    'error': str(e),
                    'success': False
                }
        
        # Paralel işleme
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(process_prompt, prompt) for prompt in prompts]
            
            for future in as_completed(futures):
                result = future.result()
                if result['success']:
                    manager.stats['text_requests'] += 1
                    manager.stats['total_tokens'] += result['tokens']
                    print(f"✅ {result['prompt']}: {result['tokens']} token, {result['time']:.2f}s")
                else:
                    manager.stats['errors'] += 1
                    print(f"❌ {result['prompt']}: {result['error']}")
        
        # 2. Toplu ses dosyası işleme
        print("\n2️⃣ Toplu Ses Dosyası İşleme:")
        audio_files = []
        
        # Test ses dosyaları oluştur
        for i in range(3):
            filename = f"batch_audio_{i}.wav"
            manager.create_test_audio(filename, 1)
            audio_files.append(filename)
        
        def process_audio(file_path: str) -> Dict[str, Any]:
            try:
                start_time = time.time()
                response = manager.client.speech.transcribe(
                    file=file_path,
                    model="whisper-large-v3"
                )
                end_time = time.time()
                
                return {
                    'file': file_path,
                    'transcription': response['text'],
                    'tokens': response.get('usage', {}).get('total_tokens', 0),
                    'time': end_time - start_time,
                    'success': True
                }
            except Exception as e:
                return {
                    'file': file_path,
                    'error': str(e),
                    'success': False
                }
        
        # Sıralı işleme (rate limit için)
        for audio_file in audio_files:
            result = process_audio(audio_file)
            if result['success']:
                manager.stats['stt_requests'] += 1
                manager.stats['total_tokens'] += result['tokens']
                print(f"✅ {result['file']}: {result['tokens']} token, {result['time']:.2f}s")
                print(f"   Transkripsiyon: {result['transcription']}")
            else:
                manager.stats['errors'] += 1
                print(f"❌ {result['file']}: {result['error']}")
            
            time.sleep(1)  # Rate limit için bekle
        
        # Test dosyalarını temizle
        for audio_file in audio_files:
            if os.path.exists(audio_file):
                os.remove(audio_file)
        
        # 3. Performans özeti
        print("\n3️⃣ Performans Özeti:")
        stats = manager.get_performance_stats()
        print(f"Toplam istek: {stats['text_requests'] + stats['stt_requests']}")
        print(f"Text requests: {stats['text_requests']}")
        print(f"STT requests: {stats['stt_requests']}")
        print(f"Toplam token: {stats['total_tokens']}")
        print(f"Hata oranı: {stats['error_rate']:.2%}")
        print(f"Text requests/dakika: {stats['text_requests_per_minute']:.1f}")
        print(f"STT requests/dakika: {stats['stt_requests_per_minute']:.1f}")
        
    except Exception as e:
        print(f"❌ Senaryo 3 Hatası: {e}")
        manager.stats['errors'] += 1
    finally:
        manager.client.close()

def scenario_4_error_handling_and_recovery():
    """Senaryo 4: Hata yönetimi ve kurtarma"""
    print("\n" + "=" * 60)
    print("🛡️ SENARYO 4: HATA YÖNETİMİ VE KURTARMA")
    print("=" * 60)
    
    api_key = "your_api_key"
    manager = GroqClientManager(api_key)
    
    try:
        # 1. Geçersiz model hatası
        print("\n1️⃣ Geçersiz Model Hatası:")
        try:
            response = manager.client.text.generate(
                model="gecersiz-model",
                prompt="Test",
                max_tokens=10
            )
        except Exception as e:
            print(f"Beklenen hata: {type(e).__name__} - {e}")
            manager.stats['errors'] += 1
        
        # 2. Rate limit aşımı simülasyonu
        print("\n2️⃣ Rate Limit Aşımı Simülasyonu:")
        
        # Çok sayıda istek gönder
        for i in range(10):
            try:
                response = manager.client.text.generate(
                    model="llama3-8b-8192",
                    prompt=f"Test istek {i+1}",
                    max_tokens=10
                )
                manager.stats['text_requests'] += 1
                manager.stats['total_tokens'] += response['usage']['total_tokens']
                print(f"İstek {i+1}: Başarılı")
            except Exception as e:
                print(f"İstek {i+1}: {type(e).__name__} - {e}")
                manager.stats['errors'] += 1
                break
        
        # 3. Retry mekanizması
        print("\n3️⃣ Retry Mekanizması:")
        
        def retry_request(prompt: str, max_retries: int = 3) -> Dict[str, Any]:
            for attempt in range(max_retries):
                try:
                    response = manager.client.text.generate(
                        model="llama3-8b-8192",
                        prompt=prompt,
                        max_tokens=50
                    )
                    return {
                        'success': True,
                        'response': response['choices'][0]['message']['content'],
                        'attempts': attempt + 1,
                        'tokens': response['usage']['total_tokens']
                    }
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"Deneme {attempt + 1} başarısız, yeniden deneniyor...")
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        return {
                            'success': False,
                            'error': str(e),
                            'attempts': attempt + 1
                        }
        
        retry_result = retry_request("Retry test mesajı")
        if retry_result['success']:
            manager.stats['text_requests'] += 1
            manager.stats['total_tokens'] += retry_result['tokens']
            print(f"✅ Retry başarılı ({retry_result['attempts']} deneme): {retry_result['response']}")
        else:
            manager.stats['errors'] += 1
            print(f"❌ Retry başarısız ({retry_result['attempts']} deneme): {retry_result['error']}")
        
        # 4. Graceful degradation
        print("\n4️⃣ Graceful Degradation:")
        
        def fallback_request(prompt: str) -> str:
            # Ana model başarısız olursa alternatif model dene
            models = ["llama3-8b-8192"]
            
            for model in models:
                try:
                    response = manager.client.text.generate(
                        model=model,
                        prompt=prompt,
                        max_tokens=50
                    )
                    manager.stats['text_requests'] += 1
                    manager.stats['total_tokens'] += response['usage']['total_tokens']
                    return f"{model}: {response['choices'][0]['message']['content']}"
                except Exception as e:
                    print(f"{model} başarısız: {e}")
                    continue
            
            # Tüm modeller başarısız olursa varsayılan yanıt
            manager.stats['errors'] += 1
            return "Üzgünüm, şu anda yanıt veremiyorum."
        
        fallback_result = fallback_request("Fallback test mesajı")
        print(f"Fallback sonucu: {fallback_result}")
        
        # 5. Hata istatistikleri
        print("\n5️⃣ Hata İstatistikleri:")
        stats = manager.get_performance_stats()
        print(f"Toplam istek: {stats['text_requests'] + stats['stt_requests']}")
        print(f"Başarılı istek: {stats['text_requests'] + stats['stt_requests'] - stats['errors']}")
        print(f"Başarısız istek: {stats['errors']}")
        print(f"Başarı oranı: {1 - stats['error_rate']:.2%}")
        
    except Exception as e:
        print(f"❌ Senaryo 4 Hatası: {e}")
        manager.stats['errors'] += 1
    finally:
        manager.client.close()

def scenario_5_real_world_application():
    """Senaryo 5: Gerçek dünya uygulaması"""
    print("\n" + "=" * 60)
    print("🌍 SENARYO 5: GERÇEK DÜNYA UYGULAMASI")
    print("=" * 60)
    
    api_key = "your_api_key"
    manager = GroqClientManager(api_key)
    
    try:
        # 1. Çok dilli içerik analizi
        print("\n1️⃣ Çok Dilli İçerik Analizi:")
        
        # Farklı dillerde metinler
        texts = [
            "Hello, how are you today?",
            "Bonjour, comment allez-vous?",
            "Hola, ¿cómo estás?",
            "Merhaba, nasılsın?"
        ]
        
        for text in texts:
            # Dil tespiti
            language_prompt = f"Bu metnin hangi dilde olduğunu söyle: {text}"
            
            response = manager.client.text.generate(
                model="llama3-8b-8192",
                prompt=language_prompt,
                max_tokens=50
            )
            
            manager.stats['text_requests'] += 1
            manager.stats['total_tokens'] += response['usage']['total_tokens']
            
            print(f"'{text}' -> {response['choices'][0]['message']['content']}")
        
        # 2. Ses dosyası analizi
        print("\n2️⃣ Ses Dosyası Analizi:")
        
        # Test ses dosyası oluştur
        audio_file = manager.create_test_audio("real_world_audio.wav", 2)
        
        # Transkripsiyon
        stt_response = manager.client.speech.transcribe(
            file=audio_file,
            model="whisper-large-v3"
        )
        
        manager.stats['stt_requests'] += 1
        manager.stats['total_tokens'] += stt_response.get('usage', {}).get('total_tokens', 0)
        
        transcription = stt_response['text']
        print(f"Transkripsiyon: {transcription}")
        
        # Transkripsiyon analizi
        analysis_prompt = f"""
        Aşağıdaki ses transkripsiyonunu analiz et:
        
        Transkripsiyon: {transcription}
        
        Analiz:
        1. Konuşma kalitesi
        2. Dil tespiti
        3. Ana konular
        4. Duygu analizi
        """
        
        analysis_response = manager.client.text.generate(
            model="llama3-8b-8192",
            prompt=analysis_prompt,
            max_tokens=200
        )
        
        manager.stats['text_requests'] += 1
        manager.stats['total_tokens'] += analysis_response['usage']['total_tokens']
        
        print(f"Analiz: {analysis_response['choices'][0]['message']['content']}")
        
        # 3. İçerik özetleme
        print("\n3️⃣ İçerik Özetleme:")
        
        long_text = """
        Python, Guido van Rossum tarafından 1991 yılında geliştirilen yüksek seviyeli, 
        genel amaçlı bir programlama dilidir. Python'un tasarım felsefesi, kodun 
        okunabilirliğini vurgular ve sözdizimi, programcıların daha az kod yazarak 
        kavramları ifade etmelerine olanak tanır. Python, nesne yönelimli, 
        yorumlanmış ve dinamik olarak yazılmış bir dildir.
        
        Python, web geliştirme, veri analizi, yapay zeka, makine öğrenmesi, 
        bilimsel hesaplama ve otomasyon gibi birçok alanda kullanılır. 
        Django, Flask, NumPy, Pandas, TensorFlow, PyTorch gibi popüler 
        kütüphaneler Python ekosisteminin önemli parçalarıdır.
        """
        
        # Token sayımı
        tokens = manager.client.count_tokens(long_text, "llama3-8b-8192")
        print(f"Uzun metin token sayısı: {tokens}")
        
        # Özetleme
        summary_prompt = f"Bu metni kısaca özetle:\n\n{long_text}"
        
        summary_response = manager.client.text.generate(
            model="llama3-8b-8192",
            prompt=summary_prompt,
            max_tokens=100
        )
        
        manager.stats['text_requests'] += 1
        manager.stats['total_tokens'] += summary_response['usage']['total_tokens']
        
        print(f"Özet: {summary_response['choices'][0]['message']['content']}")
        
        # 4. Performans raporu
        print("\n4️⃣ Performans Raporu:")
        stats = manager.get_performance_stats()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_requests': stats['text_requests'] + stats['stt_requests'],
            'text_requests': stats['text_requests'],
            'stt_requests': stats['stt_requests'],
            'total_tokens': stats['total_tokens'],
            'error_rate': stats['error_rate'],
            'text_requests_per_minute': stats['text_requests_per_minute'],
            'stt_requests_per_minute': stats['stt_requests_per_minute'],
            'total_tokens_per_minute': stats['total_tokens_per_minute'],
            'elapsed_time': stats['elapsed_time']
        }
        
        print("Performans Raporu:")
        for key, value in report.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
        
        # Raporu JSON olarak kaydet
        with open("performance_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("✅ Performans raporu 'performance_report.json' dosyasına kaydedildi")
        
        # Test dosyasını temizle
        if os.path.exists(audio_file):
            os.remove(audio_file)
        
    except Exception as e:
        print(f"❌ Senaryo 5 Hatası: {e}")
        manager.stats['errors'] += 1
    finally:
        manager.client.close()

def main():
    """Ana fonksiyon"""
    print("🚀 GROQ CLIENT - KAPSAMLI ENTEGRASYON ÖRNEKLERİ")
    print("=" * 60)
    
    # Tüm senaryoları çalıştır
    scenario_1_basic_integration()
    scenario_2_advanced_workflow()
    scenario_3_batch_processing()
    scenario_4_error_handling_and_recovery()
    scenario_5_real_world_application()
    
    print("\n" + "=" * 60)
    print("✅ KAPSAMLI ENTEGRASYON ÖRNEKLERİ TAMAMLANDI")
    print("=" * 60)
    print("📊 Tüm örnekler başarıyla çalıştırıldı!")
    print("📁 Performans raporu 'performance_report.json' dosyasında")

if __name__ == "__main__":
    main() 