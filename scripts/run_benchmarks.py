"""
Reproducible Benchmark Suite for Molavi Web Intelligence Engine (MWIE).
Measures latency, memory usage, throughput, and extraction fidelity across components.
"""

import sys
import time
import tracemalloc
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mwie.geo.analyzer import GEOAnalyzer
from mwie.parsing.html_parser import HTMLParser
from mwie.parsing.markdown_generator import MarkdownGenerator
from mwie.seo.analyzer import SEOAnalyzer

FIXTURE_PATH = Path(__file__).parent.parent / "tests" / "fixtures" / "sample_page.html"


def benchmark_html_parsing(iterations: int = 100):
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    tracemalloc.start()
    start = time.perf_counter()

    for _ in range(iterations):
        p = HTMLParser(html, "https://molavi.pro/mwie")
        _, clean_text = p.get_clean_html_and_text()
        _ = p.get_headings()
        _ = p.get_images()
        _ = p.get_links()

    elapsed = (time.perf_counter() - start) * 1000.0
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    avg_latency = elapsed / iterations
    return {
        "iterations": iterations,
        "avg_latency_ms": round(avg_latency, 2),
        "total_time_ms": round(elapsed, 2),
        "peak_memory_kb": round(peak_mem / 1024, 2),
        "throughput_ops_per_sec": round(iterations / (elapsed / 1000.0), 1),
    }


def benchmark_seo_analyzer(iterations: int = 100):
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    tracemalloc.start()
    start = time.perf_counter()

    for _ in range(iterations):
        analyzer = SEOAnalyzer(html, "https://molavi.pro/mwie", 200)
        _ = analyzer.analyze()

    elapsed = (time.perf_counter() - start) * 1000.0
    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    avg_latency = elapsed / iterations
    return {
        "iterations": iterations,
        "avg_latency_ms": round(avg_latency, 2),
        "total_time_ms": round(elapsed, 2),
        "peak_memory_kb": round(peak_mem / 1024, 2),
        "throughput_ops_per_sec": round(iterations / (elapsed / 1000.0), 1),
    }


def benchmark_geo_analyzer(iterations: int = 100):
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    p = HTMLParser(html, "https://molavi.pro/mwie")
    _, clean_text = p.get_clean_html_and_text()
    seo = SEOAnalyzer(html, "https://molavi.pro/mwie", 200).analyze()

    tracemalloc.start()
    start = time.perf_counter()

    for _ in range(iterations):
        geo = GEOAnalyzer(html, clean_text, "https://molavi.pro/mwie", seo.json_ld_schemas)
        _ = geo.analyze()

    elapsed = (time.perf_counter() - start) * 1000.0
    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    avg_latency = elapsed / iterations
    return {
        "iterations": iterations,
        "avg_latency_ms": round(avg_latency, 2),
        "total_time_ms": round(elapsed, 2),
        "peak_memory_kb": round(peak_mem / 1024, 2),
        "throughput_ops_per_sec": round(iterations / (elapsed / 1000.0), 1),
    }


def benchmark_markdown_generator(iterations: int = 100):
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    p = HTMLParser(html, "https://molavi.pro/mwie")
    clean_html, _ = p.get_clean_html_and_text()

    tracemalloc.start()
    start = time.perf_counter()

    for _ in range(iterations):
        gen = MarkdownGenerator(clean_html)
        _ = gen.generate()

    elapsed = (time.perf_counter() - start) * 1000.0
    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    avg_latency = elapsed / iterations
    return {
        "iterations": iterations,
        "avg_latency_ms": round(avg_latency, 2),
        "total_time_ms": round(elapsed, 2),
        "peak_memory_kb": round(peak_mem / 1024, 2),
        "throughput_ops_per_sec": round(iterations / (elapsed / 1000.0), 1),
    }


def main():
    print("=" * 60)
    print("MOLAVI WEB INTELLIGENCE ENGINE — BENCHMARK SUITE")
    print("=" * 60)

    html_res = benchmark_html_parsing()
    print("\n1. HTML Parsing & DOM Clean:")
    print(
        f"   Avg Latency: {html_res['avg_latency_ms']} ms | Throughput: {html_res['throughput_ops_per_sec']} ops/s | Peak RAM: {html_res['peak_memory_kb']} KB"
    )

    md_res = benchmark_markdown_generator()
    print("\n2. Markdown Generator:")
    print(
        f"   Avg Latency: {md_res['avg_latency_ms']} ms | Throughput: {md_res['throughput_ops_per_sec']} ops/s | Peak RAM: {md_res['peak_memory_kb']} KB"
    )

    seo_res = benchmark_seo_analyzer()
    print("\n3. Technical SEO Engine:")
    print(
        f"   Avg Latency: {seo_res['avg_latency_ms']} ms | Throughput: {seo_res['throughput_ops_per_sec']} ops/s | Peak RAM: {seo_res['peak_memory_kb']} KB"
    )

    geo_res = benchmark_geo_analyzer()
    print("\n4. GEO & Entity Graph Engine:")
    print(
        f"   Avg Latency: {geo_res['avg_latency_ms']} ms | Throughput: {geo_res['throughput_ops_per_sec']} ops/s | Peak RAM: {geo_res['peak_memory_kb']} KB"
    )

    print("\n" + "=" * 60)
    print("Benchmark complete.")


if __name__ == "__main__":
    main()
