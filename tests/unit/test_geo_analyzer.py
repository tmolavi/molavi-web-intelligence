from pathlib import Path

from mwie.geo.analyzer import GEOAnalyzer
from mwie.parsing.html_parser import HTMLParser
from mwie.seo.analyzer import SEOAnalyzer

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "sample_page.html"


def test_geo_analyzer_entities_and_citations():
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    parser = HTMLParser(html, "https://molavi.pro/mwie")
    _, clean_text = parser.get_clean_html_and_text()

    seo_analyzer = SEOAnalyzer(html, "https://molavi.pro/mwie")
    schemas = seo_analyzer.extract_json_ld()

    geo = GEOAnalyzer(html, clean_text, "https://molavi.pro/mwie", json_ld_schemas=schemas)
    report = geo.analyze()

    assert report.primary_brand is not None
    assert any(e.name == "Taqi Molavi" for e in report.entities)
    assert len(report.citations) >= 2
    assert len(report.qa_knowledge_blocks) >= 1
    assert report.qa_knowledge_blocks[0].question == "What is MWIE?"
    assert report.ai_readiness_score > 60
    assert len(report.semantic_chunks) >= 1
