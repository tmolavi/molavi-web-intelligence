"""
Robots.txt Parser and Policy Enforcer for MWIE.
"""

from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx

from mwie.core.config import settings


class RobotsManager:
    def __init__(self):
        self._cache: dict[str, RobotFileParser] = {}

    async def get_parser(self, url: str) -> RobotFileParser | None:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base in self._cache:
            return self._cache[base]

        robots_url = urljoin(base, "/robots.txt")
        rfp = RobotFileParser()
        rfp.set_url(robots_url)

        try:
            async with httpx.AsyncClient(
                timeout=10.0, follow_redirects=True, verify=False
            ) as client:
                resp = await client.get(robots_url)
                if resp.status_code == 200:
                    rfp.parse(resp.text.splitlines())
                else:
                    # Allow all if robots.txt is 404 or missing
                    rfp.allow_all = True
        except Exception:
            rfp.allow_all = True

        self._cache[base] = rfp
        return rfp

    async def can_fetch(self, url: str, user_agent: str | None = None) -> bool:
        if not settings.respect_robots_txt:
            return True
        ua = user_agent or settings.default_user_agent
        parser = await self.get_parser(url)
        if not parser or getattr(parser, "allow_all", False):
            return True
        return parser.can_fetch(ua, url)


robots_manager = RobotsManager()
