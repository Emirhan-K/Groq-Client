# Rate limit aşıldığında isteklerin sıraya alınmasını sağlar 

import asyncio
import time
import threading
from typing import Dict, Any, Callable, Optional, List
from enum import Enum
from dataclasses import dataclass
from core.rate_limit_handler import RateLimitHandler
from exceptions.errors import (
    RateLimitExceeded, QueueError, QueueFullError, ValidationError, 
    ThreadingError, LockError, RetryError, RequestTimeoutError
)


class Priority(Enum):
    """İstek öncelik seviyeleri"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class QueuedRequest:
    """Sıraya alınan istek bilgileri"""
    id: str
    request_func: Callable
    args: tuple
    kwargs: dict
    priority: Priority
    timestamp: float
    retry_count: int = 0
    max_retries: int = 3
    tokens_required: int = 0
    original_priority: Priority = None


class QueueManager:
    """Rate limit aşıldığında istekleri sıraya alan ve işleyen yönetici"""
    
    def __init__(self, rate_limit_handler: Optional[RateLimitHandler] = None, max_queue_size: int = 1000):
        """
        QueueManager'ı başlatır
        
        Args:
            rate_limit_handler: Rate limit handler (opsiyonel)
            max_queue_size: Maksimum sıra boyutu
            
        Raises:
            ThreadingError: Thread oluşturma hatası
            ValidationError: Geçersiz parametreler
        """
        if max_queue_size <= 0:
            raise ValidationError("max_queue_size", "Max queue size must be positive")
            
        try:
            self.rate_limit_handler = rate_limit_handler or RateLimitHandler()
            self.max_queue_size = max_queue_size
            self._queues: Dict[Priority, List[QueuedRequest]] = {
                priority: [] for priority in Priority
            }
            self._processing = False
            self._async_lock = asyncio.Lock()
            self._sync_lock = threading.Lock()
            self._request_counter = 0
            self._loop = None
            self._task = None
            
            # İstatistikler
            self._stats = {
                'total_queued': 0,
                'total_processed': 0,
                'total_failed': 0,
                'total_retries': 0
            }
        except Exception as e:
            raise ThreadingError(f"Failed to initialize QueueManager: {str(e)}")
    
    async def _generate_request_id(self) -> str:
        """
        Benzersiz istek ID'si oluşturur
        
        Raises:
            LockError: Lock edinme hatası
        """
        try:
            async with self._async_lock:
                self._request_counter += 1
                return f"req_{int(time.time())}_{self._request_counter}"
        except Exception as e:
            raise LockError(f"Failed to acquire lock: {str(e)}")
    
    async def enqueue(self, request_func: Callable, *args, priority: str = "normal", 
                tokens_required: int = 0, max_retries: int = 3, **kwargs) -> str:
        """
        İsteği sıraya alır
        
        Args:
            request_func: Çalıştırılacak fonksiyon
            *args: Fonksiyon argümanları
            priority: Öncelik seviyesi ("low", "normal", "high", "urgent")
            tokens_required: Gereken token sayısı
            max_retries: Maksimum yeniden deneme sayısı
            **kwargs: Fonksiyon keyword argümanları
            
        Returns:
            İstek ID'si
            
        Raises:
            ValidationError: Geçersiz parametreler
            QueueFullError: Sıra dolu
            LockError: Lock edinme hatası
        """
        if not callable(request_func):
            raise ValidationError("request_func", "Request function must be callable")
            
        if tokens_required < 0:
            raise ValidationError("tokens_required", "Tokens required cannot be negative")
            
        if max_retries < 0:
            raise ValidationError("max_retries", "Max retries cannot be negative")
        
        # Öncelik seviyesini doğrula
        try:
            priority_enum = Priority(priority.lower())
        except ValueError:
            priority_enum = Priority.NORMAL
        
        # Sıra boyutunu kontrol et
        try:
            async with self._async_lock:
                total_queued = sum(len(queue) for queue in self._queues.values())
                if total_queued >= self.max_queue_size:
                    raise QueueFullError(total_queued, self.max_queue_size)
        except Exception as e:
            raise LockError(f"Failed to acquire lock: {str(e)}")
        
        # İstek ID'si oluştur
        request_id = await self._generate_request_id()
        
        # İsteği oluştur
        queued_request = QueuedRequest(
            id=request_id,
            request_func=request_func,
            args=args,
            kwargs=kwargs,
            priority=priority_enum,
            timestamp=time.time(),
            max_retries=max_retries,
            tokens_required=tokens_required,
            original_priority=priority_enum
        )
        
        # Sıraya ekle
        try:
            async with self._async_lock:
                self._queues[priority_enum].append(queued_request)
                self._stats['total_queued'] += 1
        except Exception as e:
            raise LockError(f"Failed to acquire lock: {str(e)}")
        
        # İşleme başlat (eğer başlamamışsa)
        await self._start_processing()
        
        return request_id
    
    async def _start_processing(self) -> None:
        """
        İşleme döngüsünü başlatır
        
        Raises:
            ThreadingError: Thread başlatma hatası
        """
        if self._processing:
            return
        
        try:
            async with self._async_lock:
                if self._processing:
                    return
                self._processing = True
            
            # Async loop'u başlat
            if self._loop is None or self._loop.is_closed():
                self._loop = asyncio.get_event_loop()
            
            self._task = self._loop.create_task(self._process_queue_async())
        except Exception as e:
            raise ThreadingError(f"Failed to start processing: {str(e)}")
    
    async def _process_queue_async(self) -> None:
        """Async işleme döngüsü"""
        while self._processing:
            try:
                # Öncelik sırasına göre istekleri işle
                for priority in [Priority.URGENT, Priority.HIGH, Priority.NORMAL, Priority.LOW]:
                    await self._process_priority_queue(priority)
                
                # Kısa bir bekleme
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Queue processing error: {e}")
                await asyncio.sleep(1)
    
    async def _process_priority_queue(self, priority: Priority) -> None:
        """
        Belirli öncelik seviyesindeki sırayı işler
        
        Raises:
            LockError: Lock edinme hatası
        """
        try:
            async with self._async_lock:
                if not self._queues[priority]:
                    return
                
                # İsteği al (FIFO)
                request = self._queues[priority].pop(0)
        except Exception as e:
            raise LockError(f"Failed to acquire lock: {str(e)}")
        
        try:
            # Rate limit kontrolü
            if not self.rate_limit_handler.can_proceed(request.tokens_required):
                # Rate limit aşılmış, isteği tekrar sıraya al
                try:
                    async with self._async_lock:
                        self._queues[priority].insert(0, request)
                except Exception as e:
                    raise LockError(f"Failed to re-queue request: {str(e)}")
                return
            
            # İsteği işle
            await self._execute_request(request)
            
        except Exception as e:
            print(f"Error processing request {request.id}: {e}")
            await self._handle_request_error(request, e)
    
    async def _execute_request(self, request: QueuedRequest) -> None:
        """
        İsteği çalıştırır
        
        Raises:
            RequestTimeoutError: Zaman aşımı hatası
            RetryError: Yeniden deneme hatası
        """
        try:
            # Rate limit handler'dan izin al
            self.rate_limit_handler.wait_if_needed()
            
            # İsteği çalıştır
            if asyncio.iscoroutinefunction(request.request_func):
                result = await request.request_func(*request.args, **request.kwargs)
            else:
                # Sync fonksiyonlar için uyarı
                print("⚠️ Sync fonksiyon async kuyruğa eklendi. Lütfen mümkünse async fonksiyon kullanın.")
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, request.request_func, *request.args, **request.kwargs
                )
            
            # Başarılı işlem
            try:
                async with self._async_lock:
                    self._stats['total_processed'] += 1
            except Exception as e:
                raise LockError(f"Failed to update stats: {str(e)}")
            
        except asyncio.TimeoutError as e:
            raise RequestTimeoutError(30, f"Request timeout: {str(e)}")
        except Exception as e:
            raise e
    
    async def _handle_request_error(self, request: QueuedRequest, error: Exception) -> None:
        """
        İstek hatasını işler
        
        Raises:
            RetryError: Maksimum yeniden deneme sayısı aşıldığında
            LockError: Lock edinme hatası
        """
        try:
            async with self._async_lock:
                self._stats['total_failed'] += 1
        except Exception as e:
            raise LockError(f"Failed to update stats: {str(e)}")
        
        # Yeniden deneme kontrolü
        if request.retry_count < request.max_retries:
            request.retry_count += 1
            
            try:
                async with self._async_lock:
                    self._stats['total_retries'] += 1
                    # İsteği tekrar orijinal önceliğiyle sıraya al
                    request.priority = request.original_priority or request.priority
                    self._queues[request.priority].append(request)
            except Exception as e:
                raise LockError(f"Failed to retry request: {str(e)}")
        else:
            # Maksimum yeniden deneme sayısı aşıldı
            raise RetryError(request.max_retries, error)
    
    def process_queue(self) -> None:
        """
        Senkron işleme döngüsü (async kullanılamadığında)
        
        Raises:
            ThreadingError: Thread işleme hatası
        """
        try:
            while self._has_pending_requests():
                self._process_sync()
                time.sleep(0.1)
        except Exception as e:
            raise ThreadingError(f"Failed to process queue: {str(e)}")
    
    def _has_pending_requests(self) -> bool:
        """
        Bekleyen istek olup olmadığını kontrol eder
        
        Raises:
            LockError: Lock edinme hatası
        """
        try:
            with self._sync_lock:
                return any(len(queue) > 0 for queue in self._queues.values())
        except Exception as e:
            raise LockError(f"Failed to check pending requests: {str(e)}")
    
    def _process_sync(self) -> None:
        """
        Senkron işleme (tek seferlik)
        
        Raises:
            LockError: Lock edinme hatası
        """
        try:
            with self._sync_lock:
                # Öncelik sırasına göre istekleri işle
                for priority in [Priority.URGENT, Priority.HIGH, Priority.NORMAL, Priority.LOW]:
                    if self._queues[priority]:
                        request = self._queues[priority].pop(0)
                        break
                else:
                    return  # Hiç istek yok
        except Exception as e:
            raise LockError(f"Failed to get request from queue: {str(e)}")
        
        try:
            # Rate limit kontrolü
            if not self.rate_limit_handler.can_proceed(request.tokens_required):
                # Rate limit aşılmış, isteği tekrar sıraya al
                try:
                    with self._sync_lock:
                        self._queues[request.priority].insert(0, request)
                except Exception as e:
                    raise LockError(f"Failed to re-queue request: {str(e)}")
                return
            
            # İsteği işle
            self.rate_limit_handler.wait_if_needed()
            result = request.request_func(*request.args, **request.kwargs)
            
            # Başarılı işlem
            try:
                with self._sync_lock:
                    self._stats['total_processed'] += 1
            except Exception as e:
                raise LockError(f"Failed to update stats: {str(e)}")
                
        except Exception as e:
            self._handle_request_error_sync(request, e)
    
    def _handle_request_error_sync(self, request: QueuedRequest, error: Exception) -> None:
        """
        Senkron istek hatası işleme
        
        Raises:
            RetryError: Maksimum yeniden deneme sayısı aşıldığında
            LockError: Lock edinme hatası
        """
        try:
            with self._sync_lock:
                self._stats['total_failed'] += 1
        except Exception as e:
            raise LockError(f"Failed to update stats: {str(e)}")
        
        # Yeniden deneme kontrolü
        if request.retry_count < request.max_retries:
            request.retry_count += 1
            
            try:
                with self._sync_lock:
                    self._stats['total_retries'] += 1
                    # İsteği tekrar orijinal önceliğiyle sıraya al
                    request.priority = request.original_priority or request.priority
                    self._queues[request.priority].append(request)
            except Exception as e:
                raise LockError(f"Failed to retry request: {str(e)}")
        else:
            # Maksimum yeniden deneme sayısı aşıldı
            raise RetryError(request.max_retries, error)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Sıra durumunu döndürür
        
        Returns:
            Sıra durum bilgileri
            
        Raises:
            LockError: Lock edinme hatası
        """
        try:
            with self._sync_lock:
                queue_sizes = {
                    priority.value: len(queue) 
                    for priority, queue in self._queues.items()
                }
                
                return {
                    'queue_sizes': queue_sizes,
                    'total_queued': sum(queue_sizes.values()),
                    'stats': self._stats.copy(),
                    'processing': self._processing,
                    'max_queue_size': self.max_queue_size
                }
        except Exception as e:
            raise LockError(f"Failed to get queue status: {str(e)}")
    
    def clear_queue(self, priority: Optional[str] = None) -> None:
        """
        Sırayı temizler
        
        Args:
            priority: Temizlenecek öncelik seviyesi (opsiyonel)
            
        Raises:
            ValidationError: Geçersiz öncelik seviyesi
            LockError: Lock edinme hatası
        """
        try:
            with self._sync_lock:
                if priority is None:
                    # Tüm sıraları temizle
                    for queue in self._queues.values():
                        queue.clear()
                else:
                    # Belirli öncelik seviyesini temizle
                    try:
                        priority_enum = Priority(priority.lower())
                        self._queues[priority_enum].clear()
                    except ValueError:
                        raise ValidationError("priority", f"Invalid priority: {priority}")
        except Exception as e:
            raise LockError(f"Failed to clear queue: {str(e)}")
    
    def stop_processing(self) -> None:
        """
        İşlemeyi durdurur
        
        Raises:
            ThreadingError: Thread durdurma hatası
        """
        try:
            self._processing = False
            if self._task and not self._task.done():
                self._task.cancel()
        except Exception as e:
            raise ThreadingError(f"Failed to stop processing: {str(e)}") 