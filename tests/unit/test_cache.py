import time

from mwie.core.cache import MemoryCache


def test_memory_cache_ttl():
    c = MemoryCache(default_ttl=1)
    c.set("https://molavi.pro", {"status": "ok"}, ttl=1)

    assert c.get("https://molavi.pro") == {"status": "ok"}
    time.sleep(1.1)
    # Expired
    assert c.get("https://molavi.pro") is None
