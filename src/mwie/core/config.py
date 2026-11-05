"""
Configuration management for Molavi Web Intelligence Engine.
Supports environment variables with intelligent fallbacks.
"""

import os

from pydantic import BaseModel, Field


class EngineSettings(BaseModel):
    # App Settings
    app_name: str = "Molavi Web Intelligence Engine"
    app_version: str = "0.1.0"
    app_host: str = Field(default="0.0.0.0", description="API server host")
    app_port: int = Field(default=8000, description="API server port")
    debug: bool = False

    # Crawler Settings
    default_user_agent: str = (
        "Mozilla/5.0 (compatible; MolaviWebIntelligence/0.1; +https://molavi.pro/bot)"
    )
    request_timeout: float = 20.0
    max_redirects: int = 5
    max_concurrent_crawls: int = 10
    default_max_depth: int = 2
    default_max_pages: int = 50
    rate_limit_per_domain_sec: float = 0.5
    respect_robots_txt: bool = True

    # Security & SSRF Protection
    allow_private_ips: bool = False
    blocked_domains: list[str] = Field(
        default_factory=lambda: ["localhost", "127.0.0.1", "0.0.0.0"]
    )
    allowed_domains: list[str] | None = None

    # Browser Engine
    headless_browser: bool = True
    browser_timeout_ms: int = 25000
    viewport_width: int = 1280
    viewport_height: int = 800

    # Cache Settings
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    redis_url: str | None = None

    # External Adapter Settings (Optional)
    firecrawl_api_url: str | None = None
    firecrawl_api_key: str | None = None

    @classmethod
    def from_env(cls) -> "EngineSettings":
        return cls(
            app_host=os.getenv("MWIE_HOST", "0.0.0.0"),
            app_port=int(os.getenv("MWIE_PORT", "8000")),
            debug=os.getenv("MWIE_DEBUG", "false").lower() in ("true", "1", "yes"),
            default_user_agent=os.getenv(
                "MWIE_USER_AGENT",
                "Mozilla/5.0 (compatible; MolaviWebIntelligence/0.1; +https://molavi.pro/bot)",
            ),
            request_timeout=float(os.getenv("MWIE_REQUEST_TIMEOUT", "20.0")),
            max_concurrent_crawls=int(os.getenv("MWIE_MAX_CONCURRENT_CRAWLS", "10")),
            respect_robots_txt=os.getenv("MWIE_RESPECT_ROBOTS", "true").lower()
            in ("true", "1", "yes"),
            allow_private_ips=os.getenv("MWIE_ALLOW_PRIVATE_IPS", "false").lower()
            in ("true", "1", "yes"),
            cache_enabled=os.getenv("MWIE_CACHE_ENABLED", "true").lower() in ("true", "1", "yes"),
            cache_ttl_seconds=int(os.getenv("MWIE_CACHE_TTL", "3600")),
            redis_url=os.getenv("MWIE_REDIS_URL"),
            firecrawl_api_url=os.getenv("MWIE_FIRECRAWL_API_URL"),
            firecrawl_api_key=os.getenv("MWIE_FIRECRAWL_API_KEY"),
        )


settings = EngineSettings.from_env()
