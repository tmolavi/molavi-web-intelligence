"""
Hermes Agent Skill Integration for Molavi Web Intelligence Engine (MWIE).
Allows Hermes autonomous agents to trigger deep website audits, SEO diagnostics, and GEO entity graphs.
"""

from typing import Any

import httpx


class HermesMWIESkill:
    """Hermes Agent Skill wrapper connecting to MWIE REST or MCP endpoint."""

    def __init__(self, mwie_api_url: str = "http://127.0.0.1:8000"):
        self.api_url = mwie_api_url.rstrip("/")

    async def audit_url_for_seo(self, url: str) -> dict[str, Any]:
        """Audit target URL and return technical SEO scorecard."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.api_url}/api/v1/seo", json={"url": url, "options": {"extract_seo": True}}
            )
            resp.raise_for_status()
            return resp.json()

    async def extract_geo_intelligence(self, url: str) -> dict[str, Any]:
        """Extract brand entities, citations, and AI-readiness for Generative Search."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.api_url}/api/v1/geo", json={"url": url, "options": {"extract_geo": True}}
            )
            resp.raise_for_status()
            return resp.json()

    async def compare_competitors(self, urls: list[str]) -> dict[str, Any]:
        """Compare competitors side-by-side."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.api_url}/api/v1/compare", json={"urls": urls})
            resp.raise_for_status()
            return resp.json()
