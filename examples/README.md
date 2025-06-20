# Groq Client - Örnekler

Bu klasör, Groq Client'ın tüm özelliklerini gösteren kapsamlı örnekleri içerir.

## 📁 Dosya Yapısı

```
examples/
├── 01_basic_usage.py              # Temel kullanım örnekleri
├── 02_advanced_features.py        # Gelişmiş özellikler
├── 03_speech_to_text_advanced.py  # Gelişmiş STT örnekleri
├── 04_comprehensive_integration.py # Kapsamlı entegrasyon
├── 05_custom_implementations.py   # Özel implementasyonlar
└── README.md                      # Bu dosya
```

## 🚀 Örnekleri Çalıştırma

### Gereksinimler

1. **API Key**: Örneklerde kullanılan API key'i kendi key'inizle değiştirin
2. **Ses Dosyası**: `data/audio.mp3` dosyasının mevcut olduğundan emin olun
3. **Bağımlılıklar**: `requirements.txt` dosyasındaki tüm bağımlılıkları yükleyin

### Çalıştırma Komutları

```bash
# Temel kullanım örnekleri
python examples/01_basic_usage.py

# Gelişmiş özellikler
python examples/02_advanced_features.py

# Gelişmiş STT örnekleri
python examples/03_speech_to_text_advanced.py

# Kapsamlı entegrasyon
python examples/04_comprehensive_integration.py

# Özel implementasyonlar
python examples/05_custom_implementations.py
```

## 📋 Örnek İçerikleri

### 01_basic_usage.py
- **Temel Text Generation**: Prompt ve messages formatı
- **Speech-to-Text**: Ses dosyası transkripsiyonu
- **Context Manager**: `with` statement kullanımı
- **Error Handling**: Hata yönetimi örnekleri

### 02_advanced_features.py
- **Token Counting**: Metin ve mesaj token sayımı
- **Model Registry**: Model listesi ve bilgileri
- **Rate Limiting**: Rate limit kontrolü ve yönetimi
- **Queue Management**: Async ve sync queue kullanımı
- **Advanced Text Generation**: Function calling, JSON mode, parallel requests

### 03_speech_to_text_advanced.py
- **File Validation**: Dosya formatı ve boyut kontrolü
- **Plan-based Limits**: Free ve Developer plan limitleri
- **Batch Processing**: Paralel transkripsiyon
- **Error Handling**: Retry mekanizması
- **Rate Limiting**: STT rate limit kontrolü

### 04_comprehensive_integration.py
- **Senaryo 1**: Temel entegrasyon
- **Senaryo 2**: Gelişmiş iş akışı (STT + Text Analysis)
- **Senaryo 3**: Toplu işleme
- **Senaryo 4**: Hata yönetimi ve kurtarma
- **Senaryo 5**: Gerçek dünya uygulaması

### 05_custom_implementations.py
- **Custom Text Handler**: Geçmiş takibi ile text generation
- **Custom Rate Limit Strategy**: Öncelik bazlı rate limiting
- **Custom Token Analyzer**: Metin karmaşıklık analizi
- **Custom Model Selector**: Gereksinimlere göre model seçimi
- **Custom Queue Processor**: Yeniden deneme ile işleme

## 🔧 Özelleştirme

### API Key Değiştirme

Tüm örneklerde API key'i değiştirin:

```python
# Mevcut
api_key = "gsk_***"

# Kendi key'inizle değiştirin
api_key = "your-api-key-here"
```

### Model Seçimi

Farklı modeller denemek için:

```python
# Chat modelleri
models = ["llama3-8b-8192", "mixtral-8x7b-32768", "llama3-70b-8192"]

# STT modelleri
stt_models = ["whisper-large-v3", "whisper-large-v2"]
```

### Parametre Ayarları

Text generation parametrelerini özelleştirin:

```python
response = client.text.generate(
    model="llama3-8b-8192",
    prompt="Your prompt here",
    max_tokens=200,        # Maksimum token
    temperature=0.7,       # Yaratıcılık (0.0-1.0)
    top_p=0.9,            # Nucleus sampling
    stream=False          # Streaming response
)
```

## 📊 Performans İzleme

Örnekler çalıştırıldıktan sonra performans raporları oluşturulur:

- **Token kullanımı**: Toplam ve dakika başına token
- **Request sayısı**: Text ve STT istekleri
- **Hata oranı**: Başarısız isteklerin yüzdesi
- **Yanıt süreleri**: Ortalama işlem süreleri

## 🛠️ Geliştirme

### Yeni Örnek Ekleme

1. Yeni dosya oluşturun: `examples/06_your_example.py`
2. Temel yapıyı kopyalayın:

```python
#!/usr/bin/env python3
"""
Örnek Açıklaması
================
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.groq_client import GroqClient

def main():
    api_key = "your-api-key"
    client = GroqClient(api_key)
    
    # Örnek kodunuz buraya
    
    client.close()

if __name__ == "__main__":
    main()
```

### Test Dosyaları

Örnekler test dosyaları oluşturur ve temizler:
- Ses dosyaları: `test_audio.wav`, `batch_audio_*.wav`
- Raporlar: `performance_report.json`
- Geçici dosyalar: `test.txt`, `large_test.wav`

## 🚨 Hata Yönetimi

Örnekler kapsamlı hata yönetimi içerir:

- **Rate Limit**: Otomatik bekleme ve yeniden deneme
- **Network Errors**: Bağlantı hatalarında retry
- **Invalid Input**: Geçersiz parametre kontrolü
- **File Errors**: Dosya bulunamama ve format hataları

## 📈 İyi Uygulamalar

1. **API Key Güvenliği**: API key'leri environment variable olarak saklayın
2. **Rate Limiting**: Rate limit kontrolü yapmadan istek göndermeyin
3. **Error Handling**: Tüm API çağrılarını try-catch bloklarına alın
4. **Resource Management**: Context manager kullanarak kaynakları temizleyin
5. **Token Counting**: Büyük istekler öncesi token sayımı yapın

## 🤝 Katkıda Bulunma

Yeni örnekler eklemek için:

1. Fork yapın
2. Yeni örnek dosyası oluşturun
3. README.md'yi güncelleyin
4. Pull request gönderin

## 📞 Destek

Sorunlar için:
- GitHub Issues kullanın
- Dokümantasyona bakın
- Örnekleri referans alın 
