"""
Integration Tests for Composio & Enriched Audit Endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from mwie.api.app import app


@pytest.mark.asyncio
async def test_composio_connect_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/api/auth/composio/connect",
            json={
                "email": "architect@molavi.pro",
                "redirect_url": "https://molavi.pro/tools/web-intelligence",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "connection_url" in data
        assert data["entity_id"] == "architect@molavi.pro"


@pytest.mark.asyncio
async def test_composio_callback_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(
            "/api/auth/composio/callback",
            params={
                "entity_id": "architect@molavi.pro",
                "domain": "molavi.pro",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["connected"] is True
        assert "lead_email" in data
        assert "gsc_snapshot" in data
        assert "ga4_snapshot" in data


@pytest.mark.asyncio
async def test_enriched_audit_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/api/audit/enriched",
            json={
                "url": "https://molavi.pro",
                "entity_id": "lead_test@molavi.pro",
                "lead_email": "lead_test@molavi.pro",
                "lead_name": "Taqi Molavi",
                "industry_tag": "technology",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "mavi_score" in data
        # Check core scoring weights: SEO 30%, AEO 35%, GEO 35%
        assert data["weights"]["seo_weight"] == 0.30
        assert data["weights"]["aeo_weight"] == 0.35
        assert data["weights"]["geo_weight"] == 0.35

        # Check telemetry enrichment
        assert "live_telemetry_enrichment" in data
        assert "branded_clicks" in data["live_telemetry_enrichment"]["gsc"]
        assert "ai_referral_sessions" in data["live_telemetry_enrichment"]["ga4"]

        # Check telemetry summary (correlator + anomaly guard)
        assert "telemetry_summary" in data
        summary = data["telemetry_summary"]
        assert "ai_referral_share_pct" in summary
        assert "ai_engines_breakdown" in summary
        assert "chatgpt" in summary["ai_engines_breakdown"]
        assert "copilot" in summary["ai_engines_breakdown"]
        assert "branded_vs_nonbranded" in summary
        assert "anomaly_guard" in summary
        assert summary["anomaly_guard"]["anomaly_detected"] is True
        assert "correlation_insight" in summary

        # Check drift
        assert "longitudinal_drift" in data

        # Check industry benchmark comparison
        bench = data["industry_benchmark_comparison"]
        assert bench["privacy_isolation_verified"] is True
        assert "client_percentile" in bench
        assert "industry_avg_mavi" in bench
        assert "email" not in str(bench)
        assert "domain" not in str(bench)
