"""AKShare 请求速率限制与防封禁模块。

提供以下功能：
- 请求伪装（浏览器请求头）
- 请求间隔控制（避免请求过于频繁）
- 指数退避重试机制（遇到封禁时自动重试）
- 简单缓存（避免重复请求相同数据）
- 数据源轮换（主数据源失败时自动切换备选）
"""

import hashlib
import json
import logging
import random
import threading
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, TypeVar

from . import headers as req_headers

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar("T")


class RateLimiter:
    """请求速率限制器。"""

    def __init__(
        self,
        min_interval: float = 1.0,
        max_interval: float = 3.0,
        enable_random: bool = True,
    ):
        """
        初始化速率限制器。

        @param min_interval: 最小请求间隔（秒）
        @param max_interval: 最大请求间隔（秒），配合 random 使用
        @param enable_random: 是否启用随机延迟（更安全）
        """
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.enable_random = enable_random
        self._last_request_time = 0.0
        self._lock = threading.Lock()

    def wait(self) -> None:
        """等待直到可以发送下一个请求。"""
        # 初始化请求头伪装（首次调用时）
        req_headers.init_headers()
        
        # 轮换 User-Agent（每次请求前随机更换）
        req_headers.rotate_ua()
        
        with self._lock:
            now = time.time()
            elapsed = now - self._last_request_time

            if elapsed < self.min_interval:
                # 计算需要等待的时间
                if self.enable_random:
                    wait_time = random.uniform(self.min_interval, self.max_interval)
                else:
                    wait_time = self.min_interval
                
                sleep_time = wait_time - elapsed
                if sleep_time > 0:
                    logger.debug(f"速率限制: 等待 {sleep_time:.2f} 秒")
                    time.sleep(sleep_time)

            self._last_request_time = time.time()

    def set_interval(self, min_interval: float, max_interval: float | None = None) -> None:
        """动态调整间隔。"""
        self.min_interval = min_interval
        if max_interval is not None:
            self.max_interval = max_interval


class RetryHandler:
    """重试处理器，支持指数退避。"""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 5.0,
        max_delay: float = 60.0,
        enable_random: bool = True,
    ):
        """
        初始化重试处理器。

        @param max_retries: 最大重试次数
        @param base_delay: 基础延迟（秒），每次重试翻倍
        @param max_delay: 最大延迟（秒）
        @param enable_random: 是否添加随机抖动
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.enable_random = enable_random

    def is_retryable_error(self, error: Exception) -> bool:
        """判断错误是否可重试。"""
        error_str = str(error).lower()
        
        # 网络相关错误
        retryable_keywords = [
            "connection",
            "timeout",
            "reset",
            "refused",
            "403",
            "429",
            "rate limit",
            "too many request",
            "forbidden",
            "network",
        ]
        
        return any(keyword in error_str for keyword in retryable_keywords)

    def calculate_delay(self, attempt: int) -> float:
        """计算延迟时间（指数退避）。"""
        delay = self.base_delay * (2 ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.enable_random:
            delay += random.uniform(1, 3)
        
        return delay

    def execute(self, func: Callable[[], T], *args, **kwargs) -> T:
        """
        执行函数，支持重试。

        @param func: 要执行的函数
        @param args: 位置参数
        @param kwargs: 关键字参数
        @returns: 函数返回值
        @raises: 所有重试都失败后抛出最后一个异常
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e

                if not self.is_retryable_error(e):
                    logger.warning(f"不可重试的错误: {e}")
                    raise

                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt)
                    logger.warning(
                        f"请求受限 (尝试 {attempt + 1}/{self.max_retries + 1}), "
                        f"等待 {delay:.1f} 秒后重试... 错误: {e}"
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"达到最大重试次数 {self.max_retries}, 请求失败")

        raise last_error


class DataCache:
    """简单的内存缓存。"""

    def __init__(self, ttl_seconds: int = 300):
        """
        初始化缓存。

        @param ttl_seconds: 缓存有效期（秒），默认 5 分钟
        """
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self._lock = threading.Lock()

    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键。"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key: str) -> Any | None:
        """获取缓存值。"""
        with self._lock:
            if key in self._cache:
                value, expire_time = self._cache[key]
                if datetime.now() < expire_time:
                    logger.debug(f"缓存命中: {key[:16]}...")
                    return value
                else:
                    # 过期删除
                    del self._cache[key]
                    logger.debug(f"缓存过期: {key[:16]}...")
        return None

    def set(self, key: str, value: Any) -> None:
        """设置缓存值。"""
        with self._lock:
            expire_time = datetime.now() + timedelta(seconds=self.ttl_seconds)
            self._cache[key] = (value, expire_time)
            logger.debug(f"缓存写入: {key[:16]}...")

    def clear(self) -> None:
        """清空缓存。"""
        with self._lock:
            self._cache.clear()
            logger.info("缓存已清空")


class SourceRouter:
    """数据源路由器，支持自动切换。"""

    # 数据源优先级配置
    DEFAULT_SOURCES = {
        "info": ["em", "xq"],
        "spot": ["em", "sina"],
        "hist": ["em", "tx", "sina"],
        "minute": ["em", "sina"],
        "intraday": ["em", "sina"],
    }

    def __init__(self, sources: dict[str, list[str]] | None = None):
        """
        初始化数据源路由器。

        @param sources: 自定义数据源配置，默认使用 DEFAULT_SOURCES
        """
        self.sources = sources or self.DEFAULT_SOURCES
        self._failed_sources: dict[str, set[str]] = {}  # 记录失败的数据源
        self._lock = threading.Lock()

    def get_source(self, operation: str, preferred: str | None = None) -> str | None:
        """
        获取可用的数据源。

        @param operation: 操作类型 (info/spot/hist/minute/intraday)
        @param preferred: 首选数据源
        @returns: 可用的数据源名称，如果都不可用返回 None
        """
        with self._lock:
            # 获取该操作可用的数据源列表
            available_sources = self.sources.get(operation, [])
            
            # 排除已知失败的数据源
            failed = self._failed_sources.get(operation, set())
            candidates = [s for s in available_sources if s not in failed]

            # 如果有首选数据源且可用，优先使用
            if preferred and preferred in candidates:
                return preferred

            # 返回第一个候选数据源
            return candidates[0] if candidates else None

    def mark_failed(self, operation: str, source: str) -> None:
        """标记数据源失败。"""
        with self._lock:
            if operation not in self._failed_sources:
                self._failed_sources[operation] = set()
            self._failed_sources[operation].add(source)
            logger.warning(f"数据源 {source} 已标记为失败 (操作: {operation})")

    def mark_success(self, operation: str, source: str) -> None:
        """标记数据源成功，恢复使用。"""
        with self._lock:
            if operation in self._failed_sources:
                self._failed_sources[operation].discard(source)

    def reset(self) -> None:
        """重置失败记录。"""
        with self._lock:
            self._failed_sources.clear()
            logger.info("数据源失败记录已重置")


# 全局单例
_rate_limiter: RateLimiter | None = None
_retry_handler: RetryHandler | None = None
_cache: DataCache | None = None
_source_router: SourceRouter | None = None


def get_rate_limiter() -> RateLimiter:
    """获取全局速率限制器。"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(
            min_interval=1.0,
            max_interval=3.0,
            enable_random=True,
        )
    return _rate_limiter


def get_retry_handler() -> RetryHandler:
    """获取全局重试处理器。"""
    global _retry_handler
    if _retry_handler is None:
        _retry_handler = RetryHandler(
            max_retries=3,
            base_delay=5.0,
            max_delay=60.0,
            enable_random=True,
        )
    return _retry_handler


def get_cache() -> DataCache:
    """获取全局缓存。"""
    global _cache
    if _cache is None:
        _cache = DataCache(ttl_seconds=300)  # 5分钟缓存
    return _cache


def get_source_router() -> SourceRouter:
    """获取全局数据源路由器。"""
    global _source_router
    if _source_router is None:
        _source_router = SourceRouter()
    return _source_router


def configure_rate_limiter(
    min_interval: float = 1.0,
    max_interval: float = 3.0,
    enable_random: bool = True,
) -> None:
    """配置全局速率限制器。"""
    global _rate_limiter
    _rate_limiter = RateLimiter(min_interval, max_interval, enable_random)


def configure_retry_handler(
    max_retries: int = 3,
    base_delay: float = 5.0,
    max_delay: float = 60.0,
) -> None:
    """配置全局重试处理器。"""
    global _retry_handler
    _retry_handler = RetryHandler(max_retries, base_delay, max_delay)


# 装饰器：自动应用速率限制
def rate_limited(func: Callable[..., T]) -> Callable[..., T]:
    """装饰器：自动应用速率限制。"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        limiter = get_rate_limiter()
        limiter.wait()
        return func(*args, **kwargs)

    return wrapper


# 装饰器：自动重试
def with_retry(func: Callable[..., T]) -> Callable[..., T]:
    """装饰器：自动重试。"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        handler = get_retry_handler()
        return handler.execute(func, *args, **kwargs)

    return wrapper


# 装饰器：带缓存
def cached(prefix: str, ttl: int = 300) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """装饰器：带缓存的请求。"""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # 生成缓存键（排除最后几个参数中的 sensitive 数据）
            cache_key = cache._make_key(prefix, *args, **kwargs)
            
            # 尝试获取缓存
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        return wrapper

    return decorator
