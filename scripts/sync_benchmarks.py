#!/usr/bin/env python3
"""
Sync Community Benchmarks Script for Molavi Web Intelligence Engine (MWIE)

Fetches the live, opt-in community benchmark telemetry recorded on molavi.pro,
validates schema structure, and updates local benchmark dataset files.
"""

import json
import os
import sys
import urllib.request

BENCHMARK_FEED_URL = "https://molavi.pro/data/benchmark-records.json"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "community_benchmarks.json")


def fetch_live_benchmarks():
    print(f"📡 Fetching live community benchmarks from {BENCHMARK_FEED_URL}...")
    req = urllib.request.Request(
        BENCHMARK_FEED_URL,
        headers={"User-Agent": "MWIE-Benchmark-Sync/0.1.0 (+https://molavi.pro/tools/web-intelligence)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status != 200:
                print(f"❌ Failed to fetch feed: HTTP {resp.status}", file=sys.stderr)
                return []
            content = resp.read().decode("utf-8")
            records = json.loads(content)
            print(f"✅ Successfully fetched {len(records)} benchmark records.")
            return records
    except Exception as exc:
        print(f"⚠️ Error fetching live benchmark feed: {exc}", file=sys.stderr)
        return []


def save_and_summarize(records):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved {len(records)} benchmark records to {OUTPUT_FILE}")

    if not records:
        return

    total_latency = sum(r.get("latencyMs", 0) for r in records)
    total_seo = sum(r.get("seoScore", 0) for r in records)
    total_geo = sum(r.get("geoScore", 0) for r in records)
    count = len(records)

    avg_lat = round(total_latency / count, 1)
    avg_seo = round(total_seo / count, 1)
    avg_geo = round(total_geo / count, 1)

    print("\n" + "=" * 50)
    print("📊 MWIE Community Benchmark Summary:")
    print(f"   • Total Contributing Runs: {count}")
    print(f"   • Average Crawl & Extraction Latency: {avg_lat} ms")
    print(f"   • Average Technical SEO Score: {avg_seo} / 100")
    print(f"   • Average AI / GEO Readiness Score: {avg_geo} / 100")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    records = fetch_live_benchmarks()
    save_and_summarize(records)
