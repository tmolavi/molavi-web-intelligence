-- PostgreSQL Schema Migration for Molavi Web Intelligence Engine (MWIE)
-- Strict Privacy Partitioning: Private Client Audits vs. Anonymized Public Benchmarks

-- 1. Strictly Private Client Audits (Internal CRM & Longitudinal Drift Comparison Only)
-- NEVER exposed to public API endpoints.
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


-- 2. Anonymized Industry Benchmarks (Zero PII - Public Statistical Benchmark Pool)
-- Strictly stripped of email, name, domain, URL, exact search queries, and raw traffic counts.
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
