"""
Sitemap.xml Parser and URL Discovery for MWIE.
Supports standard XML sitemaps, sitemap indexes, and discovery.
"""

import xml.etree.ElementTree as ET
from typing import Any

import httpx


class SitemapParser:
    def __init__(self, sitemap_url: str):
        self.sitemap_url = sitemap_url

    async def fetch_urls(self, max_urls: int = 500) -> list[dict[str, Any]]:
        """Parses sitemap and returns list of discovered URLs and their metadata."""
        urls: list[dict[str, Any]] = []

        try:
            async with httpx.AsyncClient(
                timeout=20.0, follow_redirects=True, verify=False
            ) as client:
                resp = await client.get(self.sitemap_url)
                if resp.status_code != 200:
                    return urls

                root = ET.fromstring(resp.content)
                # Strip XML namespaces for uniform querying
                for elem in root.iter():
                    if "}" in elem.tag:
                        elem.tag = elem.tag.split("}", 1)[1]

                # Check if this is a sitemap index (<sitemapindex>)
                if root.tag == "sitemapindex":
                    for sm in root.findall("sitemap"):
                        loc = sm.find("loc")
                        if loc is not None and loc.text:
                            sub_parser = SitemapParser(loc.text.strip())
                            sub_urls = await sub_parser.fetch_urls(max_urls=max_urls - len(urls))
                            urls.extend(sub_urls)
                            if len(urls) >= max_urls:
                                break
                    return urls[:max_urls]

                # Standard urlset
                for u in root.findall("url"):
                    loc = u.find("loc")
                    if loc is not None and loc.text:
                        lastmod = u.find("lastmod")
                        changefreq = u.find("changefreq")
                        priority = u.find("priority")

                        urls.append(
                            {
                                "url": loc.text.strip(),
                                "lastmod": lastmod.text.strip()
                                if lastmod is not None and lastmod.text
                                else None,
                                "changefreq": changefreq.text.strip()
                                if changefreq is not None and changefreq.text
                                else None,
                                "priority": float(priority.text.strip())
                                if priority is not None and priority.text
                                else None,
                            }
                        )

                        if len(urls) >= max_urls:
                            break

        except Exception:
            pass

        return urls[:max_urls]
