"""
High-speed resilient HTML parser for MWIE.
Extracts clean text, structured elements, headings, links, images, and content-to-HTML ratios.
"""

from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Comment

from mwie.core.models import HeadingItem, ImageItem, LinkItem


class HTMLParser:
    UNWANTED_TAGS = [
        "script",
        "style",
        "noscript",
        "svg",
        "canvas",
        "iframe",
        "header",
        "footer",
        "nav",
        "aside",
        "form",
    ]

    def __init__(self, raw_html: str, base_url: str):
        self.raw_html = raw_html or ""
        self.base_url = base_url
        self.soup = BeautifulSoup(self.raw_html, "html.parser")

    def get_meta_title(self) -> str | None:
        title_tag = self.soup.find("title")
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        og_title = self.soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()
        return None

    def get_meta_description(self) -> str | None:
        desc_tag = self.soup.find("meta", attrs={"name": "description"})
        if desc_tag and desc_tag.get("content"):
            return desc_tag["content"].strip()
        og_desc = self.soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"].strip()
        return None

    def get_canonical_url(self) -> str | None:
        canonical = self.soup.find("link", rel=lambda r: r and "canonical" in r.lower())
        if canonical and canonical.get("href"):
            return urljoin(self.base_url, canonical["href"].strip())
        return None

    def get_meta_robots(self) -> str | None:
        meta_robots = self.soup.find("meta", attrs={"name": "robots"})
        if meta_robots and meta_robots.get("content"):
            return meta_robots["content"].strip().lower()
        return None

    def get_headings(self) -> list[HeadingItem]:
        headings: list[HeadingItem] = []
        for tag in self.soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            text = tag.get_text(separator=" ", strip=True)
            if text:
                level = int(tag.name[1])
                headings.append(HeadingItem(level=level, text=text))
        return headings

    def get_images(self) -> list[ImageItem]:
        images: list[ImageItem] = []
        for img in self.soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if not src:
                continue
            full_src = urljoin(self.base_url, src.strip())
            alt = img.get("alt")
            alt_clean = alt.strip() if alt else None
            images.append(ImageItem(src=full_src, alt=alt_clean, has_alt=bool(alt_clean)))
        return images

    def get_links(self) -> tuple[list[LinkItem], list[LinkItem]]:
        """Returns (internal_links, external_links)."""
        internal: list[LinkItem] = []
        external: list[LinkItem] = []
        base_domain = urlparse(self.base_url).netloc.lower()

        seen_urls = set()
        for a in self.soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            full_url = urljoin(self.base_url, href)
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            text = a.get_text(separator=" ", strip=True) or full_url
            rel = " ".join(a.get("rel", [])) if isinstance(a.get("rel"), list) else a.get("rel")
            target_domain = urlparse(full_url).netloc.lower()

            is_internal = (target_domain == base_domain) or (not target_domain)
            item = LinkItem(url=full_url, text=text, is_internal=is_internal, rel=rel)

            if is_internal:
                internal.append(item)
            else:
                external.append(item)

        return internal, external

    def get_open_graph(self) -> dict[str, str]:
        og: dict[str, str] = {}
        for tag in self.soup.find_all("meta", property=lambda p: p and p.startswith("og:")):
            prop = tag.get("property")
            content = tag.get("content")
            if prop and content:
                og[prop] = content.strip()
        return og

    def get_twitter_card(self) -> dict[str, str]:
        tc: dict[str, str] = {}
        for tag in self.soup.find_all(
            "meta", attrs={"name": lambda n: n and n.startswith("twitter:")}
        ):
            name = tag.get("name")
            content = tag.get("content")
            if name and content:
                tc[name] = content.strip()
        return tc

    def get_hreflangs(self) -> dict[str, str]:
        hreflangs: dict[str, str] = {}
        for tag in self.soup.find_all("link", rel=lambda r: r and "alternate" in r.lower()):
            lang = tag.get("hreflang")
            href = tag.get("href")
            if lang and href:
                hreflangs[lang.lower().strip()] = urljoin(self.base_url, href.strip())
        return hreflangs

    def get_clean_html_and_text(self) -> tuple[str, str]:
        """
        Creates clean HTML with noise removed, and returns (clean_html, clean_text).
        """
        clean_soup = BeautifulSoup(self.raw_html, "html.parser")

        # Remove comments
        for comment in clean_soup.find_all(string=lambda s: isinstance(s, Comment)):
            comment.extract()

        # Remove noise tags
        for tag_name in self.UNWANTED_TAGS:
            for tag in clean_soup.find_all(tag_name):
                tag.decompose()

        # Focus on main content container if present
        main_content = (
            clean_soup.find("main")
            or clean_soup.find("article")
            or clean_soup.find("div", attrs={"role": "main"})
            or clean_soup.find(
                "div",
                class_=lambda c: c and any(m in c.lower() for m in ["content", "post", "article"]),
            )
            or clean_soup.body
            or clean_soup
        )

        clean_text = main_content.get_text(separator="\n", strip=True)
        return str(main_content), clean_text

    def calculate_content_to_html_ratio(self, clean_text: str) -> float:
        total_len = len(self.raw_html)
        if total_len == 0:
            return 0.0
        text_len = len(clean_text)
        return round((text_len / total_len) * 100, 2)
