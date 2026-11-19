"""
PostgreSQL Persistence Layer with Strict Privacy Isolation.

Partitioning:
- private_client_audits: Strictly Private (lead identity, exact domain, raw GSC/GA4 snapshots)
- anonymized_industry_benchmarks: Zero PII (public statistical aggregates only)
"""

import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Optional

try:
    import asyncpg
except ImportError:
    asyncpg = None

logger = logging.getLogger("mwie.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS private_client_audits (
    id BIGSERIAL PRIMARY KEY,
    lead_email VARCHAR(255) NOT NULL,
    lead_name VARCHAR(255),
    composio_entity_id VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    gsc_snapshot_json JSONB DEFAULT '{}'::jsonb,
    ga4_snapshot_json JSONB DEFAULT '{}'::jsonb,
    mavi_score NUMERIC(5, 2) NOT NULL,
    evidence_score NUMERIC(5, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_private_client_audits_email_domain 
    ON private_client_audits(lead_email, domain);

CREATE INDEX IF NOT EXISTS idx_private_client_audits_entity 
    ON private_client_audits(composio_entity_id);

CREATE INDEX IF NOT EXISTS idx_private_client_audits_created 
    ON private_client_audits(created_at DESC);

CREATE TABLE IF NOT EXISTS anonymized_industry_benchmarks (
    id BIGSERIAL PRIMARY KEY,
    industry_tag VARCHAR(100) NOT NULL,
    mavi_score NUMERIC(5, 2) NOT NULL,
    rp_score NUMERIC(5, 2) NOT NULL,
    cs_score NUMERIC(5, 2) NOT NULL,
    es_score NUMERIC(5, 2) NOT NULL,
    evidence_score NUMERIC(5, 2) NOT NULL,
    ai_referral_ratio NUMERIC(5, 4) NOT NULL,
    bucket_month VARCHAR(7) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_anon_benchmarks_industry_bucket 
    ON anonymized_industry_benchmarks(industry_tag, bucket_month);

CREATE INDEX IF NOT EXISTS idx_anon_benchmarks_mavi 
    ON anonymized_industry_benchmarks(mavi_score DESC);
"""

# Fallback in-memory store for environments without a live PostgreSQL instance (e.g. unit tests)
_in_memory_private_audits: list[dict[str, Any]] = []
_in_memory_benchmarks: list[dict[str, Any]] = [
    # Seed sample baseline industry benchmarks
    {"id": 1, "industry_tag": "technology", "mavi_score": 68.5, "rp_score": 72.0, "cs_score": 65.0, "es_score": 70.0, "evidence_score": 62.0, "ai_referral_ratio": 0.2450, "bucket_month": "2026-11", "created_at": "2026-11-01T00:00:00Z"},
    {"id": 2, "industry_tag": "technology", "mavi_score": 75.0, "rp_score": 80.0, "cs_score": 74.0, "es_score": 78.0, "evidence_score": 71.0, "ai_referral_ratio": 0.2900, "bucket_month": "2026-11", "created_at": "2026-11-02T00:00:00Z"},
    {"id": 3, "industry_tag": "technology", "mavi_score": 54.0, "rp_score": 58.0, "cs_score": 51.0, "es_score": 55.0, "evidence_score": 48.0, "ai_referral_ratio": 0.1600, "bucket_month": "2026-11", "created_at": "2026-11-03T00:00:00Z"},
    {"id": 4, "industry_tag": "general", "mavi_score": 62.0, "rp_score": 64.0, "cs_score": 60.0, "es_score": 65.0, "evidence_score": 55.0, "ai_referral_ratio": 0.1950, "bucket_month": "2026-11", "created_at": "2026-11-01T00:00:00Z"},
    {"id": 5, "industry_tag": "general", "mavi_score": 71.5, "rp_score": 75.0, "cs_score": 70.0, "es_score": 73.0, "evidence_score": 68.0, "ai_referral_ratio": 0.2520, "bucket_month": "2026-11", "created_at": "2026-11-02T00:00:00Z"},
    {"id": 6, "industry_tag": "ecommerce", "mavi_score": 59.0, "rp_score": 62.0, "cs_score": 58.0, "es_score": 61.0, "evidence_score": 50.0, "ai_referral_ratio": 0.1450, "bucket_month": "2026-11", "created_at": "2026-11-01T00:00:00Z"},
]


class DatabaseManager:
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self._pool: Optional[Any] = None

    async def get_pool(self):
        if not self.database_url or asyncpg is None:
            return None
        if self._pool is None:
            try:
                self._pool = await asyncpg.create_pool(dsn=self.database_url, min_size=1, max_size=10)
                await self.init_db()
            except Exception as e:
                logger.warning("Could not connect to PostgreSQL via asyncpg: %s. Using local privacy store.", e)
                self._pool = None
        return self._pool

    async def init_db(self):
        pool = await self.get_pool()
        if pool:
            async with pool.acquire() as conn:
                await conn.execute(SCHEMA_SQL)
                logger.info("PostgreSQL tables and indexes verified successfully.")
        return True

    # -------------------------------------------------------------------------
    # 1. Private Client Audits (Strict Isolation)
    # -------------------------------------------------------------------------
    async def insert_private_client_audit(
        self,
        lead_email: str,
        lead_name: Optional[str],
        composio_entity_id: str,
        domain: str,
        gsc_snapshot: dict[str, Any],
        ga4_snapshot: dict[str, Any],
        mavi_score: float,
        evidence_score: float,
    ) -> dict[str, Any]:
        """
        Inserts a client audit into the private table.
        This record contains verified PII and raw analytics snapshots.
        It is strictly forbidden to expose this table to public endpoints.
        """
        clean_email = lead_email.strip().lower()
        clean_domain = domain.strip().lower().replace("http://", "").replace("https://", "").split("/")[0]

        pool = await self.get_pool()
        if pool:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    INSERT INTO private_client_audits (
                        lead_email, lead_name, composio_entity_id, domain,
                        gsc_snapshot_json, ga4_snapshot_json, mavi_score, evidence_score
                    ) VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb, $7, $8)
                    RETURNING id, lead_email, lead_name, composio_entity_id, domain, mavi_score, evidence_score, created_at
                    """,
                    clean_email,
                    lead_name,
                    composio_entity_id,
                    clean_domain,
                    json.dumps(gsc_snapshot),
                    json.dumps(ga4_snapshot),
                    float(mavi_score),
                    float(evidence_score),
                )
                return dict(row)

        # Fallback in-memory
        record = {
            "id": len(_in_memory_private_audits) + 1,
            "lead_email": clean_email,
            "lead_name": lead_name,
            "composio_entity_id": composio_entity_id,
            "domain": clean_domain,
            "gsc_snapshot_json": gsc_snapshot,
            "ga4_snapshot_json": ga4_snapshot,
            "mavi_score": float(mavi_score),
            "evidence_score": float(evidence_score),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        _in_memory_private_audits.append(record)
        return record

    async def get_previous_client_audit(
        self,
        lead_email: str,
        domain: str,
    ) -> Optional[dict[str, Any]]:
        """
        Retrieves the most recent previous audit for this user & domain
        to calculate longitudinal drift.
        """
        clean_email = lead_email.strip().lower()
        clean_domain = domain.strip().lower().replace("http://", "").replace("https://", "").split("/")[0]

        pool = await self.get_pool()
        if pool:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT id, lead_email, domain, gsc_snapshot_json, ga4_snapshot_json,
                           mavi_score, evidence_score, created_at
                    FROM private_client_audits
                    WHERE lead_email = $1 AND domain = $2
                    ORDER BY created_at DESC
                    LIMIT 1 OFFSET 1
                    """,
                    clean_email,
                    clean_domain,
                )
                return dict(row) if row else None

        # Fallback in-memory: find matching records sorted by created_at DESC
        matches = [
            r for r in _in_memory_private_audits
            if r["lead_email"] == clean_email and r["domain"] == clean_domain
        ]
        if len(matches) >= 2:
            # Most recent is index -1, previous is index -2
            return matches[-2]
        return None

    def calculate_drift(
        self,
        current_mavi: float,
        current_evidence: float,
        current_gsc: dict[str, Any],
        current_ga4: dict[str, Any],
        previous_audit: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Calculates score and telemetry drift between the current audit
        and the previously stored audit in PostgreSQL.
        """
        if not previous_audit:
            return {
                "has_drift": False,
                "message": "Baseline audit recorded. Longitudinal drift will be tracked on subsequent audits.",
                "mavi_drift": 0.0,
                "evidence_drift": 0.0,
                "ctr_drift": 0.0,
                "ai_referral_drift": 0.0,
                "previous_created_at": None,
            }

        prev_mavi = float(previous_audit.get("mavi_score", current_mavi))
        prev_evidence = float(previous_audit.get("evidence_score", current_evidence))

        # Previous GSC snapshot
        prev_gsc = previous_audit.get("gsc_snapshot_json") or {}
        if isinstance(prev_gsc, str):
            try:
                prev_gsc = json.loads(prev_gsc)
            except Exception:
                prev_gsc = {}

        # Previous GA4 snapshot
        prev_ga4 = previous_audit.get("ga4_snapshot_json") or {}
        if isinstance(prev_ga4, str):
            try:
                prev_ga4 = json.loads(prev_ga4)
            except Exception:
                prev_ga4 = {}

        prev_ctr = float(prev_gsc.get("average_ctr", 0.0))
        curr_ctr = float(current_gsc.get("average_ctr", 0.0))

        prev_ai_ratio = float(prev_ga4.get("ai_referral_ratio", 0.0))
        curr_ai_ratio = float(current_ga4.get("ai_referral_ratio", 0.0))

        return {
            "has_drift": True,
            "previous_audit_id": previous_audit.get("id"),
            "previous_created_at": str(previous_audit.get("created_at")),
            "mavi_drift": round(current_mavi - prev_mavi, 2),
            "evidence_drift": round(current_evidence - prev_evidence, 2),
            "ctr_drift": round(curr_ctr - prev_ctr, 4),
            "ai_referral_drift": round(curr_ai_ratio - prev_ai_ratio, 4),
            "summary": (
                f"MAVI score shifted by {'+' if current_mavi >= prev_mavi else ''}{round(current_mavi - prev_mavi, 2)} pts "
                f"since {str(previous_audit.get('created_at'))[:10]}."
            ),
        }

    # -------------------------------------------------------------------------
    # 2. Anonymized Public Benchmarks (Zero PII - Strict Sanitization)
    # -------------------------------------------------------------------------
    @staticmethod
    def sanitize_for_benchmark(
        raw_audit_data: dict[str, Any],
        industry_tag: str = "general",
    ) -> dict[str, Any]:
        """
        STRICT PRIVACY SANITIZER (Zero PII Guarantee).
        Takes raw audit data and strips:
        - lead_email, lead_name
        - domain, url, hostname
        - exact search query terms, page paths
        - raw traffic numbers (exact clicks, exact impressions, exact user counts)

        Outputs ONLY dimensionless ratios and scores:
        - industry_tag
        - mavi_score
        - rp_score (Response Probability - AEO)
        - cs_score (Citation Share - GEO)
        - es_score (Engine Synchronization - SEO)
        - evidence_score
        - ai_referral_ratio (dimensionless float)
        - bucket_month (YYYY-MM)
        """
        # 1. Prohibited keys assertion
        forbidden_substrings = ["email", "domain", "url", "name", "token", "query", "path", "ip"]
        for key in raw_audit_data.keys():
            k_lower = key.lower()
            # If anyone passes a raw PII field directly, verify it is completely discarded
            if any(sub in k_lower for sub in forbidden_substrings) and k_lower not in ["evidence_score", "rp_score", "cs_score", "es_score"]:
                logger.debug("PII key detected in raw payload and will be stripped: %s", key)

        # 2. Extract or calculate normalized scores
        seo_score = float(raw_audit_data.get("seo_score", 65.0))
        aeo_score = float(raw_audit_data.get("aeo_score", 70.0))
        geo_score = float(raw_audit_data.get("geo_score", 68.0))

        # Core weighted formula: SEO 30%, AEO 35%, GEO 35%
        mavi_score = raw_audit_data.get("mavi_score")
        if mavi_score is None:
            mavi_score = round(0.30 * seo_score + 0.35 * aeo_score + 0.35 * geo_score, 2)
        else:
            mavi_score = round(float(mavi_score), 2)

        evidence_score = round(float(raw_audit_data.get("evidence_score", 60.0)), 2)

        # Compute or sanitize ai_referral_ratio (dimensionless float between 0.0 and 1.0)
        ai_ratio = raw_audit_data.get("ai_referral_ratio")
        if ai_ratio is None:
            # Check if GA4 data has ai_referral_sessions and total_sessions
            ai_sessions = float(raw_audit_data.get("ai_referral_sessions", 0))
            tot_sessions = float(raw_audit_data.get("total_sessions", 0))
            if tot_sessions > 0:
                ai_ratio = round(ai_sessions / tot_sessions, 4)
            else:
                ai_ratio = 0.2000  # Default normalized aggregate ratio
        else:
            ai_ratio = round(float(ai_ratio), 4)

        # Clean industry tag
        clean_industry = re.sub(r"[^a-zA-Z0-9_\-]", "", industry_tag.lower().strip()) or "general"
        bucket_month = datetime.now(timezone.utc).strftime("%Y-%m")

        sanitized_record = {
            "industry_tag": clean_industry[:100],
            "mavi_score": float(mavi_score),
            "rp_score": round(aeo_score, 2),
            "cs_score": round(geo_score, 2),
            "es_score": round(seo_score, 2),
            "evidence_score": float(evidence_score),
            "ai_referral_ratio": float(ai_ratio),
            "bucket_month": bucket_month,
        }

        # FINAL INVARIANT SAFETY CHECK: Assert ZERO PII keys in sanitized record
        for k in sanitized_record.keys():
            assert k in [
                "industry_tag", "mavi_score", "rp_score", "cs_score", "es_score",
                "evidence_score", "ai_referral_ratio", "bucket_month"
            ], f"Forbidden key {k} breached privacy boundary!"

        # Assert no string values contain '@' or 'http'
        for val in sanitized_record.values():
            if isinstance(val, str):
                assert "@" not in val, "Email detected in benchmark value!"
                assert "http://" not in val and "https://" not in val, "URL detected in benchmark value!"

        return sanitized_record

    async def insert_anonymized_benchmark(
        self,
        sanitized_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Inserts sanitized, non-PII benchmark record into PostgreSQL.
        """
        # Re-enforce sanitizer
        data = self.sanitize_for_benchmark(sanitized_data, sanitized_data.get("industry_tag", "general"))

        pool = await self.get_pool()
        if pool:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    INSERT INTO anonymized_industry_benchmarks (
                        industry_tag, mavi_score, rp_score, cs_score, es_score,
                        evidence_score, ai_referral_ratio, bucket_month
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    RETURNING id, industry_tag, mavi_score, rp_score, cs_score, es_score,
                              evidence_score, ai_referral_ratio, bucket_month, created_at
                    """,
                    data["industry_tag"],
                    data["mavi_score"],
                    data["rp_score"],
                    data["cs_score"],
                    data["es_score"],
                    data["evidence_score"],
                    data["ai_referral_ratio"],
                    data["bucket_month"],
                )
                return dict(row)

        # Fallback in-memory
        record = {
            "id": len(_in_memory_benchmarks) + 1,
            **data,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        _in_memory_benchmarks.append(record)
        return record

    async def get_industry_percentiles(
        self,
        mavi_score: float,
        industry_tag: str = "general",
    ) -> dict[str, Any]:
        """
        Computes percentile ranking against the anonymized industry benchmark pool.
        Does not reveal any other entity's domain, email, or individual scores.
        """
        clean_industry = re.sub(r"[^a-zA-Z0-9_\-]", "", industry_tag.lower().strip()) or "general"

        pool = await self.get_pool()
        if pool:
            async with pool.acquire() as conn:
                stats = await conn.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as total_samples,
                        COUNT(*) FILTER (WHERE mavi_score <= $1) as below_count,
                        AVG(mavi_score) as avg_mavi,
                        AVG(ai_referral_ratio) as avg_ai_ratio,
                        AVG(evidence_score) as avg_evidence
                    FROM anonymized_industry_benchmarks
                    WHERE industry_tag = $2 OR industry_tag = 'general'
                    """,
                    float(mavi_score),
                    clean_industry,
                )
                if stats and stats["total_samples"] > 0:
                    total = stats["total_samples"]
                    below = stats["below_count"]
                    percentile = round((below / total) * 100, 1)
                    return {
                        "industry_tag": clean_industry,
                        "sample_size": total,
                        "percentile": min(99.9, max(1.0, percentile)),
                        "industry_avg_mavi": round(float(stats["avg_mavi"] or 65.0), 1),
                        "industry_avg_ai_referral_ratio": round(float(stats["avg_ai_ratio"] or 0.22), 4),
                        "industry_avg_evidence": round(float(stats["avg_evidence"] or 60.0), 1),
                    }

        # Fallback in-memory
        samples = [
            b for b in _in_memory_benchmarks
            if b["industry_tag"] in [clean_industry, "general"]
        ]
        if not samples:
            samples = _in_memory_benchmarks

        total = len(samples)
        below = sum(1 for s in samples if s["mavi_score"] <= mavi_score)
        percentile = round((below / total) * 100, 1) if total > 0 else 50.0
        avg_mavi = sum(s["mavi_score"] for s in samples) / total if total > 0 else 65.0
        avg_ai = sum(s["ai_referral_ratio"] for s in samples) / total if total > 0 else 0.22
        avg_ev = sum(s["evidence_score"] for s in samples) / total if total > 0 else 60.0

        return {
            "industry_tag": clean_industry,
            "sample_size": total,
            "percentile": min(99.9, max(1.0, percentile)),
            "industry_avg_mavi": round(avg_mavi, 1),
            "industry_avg_ai_referral_ratio": round(avg_ai, 4),
            "industry_avg_evidence": round(avg_ev, 1),
        }


db_manager = DatabaseManager()
