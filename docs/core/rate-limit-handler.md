# ⚡ RateLimitHandler API Reference

## Genel Bakış

`RateLimitHandler`, Groq API rate limit'lerini yönetmek için tasarlanmış akıllı bir bileşendir. Gerçek zamanlı limit takibi, otomatik bekleme ve dinamik limit güncelleme özellikleri sağlar.

## 📋 Sınıf Tanımı

```python
class RateLimitHandler:
    """Groq API rate limit yönetimi için akıllı handler"""
```

## 🔧 Constructor

### `__init__(api_callback: Optional[Callable] = None)`

Rate limit handler'ı başlatır.

#### Parametreler

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `api_callback` | `Optional[Callable]` | `None` | API'den limit bilgisi almak için callback |

#### Örnek

```python
from core.rate_limit_handler import RateLimitHandler

# Temel kullanım
handler = RateLimitHandler()

# API callback ile
def api_callback():
    # API'den limit bilgisi alma fonksiyonu
    return api_response_headers

handler = RateLimitHandler(api_callback=api_callback)
```

## 🔍 Core Methods

### `get_status() → Dict[str, Any]`

Mevcut rate limit durumunu döndürür.

#### Örnek

```python
status = handler.get_status()
print(f"Request remaining: {status['request_remaining']}/{status['request_limit']}")
print(f"Token remaining: {status['token_remaining']}/{status['token_limit']}")
print(f"Audio seconds: {status['audio_seconds_remaining']}/{status['audio_seconds_limit']}")
```

#### Dönen Değer

```python
{
    'request_limit': 14400,
    'request_remaining': 14399,
    'request_reset_time': 0,
    'token_limit': 6000,
    'token_remaining': 5987,
    'token_reset_time': 0,
    'audio_seconds_limit': 7200,
    'audio_seconds_remaining': 7200,
    'audio_seconds_reset_time': 0,
    'last_update': 1750393319.341,
    'current_time': 1750393319.343,
    'has_rate_limit_info': True,
    'time_since_update': 0.002
}
```

### `can_proceed(tokens: int = 0, requests: int = 1, audio_seconds: int = 0) → bool`

İsteğin yapılıp yapılamayacağını kontrol eder.

#### Parametreler

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `tokens` | `int` | `0` | Gereken token sayısı |
| `requests` | `int` | `1` | Gereken request sayısı |
| `audio_seconds` | `int` | `0` | Gereken ses saniyesi |

#### Örnek

```python
# Text generation için kontrol
can_proceed = handler.can_proceed(tokens=100, requests=1)
if can_proceed:
    # API çağrısı yap
    response = make_api_call()
else:
    # Bekle veya alternatif strateji uygula
    wait_for_rate_limit()

# STT için kontrol
can_proceed = handler.can_proceed(audio_seconds=30, requests=1)
if can_proceed:
    # STT API çağrısı yap
    transcription = transcribe_audio()
```

### `wait_if_needed(tokens: int = 0, requests: int = 1, audio_seconds: int = 0) → None`

Gerekirse rate limit için bekler.

#### Parametreler

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `tokens` | `int` | `0` | Gereken token sayısı |
| `requests` | `int` | `1` | Gereken request sayısı |
| `audio_seconds` | `int` | `0` | Gereken ses saniyesi |

#### Örnek

```python
# Otomatik bekleme ile API çağrısı
handler.wait_if_needed(tokens=100, requests=1)
response = make_api_call()

# STT için bekleme
handler.wait_if_needed(audio_seconds=30, requests=1)
transcription = transcribe_audio()
```

### `update_from_response(response_headers: Dict[str, str]) → None`

API yanıtından rate limit bilgilerini günceller.

#### Parametreler

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `response_headers` | `Dict[str, str]` | API yanıt header'ları |

#### Örnek

```python
# API çağrısından sonra
response = requests.post(url, headers=headers, json=data)
handler.update_from_response(response.headers)
```

### `force_refresh(api_callback: Optional[Callable] = None) → None`

Rate limit bilgilerini zorla yeniler.

#### Parametreler

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `api_callback` | `Optional[Callable]` | `None` | Yeni API callback fonksiyonu |

#### Örnek

```python
# Zorla yenile
handler.force_refresh()

# Yeni callback ile yenile
def new_api_callback():
    return get_latest_rate_limits()

handler.force_refresh(api_callback=new_api_callback)
```

## 📊 Status Methods

### `get_status_summary() → Dict[str, Any]`

Rate limit durumu özetini döndürür.

#### Örnek

```python
summary = handler.get_status_summary()
print(f"Can make requests: {summary['can_make_requests']}")
print(f"Request usage: {summary['request_usage_percent']}%")
print(f"Token usage: {summary['token_usage_percent']}%")
print(f"Audio usage: {summary['audio_usage_percent']}%")
```

#### Dönen Değer

```python
{
    'can_make_requests': True,
    'request_usage_percent': 0.01,
    'token_usage_percent': 0.22,
    'audio_usage_percent': 0.0,
    'request_remaining': 14399,
    'token_remaining': 5987,
    'audio_seconds_remaining': 7200,
    'last_update': 1750393319.341,
    'has_rate_limit_info': True
}
```

### `is_rate_limited() → bool`

Rate limit durumunda olup olmadığını kontrol eder.

#### Örnek

```python
if handler.is_rate_limited():
    print("Rate limit durumunda!")
    # Alternatif strateji uygula
else:
    # Normal işleme devam et
    make_api_call()
```

### `get_wait_time(tokens: int = 0, requests: int = 1, audio_seconds: int = 0) → float`

Gerekli bekleme süresini hesaplar.

#### Parametreler

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `tokens` | `int` | `0` | Gereken token sayısı |
| `requests` | `int` | `1` | Gereken request sayısı |
| `audio_seconds` | `int` | `0` | Gereken ses saniyesi |

#### Örnek

```python
wait_time = handler.get_wait_time(tokens=100, requests=1)
if wait_time > 0:
    print(f"Bekleme süresi: {wait_time} saniye")
    time.sleep(wait_time)
```

## 🔄 Advanced Methods

### `can_proceed_with_priority(tokens: int, requests: int, priority: str = "normal") → bool`

Öncelik bazlı rate limit kontrolü.

#### Parametreler

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `tokens` | `int` | **Gerekli** | Gereken token sayısı |
| `requests` | `int` | **Gerekli** | Gereken request sayısı |
| `priority` | `str` | `"normal"` | Öncelik seviyesi |

#### Örnek

```python
# Yüksek öncelikli istek
can_proceed = handler.can_proceed_with_priority(
    tokens=50, 
    requests=1, 
    priority="high"
)

# Düşük öncelikli istek
can_proceed = handler.can_proceed_with_priority(
    tokens=200, 
    requests=1, 
    priority="low"
)
```

### `get_usage_percentages() → Dict[str, float]`

Kullanım yüzdelerini döndürür.

#### Örnek

```python
percentages = handler.get_usage_percentages()
print(f"Request usage: {percentages['request']}%")
print(f"Token usage: {percentages['token']}%")
print(f"Audio usage: {percentages['audio']}%")
```

#### Dönen Değer

```python
{
    'request': 0.01,
    'token': 0.22,
    'audio': 0.0
}
```

### `get_remaining_limits() → Dict[str, int]`

Kalan limitleri döndürür.

#### Örnek

```python
remaining = handler.get_remaining_limits()
print(f"Remaining requests: {remaining['requests']}")
print(f"Remaining tokens: {remaining['tokens']}")
print(f"Remaining audio seconds: {remaining['audio_seconds']}")
```

#### Dönen Değer

```python
{
    'requests': 14399,
    'tokens': 5987,
    'audio_seconds': 7200
}
```

## 🔧 Configuration Methods

### `set_api_callback(callback: Callable) → None`

API callback fonksiyonunu ayarlar.

#### Parametreler

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `callback` | `Callable` | API'den limit bilgisi alacak fonksiyon |

#### Örnek

```python
def my_api_callback():
    # API'den limit bilgisi alma
    response = requests.get("https://api.groq.com/v1/models")
    return response.headers

handler.set_api_callback(my_api_callback)
```

### `set_refresh_interval(interval: int) → None`

Otomatik yenileme aralığını ayarlar.

#### Parametreler

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `interval` | `int` | Yenileme aralığı (saniye) |

#### Örnek

```python
# 5 dakikada bir yenile
handler.set_refresh_interval(300)
```

## 🚨 Error Handling

### Yaygın Hatalar

#### `RateLimitExceeded`
Rate limit aşıldığında.

```python
try:
    handler.wait_if_needed(tokens=10000, requests=1)
except RateLimitExceeded as e:
    print(f"Rate limit exceeded: {e}")
    # Alternatif strateji uygula
```

#### `InvalidRateLimitData`
Geçersiz rate limit verisi.

```python
try:
    handler.update_from_response(invalid_headers)
except InvalidRateLimitData as e:
    print(f"Invalid rate limit data: {e}")
```

## 📊 Performance Optimizations

### 1. **Caching Strategy**
```python
# Rate limit bilgileri cache'lenir
# Son güncelleme zamanı takip edilir
# Gereksiz API çağrıları önlenir
```

### 2. **Thread Safety**
```python
# threading.Lock() kullanılır
# Çoklu thread desteği
# Race condition'lar önlenir
```

### 3. **Smart Refresh**
```python
# Otomatik yenileme
# API callback ile dinamik güncelleme
# Manuel zorla yenileme
```

## 🔍 Monitoring & Debugging

### Debug Mode
```python
# Debug bilgileri
handler.debug = True
status = handler.get_status()
# Detaylı log çıktısı
```

### Performance Metrics
```python
# Performans metrikleri
metrics = handler.get_performance_metrics()
print(f"API calls: {metrics['api_calls']}")
print(f"Cache hits: {metrics['cache_hits']}")
print(f"Wait time: {metrics['total_wait_time']}")
```

## 🔧 Advanced Usage

### Custom Rate Limit Strategy
```python
class CustomRateLimitStrategy:
    def __init__(self, base_handler):
        self.base_handler = base_handler
    
    def can_proceed_with_business_logic(self, tokens, requests, business_priority):
        # İş mantığına göre rate limit kontrolü
        if business_priority == "critical":
            return True  # Kritik işlemler için bypass
        
        return self.base_handler.can_proceed(tokens, requests)
```

### Rate Limit Monitoring
```python
def monitor_rate_limits(handler):
    while True:
        status = handler.get_status()
        summary = handler.get_status_summary()
        
        if summary['request_usage_percent'] > 80:
            print("⚠️ Rate limit yaklaşıyor!")
        
        if summary['request_usage_percent'] > 95:
            print("🚨 Rate limit kritik seviyede!")
        
        time.sleep(60)  # Her dakika kontrol et

# Monitoring thread'i başlat
import threading
monitor_thread = threading.Thread(target=monitor_rate_limits, args=(handler,))
monitor_thread.daemon = True
monitor_thread.start()
```

### Rate Limit Analytics
```python
def analyze_rate_limit_usage(handler, duration_hours=24):
    """Rate limit kullanım analizi"""
    start_time = time.time()
    usage_data = []
    
    while time.time() - start_time < duration_hours * 3600:
        status = handler.get_status()
        usage_data.append({
            'timestamp': time.time(),
            'request_usage': status['request_remaining'] / status['request_limit'],
            'token_usage': status['token_remaining'] / status['token_limit']
        })
        time.sleep(300)  # 5 dakikada bir
    
    return usage_data
```

---

Bu handler, **akıllı**, **performanslı** ve **güvenilir** rate limit yönetimi sağlar. Gerçek zamanlı takip, otomatik bekleme ve dinamik güncelleme özellikleri ile enterprise seviyesinde API kullanımı için optimize edilmiştir. 