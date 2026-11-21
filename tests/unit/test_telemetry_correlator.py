"""
Unit Tests for TelemetryCorrelator & Reporting Anomaly Guard.
Asserts:
- Correct isolation of 5 key AI referral engines (chatgpt, perplexity, claude, gemini, copilot)
- Computation of ai_referral_share_pct
- Computation of GSC Branded vs Non-Branded click ratios
- Anomaly detection for Nov 9-11, 2026 GSC GenAI logging bug
- Verification that zero PII (email, domain, queries) enters anonymized benchmark payloads
"""

import pytest
from mwie.telemetry_correlator import TelemetryCorrelator, telemetry_correlator
from mwie.db.database import DatabaseManager


def test_isolate_ai_referrals_all_engines():
    correlator = TelemetryCorrelator()

    ga4_payload = {
        "total_sessions": 5000,
        "rows": [
            {"dimensionValues": [{"value": "chatgpt.com / referral"}], "metricValues": [{"value": "600"}]},
            {"dimensionValues": [{"value": "perplexity.ai / referral"}], "metricValues": [{"value": "350"}]},
            {"dimensionValues": [{"value": "claude.ai / referral"}], "metricValues": [{"value": "150"}]},
            {"dimensionValues": [{"value": "gemini.google.com / referral"}], "metricValues": [{"value": "80"}]},
            {"dimensionValues": [{"value": "copilot.microsoft.com / referral"}], "metricValues": [{"value": "70"}]},
            {"dimensionValues": [{"value": "google / organic"}], "metricValues": [{"value": "3000"}]},
            {"dimensionValues": [{"value": "direct / none"}], "metricValues": [{"value": "750"}]},
        ],
    }

    res = correlator.isolate_ai_referrals(ga4_payload)

    assert res["total_sessions"] == 5000
    assert res["ai_referral_sessions"] == 1250  # 600 + 350 + 150 + 80 + 70
    assert res["ai_referral_ratio"] == 0.2500
    assert res["ai_referral_share_pct"] == 25.0

    breakdown = res["engine_breakdown"]
    assert breakdown["chatgpt"]["sessions"] == 600
    assert breakdown["chatgpt"]["share_pct"] == 12.0
    assert breakdown["perplexity"]["sessions"] == 350
    assert breakdown["perplexity"]["share_pct"] == 7.0
    assert breakdown["claude"]["sessions"] == 150
    assert breakdown["claude"]["share_pct"] == 3.0
    assert breakdown["gemini"]["sessions"] == 80
    assert breakdown["gemini"]["share_pct"] == 1.6
    assert breakdown["copilot"]["sessions"] == 70
    assert breakdown["copilot"]["share_pct"] == 1.4


def test_analyze_gsc_clicks_branded_ratio():
    correlator = TelemetryCorrelator()

    gsc_payload = {
        "total_clicks": 500,
        "total_impressions": 10000,
        "average_ctr": 0.05,
        "top_queries_sample": [
            {"query": "molavi pro services", "clicks": 200, "impressions": 1000, "ctr": 0.20},
            {"query": "molavi ai audit", "clicks": 100, "impressions": 800, "ctr": 0.125},
            {"query": "best geo optimization tools", "clicks": 120, "impressions": 4000, "ctr": 0.03},
            {"query": "generative engine citation schema", "clicks": 80, "impressions": 4200, "ctr": 0.019},
        ],
    }

    res = correlator.analyze_gsc_clicks(gsc_payload, domain="molavi.pro")

    assert res["total_clicks"] == 500
    assert res["branded_clicks"] == 300
    assert res["nonbranded_clicks"] == 200
    assert res["branded_click_ratio"] == 0.6000
    assert res["branded_share_pct"] == 60.0


def test_detect_anomalies_flagging_nov_2026_bug():
    correlator = TelemetryCorrelator()

    # Case 1: Overlapping window (e.g. October 15 to November 15, 2026)
    res_overlap = correlator.detect_anomalies(start_date="2026-10-15", end_date="2026-11-15")
    assert res_overlap["anomaly_detected"] is True
    assert res_overlap["anomaly_count"] == 1
    ano = res_overlap["anomalies"][0]
    assert ano["anomaly_id"] == "GSC_GENAI_LOGGING_202611"
    assert "Nov 9–11, 2026" in ano["impact_summary"]
    assert ano["severity"] == "HIGH"

    # Case 2: Non-overlapping window (e.g. September 2026)
    res_no_overlap = correlator.detect_anomalies(start_date="2026-09-01", end_date="2026-09-30")
    assert res_no_overlap["anomaly_detected"] is False
    assert res_no_overlap["anomaly_count"] == 0


def test_correlation_insight_why_gsc_misleads():
    correlator = TelemetryCorrelator()

    insight = correlator.generate_correlation_insight(
        mavi_score=78.5,
        ai_referral_share_pct=26.4,
        total_impressions=150000,
        total_ai_sessions=1200,
    )

    assert "zero-click" in insight["why_gsc_impressions_mislead"].lower()
    assert insight["alignment"] == "EXCELLENT"
    assert insight["mavi_score"] == 78.5
    assert insight["ai_referral_share_pct"] == 26.4


@pytest.mark.asyncio
async def test_zero_pii_in_anonymized_benchmark():
    """
    STRICT PRIVACY TEST:
    Asserts that no lead email, domain, client name, exact queries,
    or internal identifiers leak into anonymized_industry_benchmarks.
    """
    correlator = TelemetryCorrelator()

    correlated_data = {
        "lead_email": "ceo@acme-secret.com",
        "domain": "acme-secret.com",
        "url": "https://acme-secret.com/deep/product",
        "client_name": "Classified Client",
        "mavi_score": 82.5,
        "ai_referral_share_pct": 29.50,
        "ai_referral_ratio": 0.2950,
        "ai_engines_breakdown": {
            "chatgpt": {"sessions": 450, "share_pct": 18.0},
            "perplexity": {"sessions": 200, "share_pct": 8.0},
        },
        "query_log": ["secret enterprise keyword 1", "secret keyword 2"],
    }

    # 1. Format using prepare_anonymized_benchmark
    sanitized = correlator.prepare_anonymized_benchmark(
        correlated_data=correlated_data,
        mavi_score=82.5,
        industry_tag="finance_tech",
        seo_score=80.0,
        aeo_score=84.0,
        geo_score=83.0,
        evidence_score=85.0,
    )

    # Allowed keys whitelist
    allowed_keys = {
        "industry_tag",
        "mavi_score",
        "rp_score",
        "cs_score",
        "es_score",
        "evidence_score",
        "ai_referral_ratio",
        "bucket_month",
    }
    assert set(sanitized.keys()) == allowed_keys, f"PII or excess keys leaked: {set(sanitized.keys()) - allowed_keys}"

    # Verify zero PII in strings
    for k, v in sanitized.items():
        if isinstance(v, str):
            assert "@" not in v, f"Email leaked in {k}: {v}"
            assert "acme" not in v.lower(), f"Domain leaked in {k}: {v}"
            assert "http" not in v.lower(), f"URL leaked in {k}: {v}"
            assert "secret" not in v.lower(), f"Secret leaked in {k}: {v}"

    # Verify insertion via DatabaseManager
    db = DatabaseManager()
    inserted = await db.insert_anonymized_benchmark(sanitized)
    assert "lead_email" not in inserted
    assert "domain" not in inserted
    assert inserted["mavi_score"] == 82.5
    assert inserted["ai_referral_ratio"] == 0.2950
