"""
Adapter Registry and Performance Telemetry for MWIE.
Tracks real execution metrics without synthetic scores.
"""

from typing import Any

from mwie.core.models import AdapterStats
from mwie.extraction.base import BaseExtractionAdapter
from mwie.extraction.firecrawl_adapter import FirecrawlAdapter
from mwie.extraction.http_adapter import NativeHttpAdapter
from mwie.extraction.playwright_adapter import PlaywrightAdapter


class AdapterRegistry:
    def __init__(self):
        self._adapters: dict[str, BaseExtractionAdapter] = {}
        self._metrics: dict[str, dict[str, Any]] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(NativeHttpAdapter())
        self.register(PlaywrightAdapter())
        self.register(FirecrawlAdapter())

    def register(self, adapter: BaseExtractionAdapter):
        self._adapters[adapter.name] = adapter
        if adapter.name not in self._metrics:
            self._metrics[adapter.name] = {
                "success_count": 0,
                "failure_count": 0,
                "total_calls": 0,
                "total_latency_ms": 0.0,
                "cost_weight": adapter.cost_weight,
            }

    def get(self, name: str) -> BaseExtractionAdapter | None:
        return self._adapters.get(name)

    def list_adapters(self) -> list[str]:
        return list(self._adapters.keys())

    def record_success(self, name: str, latency_ms: float):
        if name in self._metrics:
            m = self._metrics[name]
            m["success_count"] += 1
            m["total_calls"] += 1
            m["total_latency_ms"] += latency_ms

    def record_failure(self, name: str):
        if name in self._metrics:
            m = self._metrics[name]
            m["failure_count"] += 1
            m["total_calls"] += 1

    def get_stats(self) -> list[AdapterStats]:
        stats = []
        for name, m in self._metrics.items():
            calls = m["total_calls"]
            successes = m["success_count"]
            avg_lat = (m["total_latency_ms"] / successes) if successes > 0 else 0.0
            rate = (successes / calls) if calls > 0 else 0.0
            stats.append(
                AdapterStats(
                    name=name,
                    success_count=successes,
                    failure_count=m["failure_count"],
                    total_calls=calls,
                    avg_latency_ms=round(avg_lat, 2),
                    success_rate=round(rate, 4),
                    cost_weight=m["cost_weight"],
                )
            )
        return stats


registry = AdapterRegistry()
