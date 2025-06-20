# 🏗️ System Architecture

## Genel Bakış

Groq Dynamic Client System, **modüler**, **ölçeklenebilir** ve **thread-safe** bir mimari ile tasarlanmıştır. Sistem, farklı sorumlulukları ayrı katmanlara bölerek **Separation of Concerns** prensibini uygular.

## 🏛️ Mimari Katmanları

```
┌─────────────────────────────────────────────────────────────┐
│                    🎯 Application Layer                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   GroqClient    │  │  Custom Clients │  │   Examples   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    🔧 Handler Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │TextGeneration   │  │SpeechToText     │  │Custom Handlers│ │
│  │Handler          │  │Handler          │  │               │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    🧠 Core Layer                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │RateLimit    │ │TokenCounter │ │ModelRegistry│ │Queue    │ │
│  │Handler      │ │             │ │             │ │Manager  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    🌐 API Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   APIClient     │  │   Endpoints     │  │   HTTP/HTTPS │ │
│  │                 │  │                 │  │   Requests   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    🛡️ Exception Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Custom Errors  │  │  Error Handling │  │  Validation  │ │
│  │                 │  │                 │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Veri Akışı

### 1. **Text Generation Flow**
```
User Request → GroqClient → TextGenerationHandler → TokenCounter → RateLimitHandler → APIClient → Groq API
     ↑                                                                                           ↓
Response ← GroqClient ← TextGenerationHandler ← RateLimitHandler ← APIClient ← Groq API Response
```

### 2. **Speech-to-Text Flow**
```
Audio File → GroqClient → SpeechToTextHandler → RateLimitHandler → APIClient → Groq API
     ↑                                                                              ↓
Transcription ← GroqClient ← SpeechToTextHandler ← RateLimitHandler ← APIClient ← Groq API
```

### 3. **Queue Management Flow**
```
Request → QueueManager → RateLimitHandler → APIClient → Groq API
   ↑                                                           ↓
Response ← QueueManager ← RateLimitHandler ← APIClient ← Groq API
```

## 🧩 Bileşen Detayları

### 🎯 **Application Layer**
- **GroqClient**: Ana istemci sınıfı, tüm bileşenleri koordine eder
- **Custom Clients**: Özel kullanım senaryoları için genişletilebilir
- **Examples**: Kullanım örnekleri ve demo uygulamalar

### 🔧 **Handler Layer**
- **TextGenerationHandler**: Chat ve completion modelleri için
- **SpeechToTextHandler**: Ses dosyası transkripsiyonu için
- **Custom Handlers**: Özel işlemler için genişletilebilir

### 🧠 **Core Layer**
- **RateLimitHandler**: API rate limit yönetimi
- **TokenCounter**: Token sayımı ve limit kontrolü
- **ModelRegistry**: Model bilgileri ve kategorizasyon
- **QueueManager**: İstek sırası yönetimi

### 🌐 **API Layer**
- **APIClient**: HTTP/HTTPS istekleri
- **Endpoints**: API endpoint sabitleri
- **HTTP/HTTPS**: Ağ iletişimi

### 🛡️ **Exception Layer**
- **Custom Errors**: Özel hata sınıfları
- **Error Handling**: Hata yönetimi stratejileri
- **Validation**: Girdi doğrulama

## 🔒 Thread Safety

### Thread-Safe Bileşenler
- ✅ **RateLimitHandler**: `threading.Lock()` kullanır
- ✅ **TokenCounter**: Thread-safe token sayımı
- ✅ **ModelRegistry**: Cache thread-safe
- ✅ **QueueManager**: Async ve sync lock'lar
- ✅ **APIClient**: Session thread-safe

### Thread-Safe Olmayan Bileşenler
- ⚠️ **GroqClient**: Instance bazında thread-safe, paylaşımlı kullanımda dikkat
- ⚠️ **Handlers**: Instance bazında thread-safe

## 📊 Performance Optimizations

### 1. **Caching Strategy**
```python
# Model Registry Cache
model_cache = {
    'models': {...},      # Model listesi
    'last_update': 0,     # Son güncelleme zamanı
    'cache_duration': 300 # Cache süresi (5 dakika)
}
```

### 2. **Rate Limit Optimization**
```python
# Rate Limit Cache
rate_limit_cache = {
    'request_limit': 14400,
    'request_remaining': 14399,
    'token_limit': 6000,
    'token_remaining': 5987,
    'last_update': 1750393319.341
}
```

### 3. **Token Counting Optimization**
```python
# Token Cache
token_cache = {
    'text_hash': token_count,
    'model': 'llama3-8b-8192',
    'timestamp': 1750393319.341
}
```

## 🔄 State Management

### 1. **Rate Limit State**
```python
class RateLimitState:
    request_limit: int
    request_remaining: int
    token_limit: int
    token_remaining: int
    audio_seconds_limit: int
    audio_seconds_remaining: int
    last_update: float
```

### 2. **Queue State**
```python
class QueueState:
    queues: Dict[Priority, List[QueuedRequest]]
    processing: bool
    stats: Dict[str, int]
    max_queue_size: int
```

### 3. **Model Registry State**
```python
class ModelRegistryState:
    models: Dict[str, ModelInfo]
    categories: Dict[str, List[str]]
    last_update: float
    cache_duration: int
```

## 🎛️ Configuration Management

### 1. **Environment Variables**
```bash
GROQ_API_KEY=your-api-key
GROQ_BASE_URL=https://api.groq.com
GROQ_TIMEOUT=30
GROQ_MAX_RETRIES=3
```

### 2. **Runtime Configuration**
```python
class ClientConfig:
    api_key: str
    base_url: str
    timeout: int
    max_retries: int
    rate_limit_enabled: bool
    queue_enabled: bool
    cache_enabled: bool
```

## 🔍 Monitoring & Observability

### 1. **Performance Metrics**
- Request/Response times
- Token usage
- Rate limit utilization
- Queue performance
- Error rates

### 2. **Health Checks**
- API connectivity
- Rate limit status
- Queue health
- Model registry status

### 3. **Logging Strategy**
```python
# Log Levels
DEBUG: Detailed debugging information
INFO: General information about program execution
WARNING: Warning messages for potentially problematic situations
ERROR: Error messages for serious problems
CRITICAL: Critical error messages for fatal errors
```

## 🚀 Scalability Considerations

### 1. **Horizontal Scaling**
- Stateless design
- Shared rate limit state
- Distributed queue management
- Load balancing support

### 2. **Vertical Scaling**
- Connection pooling
- Memory optimization
- CPU utilization
- I/O optimization

### 3. **Resource Management**
- Memory usage monitoring
- Connection cleanup
- Cache size limits
- Queue size limits

## 🔧 Extension Points

### 1. **Custom Handlers**
```python
class CustomHandler:
    def __init__(self, api_client, model_registry, rate_limit_handler):
        self.api_client = api_client
        self.model_registry = model_registry
        self.rate_limit_handler = rate_limit_handler
    
    def process(self, *args, **kwargs):
        # Custom implementation
        pass
```

### 2. **Custom Rate Limit Strategies**
```python
class CustomRateLimitStrategy:
    def __init__(self, base_handler):
        self.base_handler = base_handler
    
    def can_proceed_with_priority(self, tokens, requests, priority):
        # Custom priority logic
        pass
```

### 3. **Custom Token Counting**
```python
class CustomTokenCounter:
    def __init__(self, model_registry):
        self.model_registry = model_registry
    
    def count_tokens(self, text, model):
        # Custom token counting logic
        pass
```

## 📈 Future Architecture Considerations

### 1. **Microservices Support**
- Service discovery
- Circuit breaker pattern
- Distributed tracing
- API gateway integration

### 2. **Event-Driven Architecture**
- Event sourcing
- CQRS pattern
- Message queues
- Event streaming

### 3. **Cloud-Native Features**
- Kubernetes support
- Service mesh integration
- Cloud monitoring
- Auto-scaling

---

Bu mimari, **modüler**, **genişletilebilir** ve **sürdürülebilir** bir sistem sağlar. Her katman kendi sorumluluğuna odaklanır ve diğer katmanlarla gevşek bağlantılıdır. 