# Molavi Web Intelligence Engine (MWIE)

<div align="center">

**One Engine. Complete Web Intelligence.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](pyproject.toml)
[![Tests](https://img.shields.io/badge/Tests-39%20Passed-brightgreen)](tests/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![MCP](https://img.shields.io/badge/MCP-Native%20Server-purple.svg)](https://modelcontextprotocol.io)
[![Author](https://img.shields.io/badge/Author-Taqi%20Molavi-orange.svg)](https://molavi.pro)

**[English](README.md) | [فارسی](README.fa.md) | [Türkçe](README.tr.md) | [Azərbaycan](README.az.md) | [العربية](README.ar.md)**

<br/>

> 🚀 **Live Interactive Web Analyzer (100% Free & Model-Independent):**  
> Test the engine live in your browser across all 5 supported languages:  
> [🇮🇷 فارسی (Persian)](https://molavi.pro/fa/tools/web-intelligence) • [🇬🇧 English](https://molavi.pro/en/tools/web-intelligence) • [🇹🇷 Türkçe](https://molavi.pro/tr/tools/web-intelligence) • [🇦🇿 Azərbaycanca](https://molavi.pro/az/tools/web-intelligence) • [🇸🇦 العربية](https://molavi.pro/ar/tools/web-intelligence)

<br/>

[![Molavi Web Intelligence Explainer Video](docs/assets/poster.jpg)](https://molavi.pro/videos/web-intelligence/explainer.mp4)

*Visual Architecture & Video Walkthrough — [Watch High-Res Video](https://molavi.pro/videos/web-intelligence/explainer.mp4) or browse [`docs/assets/mwie-explainer.mp4`](docs/assets/mwie-explainer.mp4)*

</div>

---

## 1. Project Introduction

**Molavi Web Intelligence Engine (MWIE)** is an open-source, self-hosted web intelligence platform designed for **Technical SEO**, **Generative Engine Optimization (GEO)**, **AI Search Indexing**, and **Autonomous AI Agents**. 

Modern search has fundamentally transitioned from simple keyword matching to generative AI engines (Perplexity, ChatGPT Search, Google Gemini Grounding). Existing web scrapers focus either only on raw HTML extraction or simple Markdown conversion without understanding semantic entity graphs, citations, or technical SEO health.

MWIE unifies high-throughput HTTP crawling, headless JavaScript rendering, resilient DOM parsing, technical SEO scorecards, and AI-readiness analysis into a modular engine accessible via **REST API** and native **Model Context Protocol (MCP)**.

---

## 2. Core Features

- **Unified Multi-Adapter Extraction:**
  - *Native Async HTTP Adapter:* Ultra-fast (sub-20ms) scraping with zero browser overhead.
  - *Playwright Headless Browser Adapter:* Renders client-side dynamic JavaScript single-page apps (SPAs).
  - *Firecrawl Clean-Room Adapter:* Decoupled REST adapter for self-hosted or cloud Firecrawl clusters.
- **Intelligent Evidence-Based Routing:**
  - Automatically selects the optimal extraction backend based on page type, JavaScript requirements, and real-time performance telemetry.
  - Seamless automatic fallbacks to alternative adapters upon network or rendering anomalies.
- **Resilient Content & Markdown Generation:**
  - Heuristic boilerplate noise removal (headers, footers, navigation, cookie banners).
  - Produces hierarchical, clean Markdown optimized for LLM prompts and RAG chunking.
- **Native Model Context Protocol (MCP) Server:**
  - Exposes 12 native tools directly to AI agent platforms (Hermes, Hamzad, Claude Desktop, Cursor).
- **Cost & Resource Efficiency:**
  - 100% self-hosted and open-source. Requires zero paid APIs to operate.

---

## 3. SEO-Native Intelligence Capabilities

Technical SEO is a first-class citizen inside MWIE:
- **Indexability & Crawl Control:** Meta robots (`noindex`, `nofollow`), `X-Robots-Tag`, HTTP status code validation.
- **Metadata Auditing:** Meta title and description length evaluation against search snippet thresholds.
- **Canonical Consistency:** Rel canonical extraction and cross-check against target request URLs.
- **Heading Hierarchy:** Deep analysis of H1-H6 tags, single H1 compliance, and semantic nesting.
- **Image Accessibility:** Total image audit, alt text detection, and missing alt reporting.
- **Link Graph Intelligence:** Separation and counting of internal vs external URLs.
- **Structured Data:** Full Schema.org JSON-LD extraction, microdata detection, and schema type mapping.
- **Social Tags:** Open Graph (`og:*`) and Twitter Cards (`twitter:*`) completeness analysis.
- **Internationalization:** Hreflang tag parsing and target language validation.
- **Content-to-HTML Ratio:** Diagnostic ratio calculation highlighting text density vs boilerplate code.
- **Weighted SEO Scorecard:** Generates an objective 0–100 score accompanied by actionable diagnostic recommendations.

---

## 4. GEO-Native Intelligence Capabilities

Generative Engine Optimization (GEO) prepares content for generative discovery:
- **Brand & Entity Recognition:** Extracts Brand, Organization, Person, and Product entities from JSON-LD and content text.
- **Citation Intelligence:** Maps external references, source links, blockquote citations, and author attribution.
- **Answer-Oriented Q&A Extraction:** Automatically discovers FAQPage structures and interrogative heading/answer pairs.
- **Semantic Content Chunking:** Splits body copy into clean, token-estimated chunks tailored for vector embeddings and RAG pipelines.
- **AI-Readiness Scorecard:** 0–100 score quantifying entity density, citation grounding, Q&A clarity, and chunkability for generative search engines.

---

## 5. Citation Evidence, Quote Density & Offer Transparency Probe

The **Citation Evidence & Offer Transparency Probe** (`mwie.citations.citation_evidence_probe`) audits whether a web page contains authoritative grounding for Generative AI engines and transparent commercial offerings:

- **Attributed Expert Quotations:** Parses `<blockquote>`, `<q>`, and natural-language quotation patterns to count expert quotes and author/source attributions.
- **Verifiable Statistical Claims & Empirical Grounding:** Detects precise percentages (`84.5%`), year-stamped figures/benchmarks (`in 2024`, `by 2026`), and outbound citations to primary research domains (`.edu`, `.org`, `arxiv.org`, `doi.org`, `nih.gov`, `nature.com`, `ieee.org`).
- **Commercial Offer Transparency:** For commercial and service pages, detects explicit pricing tables, currency disclosures (`$`, `€`, `₺`, `تومان`, `USD`, `EUR`, `TRY`), structured deliverables (checkmarked features, scope definitions), and SLA commitments.
- **Citability Scorecard & Remediation:** Produces an objective `evidence_citability_score` (0–100) and up to 3 prioritized remediation tips.

### Sample JSON Output (`evidence_citability`)
```json
{
  "evidence_citability": {
    "evidence_citability_score": 88,
    "expert_quotes_count": 2,
    "expert_quotes": [
      {
        "quote": "Generative Search Optimization requires verifiable citation density and grounded empirical evidence.",
        "author": "Dr. Alex Smith",
        "source": "https://arxiv.org/abs/2301.00000",
        "element_type": "blockquote"
      }
    ],
    "statistical_claims_count": 3,
    "statistical_claims": [
      {
        "claim_text": "organic AI citation traffic increased by 84.5% across global brands",
        "claim_type": "percentage",
        "source_url": null
      },
      {
        "claim_text": "Primary research/authority citation (stanford.edu): Stanford AI Lab",
        "claim_type": "research_citation",
        "source_url": "https://stanford.edu/research/ai-search"
      }
    ],
    "research_links_count": 2,
    "research_domains": ["stanford.edu", "arxiv.org"],
    "offer_transparency": {
      "is_commercial_url": true,
      "has_pricing_table": true,
      "has_structured_deliverables": true,
      "detected_currencies": ["$", "USD"],
      "deliverables_count": 3,
      "transparency_score": 100
    },
    "remediation_tips": [
      "Embed attributed expert quotes (`<blockquote>`, `<q>`, or author citations) to elevate domain authority.",
      "Incorporate verifiable statistical claims, date-stamped figures, and primary research links (.edu, .org, arXiv, DOI)."
    ]
  }
}
```

> 🌐 **Interactive Production Tool & Consulting Ecosystem:**  
> - Run live web intelligence audits: [https://molavi.pro/tools/web-intelligence](https://molavi.pro/tools/web-intelligence)  
> - Enterprise GEO & AI Search Consulting: [https://inten.asia](https://inten.asia)

---

## 6. Multi-Engine Shortlist & Branded-Query Defense Probe

The **Multi-Engine Shortlist & Branded-Query Defense Probe** (`mwie.engines.multi_engine_probe`) analyzes content against empirical findings across the three major AI engines:

- **ChatGPT (`GPT-5.6`) Readiness (0–100):**
  - **Entity Graph Stability:** Validates Schema.org `@graph` networks (`Organization`, `Person`, `Brand`, `Product`, `Service`).
  - **`sameAs` Disambiguation:** Checks presence of verified profile links across Wikidata, Wikipedia, LinkedIn, GitHub, and Crunchbase.
  - **Structured Brand/Product Facts:** Evaluates key product attributes, `<dl>` definition lists, structured pricing tables, and schema offers.
- **Google AI Mode Readiness (0–100):**
  - **Conversational 3x-Long Query Coverage:** Audits H2/H3 question headings and FAQPage schemas against conversational search queries in 5 languages (`en`, `fa`, `ar`, `tr`, `az`).
  - **Top-30% Answer Clarity:** Detects concise, self-contained definitional answer blocks in the opening 30% of content.
  - **Branded Entity Defense:** Checks canonical domain alignment, brand anchor in title & H1, preventing AI Overviews from prioritizing scrapers or competitor aggregators for branded searches.
- **Perplexity Readiness (0–100):**
  - **Statistical & Numeric Density:** Audits high-density verifiable claims (percentages, year-stamped milestones, comparative metrics).
  - **Outbound Primary Citations:** Verifies references to academic papers, open standards, and primary research (`.edu`, `.gov`, `arxiv.org`, `doi.org`, `w3.org`).
  - **Quote Extractability:** Detects attributed `<blockquote>`, `<q>`, and self-contained 134–167 word semantic blocks.
- **Branded Defense Status:** Determines whether the brand's entity narrative is securely controlled (`defended`, `adequate`, `vulnerable`).

### Sample JSON Output (`engine_matrix`)
```json
{
  "engine_matrix": {
    "chatgpt_score": 92,
    "google_ai_mode_score": 88,
    "perplexity_score": 95,
    "branded_defense_status": "defended",
    "chatgpt_breakdown": {
      "has_brand_schema": true,
      "has_graph_network": true,
      "same_as_count": 3,
      "disambiguation_profiles": [
        "https://www.wikidata.org/wiki/Q123456",
        "https://www.linkedin.com/in/taghimolavi",
        "https://github.com/tmolavi"
      ],
      "structured_facts_detected": 8,
      "brand_in_title": true,
      "brand_in_h1": true
    },
    "google_breakdown": {
      "conversational_questions_count": 4,
      "sample_question_headings": [
        "How does Google AI Mode evaluate conversational queries?",
        "What are the primary citation benchmarks in 2026?"
      ],
      "has_faq_schema": true,
      "has_direct_definition_top30": true,
      "has_concise_snippet_opening": true,
      "branded_defense_anchor": true
    },
    "perplexity_breakdown": {
      "statistical_claims_count": 6,
      "outbound_primary_citations_count": 3,
      "sample_primary_citations": [
        "https://arxiv.org/abs/2601.00000",
        "https://stanford.edu/research"
      ],
      "quote_blocks_count": 2,
      "optimal_length_passages_count": 3
    },
    "remediation_tips": [
      "Incorporate conversational question-based H2 headings and direct answer definitions in the top 30% of content to capture Google AI Mode queries."
    ]
  }
}
```

---

## 7. Architecture Overview

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        AI Agents & Client Apps                         │
│           (Hermes, Hamzad, Claude Desktop, Cursor, REST Clients)       │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │ MCP (Stdio/SSE)                 │ REST API (HTTP)
┌──────────────────▼─────────────────────────────────▼───────────────────┐
│               Molavi Web Intelligence Engine (MWIE) Core               │
├────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────┐    ┌────────────────────────────────────┐ │
│ │  Intelligent Router      │    │  Request Queue & Robots Manager    │ │
│ └────────────┬─────────────┘    └────────────────────────────────────┘ │
│              │                                                         │
│ ┌────────────▼───────────────────────────────────────────────────────┐ │
│ │                   Unified Extraction Adapters                      │ │
│ │  • Native HTTP Adapter    • Playwright Adapter   • Firecrawl API   │ │
│ └────────────┬───────────────────────────────────────────────────────┘ │
│              │ Raw HTML                                                │
│ ┌────────────▼───────────────────────────────────────────────────────┐ │
│ │              Parsing & Content Cleaning Pipeline                   │ │
│ │  • Noise Stripper    • HTML Parser   • Markdown Generator          │ │
│ └────────────┬───────────────────────────────────────────────────────┘ │
│              │ Clean DOM & Text                                        │
│ ┌────────────▼────────────────────────┬──────────────────────────────┐ │
│ │    Technical SEO Analyzer           │     GEO & Entity Analyzer    │ │
│ │  • Canonical & Metadata             │  • Brand Entity Extraction   │ │
│ │  • Headings & Image Alts            │  • Citations & Author Map    │ │
│ │  • JSON-LD Structured Data          │  • Q&A Knowledge Blocks      │ │
│ │  • 0-100 Weighted Scorecard         │  • AI-Readiness Scorecard    │ │
│ └─────────────────────────────────────┴──────────────────────────────┘ │
│                                                                        │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │   Memory / Redis TTL Cache   •   SSRF Security & Allowlist Gates   │ │
│ └────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Installation & Quick Start

### Prerequisites
- Python 3.10+
- Linux, macOS, or Windows

### Installation
```bash
git clone https://github.com/tmolavi/molavi-web-intelligence.git
cd molavi-web-intelligence
python3 -m pip install -e .
```

For development (including testing tools):
```bash
python3 -m pip install -e ".[dev]"
```

### Quick Start via Python SDK
```python
import asyncio
from mwie.crawler.engine import crawl_engine
from mwie.core.models import ExtractionOptions


async def main():
    options = ExtractionOptions(render_js=False, extract_seo=True, extract_geo=True)
    result = await crawl_engine.extract_single("https://molavi.pro", options)

    print(f"Title: {result.seo.meta_title}")
    print(f"SEO Score: {result.seo.seo_score}/100")
    print(f"AI Readiness: {result.geo.ai_readiness_score}/100")
    print(f"Entities: {[e.name for e in result.geo.entities]}")


asyncio.run(main())
```

---

## 7. REST API Usage

Start the REST API server:
```bash
uvicorn mwie.api.app:app --host 0.0.0.0 --port 8000
```
Visit interactive API documentation at: `http://localhost:8000/docs`

### Example: Extract & Analyze URL
```bash
curl -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://molavi.pro"}'
```

### Example: Technical SEO Audit
```bash
curl -X POST http://localhost:8000/api/v1/seo \
  -H "Content-Type: application/json" \
  -d '{"url": "https://molavi.pro"}'
```

### Example: Compare Competitor Pages
```bash
curl -X POST http://localhost:8000/api/v1/compare \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://molavi.pro", "https://example.com"]}'
```

---

## 8. Composio OAuth & PostgreSQL Telemetry Enrichment

MWIE supports live search and traffic telemetry enrichment via **Composio** OAuth and **PostgreSQL** persistence with strict data privacy isolation.

### Supported OAuth Integrations
- **Gmail:** Verified lead owner identity and automated audit report delivery.
- **Google Search Console (GSC):** Verified domain properties, top search queries, clicks, impressions, and CTR.
- **Google Analytics 4 (GA4):** AI referral traffic telemetry (ChatGPT, Perplexity, Claude, Gemini sessions, AI referral ratio, dark attribution lift).

### Endpoints
- `POST /api/auth/composio/connect`: Initiates OAuth handshake via Composio for a client email and returns `connection_url`.
- `GET /api/auth/composio/callback`: Validates connection and extracts verified Gmail profile, GSC analytics, and GA4 telemetry.
- `POST /api/audit/enriched`: Merges DOM/Schema/MAVI score with live GSC/GA4 deltas and calculates longitudinal drift against previous PostgreSQL records.

### PostgreSQL Privacy Architecture
Persistence is split across two strictly partitioned tables:
- **`private_client_audits` (Strictly Private CRM / Longitudinal Store):**
  - Columns: `id`, `lead_email`, `lead_name`, `composio_entity_id`, `domain`, `gsc_snapshot_json`, `ga4_snapshot_json`, `mavi_score`, `evidence_score`, `created_at`.
  - Accessible only to authorized backend processes; never exposed to public endpoints.
- **`anonymized_industry_benchmarks` (Public Benchmark Pool - Zero PII):**
  - Columns: `id`, `industry_tag`, `mavi_score`, `rp_score`, `cs_score`, `es_score`, `evidence_score`, `ai_referral_ratio`, `bucket_month`, `created_at`.
  - All emails, client names, domains, URLs, search query terms, and raw traffic volumes are strictly scrubbed before insertion.

### Required Environment Variables
Set the following environment variables (never commit credentials to source control):
```bash
# PostgreSQL Database Connection URL
export DATABASE_URL="postgresql://user:password@localhost:5432/mwie_db"

# Composio API Key (Discoverable from Composio Dashboard or mcp_config.json)
export COMPOSIO_API_KEY="ck_live_..."

# Optional: Default redirect URL for Composio OAuth callback
export COMPOSIO_REDIRECT_URL="https://molavi.pro/tools/web-intelligence"
```

---

## 9. Model Context Protocol (MCP) Integration

MWIE provides a native Python MCP server exposing 12 tools for autonomous agents:

| Tool Name | Description |
| :--- | :--- |
| `crawl_url` | Full extraction, SEO, and GEO audit on a single URL |
| `crawl_domain` | Multi-page recursive domain crawl |
| `extract_page_content` | Fast extraction of noise-free text and Markdown |
| `analyze_seo` | Technical SEO scorecard and recommendations |
| `analyze_geo` | Generative Engine Optimization audit and AI readiness |
| `extract_entities` | Extract brand, person, organization, and product entities |
| `extract_structured_data` | Extract Schema.org JSON-LD schemas |
| `analyze_sitemap` | Parse and discover URLs from sitemap.xml |
| `compare_pages` | Side-by-side competitor SEO and GEO comparison |
| `batch_process_urls` | Batch concurrent processing of URL lists |
| `get_job_status` | Engine health, cache state, and registered adapters |
| `get_extraction_metadata`| Real-time adapter latency and success metrics |

### Adding MWIE to Claude Desktop
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "molavi-web-intelligence": {
      "command": "python3",
      "args": ["-m", "mwie.mcp.server"]
    }
  }
}
```

---

## 10. Docker Deployment

Deploy with Docker:
```bash
docker build -t molavi-web-intelligence .
docker run -p 8000:8000 molavi-web-intelligence
```

Or using Docker Compose:
```bash
docker compose up -d
```

---

## 11. Security & Responsible Crawling

MWIE includes strict built-in security features:
- **SSRF Protection:** By default, RFC 1918 private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), localhost (`127.0.0.1`), and loopback addresses are strictly blocked.
- **Robots.txt Adherence:** Automatically respects `robots.txt` disallow rules.
- **Domain Allowlists/Blocklists:** Configurable in settings or via environment variables.

---

## 12. Empirical Benchmarks & PostgreSQL Telemetry

Empirical measurements on Linux ARM64 (100 iterations per component):
- **HTML Parsing & Noise Cleaning:** 13.10 ms avg latency (76.4 ops/sec, ~4.7 MB peak RAM)
- **Markdown Generator:** 2.56 ms avg latency (390.7 ops/sec, ~2.6 MB peak RAM)
- **Technical SEO Analyzer:** 11.25 ms avg latency (88.9 ops/sec, ~2.4 MB peak RAM)
- **GEO & Entity Graph Engine:** 8.56 ms avg latency (116.8 ops/sec, ~6.4 MB peak RAM)

### Privacy-Preserving Industry Benchmark Pool
The web tool on `molavi.pro` provides an opt-in benchmark contribution mechanism where audit scores are recorded to the PostgreSQL `anonymized_industry_benchmarks` table with zero PII:
- Stripped of emails, names, URLs, exact queries, and raw traffic counts.
- Stores exclusively normalized dimensional scores (`mavi_score`, `rp_score`, `cs_score`, `es_score`, `evidence_score`, `ai_referral_ratio`) tagged by `industry_tag` and `bucket_month`.
- Allows calculating live percentile distributions and longitudinal drift while maintaining strict privacy boundaries.

---

## 13. License & Attribution

- Released under the **Apache License 2.0**. See [LICENSE](LICENSE) for terms.
- Independent clean-room architecture developed by **Taqi Molavi**.
- Third-party research references and licenses are documented in [CREDITS.md](CREDITS.md) and [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

---

## 14. Author & Ecosystem

**Author:** Taqi Molavi  
**Website:** [https://molavi.pro](https://molavi.pro)  
**Ecosystem Integrations:** [TM Molavi Agentic OS](https://github.com/tmolavi/molavi-agentic-os) | [TM Second Brain](https://github.com/tmolavi/tm-second-brain) | [Hermes Agent](integrations/hermes/) | [Hamzad Digital Twins](integrations/hamzad/)
