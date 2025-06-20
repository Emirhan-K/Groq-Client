#!/usr/bin/env python3
"""
Temel Kullanım Örnekleri
========================

Bu dosya Groq Client'ın temel özelliklerini gösterir:
- İstemci oluşturma
- Text generation
- Speech-to-text
- Context manager kullanımı
"""

import os
import sys
import time

# Proje kök dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.groq_client import GroqClient

def basic_text_generation():
    """Temel text generation örnekleri"""
    print("=" * 60)
    print("📝 TEMEL TEXT GENERATION")
    print("=" * 60)
    
    # API key'i ayarla
    api_key = "your_api_key"
    
    # İstemci oluştur
    client = GroqClient(api_key)
    
    try:
        # 1. Basit prompt ile text generation
        print("\n1️⃣ Basit Prompt ile Text Generation:")
        response = client.text.generate(
            model="llama3-8b-8192",
            prompt="Merhaba! Sen bir yardımcı AI'sın. Kendini kısaca tanıtır mısın? Lütfen sadece Türkçe yanıt ver.",
            max_tokens=150,
            temperature=0.7
        )
        print(f"Model: {response['model']}")
        print(f"Kullanılan Token: {response['usage']['total_tokens']}")
        print(f"Yanıt: {response['choices'][0]['message']['content']}")
        
        # 2. Messages formatı ile chat
        print("\n2️⃣ Messages Formatı ile Chat:")
        messages = [
            {"role": "system", "content": "Sen Türkçe konuşan yardımcı bir AI'sın. Sadece Türkçe yanıt ver."},
            {"role": "user", "content": "Python'da liste ve tuple arasındaki farkı açıkla."}
        ]
        
        response = client.text.generate(
            model="llama3-8b-8192",
            messages=messages,
            max_tokens=200,
            temperature=0.5
        )
        print(f"Yanıt: {response['choices'][0]['message']['content']}")
        
        # 3. Uzun yanıt örneği
        print("\n3️⃣ Uzun Yanıt Örneği:")
        response = client.text.generate(
            model="llama3-8b-8192",
            prompt="Türkiye'nin en güzel 3 şehrini say ve her birini kısaca açıkla:",
            max_tokens=300
        )
        print(f"Yanıt: {response['choices'][0]['message']['content']}")
        
        # 4. Farklı modeller ile deneme
        print("\n4️⃣ Farklı Modeller:")
        models_to_try = ["llama3-8b-8192"]  # Sadece çalışan model
        
        for model in models_to_try:
            try:
                response = client.text.generate(
                    model=model,
                    prompt=f"'{model}' modeli ile kısa bir Türkçe şiir yaz:",
                    max_tokens=100,
                    temperature=0.8
                )
                print(f"\n{model}:")
                print(response['choices'][0]['message']['content'])
            except Exception as e:
                print(f"{model}: Hata - {e}")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        # İstemciyi kapat
        client.close()

def basic_speech_to_text():
    """Temel speech-to-text örnekleri"""
    print("\n" + "=" * 60)
    print("🎤 TEMEL SPEECH-TO-TEXT")
    print("=" * 60)
    
    api_key = "your_api_key"
    client = GroqClient(api_key)
    
    try:
        # Ses dosyası yolu
        audio_file = "data/audio.mp3"
        
        if not os.path.exists(audio_file):
            print(f"⚠️ Ses dosyası bulunamadı: {audio_file}")
            print("Ses dosyası olmadan STT testi yapılamıyor.")
            return
        
        print(f"\n1️⃣ Temel Transkripsiyon:")
        print(f"Ses dosyası: {audio_file}")
        
        # Temel transkripsiyon - Hata düzeltmesi
        try:
            response = client.speech.transcribe(
                file=audio_file,
                model="whisper-large-v3"
            )
            print(f"Transkripsiyon: {response['text']}")
        except Exception as e:
            print(f"⚠️ STT hatası: {e}")
            print("STT testi atlanıyor...")
            return
        
        # 2. Prompt ile transkripsiyon
        print("\n2️⃣ Prompt ile Transkripsiyon:")
        try:
            response = client.speech.transcribe(
                file=audio_file,
                model="whisper-large-v3",
                prompt="Bu ses dosyası Türkçe konuşma içeriyor."
            )
            print(f"Prompt ile transkripsiyon: {response['text']}")
        except Exception as e:
            print(f"Prompt ile transkripsiyon hatası: {e}")
        
        # 3. Dil belirtme
        print("\n3️⃣ Dil Belirtme:")
        try:
            response = client.speech.transcribe(
                file=audio_file,
                model="whisper-large-v3",
                language="tr"
            )
            print(f"Dil belirtilerek transkripsiyon: {response['text']}")
        except Exception as e:
            print(f"Dil belirtme hatası: {e}")
        
        # 4. Farklı STT modelleri
        print("\n4️⃣ Farklı STT Modelleri:")
        stt_models = ["whisper-large-v3", "whisper-large-v2"]
        
        for model in stt_models:
            try:
                response = client.speech.transcribe(
                    file=audio_file,
                    model=model
                )
                print(f"\n{model}:")
                print(f"Transkripsiyon: {response['text']}")
            except Exception as e:
                print(f"{model}: Hata - {e}")
        
    except Exception as e:
        print(f"❌ STT Hatası: {e}")
    finally:
        client.close()

def context_manager_usage():
    """Context manager kullanım örnekleri"""
    print("\n" + "=" * 60)
    print("🔧 CONTEXT MANAGER KULLANIMI")
    print("=" * 60)
    
    api_key = "your_api_key"
    
    # Context manager ile kullanım
    with GroqClient(api_key) as client:
        try:
            print("\n1️⃣ Context Manager ile Text Generation:")
            response = client.text.generate(
                model="llama3-8b-8192",
                prompt="Context manager kullanımının avantajlarını açıkla. Sadece Türkçe yanıt ver:",
                max_tokens=150
            )
            print(response['choices'][0]['message']['content'])
            
            print("\n2️⃣ Context Manager ile Birden Fazla İstek:")
            
            # Birden fazla istek
            prompts = [
                "Python nedir? Sadece Türkçe açıkla.",
                "JavaScript nedir? Sadece Türkçe açıkla.",
                "Machine Learning nedir? Sadece Türkçe açıkla."
            ]
            
            for i, prompt in enumerate(prompts, 1):
                response = client.text.generate(
                    model="llama3-8b-8192",
                    prompt=prompt,
                    max_tokens=100
                )
                print(f"\n{i}. {prompt}")
                print(f"Yanıt: {response['choices'][0]['message']['content'][:100]}...")
            
            print("\n✅ Context manager otomatik olarak kaynakları temizledi!")
            
        except Exception as e:
            print(f"❌ Context Manager Hatası: {e}")

def error_handling_examples():
    """Hata yönetimi örnekleri"""
    print("\n" + "=" * 60)
    print("🚨 HATA YÖNETİMİ ÖRNEKLERİ")
    print("=" * 60)
    
    api_key = "your_api_key"
    client = GroqClient(api_key)
    
    try:
        # 1. Geçersiz model hatası
        print("\n1️⃣ Geçersiz Model Hatası:")
        try:
            response = client.text.generate(
                model="gecersiz-model",
                prompt="Test",
                max_tokens=10
            )
        except Exception as e:
            print(f"Beklenen hata: {type(e).__name__} - {e}")
        
        # 2. Geçersiz dosya hatası
        print("\n2️⃣ Geçersiz Dosya Hatası:")
        try:
            response = client.speech.transcribe(
                file="olmayan-dosya.mp3",
                model="whisper-large-v3"
            )
        except Exception as e:
            print(f"Beklenen hata: {type(e).__name__} - {e}")
        
        # 3. Geçersiz parametre hatası
        print("\n3️⃣ Geçersiz Parametre Hatası:")
        try:
            response = client.text.generate(
                model="llama3-8b-8192",
                prompt="",  # Boş prompt
                max_tokens=10
            )
        except Exception as e:
            print(f"Beklenen hata: {type(e).__name__} - {e}")
        
    except Exception as e:
        print(f"❌ Genel Hata: {e}")
    finally:
        client.close()

def main():
    """Ana fonksiyon"""
    print("🚀 GROQ CLIENT - TEMEL KULLANIM ÖRNEKLERİ")
    print("=" * 60)
    
    # Temel örnekler
    basic_text_generation()
    basic_speech_to_text()
    context_manager_usage()
    error_handling_examples()
    
    print("\n" + "=" * 60)
    print("✅ TEMEL KULLANIM ÖRNEKLERİ TAMAMLANDI")
    print("=" * 60)

if __name__ == "__main__":
    main() 