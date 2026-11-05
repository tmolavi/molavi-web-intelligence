from pathlib import Path
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from mwie.api.app import app
from mwie.core.models import ExtractionMetadata, ExtractionResult
from mwie.geo.analyzer import GEOAnalyzer
from mwie.parsing.html_parser import HTMLParser
from mwie.seo.analyzer import SEOAnalyzer

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "sample_page.html"


@pytest.fixture
def sample_result():
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    parser = HTMLParser(html, "https://molavi.pro/mwie")
    clean_html, clean_text = parser.get_clean_html_and_text()
    seo = SEOAnalyzer(html, "https://molavi.pro/mwie").analyze()
    geo = GEOAnalyzer(html, clean_text, "https://molavi.pro/mwie", seo.json_ld_schemas).analyze()

    return ExtractionResult(
        url="https://molavi.pro/mwie",
        final_url="https://molavi.pro/mwie",
        status_code=200,
        clean_html=clean_html,
        clean_text=clean_text,
        markdown="# Molavi Web Intelligence Engine",
        seo=seo,
        geo=geo,
        metadata=ExtractionMetadata(
            adapter_used="native_http",
            execution_time_ms=50.0,
            rendered_js=False,
            status_code=200,
            content_length=len(html),
        ),
    )


def test_api_health():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Molavi Web Intelligence Engine"


@patch("mwie.crawler.engine.crawl_engine.extract_single")
def test_api_extract(mock_extract, sample_result):
    mock_extract.return_value = sample_result
    client = TestClient(app)
    resp = client.post("/api/v1/extract", json={"url": "https://molavi.pro/mwie"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["url"] == "https://molavi.pro/mwie"
    assert data["seo"]["meta_title"] == "Molavi Web Intelligence Engine — AI Search and SEO"
    assert data["geo"]["primary_brand"] is not None


@patch("mwie.crawler.engine.crawl_engine.extract_single")
def test_api_seo(mock_extract, sample_result):
    mock_extract.return_value = sample_result
    client = TestClient(app)
    resp = client.post("/api/v1/seo", json={"url": "https://molavi.pro/mwie"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["meta_title"] == "Molavi Web Intelligence Engine — AI Search and SEO"
    assert data["seo_score"] >= 80


@patch("mwie.crawler.engine.crawl_engine.extract_single")
def test_api_geo(mock_extract, sample_result):
    mock_extract.return_value = sample_result
    client = TestClient(app)
    resp = client.post("/api/v1/geo", json={"url": "https://molavi.pro/mwie"})
    assert resp.status_code == 200
    data = resp.json()
    assert "entities" in data
    assert "qa_knowledge_blocks" in data
    assert data["ai_readiness_score"] > 50


@patch("mwie.crawler.engine.crawl_engine.extract_single")
def test_api_compare(mock_extract, sample_result):
    mock_extract.return_value = sample_result
    client = TestClient(app)
    resp = client.post(
        "/api/v1/compare", json={"urls": ["https://molavi.pro/mwie", "https://example.com"]}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["pages"]) == 2
    assert len(data["insights"]) > 0


def test_api_adapter_stats():
    client = TestClient(app)
    resp = client.get("/api/v1/adapters/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert any(d["name"] == "native_http" for d in data)
