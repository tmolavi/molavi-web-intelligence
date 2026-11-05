"""
Data models and schemas for Molavi Web Intelligence Engine (MWIE).
Pure typed Pydantic models.
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class ExtractionOptions(BaseModel):
    render_js: bool = Field(
        default=False, description="Whether to render JavaScript using Playwright"
    )
    wait_for_selector: str | None = Field(default=None, description="CSS selector to wait for")
    timeout_sec: float = Field(default=20.0, description="Extraction timeout in seconds")
    clean_html: bool = Field(default=True, description="Whether to clean unwanted HTML elements")
    generate_markdown: bool = Field(default=True, description="Generate clean markdown content")
    extract_seo: bool = Field(default=True, description="Run technical SEO analysis")
    extract_geo: bool = Field(
        default=True, description="Run Generative Engine Optimization analysis"
    )
    preferred_adapter: str | None = Field(
        default=None, description="Specific adapter name or auto-route"
    )


class CrawlRequest(BaseModel):
    url: str = Field(..., description="Target root URL to crawl or extract")
    max_depth: int = Field(default=1, ge=0, le=5, description="Maximum crawl recursion depth")
    max_pages: int = Field(default=10, ge=1, le=500, description="Maximum pages to crawl")
    render_js: bool = Field(default=False, description="Enable browser JS rendering")
    respect_robots: bool = Field(default=True, description="Respect robots.txt rules")
    allowed_domains: list[str] | None = Field(default=None, description="Domain allowlist")
    options: ExtractionOptions = Field(default_factory=ExtractionOptions)


class HeadingItem(BaseModel):
    level: int = Field(..., ge=1, le=6)
    text: str


class ImageItem(BaseModel):
    src: str
    alt: str | None = None
    has_alt: bool = False


class LinkItem(BaseModel):
    url: str
    text: str
    is_internal: bool = True
    rel: str | None = None


class TechnicalSEOReport(BaseModel):
    url: str
    status_code: int
    canonical_url: str | None = None
    canonical_match: bool = True
    meta_title: str | None = None
    meta_title_length: int = 0
    meta_description: str | None = None
    meta_description_length: int = 0
    meta_robots: str | None = None
    is_indexable: bool = True
    h1_count: int = 0
    headings: list[HeadingItem] = Field(default_factory=list)
    images_total: int = 0
    images_missing_alt: int = 0
    internal_links_count: int = 0
    external_links_count: int = 0
    structured_data_types: list[str] = Field(default_factory=list)
    has_json_ld: bool = False
    json_ld_schemas: list[dict[str, Any]] = Field(default_factory=list)
    open_graph: dict[str, str] = Field(default_factory=dict)
    twitter_card: dict[str, str] = Field(default_factory=dict)
    hreflangs: dict[str, str] = Field(default_factory=dict)
    content_to_html_ratio: float = 0.0
    seo_score: int = Field(default=100, ge=0, le=100)
    recommendations: list[str] = Field(default_factory=list)


SEOReport = TechnicalSEOReport


class EntityItem(BaseModel):
    name: str
    entity_type: str = Field(description="Brand, Organization, Person, Product, Concept")
    frequency: int = 1
    context: str | None = None
    confidence: float = 1.0


class CitationItem(BaseModel):
    source_url: str | None = None
    citation_text: str
    anchor_text: str | None = None
    context_sentence: str | None = None
    author: str | None = None
    date: str | None = None


class ContentChunk(BaseModel):
    index: int
    heading: str | None = None
    text: str
    char_count: int
    token_estimate: int


class QAItem(BaseModel):
    question: str
    answer: str


class GEOReport(BaseModel):
    url: str
    primary_brand: str | None = None
    entities: list[EntityItem] = Field(default_factory=list)
    entity_types_count: dict[str, int] = Field(default_factory=dict)
    citations: list[CitationItem] = Field(default_factory=list)
    qa_knowledge_blocks: list[QAItem] = Field(default_factory=list)
    semantic_chunks: list[ContentChunk] = Field(default_factory=list)
    ai_readiness_score: int = Field(default=100, ge=0, le=100)
    ai_readiness_breakdown: dict[str, Any] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)


class ExtractionMetadata(BaseModel):
    adapter_used: str
    execution_time_ms: float
    rendered_js: bool
    status_code: int
    content_length: int
    cached: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ExtractionResult(BaseModel):
    url: str
    final_url: str
    status_code: int
    html: str | None = None
    clean_html: str | None = None
    clean_text: str = ""
    markdown: str = ""
    seo: TechnicalSEOReport | None = None
    geo: GEOReport | None = None
    metadata: ExtractionMetadata


class CrawlResult(BaseModel):
    root_url: str
    pages_crawled: int
    duration_seconds: float
    results: list[ExtractionResult]
    errors: list[dict[str, str]] = Field(default_factory=list)


class AdapterStats(BaseModel):
    name: str
    success_count: int = 0
    failure_count: int = 0
    total_calls: int = 0
    avg_latency_ms: float = 0.0
    success_rate: float = 0.0
    cost_weight: float = 1.0


class PageComparisonItem(BaseModel):
    url: str
    seo_score: int
    ai_readiness_score: int
    content_words: int
    h1: str | None
    has_schema: bool
    meta_title: str | None


class PageComparisonResult(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    pages: list[PageComparisonItem]
    insights: list[str]
