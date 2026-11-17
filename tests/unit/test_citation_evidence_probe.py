from pathlib import Path
from mwie.citations.citation_evidence_probe import CitationEvidenceProbe
from mwie.parsing.html_parser import HTMLParser

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "sample_page.html"


def test_citation_evidence_probe_sample_page():
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    parser = HTMLParser(html, "https://molavi.pro/mwie")
    _, clean_text = parser.get_clean_html_and_text()

    probe = CitationEvidenceProbe(
        raw_html=html,
        clean_text=clean_text,
        url="https://molavi.pro/mwie",
    )
    report = probe.analyze()

    assert report.evidence_citability_score >= 0
    assert report.evidence_citability_score <= 100
    assert isinstance(report.expert_quotes_count, int)
    assert isinstance(report.statistical_claims_count, int)
    assert isinstance(report.research_links_count, int)
    assert len(report.remediation_tips) <= 3


def test_citation_evidence_probe_commercial_and_evidence():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Enterprise SEO & AI Search Optimization Services</title></head>
    <body>
        <h1>Enterprise Services & Pricing Plans</h1>
        <p>According to research published in 2024, organic AI citation traffic increased by 84.5% across global brands.</p>
        <blockquote cite="https://arxiv.org/abs/2301.00000">
            "Generative Search Optimization requires verifiable citation density."
            <footer>— Dr. Alex Smith</footer>
        </blockquote>
        <p>Reference study available at <a href="https://stanford.edu/research/ai-search">Stanford AI Lab</a> and <a href="https://arxiv.org/abs/2301.00000">arXiv preprint</a>.</p>
        
        <section class="pricing-plans">
            <h2>Our Packages</h2>
            <table>
                <tr><th>Package</th><th>Price</th><th>Deliverables</th></tr>
                <tr><td>Core Audit</td><td>$2,500</td><td>Full schema healing and GEO mapping</td></tr>
            </table>
            <ul>
                <li>✓ Full GEO Citation Audit included</li>
                <li>✓ 30-Day SLA Guarantee</li>
                <li>✓ Enterprise Knowledge Graph Schema deliverable</li>
            </ul>
        </section>
    </body>
    </html>
    """
    parser = HTMLParser(html, "https://molavi.pro/services/pricing")
    _, clean_text = parser.get_clean_html_and_text()

    probe = CitationEvidenceProbe(
        raw_html=html,
        clean_text=clean_text,
        url="https://molavi.pro/services/pricing",
    )
    report = probe.analyze()

    assert report.expert_quotes_count >= 1
    assert any(q.author and "Alex Smith" in q.author for q in report.expert_quotes)
    assert report.statistical_claims_count >= 1
    assert any("84.5%" in c.claim_text for c in report.statistical_claims)
    assert report.research_links_count >= 1
    assert any("stanford.edu" in d or "arxiv.org" in d for d in report.research_domains)
    assert report.offer_transparency.is_commercial_url is True
    assert report.offer_transparency.has_pricing_table is True
    assert "$" in report.offer_transparency.detected_currencies
    assert report.offer_transparency.has_structured_deliverables is True
    assert report.evidence_citability_score >= 80
