from pathlib import Path

from mwie.parsing.html_parser import HTMLParser

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "sample_page.html"


def test_html_parser_metadata():
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    parser = HTMLParser(html, "https://molavi.pro/mwie")

    assert parser.get_meta_title() == "Molavi Web Intelligence Engine — AI Search and SEO"
    assert "Discover the next-generation" in parser.get_meta_description()
    assert parser.get_canonical_url() == "https://molavi.pro/mwie"

    og = parser.get_open_graph()
    assert og.get("og:site_name") == "Molavi"
    assert og.get("og:title") == "Molavi Web Intelligence Engine"

    tc = parser.get_twitter_card()
    assert tc.get("twitter:card") == "summary_large_image"


def test_html_parser_headings_and_images():
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    parser = HTMLParser(html, "https://molavi.pro/mwie")

    headings = parser.get_headings()
    assert len(headings) >= 3
    assert headings[0].level == 1
    assert headings[0].text == "Molavi Web Intelligence Engine"

    images = parser.get_images()
    assert len(images) == 2
    assert images[0].has_alt is True
    assert images[0].alt == "MWIE Architecture Diagram"
    assert images[1].has_alt is False


def test_html_parser_links():
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    parser = HTMLParser(html, "https://molavi.pro/mwie")

    internal, external = parser.get_links()
    assert any("molavi.pro" in link.url for link in internal)
    assert any("example.com" in link.url for link in external)


def test_html_clean_content_ratio():
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    parser = HTMLParser(html, "https://molavi.pro/mwie")

    clean_html, clean_text = parser.get_clean_html_and_text()
    assert "header" not in clean_html.lower()
    assert "footer" not in clean_html.lower()
    assert "Generative Engine Optimization" in clean_text

    ratio = parser.calculate_content_to_html_ratio(clean_text)
    assert ratio > 0.0
