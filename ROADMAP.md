# Project Roadmap

The vision for the **Molavi Web Intelligence Engine (MWIE)** is to provide the standard open-source platform for autonomous web intelligence, SEO analytics, and Generative Engine Optimization (GEO).

---

## Phase 1 — Foundation & Core Platform (Completed in v0.1.0)
- [x] Multi-adapter unified extraction architecture (HTTP, Playwright, Firecrawl API)
- [x] Resilient HTML parser and LLM Markdown generator
- [x] Technical SEO audit engine with scorecards and actionable recommendations
- [x] GEO engine: Brand entity extraction, citation mapping, Q&A blocks, and AI-readiness
- [x] Evidence-based adapter routing and automatic fallbacks
- [x] 12 native Model Context Protocol (MCP) tools
- [x] Full REST API via FastAPI
- [x] Five-language documentation (EN, FA, TR, AZ, AR)
- [x] Comprehensive test suite & reproducible benchmarks

---

## Phase 2 — Distributed Crawling & Scalability (v0.2.0)
- [ ] Redis-backed distributed `RequestQueue` with worker clustering
- [ ] Celery / Arq asynchronous task worker integration
- [ ] S3 / MinIO artifact and screenshot archival storage
- [ ] Camoufox anti-detect engine integration as an optional stealth backend
- [ ] Domain-level crawl depth visualization and interactive HTML graph export

---

## Phase 3 — Deep GEO & Citation Monitoring (v0.3.0)
- [ ] Real-time observation of AI answers across Perplexity, Gemini Grounding, and ChatGPT
- [ ] Verification of website citation persistence in generative search indexers
- [ ] Knowledge graph export in RDF, Turtle, and Neo4j formats
- [ ] Multi-lingual semantic heading optimization for multilingual content hubs
