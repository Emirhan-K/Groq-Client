# 📚 Groq Client Documentation

Bu klasör, Groq Dynamic Client System'in kapsamlı dokümantasyonunu içerir.

## 📖 Dokümantasyon İçeriği

### 🏗️ **Architecture & Design**
- [System Architecture](architecture.md) - Sistem mimarisi ve tasarım prensipleri
- [Component Overview](components.md) - Bileşen genel bakışı *(Yakında)*
- [Data Flow](data-flow.md) - Veri akışı ve işlem süreçleri *(Yakında)*

### 🔧 **API Reference**
- [GroqClient](api/groq-client.md) - Ana istemci sınıfı
- [APIClient](api/api-client.md) - HTTP API istemcisi *(Yakında)*
- [TextGenerationHandler](api/text-generation.md) - Text generation handler *(Yakında)*
- [SpeechToTextHandler](api/speech-to-text.md) - Speech-to-text handler *(Yakında)*

### 🧠 **Core Components**
- [RateLimitHandler](core/rate-limit-handler.md) - Rate limit yönetimi
- [TokenCounter](core/token-counter.md) - Token sayımı *(Yakında)*
- [ModelRegistry](core/model-registry.md) - Model kayıt sistemi *(Yakında)*
- [QueueManager](core/queue-manager.md) - İstek sırası yönetimi *(Yakında)*

### 🛡️ **Error Handling**
- [Exceptions](exceptions/errors.md) - Hata sınıfları ve kullanımı *(Yakında)*
- [Error Handling Guide](exceptions/error-handling.md) - Hata yönetimi rehberi *(Yakında)*

### 🧪 **Examples & Tutorials**
- [Basic Usage](examples/basic-usage.md) - Temel kullanım örnekleri *(Yakında)*
- [Advanced Features](examples/advanced-features.md) - Gelişmiş özellikler *(Yakında)*
- [Integration Examples](examples/integration.md) - Entegrasyon örnekleri *(Yakında)*
- [Custom Implementations](examples/custom.md) - Özel implementasyonlar *(Yakında)*

### 🔍 **Guides**
- [Installation Guide](guides/installation.md) - Kurulum rehberi *(Yakında)*
- [Configuration Guide](guides/configuration.md) - Yapılandırma rehberi *(Yakında)*
- [Performance Tuning](guides/performance.md) - Performans optimizasyonu *(Yakında)*
- [Troubleshooting](guides/troubleshooting.md) - Sorun giderme

### 📊 **Reference**
- [Models Reference](reference/models.md) - Model referansı
- [API Endpoints](reference/endpoints.md) - API endpoint'leri *(Yakında)*
- [Rate Limits](reference/rate-limits.md) - Rate limit referansı *(Yakında)*
- [Error Codes](reference/error-codes.md) - Hata kodları *(Yakında)*

## 🚀 Hızlı Başlangıç

### 📖 İlk Kez Kullanıyorsanız:
1. [Installation Guide](guides/installation.md) - Kurulum *(Yakında)*
2. [Basic Usage](examples/basic-usage.md) - Temel kullanım *(Yakında)*
3. [GroqClient API](api/groq-client.md) - Ana API referansı

### 🔧 Geliştirici iseniz:
1. [System Architecture](architecture.md) - Sistem mimarisi
2. [Component Overview](components.md) - Bileşenler *(Yakında)*
3. [Custom Implementations](examples/custom.md) - Özel implementasyonlar *(Yakında)*

### 🛠️ Production'a geçiyorsanız:
1. [Configuration Guide](guides/configuration.md) - Yapılandırma *(Yakında)*
2. [Performance Tuning](guides/performance.md) - Performans *(Yakında)*
3. [Error Handling Guide](exceptions/error-handling.md) - Hata yönetimi *(Yakında)*

## 🎯 Öne Çıkan Dokümantasyonlar

### 🏗️ **System Architecture** *(Tamamlandı)*
Sistemin mimari yapısını, bileşenler arası ilişkileri ve veri akışını detaylı olarak açıklar.

**İçerik:**
- Mimari katmanları
- Veri akışı diyagramları
- Thread safety
- Performance optimizations
- Extension points

### 🎯 **GroqClient API Reference** *(Tamamlandı)*
Ana istemci sınıfının tüm metodlarını, parametrelerini ve kullanım örneklerini içerir.

**İçerik:**
- Constructor ve properties
- Text generation methods
- Speech-to-text methods
- Token management
- Rate limit methods
- Queue management
- Error handling

### ⚡ **RateLimitHandler API Reference** *(Tamamlandı)*
Rate limit yönetimi için akıllı handler'ın detaylı dokümantasyonu.

**İçerik:**
- Core methods
- Status methods
- Advanced methods
- Configuration
- Performance optimizations
- Monitoring & debugging

### 📚 **Models Reference** *(Tamamlandı)*
Tüm Groq modellerinin detaylı referansı ve karşılaştırması.

**İçerik:**
- Text generation models
- Speech-to-text models
- Model karşılaştırması
- Seçim rehberi
- Konfigürasyon
- Dil desteği

### 🔍 **Troubleshooting Guide** *(Tamamlandı)*
Yaygın sorunlar ve çözümleri için kapsamlı rehber.

**İçerik:**
- Authentication errors
- Rate limit errors
- Model errors
- File errors
- Network errors
- Debug techniques
- Performance optimization

## 📝 Dokümantasyon Katkısı

Bu dokümantasyonu geliştirmek için:

1. **Yeni özellik** eklediyseniz → İlgili API dokümantasyonunu güncelleyin
2. **Örnek** eklediyseniz → Examples klasörüne ekleyin
3. **Hata** bulduysanız → Issues'da bildirin
4. **İyileştirme** öneriniz varsa → Pull Request açın

### Dokümantasyon Standartları

- **Markdown formatı** kullanın
- **Emoji'ler** ile görsel zenginlik katın
- **Kod örnekleri** ekleyin
- **Tablo'lar** kullanın
- **Başlık hiyerarşisi** düzenli tutun
- **Link'ler** ekleyin

## 🔗 Faydalı Linkler

- [GitHub Repository](https://github.com/yourusername/groq-client)
- [Groq API Documentation](https://console.groq.com/docs)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## 📊 Dokümantasyon Durumu

| Kategori | Durum | Tamamlanma |
|----------|-------|------------|
| Architecture | ✅ Tamamlandı | 100% |
| API Reference | 🔄 Devam Ediyor | 25% |
| Core Components | 🔄 Devam Ediyor | 25% |
| Error Handling | ⏳ Planlandı | 0% |
| Examples | ⏳ Planlandı | 0% |
| Guides | 🔄 Devam Ediyor | 25% |
| Reference | 🔄 Devam Ediyor | 25% |

**Açıklama:**
- ✅ Tamamlandı
- 🔄 Devam Ediyor
- ⏳ Planlandı

---

**💡 İpucu**: Dokümantasyonda arama yapmak için `Ctrl+F` kullanın!

**📧 Geri Bildirim**: Dokümantasyon hakkında geri bildirim için [GitHub Issues](https://github.com/yourusername/groq-client/issues) kullanın. 