"""
Firecrawl Decoupled REST API Adapter for MWIE.
Clean-room implementation that communicates with any external or self-hosted Firecrawl instance
over standard HTTP without copying or linking AGPL code.
"""

import time

import httpx

from mwie.core.config import settings
from mwie.core.models import ExtractionOptions
from mwie.core.security import validate_target_url
from mwie.extraction.base import BaseExtractionAdapter, RawExtraction


class FirecrawlAdapter(BaseExtractionAdapter):
    name: str = "firecrawl_api"
    cost_weight: float = 6.0  # External API weight
    supports_js: bool = True

    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = (api_url or settings.firecrawl_api_url or "").rstrip("/")
        self.api_key = api_key or settings.firecrawl_api_key

    async def is_available(self) -> bool:
        return bool(self.api_url)

    async def extract(self, url: str, options: ExtractionOptions) -> RawExtraction:
        if not self.api_url:
            raise RuntimeError("Firecrawl API URL is not configured. Set MWIE_FIRECRAWL_API_URL.")

        validated_url = validate_target_url(
            url,
            allow_private_ips=settings.allow_private_ips,
            allowed_domains=settings.allowed_domains,
            blocked_domains=settings.blocked_domains,
        )

        start_time = time.perf_counter()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "url": validated_url,
            "pageOptions": {
                "includeHtml": True,
                "onlyMainContent": options.clean_html,
            },
        }

        async with httpx.AsyncClient(timeout=options.timeout_sec or 30.0) as client:
            resp = await client.post(f"{self.api_url}/v1/scrape", json=payload, headers=headers)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            if resp.status_code != 200:
                raise RuntimeError(f"Firecrawl API error: {resp.status_code} - {resp.text}")

            data = resp.json().get("data", {})
            html = data.get("html") or data.get("markdown", "")

            return RawExtraction(
                url=url,
                final_url=data.get("metadata", {}).get("sourceURL", url),
                status_code=data.get("metadata", {}).get("statusCode", 200),
                html=html,
                headers={},
                rendered_js=True,
                adapter_name=self.name,
                execution_time_ms=round(elapsed_ms, 2),
            )
