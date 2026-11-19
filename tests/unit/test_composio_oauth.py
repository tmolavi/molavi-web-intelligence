"""
Unit Tests for Composio OAuth Service.
Tests OAuth connection initiation and verified profile/telemetry fetching.
"""

import pytest
from unittest.mock import AsyncMock, patch
from mwie.integrations.composio_service import ComposioService


@pytest.mark.asyncio
async def test_composio_initiate_connection():
    service = ComposioService(api_key="test_consumer_key")

    mock_resp = {
        "successful": True,
        "data": {
            "results": {
                "google_search_console": {
                    "redirect_url": "https://connect.composio.dev/link/lk_test_gsc_123",
                    "status": "initiated",
                }
            }
        },
    }

    with patch.object(service, "_call_mcp", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_resp

        res = await service.initiate_connection(
            entity_id="founder@testcorp.com",
            redirect_url="https://molavi.pro/tools/web-intelligence",
        )

        assert res["successful"] is True
        assert res["connection_url"] == "https://connect.composio.dev/link/lk_test_gsc_123"
        assert res["entity_id"] == "founder@testcorp.com"
        assert "google_search_console" in res["toolkits"]


@pytest.mark.asyncio
async def test_composio_verify_and_fetch_telemetry():
    service = ComposioService(api_key="test_consumer_key")

    mock_status = {
        "successful": True,
        "data": {
            "results": {
                "gmail": {
                    "status": "active",
                    "accounts": [{"user_info": {"email": "verified_taqi@molavi.pro", "name": "Taqi Molavi"}}],
                },
                "google_search_console": {
                    "status": "active",
                    "accounts": [{"user_info": {"siteEntry": [{"siteUrl": "sc-domain:molavi.pro"}]}}],
                },
                "google_analytics": {"status": "active"},
            }
        },
    }

    with patch.object(service, "_call_mcp", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_status

        telemetry = await service.verify_and_fetch_telemetry(
            entity_id="verified_taqi@molavi.pro",
            target_domain="molavi.pro",
        )

        assert telemetry["verified"] is True
        assert telemetry["lead_email"] == "verified_taqi@molavi.pro"
        assert telemetry["lead_name"] == "Taqi Molavi"
        assert "gsc_snapshot" in telemetry
        assert "ga4_snapshot" in telemetry
        assert telemetry["gsc_snapshot"]["total_clicks"] > 0
        assert telemetry["ga4_snapshot"]["ai_referral_ratio"] > 0
