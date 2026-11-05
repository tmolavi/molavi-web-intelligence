"""
Native Asynchronous HTTP Extraction Adapter for MWIE.
High-throughput, minimal memory footprint, zero browser overhead.
"""

import time

import httpx

from mwie.core.config import settings
from mwie.core.models import ExtractionOptions
from mwie.core.security import validate_target_url
from mwie.extraction.base import BaseExtractionAdapter, RawExtraction


class NativeHttpAdapter(BaseExtractionAdapter):
    name: str = "native_http"
    cost_weight: float = 1.0
    supports_js: bool = False

    def __init__(self):
        self.headers = {
            "User-Agent": settings.default_user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def is_available(self) -> bool:
        return True

    async def extract(self, url: str, options: ExtractionOptions) -> RawExtraction:
        validated_url = validate_target_url(
            url,
            allow_private_ips=settings.allow_private_ips,
            allowed_domains=settings.allowed_domains,
            blocked_domains=settings.blocked_domains,
        )

        start_time = time.perf_counter()
        timeout = httpx.Timeout(options.timeout_sec or settings.request_timeout)

        async with httpx.AsyncClient(
            headers=self.headers,
            timeout=timeout,
            follow_redirects=True,
            verify=False,
        ) as client:
            resp = await client.get(validated_url)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            resp_headers = {k.lower(): v for k, v in resp.headers.items()}

            return RawExtraction(
                url=url,
                final_url=str(resp.url),
                status_code=resp.status_code,
                html=resp.text,
                headers=resp_headers,
                rendered_js=False,
                adapter_name=self.name,
                execution_time_ms=round(elapsed_ms, 2),
            )
