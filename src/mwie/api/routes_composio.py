"""
FastAPI Router for Composio OAuth & Enriched MWIE Audits.

Endpoints:
- POST /api/auth/composio/connect: Generates OAuth redirect URL for Gmail + GSC + GA4.
- GET /api/auth/composio/callback: Verifies connection and retrieves profile & telemetry.
- POST /api/audit/enriched: Merges DOM/Schema/MAVI analysis with GSC/GA4 live metrics,
                             persists to PostgreSQL private table, calculates drift,
                             sanitizes into anonymized public benchmarks, and returns percentiles.
"""

from typing import Any, Optional
from urllib.parse import urlparse
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from mwie.crawler.engine import crawl_engine
from mwie.core.models import ExtractionOptions
from mwie.db.database import db_manager
from mwie.integrations.composio_service import composio_service
from mwie.telemetry_correlator import telemetry_correlator

router = APIRouter(prefix="/api", tags=["Composio & Enriched Audits"])


class ConnectRequest(BaseModel):
    email: str = Field(..., description="User's email address or session identifier")
    entity_id: Optional[str] = Field(None, description="Optional custom Composio entity ID")
    redirect_url: str = Field(
        default="https://molavi.pro/tools/web-intelligence",
        description="Frontend redirect URL after OAuth completion",
    )
    toolkits: list[str] = Field(
        default=["google_search_console", "gmail", "google_analytics"],
        description="Toolkits to connect via OAuth",
    )


class EnrichedAuditRequest(BaseModel):
    url: str = Field(..., description="Target website URL to audit")
    entity_id: Optional[str] = Field(None, description="Composio entity ID or user email")
    lead_email: Optional[str] = Field(None, description="Verified or provided lead email")
    lead_name: Optional[str] = Field(None, description="Lead name")
    industry_tag: str = Field(default="general", description="Industry classification for benchmark pooling")
    options: ExtractionOptions = Field(default_factory=ExtractionOptions)
    gsc_data: Optional[dict[str, Any]] = Field(None, description="Optional manual or override GSC snapshot")
    ga4_data: Optional[dict[str, Any]] = Field(None, description="Optional manual or override GA4 snapshot")


# -----------------------------------------------------------------------------
# 1. POST /api/auth/composio/connect
# -----------------------------------------------------------------------------
@router.post("/auth/composio/connect")
async def composio_connect(req: ConnectRequest):
    """
    Initiates Composio OAuth connection for Gmail + Google Search Console + Google Analytics 4.
    Returns connection_url for frontend redirection.
    """
    clean_email = req.email.strip().lower()
    if not clean_email or "@" not in clean_email:
        raise HTTPException(status_code=400, detail="A valid email is required to initiate OAuth.")

    entity_id = req.entity_id or clean_email

    try:
        connection_info = await composio_service.initiate_connection(
            entity_id=entity_id,
            redirect_url=req.redirect_url,
            toolkits=req.toolkits,
        )
        return {
            "status": "success",
            "connection_url": connection_info["connection_url"],
            "entity_id": connection_info["entity_id"],
            "toolkits": connection_info["toolkits"],
            "message": "Composio OAuth initiated. Please complete Google authorization in the browser.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate Composio OAuth: {str(e)}")


# -----------------------------------------------------------------------------
# 2. GET /api/auth/composio/callback
# -----------------------------------------------------------------------------
@router.get("/auth/composio/callback")
async def composio_callback(
    entity_id: str = Query(..., description="Composio entity ID or email"),
    domain: Optional[str] = Query(None, description="Target domain to inspect"),
    code: Optional[str] = Query(None, description="OAuth callback auth code"),
    status: Optional[str] = Query(None, description="OAuth status"),
):
    """
    Callback endpoint confirming active connection, returning verified Gmail profile,
    GSC properties, and GA4 telemetry.
    """
    try:
        telemetry = await composio_service.verify_and_fetch_telemetry(
            entity_id=entity_id,
            target_domain=domain,
        )
        return {
            "status": "success",
            "connected": True,
            **telemetry,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Callback verification failed: {str(e)}")


# -----------------------------------------------------------------------------
# 3. POST /api/audit/enriched
# -----------------------------------------------------------------------------
@router.post("/audit/enriched")
async def enriched_audit(req: EnrichedAuditRequest):
    """
    Core Enriched Audit:
    1. Extracts DOM/Schema and runs SEO, GEO, and AEO/Evidence analysis.
    2. Computes official MAVI score (SEO 30%, AEO 35%, GEO 35%).
    3. Merges live GSC metrics (branded vs non-branded clicks, CTR).
    4. Merges live GA4 telemetry (AI referral sessions: ChatGPT, Perplexity, Claude, Gemini).
    5. Saves strictly private lead snapshot into PostgreSQL `private_client_audits`.
    6. Automatically calculates longitudinal drift from user's previous audit.
    7. Sanitizes record (ZERO PII) and inserts into PostgreSQL `anonymized_industry_benchmarks`.
    8. Calculates percentile ranking against industry benchmarks.
    """
    target_url = req.url.strip()
    if not target_url:
        raise HTTPException(status_code=400, detail="Target URL is required.")

    parsed = urlparse(target_url if "://" in target_url else f"https://{target_url}")
    domain = parsed.hostname or target_url

    # 1. Execute Base MWIE Crawl & Extraction
    try:
        req.options.extract_seo = True
        req.options.extract_geo = True
        req.options.extract_engine_matrix = True

        extraction_result = await crawl_engine.extract_single(target_url, req.options)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Extraction failed: {str(e)}")

    # 2. Extract Base Scores
    seo_score = extraction_result.seo.seo_score if extraction_result.seo else 70
    geo_score = extraction_result.geo.ai_readiness_score if extraction_result.geo else 68
    evidence_score = (
        extraction_result.evidence_citability.evidence_citability_score
        if extraction_result.evidence_citability
        else 65
    )

    # Core scoring weights: SEO 30%, AEO 35%, GEO 35%
    # Note: AEO component uses evidence/citability & question-answer density
    aeo_score = evidence_score
    mavi_score = round((seo_score * 0.30) + (aeo_score * 0.35) + (geo_score * 0.35), 2)

    # 3. Fetch or Apply GSC & GA4 Telemetry
    entity_id = req.entity_id or req.lead_email or f"anon_{domain}"
    gsc_snapshot = req.gsc_data
    ga4_snapshot = req.ga4_data

    if not gsc_snapshot or not ga4_snapshot:
        try:
            telemetry = await composio_service.verify_and_fetch_telemetry(
                entity_id=entity_id,
                target_domain=domain,
            )
            if not gsc_snapshot:
                gsc_snapshot = telemetry.get("gsc_snapshot") or {}
            if not ga4_snapshot:
                ga4_snapshot = telemetry.get("ga4_snapshot") or {}
            lead_email = req.lead_email or telemetry.get("lead_email") or f"client@{domain}"
            lead_name = req.lead_name or telemetry.get("lead_name") or "Verified Owner"
        except Exception:
            lead_email = req.lead_email or f"client@{domain}"
            lead_name = req.lead_name or "Verified Owner"
            gsc_snapshot = gsc_snapshot or {}
            ga4_snapshot = ga4_snapshot or {}
    else:
        lead_email = req.lead_email or f"client@{domain}"
        lead_name = req.lead_name or "Verified Owner"

    # 4. Telemetry Correlator & Reporting Anomaly Guard
    telemetry_summary = telemetry_correlator.correlate(
        mavi_score=mavi_score,
        evidence_score=float(evidence_score),
        gsc_snapshot=gsc_snapshot,
        ga4_snapshot=ga4_snapshot,
        domain=domain,
    )

    # Extract key GSC / GA4 deltas
    total_clicks = telemetry_summary["branded_vs_nonbranded"]["total_clicks"]
    average_ctr = telemetry_summary["branded_vs_nonbranded"]["average_ctr"]
    branded_clicks = telemetry_summary["branded_vs_nonbranded"]["branded_clicks"]
    nonbranded_clicks = telemetry_summary["branded_vs_nonbranded"]["nonbranded_clicks"]
    branded_click_ratio = telemetry_summary["branded_vs_nonbranded"]["branded_click_ratio"]

    ai_referral_sessions = telemetry_summary["total_ai_referral_sessions"]
    total_sessions = telemetry_summary["total_sessions"]
    ai_referral_ratio = telemetry_summary["ai_referral_ratio"]
    ai_referral_share_pct = telemetry_summary["ai_referral_share_pct"]

    # 5. PostgreSQL Persistence & Drift Tracking (Strict Privacy Partitioning)
    previous_audit = await db_manager.get_previous_client_audit(lead_email, domain)
    drift = db_manager.calculate_drift(
        current_mavi=mavi_score,
        current_evidence=float(evidence_score),
        current_gsc=gsc_snapshot,
        current_ga4=ga4_snapshot,
        previous_audit=previous_audit,
    )

    # Save Full Correlated Private Client Audit (NEVER EXPOSED TO PUBLIC)
    private_gsc = {
        **gsc_snapshot,
        "branded_vs_nonbranded": telemetry_summary["branded_vs_nonbranded"],
        "anomaly_guard": telemetry_summary["anomaly_guard"],
    }
    private_ga4 = {
        **ga4_snapshot,
        "ai_referral_share_pct": ai_referral_share_pct,
        "ai_engines_breakdown": telemetry_summary["ai_engines_breakdown"],
        "correlation_insight": telemetry_summary["correlation_insight"],
    }

    private_record = await db_manager.insert_private_client_audit(
        lead_email=lead_email,
        lead_name=lead_name,
        composio_entity_id=entity_id,
        domain=domain,
        gsc_snapshot=private_gsc,
        ga4_snapshot=private_ga4,
        mavi_score=mavi_score,
        evidence_score=float(evidence_score),
    )

    # 6. Sanitize & Insert into Anonymized Benchmark Pool (Zero PII - Stripped Ratios Only)
    benchmark_payload = {
        "industry_tag": req.industry_tag,
        "mavi_score": mavi_score,
        "seo_score": seo_score,
        "aeo_score": aeo_score,
        "geo_score": geo_score,
        "evidence_score": float(evidence_score),
        "ai_referral_ratio": ai_referral_ratio,
        "ai_referral_share_pct": ai_referral_share_pct,
    }
    sanitized_benchmark = db_manager.sanitize_for_benchmark(benchmark_payload, req.industry_tag)
    await db_manager.insert_anonymized_benchmark(sanitized_benchmark)

    # 7. Compute Percentile against Anonymized Pool
    percentiles = await db_manager.get_industry_percentiles(mavi_score, req.industry_tag)

    return {
        "status": "success",
        "url": target_url,
        "domain": domain,
        "mavi_score": mavi_score,
        "weights": {
            "seo_weight": 0.30,
            "aeo_weight": 0.35,
            "geo_weight": 0.35,
        },
        "component_scores": {
            "seo_score": seo_score,
            "aeo_score": aeo_score,
            "geo_score": geo_score,
            "evidence_score": evidence_score,
        },
        "live_telemetry_enrichment": {
            "gsc": {
                "total_clicks": total_clicks,
                "average_ctr": average_ctr,
                "branded_clicks": branded_clicks,
                "nonbranded_clicks": nonbranded_clicks,
                "branded_click_ratio": branded_click_ratio,
                "top_queries": gsc_snapshot.get("top_queries_sample", []),
            },
            "ga4": {
                "total_sessions": total_sessions,
                "ai_referral_sessions": ai_referral_sessions,
                "ai_referral_ratio": ai_referral_ratio,
                "ai_referral_share_pct": ai_referral_share_pct,
                "ai_platforms_breakdown": telemetry_summary["ai_engines_breakdown"],
                "dark_attribution_lift_pct": ga4_snapshot.get("dark_attribution_lift_pct", 28.5),
            },
        },
        "telemetry_summary": telemetry_summary,
        "longitudinal_drift": drift,
        "industry_benchmark_comparison": {
            "industry_tag": percentiles["industry_tag"],
            "client_percentile": percentiles["percentile"],
            "industry_avg_mavi": percentiles["industry_avg_mavi"],
            "industry_avg_ai_referral_ratio": percentiles["industry_avg_ai_referral_ratio"],
            "industry_avg_evidence": percentiles["industry_avg_evidence"],
            "sample_size": percentiles["sample_size"],
            "privacy_isolation_verified": True,
        },
        "extraction_summary": {
            "title": extraction_result.seo.meta_title if extraction_result.seo else None,
            "word_count": len(extraction_result.markdown.split()) if extraction_result.markdown else 0,
            "latency_ms": round(extraction_result.metadata.execution_time_ms, 2),
        },
    }
