# 🔍 Troubleshooting Guide

## Genel Bakış

Bu rehber, Groq Dynamic Client System kullanırken karşılaşabileceğiniz yaygın sorunları ve çözümlerini içerir.

## 🚨 Yaygın Hatalar ve Çözümleri

### 1. Authentication Errors

#### `AuthenticationError: Invalid API key`

**Belirtiler:**
```
AuthenticationError: Invalid API key provided
```

**Olası Nedenler:**
- Geçersiz API anahtarı
- API anahtarı süresi dolmuş
- Yanlış API anahtarı kullanımı

**Çözümler:**

```python
# 1. API anahtarını kontrol et
api_key = "gsk_your_actual_api_key_here"
client = GroqClient(api_key)

# 2. Environment variable kullan
import os
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable not set")

# 3. API anahtarını test et
try:
    response = client.text.generate(
        model="llama3-8b-8192",
        prompt="Test",
        max_tokens=10
    )
    print("✅ API key geçerli")
except AuthenticationError:
    print("❌ API key geçersiz")
```

### 2. Rate Limit Errors

#### `RateLimitExceeded: Rate limit exceeded`

**Belirtiler:**
```
RateLimitExceeded: Rate limit exceeded. Please wait before making more requests.
```

**Olası Nedenler:**
- API rate limit aşımı
- Çok hızlı istek gönderimi
- Plan limitleri

**Çözümler:**

```python
# 1. Rate limit durumunu kontrol et
status = client.get_rate_limit_status()
print(f"Request remaining: {status['request_remaining']}/{status['request_limit']}")

# 2. Otomatik bekleme kullan
try:
    response = client.text.generate(...)
except RateLimitExceeded:
    print("Rate limit aşıldı, otomatik bekleme...")
    # Handler otomatik olarak bekleyecek

# 3. Manuel bekleme
import time
if not client.rate_limit_handler.can_proceed(tokens=100, requests=1):
    wait_time = client.rate_limit_handler.get_wait_time(tokens=100, requests=1)
    print(f"Bekleme süresi: {wait_time} saniye")
    time.sleep(wait_time)

# 4. Batch işleme kullan
for prompt in prompts:
    client.enqueue_request(
        client.text.generate,
        model="llama3-8b-8192",
        prompt=prompt,
        priority="normal"
    )
client.process_queue()
```

### 3. Model Errors

#### `InvalidModel: Model not found`

**Belirtiler:**
```
InvalidModel: Model 'invalid-model' not found
```

**Olası Nedenler:**
- Geçersiz model adı
- Model artık mevcut değil
- Yanlış model tipi

**Çözümler:**

```python
# 1. Kullanılabilir modelleri listele
models = client.get_available_models()
print(f"Available models: {models}")

# 2. Model tipine göre filtrele
chat_models = client.get_available_models("chat")
stt_models = client.get_available_models("stt")

# 3. Model bilgilerini kontrol et
try:
    model_info = client.get_model_info("llama3-8b-8192")
    print(f"Model info: {model_info}")
except InvalidModel:
    print("Model bulunamadı")

# 4. Model desteğini kontrol et
if client.is_model_supported("llama3-8b-8192"):
    print("Model destekleniyor")
else:
    print("Model desteklenmiyor")
```

### 4. File Errors

#### `FileNotFoundError: Audio file not found`

**Belirtiler:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'audio.mp3'
```

**Olası Nedenler:**
- Dosya yolu yanlış
- Dosya mevcut değil
- Dosya izinleri

**Çözümler:**

```python
# 1. Dosya varlığını kontrol et
import os
file_path = "audio.mp3"
if not os.path.exists(file_path):
    print(f"Dosya bulunamadı: {file_path}")

# 2. Mutlak yol kullan
import pathlib
file_path = pathlib.Path("audio.mp3").resolve()
print(f"Mutlak yol: {file_path}")

# 3. Dosya boyutunu kontrol et
file_size = os.path.getsize(file_path)
print(f"Dosya boyutu: {file_size} bytes")

# 4. Desteklenen formatları kontrol et
supported_formats = ['.mp3', '.wav', '.m4a', '.mp4', '.webm']
file_ext = pathlib.Path(file_path).suffix.lower()
if file_ext not in supported_formats:
    print(f"Desteklenmeyen format: {file_ext}")
```

### 5. Token Errors

#### `TokenLimitExceeded: Token limit exceeded`

**Belirtiler:**
```
TokenLimitExceeded: Token limit exceeded for model 'llama3-8b-8192'
```

**Olası Nedenler:**
- Çok uzun metin
- Model token limiti aşımı
- Yanlış token hesaplama

**Çözümler:**

```python
# 1. Token sayısını kontrol et
text = "Çok uzun bir metin..."
tokens = client.count_tokens(text, "llama3-8b-8192")
model_info = client.get_model_info("llama3-8b-8192")
max_tokens = model_info['max_tokens']

if tokens > max_tokens:
    print(f"Token limit aşıldı: {tokens}/{max_tokens}")

# 2. Metni böl
def split_text(text, max_tokens_per_chunk=4000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for word in words:
        word_tokens = client.count_tokens(word, "llama3-8b-8192")
        if current_tokens + word_tokens > max_tokens_per_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_tokens = word_tokens
        else:
            current_chunk.append(word)
            current_tokens += word_tokens
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

# 3. Kullanım bilgilerini kontrol et
messages = [{"role": "user", "content": "Test mesajı"}]
usage_info = client.get_usage_info(messages, "llama3-8b-8192", max_tokens=100)
print(f"Toplam token: {usage_info['total_tokens']}")
```

### 6. Network Errors

#### `ConnectionError: Failed to connect`

**Belirtiler:**
```
ConnectionError: Failed to connect to api.groq.com
```

**Olası Nedenler:**
- İnternet bağlantısı sorunu
- Firewall engeli
- DNS sorunu
- API sunucusu erişilemez

**Çözümler:**

```python
# 1. İnternet bağlantısını kontrol et
import requests
try:
    response = requests.get("https://api.groq.com", timeout=5)
    print("✅ İnternet bağlantısı var")
except requests.exceptions.RequestException:
    print("❌ İnternet bağlantısı sorunu")

# 2. Timeout ayarla
client = GroqClient(api_key)
# Timeout ayarları APIClient'da yapılır

# 3. Retry mekanizması
import time
def make_request_with_retry(client, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.text.generate(...)
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            print(f"Bağlantı hatası, yeniden deneniyor... ({attempt + 1}/{max_retries})")
            time.sleep(2 ** attempt)  # Exponential backoff
```

### 7. Queue Errors

#### `QueueFullError: Queue is full`

**Belirtiler:**
```
QueueFullError: Queue is full (1000 items)
```

**Olası Nedenler:**
- Sıra dolu
- İşleme durmuş
- Çok fazla istek

**Çözümler:**

```python
# 1. Sıra durumunu kontrol et
queue_status = client.get_queue_status()
print(f"Queue size: {queue_status['total_queued']}")
print(f"Processing: {queue_status['processing']}")

# 2. Sırayı temizle
client.clear_queue()

# 3. İşlemeyi başlat
client.process_queue()

# 4. Sıra boyutunu ayarla
# QueueManager'da max_queue_size parametresi
```

### 8. Memory Errors

#### `MemoryError: Out of memory`

**Belirtiler:**
```
MemoryError: Out of memory
```

**Olası Nedenler:**
- Çok büyük dosyalar
- Bellek sızıntısı
- Çok fazla eşzamanlı işlem

**Çözümler:**

```python
# 1. Dosya boyutunu kontrol et
import os
file_size = os.path.getsize("large_audio.mp3")
max_size = 25 * 1024 * 1024  # 25MB

if file_size > max_size:
    print(f"Dosya çok büyük: {file_size / 1024 / 1024:.2f}MB")

# 2. Bellek kullanımını izle
import psutil
process = psutil.Process()
memory_usage = process.memory_info().rss / 1024 / 1024
print(f"Bellek kullanımı: {memory_usage:.2f}MB")

# 3. Büyük dosyaları böl
def split_audio_file(file_path, chunk_duration=300):  # 5 dakika
    # Audio dosyasını böl
    pass
```

## 🔧 Debug Techniques

### 1. Debug Mode

```python
# Debug modunu etkinleştir
import logging
logging.basicConfig(level=logging.DEBUG)

# Client debug modu
client.debug = True
```

### 2. Request/Response Logging

```python
# API çağrılarını logla
import requests
import logging

# HTTP debug
import http.client
http.client.HTTPConnection.debuglevel = 1

# Requests session debug
session = requests.Session()
session.hooks['response'].append(lambda r, *args, **kwargs: print(f"Response: {r.status_code}"))
```

### 3. Performance Monitoring

```python
import time
import cProfile
import pstats

# Profiling
def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    return result

# Kullanım
profile_function(client.text.generate, model="llama3-8b-8192", prompt="Test")
```

## 📊 Monitoring & Alerting

### 1. Health Check

```python
def health_check(client):
    """Sistem sağlık kontrolü"""
    checks = {}
    
    # API bağlantısı
    try:
        models = client.get_available_models()
        checks['api_connection'] = True
    except Exception as e:
        checks['api_connection'] = False
        checks['api_error'] = str(e)
    
    # Rate limit durumu
    try:
        status = client.get_rate_limit_status()
        checks['rate_limit'] = status['has_rate_limit_info']
        checks['request_remaining'] = status['request_remaining']
    except Exception as e:
        checks['rate_limit'] = False
        checks['rate_limit_error'] = str(e)
    
    # Queue durumu
    try:
        queue_status = client.get_queue_status()
        checks['queue'] = not queue_status['processing']
        checks['queue_size'] = queue_status['total_queued']
    except Exception as e:
        checks['queue'] = False
        checks['queue_error'] = str(e)
    
    return checks

# Kullanım
health = health_check(client)
for check, status in health.items():
    print(f"{check}: {'✅' if status else '❌'}")
```

### 2. Error Tracking

```python
import traceback
from datetime import datetime

class ErrorTracker:
    def __init__(self):
        self.errors = []
    
    def track_error(self, error, context=None):
        error_info = {
            'timestamp': datetime.now(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context
        }
        self.errors.append(error_info)
        
        # Kritik hataları logla
        if isinstance(error, (AuthenticationError, RateLimitExceeded)):
            print(f"🚨 Critical error: {error}")
    
    def get_error_summary(self):
        error_counts = {}
        for error in self.errors:
            error_type = error['error_type']
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        return error_counts

# Kullanım
error_tracker = ErrorTracker()

try:
    response = client.text.generate(...)
except Exception as e:
    error_tracker.track_error(e, context="text_generation")
```

## 🚀 Performance Optimization

### 1. Connection Pooling

```python
# APIClient'da connection pooling
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)
```

### 2. Caching

```python
# Model bilgilerini cache'le
import functools
import time

@functools.lru_cache(maxsize=128)
def get_cached_model_info(model_name):
    return client.get_model_info(model_name)

# Token sayımını cache'le
@functools.lru_cache(maxsize=1000)
def get_cached_token_count(text, model):
    return client.count_tokens(text, model)
```

### 3. Batch Processing

```python
# Toplu işleme
def batch_process_texts(texts, batch_size=10):
    results = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        # Batch'i sıraya al
        for text in batch:
            client.enqueue_request(
                client.text.generate,
                model="llama3-8b-8192",
                prompt=text,
                priority="normal"
            )
        
        # Batch'i işle
        client.process_queue()
        
        # Sonuçları topla
        # (Queue'dan sonuçları alma implementasyonu gerekli)
    
    return results
```

## 📞 Support

### 1. Log Collection

```python
def collect_logs():
    """Sorun giderme için log toplama"""
    logs = {
        'system_info': {
            'python_version': sys.version,
            'platform': sys.platform,
            'memory_usage': psutil.virtual_memory().percent
        },
        'client_info': {
            'rate_limit_status': client.get_rate_limit_status(),
            'queue_status': client.get_queue_status(),
            'available_models': client.get_available_models()
        },
        'recent_errors': error_tracker.errors[-10:]  # Son 10 hata
    }
    return logs
```

### 2. Issue Reporting

Sorun yaşadığınızda şu bilgileri toplayın:

1. **Hata mesajı** (tam hata)
2. **Kod örneği** (minimal reproducible example)
3. **Sistem bilgileri** (Python versiyonu, işletim sistemi)
4. **Log dosyaları** (varsa)
5. **Çevre değişkenleri** (API key hariç)

### 3. Community Support

- **GitHub Issues**: [Repository Issues](https://github.com/yourusername/groq-client/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/groq-client/discussions)
- **Documentation**: [docs/](docs/) klasörü

---

Bu rehber, karşılaşabileceğiniz yaygın sorunları çözmek için tasarlanmıştır. Sorununuz burada çözülmediyse, lütfen GitHub Issues'da bildirin. 