"""
Unified Crawling and Extraction Engine for MWIE.
Orchestrates request queues, extraction routing, SEO/GEO analysis, and result caching.
"""

import time
from urllib.parse import urlparse

from mwie.core.cache import cache
from mwie.core.models import (
    CrawlRequest,
    CrawlResult,
    ExtractionMetadata,
    ExtractionOptions,
    ExtractionResult,
)
from mwie.core.router import router
from mwie.crawler.queue import RequestQueue
from mwie.crawler.robots import robots_manager
from mwie.geo.analyzer import GEOAnalyzer
from mwie.parsing.html_parser import HTMLParser
from mwie.parsing.markdown_generator import MarkdownGenerator
from mwie.seo.analyzer import SEOAnalyzer


class CrawlEngine:
    def __init__(self, extraction_router=None):
        self.router = extraction_router or router

    async def extract_single(
        self, url: str, options: ExtractionOptions | None = None
    ) -> ExtractionResult:
        """Extract content and run SEO/GEO analysis on a single target URL."""
        options = options or ExtractionOptions()

        # Check Cache
        cached_data = cache.get(url, str(options.model_dump()))
        if cached_data:
            return cached_data

        # 1. Fetch via Router with Fallbacks
        raw = await self.router.execute_with_fallback(url, options)

        # 2. Parsing & Content Cleaning
        parser = HTMLParser(raw.html, raw.final_url)
        clean_html, clean_text = parser.get_clean_html_and_text()

        # 3. Markdown Generation
        markdown = ""
        if options.generate_markdown:
            md_gen = MarkdownGenerator(clean_html)
            markdown = md_gen.generate()

        # 4. Technical SEO Analysis
        seo_report = None
        if options.extract_seo:
            analyzer = SEOAnalyzer(
                raw_html=raw.html,
                url=raw.final_url,
                status_code=raw.status_code,
                response_headers=raw.headers,
            )
            seo_report = analyzer.analyze()

        # 5. Generative Engine Optimization (GEO) Analysis
        geo_report = None
        if options.extract_geo:
            json_lds = seo_report.json_ld_schemas if seo_report else []
            geo_analyzer = GEOAnalyzer(
                raw_html=raw.html,
                clean_text=clean_text,
                url=raw.final_url,
                json_ld_schemas=json_lds,
            )
            geo_report = geo_analyzer.analyze()

        metadata = ExtractionMetadata(
            adapter_used=raw.adapter_name,
            execution_time_ms=raw.execution_time_ms,
            rendered_js=raw.rendered_js,
            status_code=raw.status_code,
            content_length=len(raw.html),
            cached=False,
        )

        result = ExtractionResult(
            url=url,
            final_url=raw.final_url,
            status_code=raw.status_code,
            html=raw.html if not options.clean_html else None,
            clean_html=clean_html,
            clean_text=clean_text,
            markdown=markdown,
            seo=seo_report,
            geo=geo_report,
            metadata=metadata,
        )

        # Store in Cache
        cache.set(url, result, str(options.model_dump()))
        return result

    async def crawl_site(self, request: CrawlRequest) -> CrawlResult:
        """Crawl a website starting at request.url up to max_pages and max_depth."""
        start_time = time.perf_counter()
        queue = RequestQueue(max_pages=request.max_pages, max_depth=request.max_depth)
        queue.push(request.url, depth=0)

        results: list[ExtractionResult] = []
        errors: list[dict[str, str]] = []

        base_domain = urlparse(request.url).netloc.lower()

        while not queue.is_empty():
            item = queue.pop()
            if not item:
                break

            target_url = item.url
            curr_depth = item.depth

            # Check robots.txt
            if request.respect_robots:
                allowed = await robots_manager.can_fetch(target_url)
                if not allowed:
                    errors.append({"url": target_url, "error": "Disallowed by robots.txt"})
                    continue

            try:
                page_result = await self.extract_single(target_url, request.options)
                results.append(page_result)

                # Discover next links if within depth limit
                if curr_depth < request.max_depth:
                    p = HTMLParser(page_result.clean_html or "", page_result.final_url)
                    internal_links, _ = p.get_links()

                    for link in internal_links:
                        link_domain = urlparse(link.url).netloc.lower()
                        # Domain restriction
                        if link_domain == base_domain:
                            queue.push(link.url, depth=curr_depth + 1)

            except Exception as e:
                errors.append({"url": target_url, "error": str(e)})

        duration = round(time.perf_counter() - start_time, 2)

        return CrawlResult(
            root_url=request.url,
            pages_crawled=len(results),
            duration_seconds=duration,
            results=results,
            errors=errors,
        )


crawl_engine = CrawlEngine()
