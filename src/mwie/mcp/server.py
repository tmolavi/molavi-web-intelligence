"""
Model Context Protocol (MCP) Server for Molavi Web Intelligence Engine (MWIE).
Provides 12 native tools for autonomous AI agents (Hermes, Hamzad, Claude, Cursor).
"""

import asyncio
import json

from mcp.server.mcpserver import MCPServer

from mwie import __version__
from mwie.core.cache import cache
from mwie.core.models import CrawlRequest, ExtractionOptions
from mwie.crawler.engine import crawl_engine
from mwie.crawler.sitemap import SitemapParser
from mwie.extraction.registry import registry
from mwie.seo.comparator import PageComparator

mcp = MCPServer("molavi-web-intelligence")


@mcp.tool()
async def crawl_url(url: str, render_js: bool = False) -> str:
    """Extract content, technical SEO, and GEO intelligence from a single URL."""
    options = ExtractionOptions(render_js=render_js, extract_seo=True, extract_geo=True)
    res = await crawl_engine.extract_single(url, options)
    return res.model_dump_json(indent=2)


@mcp.tool()
async def crawl_domain(
    url: str, max_pages: int = 10, max_depth: int = 2, render_js: bool = False
) -> str:
    """Perform a recursive crawl of a domain up to max_pages and max_depth."""
    req = CrawlRequest(
        url=url,
        max_pages=max_pages,
        max_depth=max_depth,
        render_js=render_js,
    )
    res = await crawl_engine.crawl_site(req)
    return res.model_dump_json(indent=2)


@mcp.tool()
async def extract_page_content(
    url: str, render_js: bool = False, generate_markdown: bool = True
) -> str:
    """Extract clean text and structured Markdown from a webpage, discarding web noise."""
    options = ExtractionOptions(
        render_js=render_js,
        generate_markdown=generate_markdown,
        extract_seo=False,
        extract_geo=False,
    )
    res = await crawl_engine.extract_single(url, options)
    return json.dumps(
        {
            "url": res.url,
            "final_url": res.final_url,
            "clean_text": res.clean_text,
            "markdown": res.markdown,
            "adapter_used": res.metadata.adapter_used,
            "execution_time_ms": res.metadata.execution_time_ms,
        },
        indent=2,
    )


@mcp.tool()
async def analyze_seo(url: str, render_js: bool = False) -> str:
    """Run a technical SEO audit: title, description, headings, images, canonical, schemas, and score."""
    options = ExtractionOptions(render_js=render_js, extract_seo=True, extract_geo=False)
    res = await crawl_engine.extract_single(url, options)
    if not res.seo:
        return json.dumps({"error": "Failed to generate SEO report."})
    return res.seo.model_dump_json(indent=2)


@mcp.tool()
async def analyze_geo(url: str, render_js: bool = False) -> str:
    """Run Generative Engine Optimization (GEO) audit: brand entities, citations, Q&A blocks, AI-readiness."""
    options = ExtractionOptions(render_js=render_js, extract_seo=True, extract_geo=True)
    res = await crawl_engine.extract_single(url, options)
    if not res.geo:
        return json.dumps({"error": "Failed to generate GEO report."})
    return res.geo.model_dump_json(indent=2)


@mcp.tool()
async def extract_entities(url: str) -> str:
    """Extract brand, organization, person, and product entities from a webpage."""
    options = ExtractionOptions(extract_seo=True, extract_geo=True)
    res = await crawl_engine.extract_single(url, options)
    if not res.geo:
        return json.dumps([])
    return json.dumps([e.model_dump() for e in res.geo.entities], indent=2)


@mcp.tool()
async def extract_structured_data(url: str) -> str:
    """Extract all Schema.org JSON-LD structured data and detected schemas from a webpage."""
    options = ExtractionOptions(extract_seo=True, extract_geo=False)
    res = await crawl_engine.extract_single(url, options)
    if not res.seo:
        return json.dumps([])
    return json.dumps(
        {
            "url": url,
            "has_json_ld": res.seo.has_json_ld,
            "structured_data_types": res.seo.structured_data_types,
            "schemas": res.seo.json_ld_schemas,
        },
        indent=2,
    )


@mcp.tool()
async def analyze_sitemap(sitemap_url: str, max_urls: int = 100) -> str:
    """Discover and parse URLs from an XML sitemap or sitemap index."""
    parser = SitemapParser(sitemap_url)
    urls = await parser.fetch_urls(max_urls=max_urls)
    return json.dumps(
        {
            "sitemap_url": sitemap_url,
            "discovered_urls_count": len(urls),
            "urls": urls,
        },
        indent=2,
    )


@mcp.tool()
async def compare_pages(urls: list[str]) -> str:
    """Compare multiple competitor pages side-by-side on SEO and GEO readiness."""
    if len(urls) < 2:
        return json.dumps({"error": "At least 2 URLs are required for comparison."})
    results = []
    options = ExtractionOptions(extract_seo=True, extract_geo=True)
    for u in urls:
        r = await crawl_engine.extract_single(u, options)
        results.append(r)
    comp = PageComparator.compare(results)
    return comp.model_dump_json(indent=2)


@mcp.tool()
async def batch_process_urls(urls: list[str], render_js: bool = False) -> str:
    """Process a batch of URLs concurrently and return summarized SEO/GEO metrics."""
    options = ExtractionOptions(render_js=render_js, extract_seo=True, extract_geo=True)
    tasks = [crawl_engine.extract_single(u, options) for u in urls[:25]]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    summary = []
    for u, res in zip(urls, results):
        if isinstance(res, Exception):
            summary.append({"url": u, "status": "error", "message": str(res)})
        else:
            summary.append(
                {
                    "url": u,
                    "status": "success",
                    "seo_score": res.seo.seo_score if res.seo else None,
                    "ai_readiness_score": res.geo.ai_readiness_score if res.geo else None,
                    "word_count": len(res.clean_text.split()),
                    "adapter": res.metadata.adapter_used,
                }
            )
    return json.dumps(summary, indent=2)


@mcp.tool()
async def get_job_status() -> str:
    """Report engine status, version, memory cache entries, and health."""
    return json.dumps(
        {
            "engine": "Molavi Web Intelligence Engine",
            "version": __version__,
            "author": "Taqi Molavi",
            "cache_entries": cache.size(),
            "registered_adapters": registry.list_adapters(),
        },
        indent=2,
    )


@mcp.tool()
async def get_extraction_metadata() -> str:
    """Retrieve runtime performance telemetry and success metrics for all extraction adapters."""
    stats = registry.get_stats()
    return json.dumps([s.model_dump() for s in stats], indent=2)


def main():
    """Runs the MCP server over standard stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
