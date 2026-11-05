"""
FastAPI REST API Server for Molavi Web Intelligence Engine (MWIE).
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from mwie import __version__
from mwie.core.models import (
    AdapterStats,
    CrawlRequest,
    CrawlResult,
    ExtractionOptions,
    ExtractionResult,
    GEOReport,
    PageComparisonResult,
    TechnicalSEOReport,
)
from mwie.crawler.engine import crawl_engine
from mwie.crawler.sitemap import SitemapParser
from mwie.extraction.registry import registry
from mwie.seo.comparator import PageComparator

app = FastAPI(
    title="Molavi Web Intelligence Engine (MWIE) API",
    description="Open-source, self-hosted web intelligence engine for SEO, GEO, AI Search, and autonomous AI agents.",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExtractRequest(BaseModel):
    url: str
    options: ExtractionOptions = ExtractionOptions()


class SitemapRequest(BaseModel):
    sitemap_url: str
    max_urls: int = 100


class CompareRequest(BaseModel):
    urls: list[str]
    options: ExtractionOptions = ExtractionOptions()


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Molavi Web Intelligence Engine",
        "version": __version__,
        "author": "Taqi Molavi",
        "website": "https://molavi.pro",
    }


@app.post("/api/v1/extract", response_model=ExtractionResult, tags=["Extraction"])
async def extract_url(req: ExtractRequest):
    try:
        return await crawl_engine.extract_single(req.url, req.options)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/crawl", response_model=CrawlResult, tags=["Crawling"])
async def crawl_site(req: CrawlRequest):
    try:
        return await crawl_engine.crawl_site(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/seo", response_model=TechnicalSEOReport, tags=["SEO"])
async def analyze_seo(req: ExtractRequest):
    try:
        req.options.extract_seo = True
        res = await crawl_engine.extract_single(req.url, req.options)
        if not res.seo:
            raise HTTPException(status_code=500, detail="SEO analysis failed to produce report.")
        return res.seo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/geo", response_model=GEOReport, tags=["GEO"])
async def analyze_geo(req: ExtractRequest):
    try:
        req.options.extract_geo = True
        res = await crawl_engine.extract_single(req.url, req.options)
        if not res.geo:
            raise HTTPException(status_code=500, detail="GEO analysis failed to produce report.")
        return res.geo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/sitemap", tags=["Discovery"])
async def parse_sitemap(req: SitemapRequest):
    try:
        parser = SitemapParser(req.sitemap_url)
        urls = await parser.fetch_urls(max_urls=req.max_urls)
        return {
            "sitemap_url": req.sitemap_url,
            "discovered_urls_count": len(urls),
            "urls": urls,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/compare", response_model=PageComparisonResult, tags=["Comparison"])
async def compare_pages(req: CompareRequest):
    if len(req.urls) < 2:
        raise HTTPException(status_code=400, detail="At least 2 URLs are required for comparison.")
    try:
        results = []
        for u in req.urls:
            r = await crawl_engine.extract_single(u, req.options)
            results.append(r)
        return PageComparator.compare(results)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/adapters/stats", response_model=list[AdapterStats], tags=["Adapters"])
async def get_adapter_stats():
    return registry.get_stats()
