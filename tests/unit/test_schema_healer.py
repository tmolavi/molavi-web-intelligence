import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from mwie.core.models import ExtractionOptions
from mwie.crawler.engine import CrawlEngine
from mwie.extraction.base import RawExtraction
from mwie.seo.schema_healer import ATTRIBUTION_COMMENT, SchemaHealer

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "sample_page.html"


def _parse_healed_json(healed_schema: str) -> dict:
    lines = healed_schema.splitlines()
    assert lines[0] == ATTRIBUTION_COMMENT
    return json.loads("\n".join(lines[1:]))


def test_schema_healer_detects_gaps_and_synthesizes_graph():
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    healer = SchemaHealer(raw_html=html, url="https://molavi.pro/mwie")
    gaps, healed_schema = healer.heal()

    assert gaps.needs_healing is True
    assert gaps.is_healthy is False
    assert gaps.has_unified_graph is False
    assert gaps.has_anchored_person is False
    assert gaps.has_authoritative_same_as is False
    assert gaps.has_in_language is False
    assert gaps.has_valid_organization is False
    assert len(gaps.detected_gaps) >= 4

    payload = _parse_healed_json(healed_schema)
    assert payload["@context"] == "https://schema.org"
    graph = payload["@graph"]
    types = {node["@type"] for node in graph}
    assert {"WebSite", "Organization", "Person", "Service"}.issubset(types)

    org_node = next(n for n in graph if n["@type"] == "Organization")
    person_node = next(n for n in graph if n["@type"] == "Person")
    website_node = next(n for n in graph if n["@type"] == "WebSite")
    service_node = next(n for n in graph if n["@type"] == "Service")

    assert person_node["name"] == "Taqi Molavi"
    assert org_node["founder"]["@id"] == person_node["@id"]
    assert website_node["inLanguage"] == "en"
    assert service_node["provider"]["@id"] == org_node["@id"]
    assert any("wikidata.org" in u for u in org_node["sameAs"])
    assert any("linkedin.com" in u for u in org_node["sameAs"])
    assert any("github.com" in u for u in org_node["sameAs"])


def test_schema_healer_recognizes_healthy_graph():
    healthy_html = """<!DOCTYPE html>
    <html lang="fa">
    <head>
      <title>Molavi Pro</title>
      <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@graph": [
          {
            "@type": "WebSite",
            "@id": "https://molavi.pro/#website",
            "url": "https://molavi.pro/",
            "name": "Molavi Pro",
            "inLanguage": "fa",
            "publisher": {"@id": "https://molavi.pro/#organization"}
          },
          {
            "@type": "Organization",
            "@id": "https://molavi.pro/#organization",
            "name": "InTen Agency",
            "url": "https://molavi.pro/",
            "logo": "https://molavi.pro/logo.png",
            "founder": {"@id": "https://molavi.pro/#person"},
            "sameAs": [
              "https://www.wikidata.org/wiki/Q123456",
              "https://www.linkedin.com/in/taqimolavi",
              "https://github.com/tmolavi"
            ]
          },
          {
            "@type": "Person",
            "@id": "https://molavi.pro/#person",
            "name": "Taqi Molavi"
          },
          {
            "@type": "Service",
            "@id": "https://molavi.pro/#service",
            "name": "GEO Audit",
            "inLanguage": "fa",
            "provider": {"@id": "https://molavi.pro/#organization"}
          }
        ]
      }
      </script>
    </head>
    <body><h1>Molavi Pro</h1></body>
    </html>
    """
    healer = SchemaHealer(raw_html=healthy_html, url="https://molavi.pro/")
    gaps, healed_schema = healer.heal()

    assert gaps.is_healthy is True
    assert gaps.needs_healing is False
    assert gaps.has_unified_graph is True
    assert gaps.has_anchored_person is True
    assert gaps.has_authoritative_same_as is True
    assert gaps.has_in_language is True
    assert gaps.has_valid_organization is True
    assert gaps.has_valid_website is True
    assert gaps.detected_gaps == []

    payload = _parse_healed_json(healed_schema)
    assert len(payload["@graph"]) >= 4


def test_schema_healer_discovers_html_authority_links_and_article():
    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
      <title>AI Visibility Guide | ExampleBrand</title>
      <meta name="description" content="Complete guide to AI visibility.">
      <meta property="og:type" content="article">
    </head>
    <body>
      <h1>AI Visibility Guide</h1>
      <a href="https://github.com/examplebrand">GitHub</a>
      <a href="https://www.linkedin.com/company/examplebrand">LinkedIn</a>
      <a href="https://www.wikidata.org/wiki/Q999999">Wikidata</a>
    </body>
    </html>
    """
    healer = SchemaHealer(raw_html=html, url="https://examplebrand.com/blog/ai-visibility")
    gaps, healed_schema = healer.heal()

    assert gaps.needs_healing is True
    payload = _parse_healed_json(healed_schema)
    types = {node["@type"] for node in payload["@graph"]}
    assert {"WebSite", "Organization", "Person", "Service", "Article"}.issubset(types)

    org_node = next(n for n in payload["@graph"] if n["@type"] == "Organization")
    assert "https://github.com/examplebrand" in org_node["sameAs"]
    assert "https://www.linkedin.com/company/examplebrand" in org_node["sameAs"]
    assert "https://www.wikidata.org/wiki/Q999999" in org_node["sameAs"]


@pytest.mark.asyncio
async def test_crawl_engine_populates_healed_schema():
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    mock_router = AsyncMock()
    mock_router.execute_with_fallback.return_value = RawExtraction(
        url="https://example-healer-test.com/",
        final_url="https://example-healer-test.com/",
        status_code=200,
        html=html,
        headers={},
        adapter_name="native_http",
        execution_time_ms=12.0,
        rendered_js=False,
    )
    engine = CrawlEngine(extraction_router=mock_router)
    res = await engine.extract_single(
        "https://example-healer-test.com/", ExtractionOptions(extract_seo=True, extract_geo=True)
    )

    assert res.healed_schema is not None
    assert res.healed_schema.startswith(ATTRIBUTION_COMMENT)
    assert res.schema_gaps is not None
    assert res.schema_gaps.needs_healing is True
    assert res.seo is not None
    assert res.seo.healed_schema == res.healed_schema
