# 🚀 Groq Dynamic Client System

**Enterprise-Grade Groq API Client with Advanced Features**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()
[![Documentation](https://img.shields.io/badge/Documentation-Complete-blue.svg)](docs/)

Modern, güçlü ve ölçeklenebilir Groq API istemci sistemi. Text generation, speech-to-text, rate limiting, token management ve queue management özellikleri ile enterprise seviyesinde API entegrasyonu sağlar.

## ✨ Öne Çıkan Özellikler

### 🎯 **Core Features**
- **🤖 Text Generation**: Chat ve completion modelleri ile gelişmiş metin üretimi
- **🎤 Speech-to-Text**: Çoklu format desteği ile ses dosyası transkripsiyonu
- **⚡ Rate Limiting**: Akıllı rate limit yönetimi ve otomatik bekleme
- **🔢 Token Management**: Gerçek zamanlı token sayımı ve limit kontrolü
- **📋 Queue Management**: Öncelikli istek sırası yönetimi
- **📚 Dynamic Model Registry**: Gerçek zamanlı model bilgisi ve kategorizasyon

### 🛡️ **Enterprise Features**
- **🔒 Thread-Safe Operations**: Çoklu thread desteği
- **🔄 Automatic Retry**: Akıllı yeniden deneme mekanizması
- **📊 Performance Monitoring**: Detaylı performans metrikleri
- **🎛️ Configurable Limits**: Plan bazlı limit yönetimi
- **🔍 Comprehensive Logging**: Kapsamlı hata ve işlem logları

### 🎨 **Developer Experience**
- **📖 Rich Documentation**: Detaylı API dokümantasyonu
- **🧪 Extensive Examples**: 5 farklı kullanım senaryosu
- **🔧 Easy Integration**: Basit ve sezgisel API
- **⚙️ Flexible Configuration**: Esnek yapılandırma seçenekleri

## 🚀 Hızlı Başlangıç

### 📦 Kurulum

```bash
# Repository'yi klonla
git clone https://github.com/yourusername/groq-client.git
cd groq-client

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 🔑 Temel Kullanım

```python
from client.groq_client import GroqClient

# İstemci oluştur
client = GroqClient("your-groq-api-key")

# Text Generation
response = client.text.generate(
    model="llama3-8b-8192",
    messages=[{"role": "user", "content": "Merhaba, nasılsın?"}],
    max_tokens=100
)
print(response['choices'][0]['message']['content'])

# Speech-to-Text
response = client.speech.transcribe(
    file="audio.mp3",
    model="whisper-large-v3"
)
print(response['text'])
```

## 📚 Detaylı Kullanım

### 🎯 Text Generation

```python
# Basit prompt ile
response = client.text.generate(
    model="llama3-8b-8192",
    prompt="Python programlama dilini açıkla",
    max_tokens=200,
    temperature=0.7
)

# Mesaj listesi ile
messages = [
    {"role": "system", "content": "Sen yardımcı bir asistansın."},
    {"role": "user", "content": "Merhaba!"},
    {"role": "assistant", "content": "Merhaba! Size nasıl yardımcı olabilirim?"},
    {"role": "user", "content": "Python nedir?"}
]

response = client.text.generate(
    model="llama3-8b-8192",
    messages=messages,
    max_tokens=150
)
```

### 🎤 Speech-to-Text

```python
# Temel transkripsiyon
response = client.speech.transcribe(
    file="audio.mp3",
    model="whisper-large-v3"
)

# Dil belirtme ile
response = client.speech.transcribe(
    file="audio.wav",
    model="whisper-large-v3",
    language="tr"
)

# Prompt ile
response = client.speech.transcribe(
    file="audio.m4a",
    model="whisper-large-v3",
    prompt="Bu ses dosyası teknik bir konuşma içeriyor"
)
```

### 🔢 Token Management

```python
# Token sayımı
tokens = client.count_tokens("Bu bir test metnidir.", "llama3-8b-8192")
print(f"Token sayısı: {tokens}")

# Mesaj listesi token sayımı
messages = [
    {"role": "user", "content": "Merhaba"},
    {"role": "assistant", "content": "Merhaba! Size nasıl yardımcı olabilirim?"}
]
tokens = client.count_message_tokens(messages, "llama3-8b-8192")

# Kullanım bilgileri
usage_info = client.get_usage_info(messages, "llama3-8b-8192", max_tokens=100)
print(f"Toplam token: {usage_info['total_tokens']}")
```

### 📊 Rate Limit Management

```python
# Rate limit durumu
status = client.get_rate_limit_status()
print(f"Request remaining: {status['request_remaining']}/{status['request_limit']}")
print(f"Token remaining: {status['token_remaining']}/{status['token_limit']}")

# Özet bilgiler
summary = client.rate_limit_handler.get_status_summary()
print(f"Can make requests: {summary['can_make_requests']}")
print(f"Usage percentage: {summary['request_usage_percent']}%")
```

### 📋 Queue Management

```python
# İsteği sıraya al
request_id = client.enqueue_request(
    client.text.generate,
    model="llama3-8b-8192",
    prompt="Test mesajı",
    priority="high",
    tokens_required=50
)

# Sırayı işle
client.process_queue()

# Sıra durumu
queue_status = client.get_queue_status()
print(f"Total queued: {queue_status['total_queued']}")
```

### 🔍 Model Information

```python
# Kullanılabilir modeller
chat_models = client.get_available_models("chat")
stt_models = client.get_available_models("stt")
print(f"Chat models: {len(chat_models)}")
print(f"STT models: {len(stt_models)}")

# Model bilgileri
model_info = client.get_model_info("llama3-8b-8192")
print(f"Max tokens: {model_info['max_tokens']}")
print(f"Model type: {model_info['type']}")

# Model desteği kontrolü
is_supported = client.is_model_supported("llama3-8b-8192")
```

## 🏗️ Proje Yapısı

```
Groq Client/
├── 📁 api/                    # API Katmanı
│   ├── api_client.py         # HTTP API istemcisi
│   ├── endpoints.py          # API endpoint sabitleri
│   └── __init__.py
├── 📁 client/                # Ana İstemci
│   ├── groq_client.py        # Ana istemci sınıfı
│   └── __init__.py
├── 📁 core/                  # Çekirdek Bileşenler
│   ├── rate_limit_handler.py # Rate limit yönetimi
│   ├── token_counter.py      # Token sayımı
│   ├── model_registry.py     # Model kayıt sistemi
│   ├── queue_manager.py      # İstek sırası yönetimi
│   └── __init__.py
├── 📁 handlers/              # İşleyiciler
│   ├── text_generation.py    # Text generation handler
│   ├── speech_to_text.py     # Speech-to-text handler
│   └── __init__.py
├── 📁 exceptions/            # Hata Yönetimi
│   ├── errors.py             # Özel hata sınıfları
│   └── __init__.py
├── 📁 examples/              # Kullanım Örnekleri
│   ├── 01_basic_usage.py     # Temel kullanım
│   ├── 02_advanced_features.py # Gelişmiş özellikler
│   ├── 03_speech_to_text_advanced.py # STT gelişmiş
│   ├── 04_comprehensive_integration.py # Kapsamlı entegrasyon
│   ├── 05_custom_implementations.py # Özel implementasyonlar
│   └── README.md
├── 📁 docs/                  # 📚 Kapsamlı Dokümantasyon
│   ├── README.md             # Dokümantasyon ana sayfası
│   ├── architecture.md       # Sistem mimarisi
│   ├── api/                  # API Referansları
│   │   └── groq-client.md    # GroqClient API
│   ├── core/                 # Çekirdek Bileşenler
│   │   └── rate-limit-handler.md # RateLimitHandler API
│   ├── guides/               # Rehberler
│   │   └── troubleshooting.md # Sorun Giderme
│   └── reference/            # Referanslar
│       └── models.md         # Model Referansı
├── 📁 data/                  # Veri Dosyaları
│   └── audio.mp3            # Test ses dosyası
├── 📄 README.md             # Bu dosya
├── 📄 requirements.txt      # Bağımlılıklar
└── 📄 __init__.py           # Paket başlatıcı
```

## 📖 Dokümantasyon

### 🎯 **Hızlı Erişim**
- **[📚 Dokümantasyon Ana Sayfası](docs/)** - Tüm dokümantasyonun genel bakışı
- **[🏗️ Sistem Mimarisi](docs/architecture.md)** - Mimari tasarım ve bileşenler
- **[🎯 GroqClient API](docs/api/groq-client.md)** - Ana istemci API referansı
- **[⚡ RateLimitHandler API](docs/core/rate-limit-handler.md)** - Rate limit yönetimi
- **[📚 Model Referansı](docs/reference/models.md)** - Tüm modeller ve özellikleri
- **[🔍 Sorun Giderme](docs/guides/troubleshooting.md)** - Yaygın sorunlar ve çözümleri

### 📊 **Dokümantasyon İstatistikleri**
- **6 Ana Dokümantasyon** dosyası
- **2000+ Satır** detaylı açıklama
- **100+ Kod Örneği** ve kullanım senaryosu
- **20+ Tablo ve Diyagram** görsel içerik
- **100+ Emoji ve İkon** görsel zenginlik

## 🧪 Örnekler

Proje 5 farklı kullanım senaryosu içerir:

### 1️⃣ **Temel Kullanım** (`examples/01_basic_usage.py`)
- Basit text generation
- Context manager kullanımı
- Hata yönetimi

### 2️⃣ **Gelişmiş Özellikler** (`examples/02_advanced_features.py`)
- Token sayımı
- Rate limit kontrolü
- Model bilgileri

### 3️⃣ **STT Gelişmiş** (`examples/03_speech_to_text_advanced.py`)
- Çoklu format desteği
- Dil belirtme
- Prompt kullanımı

### 4️⃣ **Kapsamlı Entegrasyon** (`examples/04_comprehensive_integration.py`)
- Gerçek dünya senaryoları
- Performans izleme
- Batch işleme

### 5️⃣ **Özel Implementasyonlar** (`examples/05_custom_implementations.py`)
- Custom handlers
- Özel rate limit stratejileri
- Token analizi

## 🔧 Konfigürasyon

### Environment Variables

```bash
export GROQ_API_KEY="your-api-key"
export GROQ_BASE_URL="https://api.groq.com"
```

### Custom Configuration

```python
from client.groq_client import GroqClient

# Özel base URL ile
client = GroqClient(
    api_key="your-api-key",
    base_url="https://api.groq.com"
)
```

## 📊 Performance & Monitoring

### Rate Limit Monitoring

```python
# Gerçek zamanlı rate limit durumu
status = client.get_rate_limit_status()
print(f"Request Usage: {status['request_remaining']}/{status['request_limit']}")
print(f"Token Usage: {status['token_remaining']}/{status['token_limit']}")
print(f"Audio Seconds: {status['audio_seconds_remaining']}/{status['audio_seconds_limit']}")
```

### Performance Metrics

```python
# Queue performansı
queue_stats = client.get_queue_status()
print(f"Total Processed: {queue_stats['stats']['total_processed']}")
print(f"Success Rate: {queue_stats['stats']['total_processed'] - queue_stats['stats']['total_failed']}")
```

## 🛠️ Geliştirme

### Kurulum

```bash
# Development bağımlılıkları
pip install -r requirements.txt

# Pre-commit hooks
pre-commit install
```

### Test

```bash
# Tüm testleri çalıştır
python -m pytest

# Coverage ile
python -m pytest --cov=.

# Belirli test
python -m pytest tests/test_groq_client.py
```

### Code Quality

```bash
# Format
black .

# Lint
flake8 .

# Type checking
mypy .

# Security check
bandit -r .
```

## 🔍 Troubleshooting

### Yaygın Sorunlar

#### Rate Limit Hatası
```python
# Rate limit durumunu kontrol et
status = client.get_rate_limit_status()
if not status['has_rate_limit_info']:
    print("Rate limit bilgisi alınamadı")
```

#### Model Bulunamadı
```python
# Kullanılabilir modelleri kontrol et
models = client.get_available_models("chat")
print(f"Available models: {models}")
```

#### Token Limit Aşımı
```python
# Token sayımı yap
tokens = client.count_tokens(text, model)
if tokens > model_limit:
    print(f"Token limit aşıldı: {tokens}/{model_limit}")
```

**💡 Daha detaylı sorun giderme için [🔍 Sorun Giderme Rehberi](docs/guides/troubleshooting.md) sayfasını ziyaret edin.**

## 🤝 Katkıda Bulunma

1. **Fork** yapın
2. **Feature branch** oluşturun (`git checkout -b feature/amazing-feature`)
3. **Commit** yapın (`git commit -m 'Add amazing feature'`)
4. **Push** yapın (`git push origin feature/amazing-feature`)
5. **Pull Request** oluşturun

### Geliştirme Kuralları

- **Code Style**: Black, Flake8, MyPy kullanın
- **Tests**: Yeni özellikler için test yazın
- **Documentation**: Docstring'leri güncelleyin
- **Type Hints**: Tüm fonksiyonlarda type hint kullanın

## 📄 Lisans

Bu proje [MIT License](LICENSE) altında lisanslanmıştır.

## 🆘 Destek

- **📖 Documentation**: [docs/](docs/) klasörüne bakın
- **🐛 Issues**: [GitHub Issues](https://github.com/yourusername/groq-client/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/yourusername/groq-client/discussions)
- **📧 Email**: your-email@example.com

## 🙏 Teşekkürler

- [Groq](https://groq.com) - API sağlayıcısı
- [OpenAI](https://openai.com) - API formatı
- Tüm katkıda bulunanlara

---

**⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**

**📚 Dokümantasyon**: [docs/](docs/) klasöründe kapsamlı dokümantasyon bulabilirsiniz. 