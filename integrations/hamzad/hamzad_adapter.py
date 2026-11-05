"""
Hamzad AI Ecosystem Adapter for Molavi Web Intelligence Engine (MWIE).
Enables Hamzad voice/avatar intelligence agents and digital twin pipelines to ingest
live website knowledge, verify author source citations, and extract brand entity graphs.
"""

from typing import Any

import httpx


class HamzadMWIEAdapter:
    """Hamzad intelligence pipeline adapter."""

    def __init__(self, endpoint_url: str = "http://127.0.0.1:8000"):
        self.endpoint = endpoint_url.rstrip("/")

    async def ingest_brand_knowledge(self, url: str) -> dict[str, Any]:
        """
        Extract brand knowledge, Q&A blocks, and semantic text chunks
        for Hamzad memory stores and talking avatar prompts.
        """
        async with httpx.AsyncClient(timeout=40.0) as client:
            resp = await client.post(
                f"{self.endpoint}/api/v1/extract",
                json={
                    "url": url,
                    "options": {
                        "clean_html": True,
                        "generate_markdown": True,
                        "extract_seo": True,
                        "extract_geo": True,
                    },
                },
            )
            resp.raise_for_status()
            data = resp.json()

            geo = data.get("geo") or {}
            return {
                "url": url,
                "primary_brand": geo.get("primary_brand"),
                "entities": geo.get("entities", []),
                "qa_blocks": geo.get("qa_knowledge_blocks", []),
                "semantic_chunks": geo.get("semantic_chunks", []),
                "ai_readiness_score": geo.get("ai_readiness_score"),
                "markdown": data.get("markdown", ""),
            }
