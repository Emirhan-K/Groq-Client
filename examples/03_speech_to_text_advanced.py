#!/usr/bin/env python3
"""
Gelişmiş Speech-to-Text Örnekleri
=================================

Bu dosya Groq Client'ın gelişmiş speech-to-text özelliklerini gösterir:
- Farklı ses formatları
- Plan bazlı limitler
- Dosya validasyonu
- Batch processing
- Error handling
"""

import os
import sys
import time
import wave
import struct
import tempfile
from pathlib import Path

# Proje kök dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.groq_client import GroqClient
from handlers.speech_to_text import SpeechToTextHandler
from core.model_registry import ModelRegistry
from core.rate_limit_handler import RateLimitHandler

def create_test_audio_files():
    """Test için farklı formatlarda ses dosyaları oluşturur"""
    print("🎵 Test ses dosyaları oluşturuluyor...")
    
    # WAV dosyası oluştur
    def create_wav_file(filename, duration=2):
        import math
        sample_rate = 44100
        frequency = 440  # 440 Hz
        num_samples = sample_rate * duration
        
        samples = []
        for i in range(num_samples):
            value = 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate)
            sample = int(32767 * value)
            sample = max(-32768, min(32767, sample))  # Sınırla!
            samples.append(struct.pack('h', sample))
        
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b''.join(samples))
    
    # Test dosyaları oluştur
    test_files = {}
    
    # WAV dosyası
    wav_file = "test_audio.wav"
    create_wav_file(wav_file, 2)
    test_files['wav'] = wav_file
    
    # MP3 dosyası (mevcut dosyayı kullan)
    if os.path.exists("data/audio.mp3"):
        test_files['mp3'] = "data/audio.mp3"
    
    print(f"✅ Test dosyaları oluşturuldu: {list(test_files.keys())}")
    return test_files

def file_validation_examples():
    """Dosya validasyon örnekleri"""
    print("=" * 60)
    print("📁 DOSYA VALİDASYON ÖRNEKLERİ")
    print("=" * 60)
    
    api_key = "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"
    
    # Handler'ı doğrudan kullan
    model_registry = ModelRegistry(api_key)
    rate_handler = RateLimitHandler()
    stt_handler = SpeechToTextHandler(api_key, model_registry, rate_handler)
    
    try:
        # 1. Desteklenen formatlar
        print("\n1️⃣ Desteklenen Formatlar:")
        supported_formats = stt_handler.supported_formats
        print(f"Desteklenen formatlar: {', '.join(supported_formats)}")
        
        # 2. Plan bilgileri
        print("\n2️⃣ Plan Bilgileri:")
        plan_info = stt_handler.get_plan_info()
        
        print(f"Plan: {plan_info['plan']}")
        print(f"  - Max dosya boyutu: {plan_info['max_file_size_mb']} MB")
        print(f"  - Desteklenen formatlar: {', '.join(plan_info['supported_formats'])}")
        
        # 3. Dosya uyumluluk kontrolü
        print("\n3️⃣ Dosya Uyumluluk Kontrolü:")
        test_files = create_test_audio_files()
        
        for format_type, file_path in test_files.items():
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                max_size = plan_info['max_file_size_bytes']
                is_compatible = file_size <= max_size
                print(f"{file_path}: {'✅ Uyumlu' if is_compatible else '❌ Uyumsuz'} ({file_size/1024:.1f}KB)")
        
        # 4. Geçersiz dosya testleri
        print("\n4️⃣ Geçersiz Dosya Testleri:")
        
        # Olmayan dosya
        try:
            stt_handler.transcribe("olmayan-dosya.mp3", "whisper-large-v3")
        except Exception as e:
            print(f"Olmayan dosya hatası: {type(e).__name__}")
        
        # Geçersiz format
        try:
            # Geçersiz uzantılı dosya oluştur
            with open("test.txt", "w") as f:
                f.write("Bu bir ses dosyası değil")
            
            stt_handler.transcribe("test.txt", "whisper-large-v3")
        except Exception as e:
            print(f"Geçersiz format hatası: {type(e).__name__}")
        
        # Çok büyük dosya simülasyonu
        try:
            # Büyük dosya oluştur (30MB)
            with open("large_test.wav", "wb") as f:
                f.write(b"0" * 30 * 1024 * 1024)  # 30MB
            
            stt_handler.transcribe("large_test.wav", "whisper-large-v3")
        except Exception as e:
            print(f"Büyük dosya hatası: {type(e).__name__}")
        
        # 5. Dosya boyutu ve süre tahmini
        print("\n5️⃣ Dosya Boyutu ve Süre Tahmini:")
        for format_type, file_path in test_files.items():
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                estimated_duration = stt_handler._estimate_audio_duration(file_size)
                
                print(f"{file_path}:")
                print(f"  - Boyut: {file_size / 1024:.1f}KB")
                print(f"  - Tahmini süre: {estimated_duration:.2f}s")
        
    except Exception as e:
        print(f"❌ Dosya Validasyon Hatası: {e}")
    finally:
        # Test dosyalarını temizle
        cleanup_test_files()

def advanced_stt_features():
    """Gelişmiş STT özellikleri"""
    print("\n" + "=" * 60)
    print("🎤 GELİŞMİŞ STT ÖZELLİKLERİ")
    print("=" * 60)
    
    api_key = "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"
    client = GroqClient(api_key)
    
    try:
        # Test dosyalarını oluştur
        test_files = create_test_audio_files()
        
        # 1. Farklı modeller ile transkripsiyon
        print("\n1️⃣ Farklı STT Modelleri:")
        stt_models = ["whisper-large-v3", "whisper-large-v2"]
        
        for model in stt_models:
            for format_type, file_path in test_files.items():
                if os.path.exists(file_path):
                    try:
                        print(f"\n{model} ile {file_path}:")
                        response = client.speech.transcribe(
                            file=file_path,
                            model=model
                        )
                        print(f"Transkripsiyon: {response['text']}")
                    except Exception as e:
                        print(f"Hata: {e}")
        
        # 2. Prompt ile transkripsiyon
        print("\n2️⃣ Prompt ile Transkripsiyon:")
        for format_type, file_path in test_files.items():
            if os.path.exists(file_path):
                try:
                    response = client.speech.transcribe(
                        file=file_path,
                        model="whisper-large-v3",
                        prompt="Bu ses dosyası Türkçe konuşma içeriyor ve teknik terimler kullanıyor."
                    )
                    print(f"{file_path} (prompt ile): {response['text']}")
                except Exception as e:
                    print(f"{file_path} hatası: {e}")
        
        # 3. Dil belirtme
        print("\n3️⃣ Dil Belirtme:")
        languages = ["tr", "en"]  # 'auto' desteklenmiyor
        
        for lang in languages:
            for format_type, file_path in test_files.items():
                if os.path.exists(file_path):
                    try:
                        response = client.speech.transcribe(
                            file=file_path,
                            model="whisper-large-v3",
                            language=lang
                        )
                        print(f"{file_path} ({lang}): {response['text']}")
                    except Exception as e:
                        print(f"{file_path} ({lang}) hatası: {e}")
        
        # 4. Batch processing
        print("\n4️⃣ Batch Processing:")
        import concurrent.futures
        
        def transcribe_file(file_path, model="whisper-large-v3"):
            try:
                response = client.speech.transcribe(file=file_path, model=model)
                return f"{file_path}: {response['text']}"
            except Exception as e:
                return f"{file_path}: Hata - {e}"
        
        # Paralel transkripsiyon
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for format_type, file_path in test_files.items():
                if os.path.exists(file_path):
                    future = executor.submit(transcribe_file, file_path)
                    futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                print(result)
        
        # 5. Error handling ve retry
        print("\n5️⃣ Error Handling ve Retry:")
        
        def transcribe_with_retry(file_path, max_retries=3):
            for attempt in range(max_retries):
                try:
                    response = client.speech.transcribe(
                        file=file_path,
                        model="whisper-large-v3"
                    )
                    print(f"✅ Başarılı (deneme {attempt + 1}): {response['text']}")
                    return response
                except Exception as e:
                    print(f"❌ Deneme {attempt + 1} başarısız: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # 2 saniye bekle
                    else:
                        print("Maksimum deneme sayısına ulaşıldı")
                        raise
        
        for format_type, file_path in test_files.items():
            if os.path.exists(file_path):
                try:
                    transcribe_with_retry(file_path)
                except Exception as e:
                    print(f"Retry başarısız: {e}")
        
    except Exception as e:
        print(f"❌ Gelişmiş STT Hatası: {e}")
    finally:
        client.close()
        cleanup_test_files()

def stt_with_rate_limiting():
    """Rate limiting ile STT örnekleri"""
    print("\n" + "=" * 60)
    print("⏱️ RATE LIMITING İLE STT")
    print("=" * 60)
    
    api_key = "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"
    client = GroqClient(api_key)
    
    try:
        # Test dosyalarını oluştur
        test_files = create_test_audio_files()
        
        # 1. Rate limit kontrolü
        print("\n1️⃣ Rate Limit Kontrolü:")
        status = client.get_rate_limit_status()
        print(f"Audio seconds limit: {status['audio_seconds_limit']}")
        print(f"Audio seconds remaining: {status['audio_seconds_remaining']}")
        print(f"Request limit: {status['request_limit']}")
        print(f"Request remaining: {status['request_remaining']}")
        
        # 2. Rate limit ile transkripsiyon
        print("\n2️⃣ Rate Limit ile Transkripsiyon:")
        for format_type, file_path in test_files.items():
            if os.path.exists(file_path):
                try:
                    # Rate limit kontrolü
                    can_proceed = client.rate_limit_handler.can_proceed(
                        requests=1, 
                        audio_seconds=10  # Tahmini süre
                    )
                    
                    if can_proceed:
                        print(f"{file_path}: Rate limit uygun, transkripsiyon yapılıyor...")
                        response = client.speech.transcribe(
                            file=file_path,
                            model="whisper-large-v3"
                        )
                        print(f"Sonuç: {response['text']}")
                    else:
                        print(f"{file_path}: Rate limit aşıldı, bekleme gerekli")
                        # Rate limit aşıldıysa bekle
                        client.rate_limit_handler.wait_if_needed()
                        
                        response = client.speech.transcribe(
                            file=file_path,
                            model="whisper-large-v3"
                        )
                        print(f"Bekleme sonrası sonuç: {response['text']}")
                        
                except Exception as e:
                    print(f"{file_path} hatası: {e}")
        
        # 3. Batch processing with rate limiting
        print("\n3️⃣ Rate Limiting ile Batch Processing:")
        
        def transcribe_with_rate_limit(file_path):
            try:
                # Rate limit kontrolü
                if client.rate_limit_handler.can_proceed(requests=1, audio_seconds=10):
                    response = client.speech.transcribe(
                        file=file_path,
                        model="whisper-large-v3"
                    )
                    return f"{file_path}: {response['text']}"
                else:
                    return f"{file_path}: Rate limit aşıldı"
            except Exception as e:
                return f"{file_path}: Hata - {e}"
        
        # Sıralı işleme (rate limit için)
        for format_type, file_path in test_files.items():
            if os.path.exists(file_path):
                result = transcribe_with_rate_limit(file_path)
                print(result)
                time.sleep(1)  # Rate limit için bekle
        
    except Exception as e:
        print(f"❌ Rate Limiting STT Hatası: {e}")
    finally:
        client.close()
        cleanup_test_files()

def cleanup_test_files():
    """Test dosyalarını temizle"""
    test_files = [
        "test_audio.wav",
        "test.txt",
        "large_test.wav"
    ]
    
    for file_path in test_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

def main():
    """Ana fonksiyon"""
    print("🚀 GROQ CLIENT - GELİŞMİŞ SPEECH-TO-TEXT ÖRNEKLERİ")
    print("=" * 60)
    
    # Gelişmiş STT örnekleri
    file_validation_examples()
    advanced_stt_features()
    stt_with_rate_limiting()
    
    print("\n" + "=" * 60)
    print("✅ GELİŞMİŞ SPEECH-TO-TEXT ÖRNEKLERİ TAMAMLANDI")
    print("=" * 60)

if __name__ == "__main__":
    main() 