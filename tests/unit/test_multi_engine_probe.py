from pathlib import Path
from mwie.engines.multi_engine_probe import MultiEngineProbe
from mwie.parsing.html_parser import HTMLParser

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "sample_page.html"


def test_multi_engine_probe_sample_page():
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    parser = HTMLParser(html, "https://molavi.pro/tools/web-intelligence")
    _, clean_text = parser.get_clean_html_and_text()

    probe = MultiEngineProbe(
        raw_html=html,
        clean_text=clean_text,
        url="https://molavi.pro/tools/web-intelligence",
    )
    report = probe.analyze()

    assert 0 <= report.chatgpt_score <= 100
    assert 0 <= report.google_ai_mode_score <= 100
    assert 0 <= report.perplexity_score <= 100
    assert report.branded_defense_status in ("defended", "adequate", "vulnerable")
    assert isinstance(report.chatgpt_breakdown, dict)
    assert isinstance(report.google_breakdown, dict)
    assert isinstance(report.perplexity_breakdown, dict)
    assert len(report.remediation_tips) <= 3


def test_multi_engine_probe_defended_page():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Molavi Web Intelligence | Autonomous AI Search Engine Optimization</title>
        <link rel="canonical" href="https://molavi.pro/tools/web-intelligence" />
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Organization",
                    "@id": "https://molavi.pro/#organization",
                    "name": "Molavi",
                    "url": "https://molavi.pro",
                    "sameAs": [
                        "https://www.wikidata.org/wiki/Q123456",
                        "https://www.linkedin.com/in/taghimolavi",
                        "https://github.com/tmolavi"
                    ]
                },
                {
                    "@type": "FAQPage",
                    "mainEntity": [
                        {
                            "@type": "Question",
                            "name": "What is Molavi Web Intelligence?",
                            "acceptedAnswer": {
                                "@type": "Answer",
                                "text": "Molavi Web Intelligence is an open-source engine providing unified SEO and GEO analysis."
                            }
                        }
                    ]
                }
            ]
        }
        </script>
    </head>
    <body>
        <h1>Molavi Web Intelligence Platform</h1>
        <p>Molavi is a next-generation web intelligence and generative engine optimization system designed to audit digital properties across AI answer engines.</p>
        
        <h2>How does Google AI Mode evaluate conversational queries?</h2>
        <p>Google AI Mode decomposes multi-facet conversational queries into four subtopics, evaluating entity alignment and top-30% direct answer extractability.</p>
        
        <h2>What are the primary citation benchmarks in 2026?</h2>
        <p>According to empirical studies conducted in 2026 across 50,000 domains, AI citation reach grew by 85.4% year-over-year.</p>
        
        <blockquote cite="https://arxiv.org/abs/2601.00000">
            "Direct answer clarity and verifiable statistics protect branded search visibility."
            <footer>— Lead Researcher at <a href="https://stanford.edu/research">Stanford AI</a> and <a href="https://arxiv.org/abs/2601.00000">arXiv.org</a></footer>
        </blockquote>
        
        <table>
            <tr><th>Engine</th><th>Readiness Vector</th><th>Score</th></tr>
            <tr><td>ChatGPT GPT-5.6</td><td>Entity Graph & sameAs</td><td>95</td></tr>
            <tr><td>Google AI Mode</td><td>Conversational 3x Q&A</td><td>92</td></tr>
            <tr><td>Perplexity Sonar</td><td>Statistical Density</td><td>94</td></tr>
        </table>
    </body>
    </html>
    """
    parser = HTMLParser(html, "https://molavi.pro/tools/web-intelligence")
    _, clean_text = parser.get_clean_html_and_text()

    probe = MultiEngineProbe(
        raw_html=html,
        clean_text=clean_text,
        url="https://molavi.pro/tools/web-intelligence",
    )
    report = probe.analyze()

    assert report.chatgpt_score >= 70
    assert report.google_ai_mode_score >= 70
    assert report.perplexity_score >= 70
    assert report.branded_defense_status == "defended"
    assert report.chatgpt_breakdown["same_as_count"] >= 3
    assert report.google_breakdown["conversational_questions_count"] >= 2
    assert report.google_breakdown["has_direct_definition_top30"] is True
    assert report.perplexity_breakdown["statistical_claims_count"] >= 2
