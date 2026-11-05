from pathlib import Path

from mwie.seo.analyzer import SEOAnalyzer

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "sample_page.html"


def test_seo_analyzer_comprehensive():
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    analyzer = SEOAnalyzer(html, "https://molavi.pro/mwie", status_code=200)
    report = analyzer.analyze()

    assert report.is_indexable is True
    assert report.meta_title == "Molavi Web Intelligence Engine — AI Search and SEO"
    assert report.canonical_match is True
    assert report.h1_count == 1
    assert report.has_json_ld is True
    assert "SoftwareApplication" in report.structured_data_types
    assert "FAQPage" in report.structured_data_types
    assert report.images_total == 2
    assert report.images_missing_alt == 1
    assert report.seo_score >= 80
    assert len(report.recommendations) > 0
