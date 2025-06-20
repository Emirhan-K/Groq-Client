# 📚 Models Reference

## Genel Bakış

Bu dokümantasyon, Groq API'de kullanılabilir tüm modellerin detaylı referansını içerir. Her model için özellikler, kullanım alanları ve performans bilgileri sağlanır.

## 🤖 Text Generation Models

### Chat Models

#### `llama3-8b-8192`
**En popüler ve dengeli model**

- **Tip**: Chat/Completion
- **Parametre Sayısı**: 8B
- **Context Length**: 8,192 tokens
- **Max Output**: 8,192 tokens
- **Hız**: ⚡⚡⚡⚡⚡ (Çok hızlı)
- **Kalite**: ⭐⭐⭐⭐ (İyi)

**Özellikler:**
- Çok hızlı yanıt süresi
- Genel amaçlı kullanım
- Türkçe desteği
- Uygun fiyat

**Kullanım Alanları:**
- Genel sohbet
- Kod yazma
- Metin analizi
- Hızlı prototipleme

**Örnek Kullanım:**
```python
response = client.text.generate(
    model="llama3-8b-8192",
    messages=[
        {"role": "user", "content": "Python'da bir web scraper nasıl yazılır?"}
    ],
    max_tokens=500,
    temperature=0.7
)
```

#### `llama3-70b-8192`
**Yüksek kaliteli, büyük model**

- **Tip**: Chat/Completion
- **Parametre Sayısı**: 70B
- **Context Length**: 8,192 tokens
- **Max Output**: 8,192 tokens
- **Hız**: ⚡⚡⚡ (Orta)
- **Kalite**: ⭐⭐⭐⭐⭐ (Mükemmel)

**Özellikler:**
- Yüksek kaliteli yanıtlar
- Karmaşık görevler için uygun
- Detaylı analiz
- Yaratıcı içerik

**Kullanım Alanları:**
- Karmaşık analizler
- Yaratıcı yazım
- Teknik dokümantasyon
- Eğitim materyali

**Örnek Kullanım:**
```python
response = client.text.generate(
    model="llama3-70b-8192",
    messages=[
        {"role": "system", "content": "Sen deneyimli bir yazılım mimarısın."},
        {"role": "user", "content": "Mikroservis mimarisi hakkında detaylı bir analiz yap."}
    ],
    max_tokens=1000,
    temperature=0.3
)
```

#### `mixtral-8x7b-32768`
**Uzun context desteği**

- **Tip**: Chat/Completion
- **Parametre Sayısı**: 47B (8x7B mixture)
- **Context Length**: 32,768 tokens
- **Max Output**: 32,768 tokens
- **Hız**: ⚡⚡⚡⚡ (Hızlı)
- **Kalite**: ⭐⭐⭐⭐⭐ (Mükemmel)

**Özellikler:**
- Çok uzun context desteği
- Yüksek kalite
- Hızlı yanıt
- Çok dilli destek

**Kullanım Alanları:**
- Uzun doküman analizi
- Çok adımlı görevler
- Çeviri
- Kod analizi

**Örnek Kullanım:**
```python
response = client.text.generate(
    model="mixtral-8x7b-32768",
    messages=[
        {"role": "user", "content": "Bu uzun dokümanı analiz et ve özetle..."}
    ],
    max_tokens=2000,
    temperature=0.5
)
```

#### `gemma2-9b-it`
**Google'ın Gemma modeli**

- **Tip**: Chat/Completion
- **Parametre Sayısı**: 9B
- **Context Length**: 8,192 tokens
- **Max Output**: 8,192 tokens
- **Hız**: ⚡⚡⚡⚡ (Hızlı)
- **Kalite**: ⭐⭐⭐⭐ (İyi)

**Özellikler:**
- Google'ın açık kaynak modeli
- İyi performans
- Güvenli yanıtlar
- Çok dilli destek

**Kullanım Alanları:**
- Genel sohbet
- Eğitim
- İçerik oluşturma
- Güvenli uygulamalar

**Örnek Kullanım:**
```python
response = client.text.generate(
    model="gemma2-9b-it",
    messages=[
        {"role": "user", "content": "Güvenli şifre oluşturma hakkında bilgi ver."}
    ],
    max_tokens=300,
    temperature=0.2
)
```

### Completion Models

#### `llama3-8b-8192`
**Completion için de kullanılabilir**

```python
response = client.text.generate(
    model="llama3-8b-8192",
    prompt="Python'da bir fonksiyon yaz:",
    max_tokens=200,
    temperature=0.1
)
```

## 🎤 Speech-to-Text Models

### Whisper Models

#### `whisper-large-v3`
**En yüksek kaliteli STT modeli**

- **Tip**: Speech-to-Text
- **Dil Desteği**: 99+ dil
- **Maksimum Dosya Boyutu**: 25MB
- **Desteklenen Formatlar**: mp3, mp4, mpeg, mpga, m4a, wav, webm
- **Kalite**: ⭐⭐⭐⭐⭐ (Mükemmel)
- **Hız**: ⚡⚡⚡ (Orta)

**Özellikler:**
- Yüksek doğruluk
- Çok dilli destek
- Gürültü toleransı
- Punctuation desteği

**Kullanım Alanları:**
- Profesyonel transkripsiyon
- Çok dilli içerik
- Gürültülü ortamlar
- Yüksek doğruluk gerektiren uygulamalar

**Örnek Kullanım:**
```python
response = client.speech.transcribe(
    file="audio.mp3",
    model="whisper-large-v3",
    language="tr",  # Türkçe
    prompt="Bu ses dosyası teknik bir konuşma içeriyor"
)
```

#### `whisper-large-v3-turbo`
**Hızlı STT modeli**

- **Tip**: Speech-to-Text
- **Dil Desteği**: 99+ dil
- **Maksimum Dosya Boyutu**: 25MB
- **Desteklenen Formatlar**: mp3, mp4, mpeg, mpga, m4a, wav, webm
- **Kalite**: ⭐⭐⭐⭐ (İyi)
- **Hız**: ⚡⚡⚡⚡⚡ (Çok hızlı)

**Özellikler:**
- Çok hızlı işleme
- İyi doğruluk
- Gerçek zamanlı uygulamalar
- Düşük maliyet

**Kullanım Alanları:**
- Gerçek zamanlı transkripsiyon
- Canlı yayın
- Hızlı not alma
- Mobil uygulamalar

**Örnek Kullanım:**
```python
response = client.speech.transcribe(
    file="audio.wav",
    model="whisper-large-v3-turbo",
    language="en",  # İngilizce
    response_format="text"
)
```

## 📊 Model Karşılaştırması

### Text Generation Models

| Model | Parametre | Context | Hız | Kalite | Fiyat | Kullanım |
|-------|-----------|---------|-----|--------|-------|----------|
| `llama3-8b-8192` | 8B | 8K | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | $ | Genel |
| `llama3-70b-8192` | 70B | 8K | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | $$$ | Karmaşık |
| `mixtral-8x7b-32768` | 47B | 32K | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | $$ | Uzun |
| `gemma2-9b-it` | 9B | 8K | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | $ | Güvenli |

### Speech-to-Text Models

| Model | Kalite | Hız | Dil | Kullanım |
|-------|--------|-----|-----|----------|
| `whisper-large-v3` | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | 99+ | Profesyonel |
| `whisper-large-v3-turbo` | ⭐⭐⭐⭐ | ⚡⚡⚡⚡⚡ | 99+ | Hızlı |

## 🎯 Model Seçim Rehberi

### Text Generation için

#### Hızlı ve Ekonomik
```python
# Günlük kullanım, hızlı yanıt
model = "llama3-8b-8192"
```

#### Yüksek Kalite
```python
# Karmaşık görevler, detaylı analiz
model = "llama3-70b-8192"
```

#### Uzun Context
```python
# Uzun dokümanlar, çok adımlı görevler
model = "mixtral-8x7b-32768"
```

#### Güvenli Uygulamalar
```python
# Eğitim, güvenlik odaklı
model = "gemma2-9b-it"
```

### Speech-to-Text için

#### Profesyonel Kullanım
```python
# Yüksek doğruluk gerektiren
model = "whisper-large-v3"
```

#### Hızlı İşleme
```python
# Gerçek zamanlı, hızlı
model = "whisper-large-v3-turbo"
```

## 🔧 Model Konfigürasyonu

### Temperature Ayarları

```python
# Yaratıcı içerik (0.7-1.0)
response = client.text.generate(
    model="llama3-8b-8192",
    prompt="Yaratıcı bir hikaye yaz",
    temperature=0.8
)

# Dengeli yanıtlar (0.3-0.7)
response = client.text.generate(
    model="llama3-8b-8192",
    prompt="Bir konuyu açıkla",
    temperature=0.5
)

# Kesin yanıtlar (0.0-0.3)
response = client.text.generate(
    model="llama3-8b-8192",
    prompt="Faktları listele",
    temperature=0.1
)
```

### Max Tokens Ayarları

```python
# Kısa yanıtlar (50-200 tokens)
response = client.text.generate(
    model="llama3-8b-8192",
    prompt="Kısa bir özet yaz",
    max_tokens=100
)

# Orta yanıtlar (200-500 tokens)
response = client.text.generate(
    model="llama3-8b-8192",
    prompt="Detaylı açıklama yap",
    max_tokens=300
)

# Uzun yanıtlar (500+ tokens)
response = client.text.generate(
    model="llama3-8b-8192",
    prompt="Kapsamlı analiz yap",
    max_tokens=1000
)
```

## 🌍 Dil Desteği

### Desteklenen Diller

#### Text Generation
- **Türkçe**: ✅ Mükemmel
- **İngilizce**: ✅ Mükemmel
- **Almanca**: ✅ İyi
- **Fransızca**: ✅ İyi
- **İspanyolca**: ✅ İyi
- **İtalyanca**: ✅ İyi
- **Portekizce**: ✅ İyi
- **Rusça**: ✅ İyi
- **Çince**: ✅ İyi
- **Japonca**: ✅ İyi
- **Korece**: ✅ İyi
- **Arapça**: ✅ İyi

#### Speech-to-Text
- **Türkçe**: ✅ Mükemmel
- **İngilizce**: ✅ Mükemmel
- **99+ dil**: ✅ Destekleniyor

### Dil Belirtme

```python
# Text generation için
messages = [
    {"role": "system", "content": "Sen Türkçe konuşan bir asistansın."},
    {"role": "user", "content": "Merhaba!"}
]

# STT için
response = client.speech.transcribe(
    file="audio.mp3",
    model="whisper-large-v3",
    language="tr"  # Türkçe
)
```

## 📈 Performans Optimizasyonu

### Model Seçimi

```python
def choose_model(task_type, requirements):
    """Görev tipine göre model seçimi"""
    
    if task_type == "fast_response":
        return "llama3-8b-8192"
    elif task_type == "high_quality":
        return "llama3-70b-8192"
    elif task_type == "long_context":
        return "mixtral-8x7b-32768"
    elif task_type == "safe":
        return "gemma2-9b-it"
    else:
        return "llama3-8b-8192"  # Varsayılan
```

### Batch Processing

```python
def batch_process_with_optimal_model(texts):
    """Toplu işleme için optimal model seçimi"""
    
    # Kısa metinler için hızlı model
    short_texts = [t for t in texts if len(t) < 100]
    if short_texts:
        for text in short_texts:
            client.enqueue_request(
                client.text.generate,
                model="llama3-8b-8192",
                prompt=text,
                priority="high"
            )
    
    # Uzun metinler için kaliteli model
    long_texts = [t for t in texts if len(t) >= 100]
    if long_texts:
        for text in long_texts:
            client.enqueue_request(
                client.text.generate,
                model="llama3-70b-8192",
                prompt=text,
                priority="normal"
            )
    
    client.process_queue()
```

## 🔍 Model Bilgilerini Alma

### Kullanılabilir Modeller

```python
# Tüm modeller
all_models = client.get_available_models()
print(f"Toplam model sayısı: {len(all_models)}")

# Chat modelleri
chat_models = client.get_available_models("chat")
print(f"Chat modelleri: {chat_models}")

# STT modelleri
stt_models = client.get_available_models("stt")
print(f"STT modelleri: {stt_models}")
```

### Model Detayları

```python
# Model bilgileri
model_info = client.get_model_info("llama3-8b-8192")
print(f"Model ID: {model_info['id']}")
print(f"Max tokens: {model_info['max_tokens']}")
print(f"Model type: {model_info['type']}")
print(f"Context length: {model_info['context_length']}")
```

### Model Desteği Kontrolü

```python
# Model desteği
def check_model_support(model_name, task_type):
    """Model desteğini kontrol et"""
    
    if not client.is_model_supported(model_name):
        return False, "Model bulunamadı"
    
    model_info = client.get_model_info(model_name)
    
    if task_type == "chat" and model_info['type'] != "chat":
        return False, "Model chat için uygun değil"
    
    if task_type == "stt" and model_info['type'] != "stt":
        return False, "Model STT için uygun değil"
    
    return True, "Model destekleniyor"

# Kullanım
is_supported, message = check_model_support("llama3-8b-8192", "chat")
print(f"Destek: {is_supported}, Mesaj: {message}")
```

## 🚀 Gelecek Modeller

### Planlanan Özellikler

- **Daha büyük context**: 100K+ token desteği
- **Çok modal modeller**: Text + Image + Audio
- **Özel alan modelleri**: Tıp, hukuk, finans
- **Daha hızlı modeller**: Real-time uygulamalar
- **Daha küçük modeller**: Edge cihazlar için

### Model Güncellemeleri

```python
# Model güncellemelerini kontrol et
def check_model_updates():
    """Model güncellemelerini kontrol et"""
    
    current_models = set(client.get_available_models())
    cached_models = set(get_cached_model_list())
    
    new_models = current_models - cached_models
    removed_models = cached_models - current_models
    
    if new_models:
        print(f"Yeni modeller: {new_models}")
    
    if removed_models:
        print(f"Kaldırılan modeller: {removed_models}")
    
    return new_models, removed_models
```

---

Bu referans, tüm Groq modellerinin detaylı bilgilerini içerir. Model seçimi yaparken görev gereksinimlerinizi, performans ihtiyaçlarınızı ve maliyet kısıtlarınızı göz önünde bulundurun. 