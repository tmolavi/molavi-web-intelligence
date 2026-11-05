# Technology Comparison Matrix

A structured comparative matrix comparing the 10 reference systems across key architecture vectors, capabilities, licensing, and integration with the **Molavi Web Intelligence Engine (MWIE)**.

| Project | Primary Language | License | Primary Architectural Focus | Browser Engine | LLM / AI Native | MCP Server | SEO / GEO Depth | MWIE Architectural Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01. Firecrawl** | TypeScript | AGPL-3.0 | API-first web scraping & crawling | Chromium (Playwright) | Yes (Markdown / Schema) | External | General / Minimal | External HTTP Adapter (clean-room) |
| **02. Camoufox** | Python / C++ | MPL-2.0 | Anti-detect browser stealth & fingerprint spoofing | Firefox (C++ Patch) | No | No | Indirect (SPA rendering) | Optional High-Stealth Browser Engine |
| **03. Scrapling** | Python | BSD-3-Clause | Ultra-fast adaptive parsing & resilient selectors | Optional | No | No | Structural extraction | Native DOM Parser & Selector Engine |
| **04. Crawl4AI** | Python | Apache-2.0 | LLM-ready markdown extraction & RAG chunking | Playwright | Yes (Markdown / Vectors) | Community | Medium (LLM focus) | Semantic Extractor & Markdown Pipeline |
| **05. ScrapeGraphAI** | Python | MIT | Graph-based prompt scraping pipelines | Playwright | Yes (Graph LLM) | No | Schema generation | Optional Graph-based AI Enrichment |
| **06. Apify MCP Server**| TypeScript | MIT | MCP protocol bridge for external actors | Cloud Actors | Yes (Agent interface) | Yes (Native) | Actor-dependent | Pattern for MWIE Native Python MCP |
| **07. Nanobrowser** | TypeScript | Apache-2.0 | In-browser user-authenticated AI agent | Chrome (Extension) | Yes (Agent actions) | No | Content inspection | Authenticated Context Patterns |
| **08. Agent Desktop** | Rust / TS | Apache-2.0 | Computer-use via Accessibility Tree (AXTree) | OS Level | Yes (Computer Use) | No | Indirect (a11y hierarchy) | ARIA & Semantic a11y Signal Parser |
| **09. Maxun** | TypeScript | AGPL-3.0 | No-code visual scraper builder & scheduler | Playwright | Partial | No | Monitoring only | Clean-room Job Scheduler & Monitoring |
| **10. Crawlee** | TS / Python | Apache-2.0 | Industrial request queues & autoscaled pool | Multi-tier | No | No | Crawl infrastructure | Request Queue & Crawler Lifecycle Core |
| **MWIE (Our System)** | **Python 3.12+** | **Apache-2.0** | **Unified Web, SEO & GEO Intelligence Engine** | **Playwright + Native HTTP** | **Yes (GEO / Entity Graph)**| **Yes (Native)** | **Deep First-Class Native**| **Unified Engine Platform** |

---

## Detailed Dimensions Comparison

### 1. Crawling & Queue Scalability
- **Crawlee** sets the standard for memory-bounded `RequestQueue` and self-throttling concurrency (`AutoscaledPool`).
- **Firecrawl** achieves scale via Redis + BullMQ worker clustering.
- **MWIE Approach:** Implements a dual-mode async Request Queue: an in-memory priority queue with URL canonicalization and deduplication for standalone lightweight single-node instances, with an optional Redis-backed queue for clustered scale.

### 2. Browser Automation vs Direct Fetch
- **Pure Browser Only (e.g. Nanobrowser, Camoufox):** High fidelity for dynamic single-page applications (SPAs), but heavy CPU/memory cost (300MB–1GB RAM per worker, 1–3s latency).
- **Fast HTTP Only (e.g. Scrapling HTTP mode):** Single-digit millisecond latency and minimal RAM, but fails on client-rendered client hydration.
- **MWIE Hybrid Routing:** Automatically routes static pages, sitemaps, and robots.txt to the lightning-fast asynchronous native HTTP fetcher; transparently promotes pages requiring JavaScript execution to the Playwright browser adapter based on dynamic heuristics.

### 3. SEO & GEO (Generative Engine Optimization) Native Capabilities
- None of the 10 existing open-source projects offer a comprehensive, dedicated **Technical SEO + GEO + Entity Relationship** analyzer out of the box:
  - Crawl4AI focuses on Markdown and LLM chunking.
  - Firecrawl provides Markdown and clean HTML.
  - Crawlee provides extraction building blocks.
- **MWIE Innovation:** Technical SEO (indexing rules, canonicals, hreflang, OpenGraph, JSON-LD schema parsing, heading hierarchy) and GEO Intelligence (brand entity recognition, quotation and citation context extraction, AI-readiness scoring, and Q&A knowledge mapping) are built into the primary extraction loop as first-class citizens.

### 4. Agent & Protocol Interoperability
- Only **Apify MCP Server** implements the Model Context Protocol (MCP) natively, but ties it to Apify's cloud ecosystem.
- **MWIE Innovation:** Ships with a zero-cloud, 100% self-hosted, native Python MCP server implementing the official Model Context Protocol specifications. Any agent (Hermes, Hamzad, Claude Desktop, Cursor) can directly inspect websites, run SEO audits, and extract GEO entity graphs locally.
