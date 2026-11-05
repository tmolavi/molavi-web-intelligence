"""
In-Memory Priority Request Queue for MWIE Crawlers.
Provides URL deduplication, depth tracking, and domain-bounded filtering.
"""

import hashlib
from collections import deque
from urllib.parse import urlparse, urlunparse


class CrawlItem:
    def __init__(self, url: str, depth: int = 0):
        self.url = url
        self.depth = depth


class RequestQueue:
    def __init__(self, max_pages: int = 100, max_depth: int = 2):
        self.max_pages = max_pages
        self.max_depth = max_depth
        self._queue = deque()
        self._visited_hashes: set[str] = set()

    def _canonicalize(self, url: str) -> str:
        parsed = urlparse(url)
        # Lowercase scheme and netloc, strip trailing slash and default ports
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"
        clean = urlunparse((parsed.scheme.lower(), netloc, path, "", parsed.query, ""))
        return clean

    def _hash(self, url: str) -> str:
        clean = self._canonicalize(url)
        return hashlib.sha256(clean.encode("utf-8")).hexdigest()

    def push(self, url: str, depth: int = 0) -> bool:
        if depth > self.max_depth:
            return False
        if len(self._visited_hashes) >= self.max_pages:
            return False

        h = self._hash(url)
        if h in self._visited_hashes:
            return False

        self._visited_hashes.add(h)
        self._queue.append(CrawlItem(url, depth))
        return True

    def pop(self) -> CrawlItem | None:
        if not self._queue:
            return None
        return self._queue.popleft()

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def total_enqueued(self) -> int:
        return len(self._visited_hashes)

    def remaining(self) -> int:
        return len(self._queue)
