# Molavi Web Intelligence Engine (MWIE)

<div align="center">

**One Engine. Complete Web Intelligence.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](pyproject.toml)
[![Tests](https://img.shields.io/badge/Tests-23%20Passed-brightgreen)](tests/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![MCP](https://img.shields.io/badge/MCP-Native%20Server-purple.svg)](https://modelcontextprotocol.io)
[![Author](https://img.shields.io/badge/Author-Taqi%20Molavi-orange.svg)](https://molavi.pro)

**[English](README.md) | [فارسی](README.fa.md) | [Türkçe](README.tr.md) | [Azərbaycan](README.az.md) | [العربية](README.ar.md)**

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

## 5. Architecture Overview

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

## 8. Model Context Protocol (MCP) Integration

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

## 9. Docker Deployment

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

## 10. Security & Responsible Crawling

MWIE includes strict built-in security features:
- **SSRF Protection:** By default, RFC 1918 private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), localhost (`127.0.0.1`), and loopback addresses are strictly blocked.
- **Robots.txt Adherence:** Automatically respects `robots.txt` disallow rules.
- **Domain Allowlists/Blocklists:** Configurable in settings or via environment variables.

---

## 11. Empirical Benchmarks

Empirical measurements on Linux ARM64 (100 iterations per component):
- **HTML Parsing & Noise Cleaning:** 13.10 ms avg latency (76.4 ops/sec, ~4.7 MB peak RAM)
- **Markdown Generator:** 2.56 ms avg latency (390.7 ops/sec, ~2.6 MB peak RAM)
- **Technical SEO Analyzer:** 11.25 ms avg latency (88.9 ops/sec, ~2.4 MB peak RAM)
- **GEO & Entity Graph Engine:** 8.56 ms avg latency (116.8 ops/sec, ~6.4 MB peak RAM)

See [docs/BENCHMARKS.md](docs/BENCHMARKS.md) for full reproducible details.

---

## 12. License & Attribution

- Released under the **Apache License 2.0**. See [LICENSE](LICENSE) for terms.
- Independent clean-room architecture developed by **Taqi Molavi**.
- Third-party research references and licenses are documented in [CREDITS.md](CREDITS.md) and [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

---

## 13. Author & Ecosystem

**Author:** Taqi Molavi  
**Website:** [https://molavi.pro](https://molavi.pro)  
**Ecosystem Integrations:** [Hermes Agent](integrations/hermes/) | [Hamzad Digital Twins](integrations/hamzad/)
