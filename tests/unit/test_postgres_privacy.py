"""
Unit Tests for PostgreSQL Persistence & Strict Privacy Isolation.
Asserts zero email/domain/query leakage into anonymized_industry_benchmarks.
"""

import pytest
from mwie.db.database import DatabaseManager


@pytest.mark.asyncio
async def test_sanitize_for_benchmark_zero_pii():
    """
    STRICT PRIVACY TEST: Asserts that email, domain, URLs, exact search queries,
    and raw traffic numbers are 100% stripped from benchmark records.
    """
    raw_client_audit = {
        "lead_email": "client-ceo@secretcorporation.com",
        "lead_name": "Jane Doe",
        "domain": "secretcorporation.com",
        "url": "https://secretcorporation.com/enterprise/pricing",
        "query_term": "best enterprise pricing",
        "seo_score": 85,
        "aeo_score": 80,
        "geo_score": 75,
        "evidence_score": 88,
        "mavi_score": 79.75,
        "ai_referral_sessions": 320,
        "total_sessions": 1000,
        "ai_referral_ratio": 0.3200,
        "industry_tag": "fintech",
        "internal_ip": "192.168.1.10",
        "token": "secret_oauth_token_xyz",
    }

    sanitized = DatabaseManager.sanitize_for_benchmark(raw_client_audit, "fintech")

    # 1. Allowed keys whitelist check
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
    assert set(sanitized.keys()) == allowed_keys, f"Leakage detected! Extra keys: {set(sanitized.keys()) - allowed_keys}"

    # 2. String value checks: assert no email, domain, or protocol leaks
    for key, val in sanitized.items():
        if isinstance(val, str):
            assert "@" not in val, f"Email leaked in key '{key}': {val}"
            assert "secretcorporation" not in val, f"Domain leaked in key '{key}': {val}"
            assert "http" not in val, f"URL leaked in key '{key}': {val}"
            assert "Jane" not in val, f"Name leaked in key '{key}': {val}"

    # 3. Numeric values check: ensure only normalized percentages/scores
    assert sanitized["mavi_score"] == 79.75
    assert sanitized["rp_score"] == 80.0
    assert sanitized["cs_score"] == 75.0
    assert sanitized["es_score"] == 85.0
    assert sanitized["evidence_score"] == 88.0
    assert sanitized["ai_referral_ratio"] == 0.3200
    assert sanitized["industry_tag"] == "fintech"


@pytest.mark.asyncio
async def test_private_client_audits_persistence_and_drift():
    """
    Tests saving private client audit, retrieving previous audit, and
    calculating longitudinal drift without local files.
    """
    db = DatabaseManager()

    # 1. First baseline audit
    audit1 = await db.insert_private_client_audit(
        lead_email="architect@acme.com",
        lead_name="Acme Architect",
        composio_entity_id="entity_acme_123",
        domain="acme.com",
        gsc_snapshot={"average_ctr": 0.082, "branded_clicks": 50, "total_clicks": 100},
        ga4_snapshot={"total_sessions": 2000, "ai_referral_sessions": 400, "ai_referral_ratio": 0.2000},
        mavi_score=65.0,
        evidence_score=60.0,
    )
    assert audit1["lead_email"] == "architect@acme.com"
    assert audit1["domain"] == "acme.com"

    # Baseline drift should indicate no prior audit
    drift1 = db.calculate_drift(
        current_mavi=65.0,
        current_evidence=60.0,
        current_gsc={"average_ctr": 0.082},
        current_ga4={"ai_referral_ratio": 0.2000},
        previous_audit=None,
    )
    assert drift1["has_drift"] is False

    # 2. Second audit (30 days later) with improved scores
    audit2 = await db.insert_private_client_audit(
        lead_email="architect@acme.com",
        lead_name="Acme Architect",
        composio_entity_id="entity_acme_123",
        domain="acme.com",
        gsc_snapshot={"average_ctr": 0.125, "branded_clicks": 120, "total_clicks": 200},
        ga4_snapshot={"total_sessions": 3500, "ai_referral_sessions": 980, "ai_referral_ratio": 0.2800},
        mavi_score=78.5,
        evidence_score=82.0,
    )

    # Query previous audit
    prev_audit = await db.get_previous_client_audit("architect@acme.com", "acme.com")
    assert prev_audit is not None
    assert prev_audit["mavi_score"] == 65.0

    # Calculate drift
    drift2 = db.calculate_drift(
        current_mavi=78.5,
        current_evidence=82.0,
        current_gsc={"average_ctr": 0.125},
        current_ga4={"ai_referral_ratio": 0.2800},
        previous_audit=prev_audit,
    )
    assert drift2["has_drift"] is True
    assert drift2["mavi_drift"] == 13.5
    assert drift2["evidence_drift"] == 22.0
    assert drift2["ctr_drift"] == 0.043
    assert drift2["ai_referral_drift"] == 0.0800


@pytest.mark.asyncio
async def test_anonymized_industry_benchmark_pool_and_percentiles():
    """
    Tests inserting sanitized benchmarks and computing percentiles
    without leaking private client data.
    """
    db = DatabaseManager()

    # Insert sanitized records
    rec1 = await db.insert_anonymized_benchmark({
        "industry_tag": "saas",
        "mavi_score": 70.0,
        "seo_score": 75.0,
        "aeo_score": 70.0,
        "geo_score": 66.0,
        "evidence_score": 68.0,
        "ai_referral_ratio": 0.2200,
    })
    assert "lead_email" not in rec1
    assert "domain" not in rec1

    # Insert another with higher score
    await db.insert_anonymized_benchmark({
        "industry_tag": "saas",
        "mavi_score": 85.0,
        "seo_score": 90.0,
        "aeo_score": 84.0,
        "geo_score": 82.0,
        "evidence_score": 85.0,
        "ai_referral_ratio": 0.3100,
    })

    # Test percentile calculation for client with score 78.0
    percentiles = await db.get_industry_percentiles(mavi_score=78.0, industry_tag="saas")
    assert "percentile" in percentiles
    assert percentiles["industry_tag"] == "saas"
    assert percentiles["sample_size"] >= 2
    assert 0 < percentiles["percentile"] <= 100
    assert "industry_avg_mavi" in percentiles
    # Ensure no PII in percentiles response
    assert "email" not in str(percentiles)
    assert "domain" not in str(percentiles)
