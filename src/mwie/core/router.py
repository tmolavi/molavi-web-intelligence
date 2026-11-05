"""
Intelligent Extraction Router with Evidence-Based Fallbacks for MWIE.
Selects optimal extraction backend based on requirements, historical metrics, and resource costs.
"""

from mwie.core.models import ExtractionOptions
from mwie.extraction.base import BaseExtractionAdapter, RawExtraction
from mwie.extraction.registry import registry


class ExtractionRouter:
    def __init__(self, adapter_registry=None):
        self.registry = adapter_registry or registry

    async def select_adapter(self, options: ExtractionOptions) -> BaseExtractionAdapter:
        """Select primary adapter based on options, availability, and cost."""
        # 1. Explicit user override
        if options.preferred_adapter:
            adapter = self.registry.get(options.preferred_adapter)
            if adapter and await adapter.is_available():
                return adapter

        # 2. If JavaScript rendering is explicitly requested
        if options.render_js:
            browser_adapter = self.registry.get("playwright_browser")
            if browser_adapter and await browser_adapter.is_available():
                return browser_adapter
            firecrawl_adapter = self.registry.get("firecrawl_api")
            if firecrawl_adapter and await firecrawl_adapter.is_available():
                return firecrawl_adapter

        # 3. Default: low-cost, high-speed native HTTP
        http_adapter = self.registry.get("native_http")
        if http_adapter and await http_adapter.is_available():
            return http_adapter

        # 4. Fallback to any available adapter
        for name in self.registry.list_adapters():
            ad = self.registry.get(name)
            if ad and await ad.is_available():
                return ad

        raise RuntimeError("No available extraction adapters found in registry.")

    async def execute_with_fallback(self, url: str, options: ExtractionOptions) -> RawExtraction:
        """
        Executes extraction using the selected adapter and falls back cleanly if a failure occurs.
        """
        primary = await self.select_adapter(options)
        candidates: list[BaseExtractionAdapter] = [primary]

        # Populate fallbacks
        for name in self.registry.list_adapters():
            ad = self.registry.get(name)
            if ad and ad.name != primary.name and await ad.is_available():
                candidates.append(ad)

        last_error = None
        for adapter in candidates:
            try:
                raw = await adapter.extract(url, options)
                self.registry.record_success(adapter.name, raw.execution_time_ms)
                return raw
            except Exception as e:
                self.registry.record_failure(adapter.name)
                last_error = e
                continue

        raise RuntimeError(
            f"All extraction adapters failed for URL '{url}'. Last error: {last_error}"
        )


router = ExtractionRouter()
