#!/usr/bin/env python3
"""
Industry AI Visibility Leaderboard Batch Benchmark Runner.
Part of Molavi Web Intelligence Engine (MWIE) in collaboration with InTen Agency.

Audits a list of competitor URLs in batch, evaluates them across 3 diagnostic pillars:
  - Technical SEO (30%)
  - Answer Engine Optimization / Schema Graph (35%)
  - Generative Engine Optimization / Passage Density (35%)
and synthesizes a ranked Industry AI Visibility Leaderboard (Markdown + JSON).

Attribution:
  - MWIE: https://molavi.pro/tools/web-intelligence
  - InTen Agency: https://inten.asia
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

# Ensure MWIE and SAGE source directories are in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
MWIE_SRC = REPO_ROOT / "src"
if str(MWIE_SRC) not in sys.path:
    sys.path.insert(0, str(MWIE_SRC))

# Search for sibling sage-audit directory if available
POSSIBLE_SAGE_PATHS = [
    REPO_ROOT.parent / "sage-audit" / "src",
    Path("/Users/taghimolavi/Downloads/git/sage-audit/src"),
]
for p in POSSIBLE_SAGE_PATHS:
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("industry_benchmark")

# Try importing SAGE audit
try:
    from sage_audit.core import SageAuditor
    HAS_SAGE = True
except ImportError:
    HAS_SAGE = False
    logger.warning("sage-audit not found in path; falling back to native MWIE analyzers.")

# Import MWIE components
try:
    from mwie.geo.analyzer import GEOAnalyzer
    from mwie.parsing.html_parser import HTMLParser
    from mwie.seo.analyzer import SEOAnalyzer
    from mwie.seo.schema_healer import SchemaHealer
    HAS_MWIE = True
except ImportError as e:
    HAS_MWIE = False
    logger.warning(f"MWIE native analyzers import warning: {e}")


def normalize_url(raw: str) -> str:
    """Ensure URL has a valid scheme and normalized format."""
    clean = raw.strip()
    if not clean:
        return ""
    if not clean.startswith(("http://", "https://")):
        clean = f"https://{clean}"
    return clean


def parse_domains_input(input_arg: str | None, urls_arg: list[str] | None) -> list[str]:
    """Parse domain targets from file or comma-separated string."""
    targets: list[str] = []

    if input_arg:
        p = Path(input_arg)
        if p.is_file():
            logger.info(f"Loading target domains from file: {p}")
            lines = p.read_text(encoding="utf-8").splitlines()
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    targets.append(normalize_url(line))
        else:
            # Treat as comma-separated or whitespace-separated list
            parts = re.split(r"[,\s]+", input_arg)
            for part in parts:
                part = part.strip()
                if part and not part.startswith("#"):
                    targets.append(normalize_url(part))

    if urls_arg:
        for u in urls_arg:
            parts = re.split(r"[,\s]+", u)
            for part in parts:
                part = part.strip()
                if part and not part.startswith("#"):
                    targets.append(normalize_url(part))

    # Deduplicate while preserving order
    seen = set()
    deduped: list[str] = []
    for t in targets:
        if t and t not in seen:
            seen.add(t)
            deduped.append(t)

    return deduped


def extract_domain_name(url: str) -> str:
    """Extract clean domain display name from URL."""
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc or parsed.path
        return netloc.lower().removeprefix("www.")
    except Exception:
        return url


def calculate_grade(score: float) -> str:
    """Map numeric score (0-100) to standard letter grade."""
    if score >= 93.0:
        return "A+"
    if score >= 85.0:
        return "A"
    if score >= 75.0:
        return "B"
    if score >= 65.0:
        return "C"
    if score >= 50.0:
        return "D"
    return "F"


def audit_domain_sync(target_url: str, timeout: float = 20.0) -> dict[str, Any]:
    """
    Execute full 3-pillar audit on a single domain.
    Reuses SAGE Auditor or MWIE native pipeline.
    """
    domain = extract_domain_name(target_url)
    start_time = time.perf_counter()

    if HAS_SAGE:
        try:
            auditor = SageAuditor(timeout=timeout, embedding_backend="hashing")
            report = auditor.audit(target_url)

            # Extract scores (Weights: SEO 30%, AEO 35%, GEO 35%)
            seo_score = round(report.seo.score, 1)
            aeo_score = round(report.aeo.score, 1)
            geo_score = round(report.geo.score, 1)
            mavi_score = round(report.overall_score, 1)
            grade = report.grade or calculate_grade(mavi_score)

            # Schema Graph Analysis
            entity_nodes = report.aeo.metrics.get("entity_nodes", 0)
            entity_types = report.aeo.metrics.get("entity_types", [])
            types_str = ", ".join(entity_types[:3]) + (f" +{len(entity_types)-3}" if len(entity_types) > 3 else "")
            if entity_nodes > 0:
                schema_graph_summary = f"{entity_nodes} nodes ({types_str})"
            else:
                schema_graph_summary = "Deficient (0 nodes)"

            # Passage Density Analysis
            chunk_count = report.geo.metrics.get("chunk_count", 0)
            total_tokens = report.geo.metrics.get("total_tokens", 0)
            word_count = report.page.get("word_count", 0)
            density_str = f"{chunk_count} chunks ({total_tokens} tokens)"

            # Critical Blocker identification: pick highest impact recommendation
            actionable = report.seo.actionable() + report.aeo.actionable() + report.geo.actionable()
            actionable.sort(key=lambda f: f.weight * (1.0 - f.score), reverse=True)
            if actionable:
                critical_blocker = actionable[0].recommendation or actionable[0].details
            else:
                critical_blocker = "None (Healthy baseline)"

            # Enrich with MWIE SchemaHealer if available
            schema_gaps_list = []
            needs_healing = False
            if HAS_MWIE and report.artifacts:
                try:
                    # Look up snapshot or clean text if possible
                    html_source = getattr(report, "html", "")
                    if not html_source and hasattr(report, "page"):
                        pass
                except Exception:
                    pass

            elapsed = round((time.perf_counter() - start_time) * 1000.0, 2)

            return {
                "domain": domain,
                "url": target_url,
                "status": "success",
                "mavi_score": mavi_score,
                "grade": grade,
                "seo_score": seo_score,
                "aeo_score": aeo_score,
                "geo_score": geo_score,
                "schema_graph": schema_graph_summary,
                "entity_nodes_count": entity_nodes,
                "entity_types": entity_types,
                "passage_density": density_str,
                "chunk_count": chunk_count,
                "total_tokens": total_tokens,
                "word_count": word_count,
                "critical_blocker": critical_blocker,
                "duration_ms": elapsed,
            }
        except Exception as err:
            logger.error(f"SAGE audit failed for {target_url}: {err}")

    # Fallback to MWIE Native Pipeline
    if HAS_MWIE:
        try:
            import httpx

            with httpx.Client(timeout=timeout, follow_redirects=True, verify=False) as client:
                resp = client.get(
                    target_url,
                    headers={
                        "User-Agent": "MWIE-Batch-Benchmark/1.0 (+https://molavi.pro/tools/web-intelligence)",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    },
                )
                html = resp.text
                final_url = str(resp.url)
                status_code = resp.status_code

            parser = HTMLParser(html, final_url)
            clean_html, clean_text = parser.get_clean_html_and_text()

            # SEO Analysis (30%)
            seo_analyzer = SEOAnalyzer(
                raw_html=html,
                url=final_url,
                status_code=status_code,
                response_headers=dict(resp.headers),
            )
            seo_rep = seo_analyzer.analyze()

            # GEO Analysis (35%)
            geo_analyzer = GEOAnalyzer(
                raw_html=html,
                clean_text=clean_text,
                url=final_url,
                json_ld_schemas=seo_rep.json_ld_schemas,
            )
            geo_rep = geo_analyzer.analyze()

            # Schema Healer (AEO 35%)
            healer = SchemaHealer(
                raw_html=html,
                url=final_url,
                seo_report=seo_rep,
                geo_report=geo_rep,
            )
            schema_gaps, _ = healer.heal()

            # Calculate Scores
            seo_score = float(seo_rep.seo_score)
            geo_score = float(geo_rep.ai_readiness_score)

            # AEO score derived from schema graph health and entity density
            aeo_base = 100.0
            if schema_gaps.detected_gaps:
                aeo_base -= min(60.0, len(schema_gaps.detected_gaps) * 12.0)
            if not schema_gaps.has_unified_graph:
                aeo_base -= 15.0
            if not schema_gaps.has_authoritative_same_as:
                aeo_base -= 15.0
            aeo_score = max(0.0, min(100.0, aeo_base))

            # Weighted MAVI Score: SEO 30%, AEO 35%, GEO 35%
            mavi_score = round(seo_score * 0.30 + aeo_score * 0.35 + geo_score * 0.35, 1)
            grade = calculate_grade(mavi_score)

            # Schema summary
            node_count = len(healer.nodes) if hasattr(healer, "nodes") else len(seo_rep.json_ld_schemas)
            schema_summary = f"{node_count} nodes" if node_count > 0 else "Deficient (0 nodes)"

            # Passage density
            chunks_cnt = len(geo_rep.semantic_chunks)
            total_toks = sum(c.token_estimate for c in geo_rep.semantic_chunks)
            density_str = f"{chunks_cnt} chunks (~{total_toks} tokens)"

            # Critical blocker
            blocker = "None (Healthy baseline)"
            if schema_gaps.detected_gaps:
                blocker = schema_gaps.detected_gaps[0]
            elif seo_rep.recommendations:
                blocker = seo_rep.recommendations[0]
            elif geo_rep.recommendations:
                blocker = geo_rep.recommendations[0]

            elapsed = round((time.perf_counter() - start_time) * 1000.0, 2)
            return {
                "domain": domain,
                "url": target_url,
                "status": "success",
                "mavi_score": mavi_score,
                "grade": grade,
                "seo_score": seo_score,
                "aeo_score": round(aeo_score, 1),
                "geo_score": geo_score,
                "schema_graph": schema_summary,
                "entity_nodes_count": node_count,
                "entity_types": [s.get("@type", "Entity") for s in seo_rep.json_ld_schemas if isinstance(s, dict)],
                "passage_density": density_str,
                "chunk_count": chunks_cnt,
                "total_tokens": total_toks,
                "word_count": len(clean_text.split()),
                "critical_blocker": blocker,
                "duration_ms": elapsed,
            }
        except Exception as err:
            logger.error(f"MWIE native audit failed for {target_url}: {err}")
            return {
                "domain": domain,
                "url": target_url,
                "status": "error",
                "error_message": str(err),
                "mavi_score": 0.0,
                "grade": "F",
                "seo_score": 0.0,
                "aeo_score": 0.0,
                "geo_score": 0.0,
                "schema_graph": "Error",
                "passage_density": "0 chunks",
                "critical_blocker": f"Audit Error: {err}",
                "duration_ms": round((time.perf_counter() - start_time) * 1000.0, 2),
            }

    # If neither is available
    return {
        "domain": domain,
        "url": target_url,
        "status": "error",
        "error_message": "No audit engine available",
        "mavi_score": 0.0,
        "grade": "F",
        "seo_score": 0.0,
        "aeo_score": 0.0,
        "geo_score": 0.0,
        "schema_graph": "Unavailable",
        "passage_density": "0 chunks",
        "critical_blocker": "Engines unavailable",
        "duration_ms": 0.0,
    }


async def audit_with_semaphore(
    sem: asyncio.Semaphore, target_url: str, timeout: float = 20.0
) -> dict[str, Any]:
    """Audit single domain bounded by semaphore concurrency."""
    async with sem:
        domain = extract_domain_name(target_url)
        logger.info(f"Auditing [{domain}] ({target_url})...")
        try:
            result = await asyncio.to_thread(audit_domain_sync, target_url, timeout)
            logger.info(
                f"✓ [{domain}] MAVI: {result.get('mavi_score', 0)} ({result.get('grade', 'F')}) in {result.get('duration_ms', 0)} ms"
            )
            return result
        except Exception as e:
            logger.error(f"✗ [{domain}] Unexpected audit failure: {e}")
            return {
                "domain": domain,
                "url": target_url,
                "status": "error",
                "error_message": str(e),
                "mavi_score": 0.0,
                "grade": "F",
                "seo_score": 0.0,
                "aeo_score": 0.0,
                "geo_score": 0.0,
                "schema_graph": "Error",
                "passage_density": "0 chunks",
                "critical_blocker": f"Failed: {e}",
                "duration_ms": 0.0,
            }


def generate_leaderboard_markdown(
    industry: str,
    results: list[dict[str, Any]],
) -> str:
    """Render structured GitHub-flavored Markdown leaderboard report."""
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        f"# Industry AI Visibility Leaderboard — {industry}",
        "",
        f"> **Generated:** {now_utc}  ",
        f"> **Vertical / Industry:** {industry}  ",
        "> **Methodology:** Diagnostic composite based on **Technical SEO (30%)**, **Answer Engine Optimization / Schema Graph (35%)**, and **Generative Engine Optimization / Passage Density (35%)**.",
        "",
        "## 🏆 Executive Benchmark Leaderboard",
        "",
        "| Rank | Domain | MAVI Score | Grade | SEO (30%) | AEO (35%) | GEO (35%) | Schema Graph Integrity | Passage Density | Critical Blocker |",
        "| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :--- |",
    ]

    for idx, r in enumerate(results, start=1):
        rank = f"**#{idx}**" if idx <= 3 else f"#{idx}"
        badge = "🥇 " if idx == 1 else "🥈 " if idx == 2 else "🥉 " if idx == 3 else ""
        domain_cell = f"{badge}`{r['domain']}`"
        mavi_cell = f"**{r['mavi_score']:.1f}**"
        grade_cell = f"`{r['grade']}`"
        seo_cell = f"{r['seo_score']:.1f}"
        aeo_cell = f"{r['aeo_score']:.1f}"
        geo_cell = f"{r['geo_score']:.1f}"
        schema_cell = r["schema_graph"]
        density_cell = r["passage_density"]
        blocker_cell = r["critical_blocker"].replace("|", "\\|")

        lines.append(
            f"| {rank} | {domain_cell} | {mavi_cell} | {grade_cell} | {seo_cell} | {aeo_cell} | {geo_cell} | {schema_cell} | {density_cell} | {blocker_cell} |"
        )

    lines.extend([
        "",
        "## 🔍 Strategic Diagnostics & Key Findings",
        "",
    ])

    for idx, r in enumerate(results, start=1):
        lines.append(f"### #{idx}. `{r['domain']}` — MAVI Score: {r['mavi_score']:.1f} ({r['grade']})")
        lines.append(f"- **URL:** [{r['url']}]({r['url']})")
        lines.append(f"- **Pillar Breakdown:** Technical SEO `{r['seo_score']:.1f}/100` | Entity AEO `{r['aeo_score']:.1f}/100` | GEO `{r['geo_score']:.1f}/100`")
        lines.append(f"- **Schema Graph Integrity:** {r['schema_graph']}")
        lines.append(f"- **Passage Density:** {r['passage_density']}")
        lines.append(f"- **Primary Actionable Blocker:** {r['critical_blocker']}")
        lines.append("")

    lines.extend([
        "---",
        "### 💡 Attribution & Verification Protocol",
        "",
        "- **Audit Engine:** Evaluated autonomously with [Molavi Web Intelligence Engine (MWIE)](https://molavi.pro/tools/web-intelligence) and [SAGE Audit Core](https://github.com/tmolavi/sage-audit).",
        "- **Strategic Advisory:** Architecture & Generative Engine Optimization by [InTen Agency](https://inten.asia).",
        "- **Scoring Weights:** Exact parity preserved — `Technical SEO 30%` · `Answer Engine Optimization 35%` · `Generative Engine Optimization 35%`.",
        "- **Zero Paid APIs:** All audits executed locally without external commercial token dependencies.",
        "",
    ])

    return "\n".join(lines)


async def main_async(args: argparse.Namespace) -> int:
    start_total = time.perf_counter()

    # Parse input targets
    targets = parse_domains_input(args.input, args.urls)
    if not targets:
        logger.error("No valid domain URLs provided. Use --input <file_or_urls> or pass URLs directly.")
        return 1

    industry = args.industry.strip() or "General"
    concurrency = max(1, min(10, args.concurrency))

    logger.info("=" * 65)
    logger.info(f"INDUSTRY AI VISIBILITY BENCHMARK — {industry}")
    logger.info(f"Targets ({len(targets)}): {', '.join(targets)}")
    logger.info(f"Concurrency: {concurrency} workers | Timeout: {args.timeout}s")
    logger.info("=" * 65)

    # Bounded concurrent execution
    sem = asyncio.Semaphore(concurrency)
    tasks = [audit_with_semaphore(sem, url, timeout=args.timeout) for url in targets]
    raw_results = await asyncio.gather(*tasks)

    # Sort descending by MAVI score
    results = sorted(raw_results, key=lambda x: x.get("mavi_score", 0.0), reverse=True)

    # Output directory
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize industry filename
    industry_slug = re.sub(r"[\s/\\:]+", "_", industry).strip("_")
    md_filename = f"{industry_slug}_leaderboard.md"
    json_filename = f"{industry_slug}_leaderboard.json"

    md_path = output_dir / md_filename
    json_path = output_dir / json_filename

    # Generate Markdown Leaderboard
    md_content = generate_leaderboard_markdown(industry, results)
    md_path.write_text(md_content, encoding="utf-8")
    logger.info(f"✓ Markdown Leaderboard written to: {md_path}")

    # Generate JSON Export
    json_payload = {
        "industry": industry,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "methodology": {
            "name": "Molavi AI Visibility Index (MAVI)",
            "weights": {"technical_seo": 0.30, "aeo_schema_graph": 0.35, "geo_passage_density": 0.35},
            "attribution": {
                "engine": "https://molavi.pro/tools/web-intelligence",
                "agency": "https://inten.asia",
            },
        },
        "total_domains": len(results),
        "leaderboard": results,
    }
    json_path.write_text(json.dumps(json_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"✓ JSON Export written to: {json_path}")

    total_time = round(time.perf_counter() - start_total, 2)
    logger.info(f"Benchmark completed successfully in {total_time}s.")

    # Print quick console preview
    print("\n" + "=" * 65)
    print(f"🏆 {industry.upper()} AI VISIBILITY LEADERBOARD SUMMARY")
    print("=" * 65)
    for idx, r in enumerate(results, start=1):
        print(
            f"#{idx:<2} | {r['domain']:<22} | MAVI: {r['mavi_score']:>5.1f} ({r['grade']:<2}) | SEO: {r['seo_score']:>5.1f} | AEO: {r['aeo_score']:>5.1f} | GEO: {r['geo_score']:>5.1f}"
        )
    print("=" * 65)
    print(f"Reports saved to:\n  - Markdown: {md_path}\n  - JSON:     {json_path}\n")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Batch-audit competitor URLs and generate an Industry AI Visibility Leaderboard (MWIE + SAGE).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=None,
        help="Path to domains.txt (one per line) or comma-separated list of URLs.",
    )
    parser.add_argument(
        "--industry",
        "-n",
        type=str,
        default="Digital Marketing & AI Tech",
        help="Name of the industry / business vertical.",
    )
    parser.add_argument(
        "--urls",
        "-u",
        nargs="*",
        default=[],
        help="Additional URLs/domains to audit.",
    )
    parser.add_argument(
        "--concurrency",
        "-c",
        type=int,
        default=3,
        help="Maximum concurrent audit workers (bounded async).",
    )
    parser.add_argument(
        "--timeout",
        "-t",
        type=float,
        default=20.0,
        help="Network timeout in seconds per domain.",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="reports",
        help="Target directory for generated Markdown and JSON reports.",
    )

    args = parser.parse_args()

    # If no input provided via flags, check if positional or fallback
    if not args.input and not args.urls:
        parser.print_help()
        sys.exit(1)

    code = asyncio.run(main_async(args))
    sys.exit(code)


if __name__ == "__main__":
    main()
