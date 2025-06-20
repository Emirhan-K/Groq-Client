# 🎯 GroqClient API Reference

## Genel Bakış

`GroqClient`, Groq API ile etkileşim kurmak için tasarlanmış ana istemci sınıfıdır. Tüm bileşenleri koordine eder ve kullanıcı dostu bir arayüz sağlar.

## 📋 Sınıf Tanımı

```python
class GroqClient:
    """Groq API ile etkileşim için ana istemci sınıfı"""
```

## 🔧 Constructor

### `__init__(api_key: str, base_url: str = "https://api.groq.com")`

Ana istemciyi başlatır.

#### Parametreler

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `api_key` | `str` | **Gerekli** | Groq API anahtarı |
| `base_url` | `str` | `"https://api.groq.com"` | API base URL'i |

#### Örnek

```python
from client.groq_client import GroqClient

# Temel kullanım
client = GroqClient("your-api-key")

# Özel base URL ile
client = GroqClient(
    api_key="your-api-key",
    base_url="https://api.groq.com"
)
```

#### Hatalar

- `ValidationError`: Geçersiz parametreler
- `ConfigurationError`: Yapılandırma hatası
- `ClientInitializationError`: Başlatma hatası

## 🎯 Properties

### `text` → `TextGenerationHandler`

Text generation handler'ına erişim sağlar.

```python
# Text generation
response = client.text.generate(
    model="llama3-8b-8192",
    messages=[{"role": "user", "content": "Merhaba!"}],
    max_tokens=100
)
```

### `speech` → `SpeechToTextHandler`

Speech-to-text handler'ına erişim sağlar.

```python
# Speech-to-text
response = client.speech.transcribe(
    file="audio.mp3",
    model="whisper-large-v3"
)
```

### `rate_limit_handler` → `RateLimitHandler`

Rate limit handler'ına erişim sağlar.

```python
# Rate limit durumu
status = client.rate_limit_handler.get_status()
print(f"Request remaining: {status['request_remaining']}")
```

## 🔤 Text Generation Methods

### `text.generate(model: str, prompt: str = None, messages: List[Dict[str, str]] = None, **kwargs) → Dict[str, Any]`

Text tamamlaması oluşturur.

#### Parametreler

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `model` | `str` | **Gerekli** | Kullanılacak model adı |
| `prompt` | `str` | `None` | Tek satırlık prompt |
| `messages` | `List[Dict[str, str]]` | `None` | Mesaj listesi |
| `max_tokens` | `int` | `None` | Maksimum token sayısı |
| `temperature` | `float` | `None` | Yaratıcılık seviyesi (0-2) |
| `top_p` | `float` | `None` | Nucleus sampling parametresi |
| `stream` | `bool` | `False` | Streaming yanıt |

#### Örnek

```python
# Prompt ile
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

print(response['choices'][0]['message']['content'])
```

#### Dönen Değer

```python
{
    'id': 'chatcmpl-...',
    'object': 'chat.completion',
    'created': 1750393319,
    'model': 'llama3-8b-8192',
    'choices': [
        {
            'index': 0,
            'message': {
                'role': 'assistant',
                'content': 'Yanıt metni...'
            },
            'finish_reason': 'stop'
        }
    ],
    'usage': {
        'prompt_tokens': 21,
        'completion_tokens': 50,
        'total_tokens': 71
    }
}
```

## 🎤 Speech-to-Text Methods

### `speech.transcribe(file: Union[str, Path], model: str, **kwargs) → Dict[str, Any]`

Ses dosyasını yazıya çevirir.

#### Parametreler

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `file` | `Union[str, Path]` | **Gerekli** | Ses dosyası yolu |
| `model` | `str` | **Gerekli** | STT model adı |
| `language` | `str` | `None` | Dil kodu (tr, en, es, vb.) |
| `prompt` | `str` | `None` | Transkripsiyon için prompt |
| `response_format` | `str` | `"text"` | Yanıt formatı |

#### Örnek

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

print(response['text'])
```

#### Dönen Değer

```python
{
    'text': 'Transkripsiyon metni...',
    'x_groq': {
        'id': 'req_...'
    }
}
```

## 🔢 Token Management Methods

### `count_tokens(text: str, model: str) → int`

Metnin token sayısını hesaplar.

#### Parametreler

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `text` | `str` | Hesaplanacak metin |
| `model` | `str` | Model adı |

#### Örnek

```python
tokens = client.count_tokens("Bu bir test metnidir.", "llama3-8b-8192")
print(f"Token sayısı: {tokens}")
```

### `count_message_tokens(messages: List[Dict[str, str]], model: str) → int`

Mesaj listesinin token sayısını hesaplar.

#### Parametreler

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `messages` | `List[Dict[str, str]]` | Mesaj listesi |
| `model` | `str` | Model adı |

#### Örnek

```python
messages = [
    {"role": "user", "content": "Merhaba"},
    {"role": "assistant", "content": "Merhaba! Size nasıl yardımcı olabilirim?"}
]
tokens = client.count_message_tokens(messages, "llama3-8b-8192")
print(f"Mesaj token sayısı: {tokens}")
```

### `get_usage_info(messages: List[Dict[str, str]], model: str, max_tokens: int = 0) → Dict[str, Any]`

Token kullanım bilgilerini döndürür.

#### Parametreler

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `messages` | `List[Dict[str, str]]` | **Gerekli** | Mesaj listesi |
| `model` | `str` | **Gerekli** | Model adı |
| `max_tokens` | `int` | `0` | Maksimum token sayısı |

#### Örnek

```python
usage_info = client.get_usage_info(messages, "llama3-8b-8192", max_tokens=100)
print(f"Toplam token: {usage_info['total_tokens']}")
print(f"Prompt token: {usage_info['prompt_tokens']}")
print(f"Completion token: {usage_info['completion_tokens']}")
```

## 📊 Rate Limit Methods

### `get_rate_limit_status() → Dict[str, Any]`

Rate limit durumunu döndürür.

#### Örnek

```python
status = client.get_rate_limit_status()
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

## 📋 Queue Management Methods

### `enqueue_request(request_func, *args, priority: str = "normal", tokens_required: int = 0, max_retries: int = 3, **kwargs) → str`

İsteği sıraya alır.

#### Parametreler

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `request_func` | `Callable` | **Gerekli** | Çalıştırılacak fonksiyon |
| `*args` | `tuple` | - | Fonksiyon argümanları |
| `priority` | `str` | `"normal"` | Öncelik seviyesi |
| `tokens_required` | `int` | `0` | Gereken token sayısı |
| `max_retries` | `int` | `3` | Maksimum yeniden deneme |
| `**kwargs` | `dict` | - | Fonksiyon keyword argümanları |

#### Örnek

```python
request_id = client.enqueue_request(
    client.text.generate,
    model="llama3-8b-8192",
    prompt="Test mesajı",
    priority="high",
    tokens_required=50
)
print(f"İstek ID: {request_id}")
```

### `process_queue() → None`

İstek sırasını işler.

#### Örnek

```python
client.process_queue()
```

### `get_queue_status() → Dict[str, Any]`

Sıra durumunu döndürür.

#### Örnek

```python
queue_status = client.get_queue_status()
print(f"Total queued: {queue_status['total_queued']}")
print(f"Processing: {queue_status['processing']}")
```

#### Dönen Değer

```python
{
    'queue_sizes': {
        'low': 0,
        'normal': 0,
        'high': 0,
        'urgent': 0
    },
    'total_queued': 0,
    'stats': {
        'total_queued': 0,
        'total_processed': 0,
        'total_failed': 0,
        'total_retries': 0
    },
    'processing': False,
    'max_queue_size': 1000
}
```

### `clear_queue(priority: Optional[str] = None) → None`

Sırayı temizler.

#### Parametreler

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `priority` | `Optional[str]` | `None` | Temizlenecek öncelik |

#### Örnek

```python
# Tüm sırayı temizle
client.clear_queue()

# Sadece düşük öncelikli istekleri temizle
client.clear_queue(priority="low")
```

### `stop_queue_processing() → None`

Sıra işlemeyi durdurur.

#### Örnek

```python
client.stop_queue_processing()
```

## 🔍 Model Information Methods

### `get_available_models(model_type: Optional[str] = None) → List[str]`

Kullanılabilir modelleri listeler.

#### Parametreler

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `model_type` | `Optional[str]` | `None` | Model tipi filtresi |

#### Örnek

```python
# Tüm modeller
all_models = client.get_available_models()

# Sadece chat modelleri
chat_models = client.get_available_models("chat")

# Sadece STT modelleri
stt_models = client.get_available_models("stt")

print(f"Chat models: {len(chat_models)}")
print(f"STT models: {len(stt_models)}")
```

### `get_model_info(model: str) → Dict[str, Any]`

Model bilgilerini döndürür.

#### Parametreler

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `model` | `str` | Model adı |

#### Örnek

```python
model_info = client.get_model_info("llama3-8b-8192")
print(f"Max tokens: {model_info['max_tokens']}")
print(f"Model type: {model_info['type']}")
```

#### Dönen Değer

```python
{
    'id': 'llama3-8b-8192',
    'object': 'model',
    'created': 1703120000,
    'owned_by': 'groq',
    'max_tokens': 8192,
    'type': 'chat',
    'context_length': 8192
}
```

### `is_model_supported(model: str) → bool`

Model'in desteklenip desteklenmediğini kontrol eder.

#### Parametreler

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `model` | `str` | Model adı |

#### Örnek

```python
is_supported = client.is_model_supported("llama3-8b-8192")
if is_supported:
    print("Model destekleniyor")
else:
    print("Model desteklenmiyor")
```

## 🔄 Context Manager Methods

### `__enter__() → GroqClient`

Context manager girişi.

### `__exit__(exc_type, exc_val, exc_tb) → None`

Context manager çıkışı.

#### Örnek

```python
with GroqClient("your-api-key") as client:
    response = client.text.generate(
        model="llama3-8b-8192",
        prompt="Merhaba!",
        max_tokens=50
    )
    print(response['choices'][0]['message']['content'])
```

## 🧹 Cleanup Methods

### `close() → None`

İstemciyi kapatır ve kaynakları temizler.

#### Örnek

```python
client = GroqClient("your-api-key")
try:
    # İstemci kullanımı
    response = client.text.generate(...)
finally:
    client.close()
```

## 🚨 Error Handling

### Yaygın Hatalar

#### `ValidationError`
Geçersiz parametreler için.

```python
try:
    client = GroqClient("")  # Boş API key
except ValidationError as e:
    print(f"Validation error: {e}")
```

#### `AuthenticationError`
Kimlik doğrulama hatası.

```python
try:
    response = client.text.generate(...)
except AuthenticationError as e:
    print(f"Authentication error: {e}")
```

#### `RateLimitExceeded`
Rate limit aşımı.

```python
try:
    response = client.text.generate(...)
except RateLimitExceeded as e:
    print(f"Rate limit exceeded: {e}")
    # Otomatik bekleme yapılır
```

#### `InvalidModel`
Geçersiz model.

```python
try:
    response = client.text.generate(
        model="gecersiz-model",
        prompt="Test"
    )
except InvalidModel as e:
    print(f"Invalid model: {e}")
```

## 📊 Performance Tips

### 1. **Connection Reuse**
```python
# İstemciyi yeniden kullan
client = GroqClient("your-api-key")

for i in range(10):
    response = client.text.generate(...)
    # İstemci otomatik olarak connection'ı yeniden kullanır
```

### 2. **Batch Processing**
```python
# Toplu işleme için queue kullan
for prompt in prompts:
    client.enqueue_request(
        client.text.generate,
        model="llama3-8b-8192",
        prompt=prompt,
        priority="normal"
    )

client.process_queue()
```

### 3. **Rate Limit Monitoring**
```python
# Rate limit durumunu sürekli izle
status = client.get_rate_limit_status()
if status['request_remaining'] < 10:
    print("Rate limit yaklaşıyor!")
```

## 🔧 Advanced Usage

### Custom Configuration
```python
# Özel yapılandırma ile
client = GroqClient(
    api_key="your-api-key",
    base_url="https://api.groq.com"
)

# Rate limit handler'a erişim
rate_handler = client.rate_limit_handler
rate_handler.force_refresh(api_callback)
```

### Error Recovery
```python
def safe_generate(client, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.text.generate(
                model="llama3-8b-8192",
                prompt=prompt,
                max_tokens=100
            )
        except RateLimitExceeded:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
```

---

Bu API, **güçlü**, **esnek** ve **kullanıcı dostu** bir arayüz sağlar. Tüm temel işlemler için optimize edilmiş metodlar içerir ve enterprise seviyesinde hata yönetimi sunar. 