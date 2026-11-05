import json
from pathlib import Path
from unittest.mock import patch

import pytest

from mwie.core.models import ExtractionMetadata, ExtractionResult
from mwie.geo.analyzer import GEOAnalyzer
from mwie.mcp.server import (
    analyze_geo,
    analyze_seo,
    batch_process_urls,
    compare_pages,
    crawl_url,
    extract_entities,
    extract_page_content,
    extract_structured_data,
    get_extraction_metadata,
    get_job_status,
)
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


@pytest.mark.asyncio
async def test_mcp_job_status():
    status_str = await get_job_status()
    data = json.loads(status_str)
    assert data["engine"] == "Molavi Web Intelligence Engine"
    assert "version" in data
    assert "registered_adapters" in data


@pytest.mark.asyncio
async def test_mcp_extraction_metadata():
    meta_str = await get_extraction_metadata()
    data = json.loads(meta_str)
    assert isinstance(data, list)
    assert any(d["name"] == "native_http" for d in data)


@pytest.mark.asyncio
@patch("mwie.crawler.engine.crawl_engine.extract_single")
async def test_mcp_crawl_tools(mock_extract, sample_result):
    mock_extract.return_value = sample_result

    # 1. crawl_url
    res_str = await crawl_url("https://molavi.pro/mwie")
    res = json.loads(res_str)
    assert res["url"] == "https://molavi.pro/mwie"

    # 2. extract_page_content
    content_str = await extract_page_content("https://molavi.pro/mwie")
    content = json.loads(content_str)
    assert "clean_text" in content
    assert "markdown" in content

    # 3. analyze_seo
    seo_str = await analyze_seo("https://molavi.pro/mwie")
    seo = json.loads(seo_str)
    assert seo["seo_score"] >= 80

    # 4. analyze_geo
    geo_str = await analyze_geo("https://molavi.pro/mwie")
    geo = json.loads(geo_str)
    assert geo["ai_readiness_score"] > 50

    # 5. extract_entities
    ent_str = await extract_entities("https://molavi.pro/mwie")
    ent = json.loads(ent_str)
    assert len(ent) > 0

    # 6. extract_structured_data
    struct_str = await extract_structured_data("https://molavi.pro/mwie")
    struct = json.loads(struct_str)
    assert struct["has_json_ld"] is True

    # 7. compare_pages
    comp_str = await compare_pages(["https://molavi.pro/mwie", "https://example.com"])
    comp = json.loads(comp_str)
    assert len(comp["pages"]) == 2

    # 8. batch_process_urls
    batch_str = await batch_process_urls(["https://molavi.pro/mwie"])
    batch = json.loads(batch_str)
    assert len(batch) == 1
    assert batch[0]["status"] == "success"
