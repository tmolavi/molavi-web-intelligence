"""
High-performance TTL caching layer for crawl and extraction results.
Supports local in-memory storage and optional Redis integration.
"""

import hashlib
import time
from typing import Any

from mwie.core.config import settings


class MemoryCache:
    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl
        self._store: dict[str, dict[str, Any]] = {}

    def _make_key(self, url: str, options_hash: str = "") -> str:
        raw = f"{url}:{options_hash}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, url: str, options_hash: str = "") -> Any | None:
        if not settings.cache_enabled:
            return None
        key = self._make_key(url, options_hash)
        entry = self._store.get(key)
        if not entry:
            return None
        if time.time() > entry["expires_at"]:
            del self._store[key]
            return None
        return entry["data"]

    def set(self, url: str, data: Any, options_hash: str = "", ttl: int | None = None) -> None:
        if not settings.cache_enabled:
            return
        key = self._make_key(url, options_hash)
        ttl = ttl if ttl is not None else self.default_ttl
        self._store[key] = {
            "data": data,
            "expires_at": time.time() + ttl,
        }

    def clear(self) -> None:
        self._store.clear()

    def size(self) -> int:
        # Purge expired before returning count
        now = time.time()
        expired = [k for k, v in self._store.items() if now > v["expires_at"]]
        for k in expired:
            del self._store[k]
        return len(self._store)


cache = MemoryCache(default_ttl=settings.cache_ttl_seconds)
