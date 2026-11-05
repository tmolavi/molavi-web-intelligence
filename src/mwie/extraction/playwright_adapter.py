"""
Playwright Headless Browser Adapter for MWIE.
Renders client-side JavaScript, handles dynamic single-page apps (SPAs), and captures rendered DOM.
"""

import time

from mwie.core.config import settings
from mwie.core.models import ExtractionOptions
from mwie.core.security import validate_target_url
from mwie.extraction.base import BaseExtractionAdapter, RawExtraction


class PlaywrightAdapter(BaseExtractionAdapter):
    name: str = "playwright_browser"
    cost_weight: float = 4.5  # Higher CPU/memory weight than raw HTTP
    supports_js: bool = True

    def __init__(self):
        self._available: bool | None = None

    async def is_available(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                # Quick verification that chromium executable can be found
                browser = await p.chromium.launch(headless=True)
                await browser.close()
            self._available = True
        except Exception:
            self._available = False
        return self._available

    async def extract(self, url: str, options: ExtractionOptions) -> RawExtraction:
        validated_url = validate_target_url(
            url,
            allow_private_ips=settings.allow_private_ips,
            allowed_domains=settings.allowed_domains,
            blocked_domains=settings.blocked_domains,
        )

        from playwright.async_api import async_playwright

        start_time = time.perf_counter()
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=settings.headless_browser,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
            )
            context = await browser.new_context(
                user_agent=settings.default_user_agent,
                viewport={"width": settings.viewport_width, "height": settings.viewport_height},
            )
            page = await context.new_page()

            timeout_ms = int((options.timeout_sec or 25.0) * 1000)
            page.set_default_timeout(timeout_ms)

            response = await page.goto(validated_url, wait_until="domcontentloaded")

            if options.wait_for_selector:
                try:
                    await page.wait_for_selector(options.wait_for_selector, timeout=5000)
                except Exception:
                    pass

            # Optional extra idle wait for SPAs
            await page.wait_for_timeout(500)

            html = await page.content()
            final_url = page.url
            status_code = response.status if response else 200
            headers = response.headers if response else {}

            await browser.close()

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            return RawExtraction(
                url=url,
                final_url=final_url,
                status_code=status_code,
                html=html,
                headers=headers,
                rendered_js=True,
                adapter_name=self.name,
                execution_time_ms=round(elapsed_ms, 2),
            )
