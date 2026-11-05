# Empirical Benchmarks & Performance Analysis

This document reports empirical performance measurements for the core processing engines of the **Molavi Web Intelligence Engine (MWIE)**. All metrics are measured using native profiling tools (`cProfile`, `time.perf_counter`, and `tracemalloc`) on real HTML fixtures.

---

## 1. Benchmark Environment

- **OS:** Linux (ARM64 / aarch64)
- **Python Version:** 3.14.4
- **Measurement Tool:** `scripts/run_benchmarks.py`
- **Fixture:** `tests/fixtures/sample_page.html` (Full semantic HTML document containing metadata, open graph tags, JSON-LD schemas, tables, headings, and images)
- **Iterations:** 100 consecutive operations per pipeline component

---

## 2. Empirical Benchmark Results

| Engine Component | Avg Latency (ms) | Throughput (ops/sec) | Peak Memory Allocated (KB) | Output Validity & Completeness |
| :--- | :--- | :--- | :--- | :--- |
| **HTML Parser & DOM Noise Cleaner** | 13.10 ms | 76.4 ops/s | 4,832.32 KB (~4.7 MB) | 100% clean DOM, boilerplate stripped |
| **Markdown Generator** | 2.56 ms | 390.7 ops/s | 2,697.00 KB (~2.6 MB) | Clean Markdown with headings, tables, links |
| **Technical SEO Engine** | 11.25 ms | 88.9 ops/s | 2,509.35 KB (~2.4 MB) | Full indexability, canonical, tags & score |
| **GEO & Entity Graph Engine** | 8.56 ms | 116.8 ops/s | 6,558.10 KB (~6.4 MB) | Brand entities, citations, Q&A blocks |

---

## 3. Adapter Characteristics Comparison

| Adapter Backend | Typical Latency | RAM per Worker | JavaScript Support | Operating Cost | Best Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Native HTTP (`native_http`)** | 20–80 ms | < 25 MB | No | Zero (Local async socket) | Static websites, blogs, APIs, sitemaps, robots.txt |
| **Playwright Browser (`playwright_browser`)** | 600–1800 ms | 250–500 MB | Yes (Full DOM) | Low (Local headless Chromium) | Dynamic SPAs, client-rendered React/Vue/Angular |
| **Firecrawl Adapter (`firecrawl_api`)** | 800–2500 ms | Minimal (Client) | Yes | Variable (Self-hosted or Cloud) | Delegated crawling jobs & external worker clusters |

---

## 4. Reproducing the Benchmarks

To reproduce these measurements locally:

```bash
git clone https://github.com/tmolavi/molavi-web-intelligence.git
cd molavi-web-intelligence
python3 -m pip install -e ".[dev]"
python3 scripts/run_benchmarks.py
```
