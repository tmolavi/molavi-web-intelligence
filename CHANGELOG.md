# Changelog

All notable changes to the **Molavi Web Intelligence Engine (MWIE)** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-11-05

### Added
- **Core Engine:**
  - High-performance modular architecture with typed Pydantic models.
  - Native SSRF protection blocking private, loopback, and reserved IP ranges.
  - TTL-based memory caching layer.
  - In-memory request queue with URL canonicalization, deduplication, and recursion depth limits.
- **Unified Extraction Engine & Adapters:**
  - Native Async HTTP Adapter for high-speed, zero-browser static extraction.
  - Playwright Headless Browser Adapter for client-rendered JavaScript SPAs.
  - Clean-room decoupled REST client adapter for external Firecrawl instances.
  - Adapter registry with real-time performance telemetry (latency, calls, success rates).
  - Evidence-based extraction router with automatic fallback execution.
- **Parsing & Markdown Generation:**
  - High-speed resilient HTML parser with DOM noise and boilerplate removal.
  - Deterministic Markdown generator producing hierarchical, LLM-ready markdown.
- **SEO-Native Intelligence:**
  - Technical SEO analyzer: meta titles, descriptions, canonicals, heading hierarchy, image alt audits, link graph extraction, OpenGraph, Twitter Cards, hreflang tags, and indexability rules.
  - Comprehensive weighted SEO score (0-100) with diagnostic recommendations.
  - Multi-page and competitor SEO comparison engine.
- **GEO-Native Intelligence (Generative Engine Optimization):**
  - Entity extraction (Brand, Organization, Person, Product) from JSON-LD schemas and body text.
  - Citation intelligence mapping external source links, blockquote references, and author attribution.
  - Answer-oriented Q&A knowledge block detection.
  - Semantic content chunking with character counts and token estimates for RAG pipelines.
  - AI-Readiness scorecard (0-100) tailored for generative engines (Perplexity, ChatGPT, Gemini).
- **Protocols & Interfaces:**
  - REST API powered by FastAPI with interactive Swagger UI (`/docs`).
  - Model Context Protocol (MCP) server exposing 12 native tools for autonomous AI agents.
  - Integration wrappers and examples for Hermes and Hamzad AI ecosystems.
- **Quality & Documentation:**
  - 23 automated unit and integration tests passing with 100% success rate.
  - Empirical, reproducible benchmark suite (`scripts/run_benchmarks.py`).
  - 5-language documentation suite (English, Persian, Turkish, Azerbaijani, Arabic).
