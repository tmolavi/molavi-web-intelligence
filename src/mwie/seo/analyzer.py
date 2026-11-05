"""
Technical SEO Analyzer for Molavi Web Intelligence Engine (MWIE).
Evaluates indexability, metadata, structured data, link graph, heading hierarchy, and performance signals.
"""

import json
from typing import Any

from mwie.core.models import TechnicalSEOReport
from mwie.parsing.html_parser import HTMLParser


class SEOAnalyzer:
    def __init__(
        self,
        raw_html: str,
        url: str,
        status_code: int = 200,
        response_headers: dict[str, str] | None = None,
    ):
        self.raw_html = raw_html or ""
        self.url = url
        self.status_code = status_code
        self.headers = response_headers or {}
        self.parser = HTMLParser(self.raw_html, self.url)
        self.soup = self.parser.soup

    def extract_json_ld(self) -> list[dict[str, Any]]:
        schemas = []
        for script in self.soup.find_all("script", type="application/ld+json"):
            try:
                content = script.string
                if content:
                    data = json.loads(content.strip())
                    if isinstance(data, list):
                        schemas.extend(data)
                    elif isinstance(data, dict):
                        # Handle @graph schemas
                        if "@graph" in data and isinstance(data["@graph"], list):
                            schemas.extend(data["@graph"])
                        else:
                            schemas.append(data)
            except Exception:
                continue
        return schemas

    def analyze(self) -> TechnicalSEOReport:
        meta_title = self.parser.get_meta_title()
        meta_desc = self.parser.get_meta_description()
        canonical = self.parser.get_canonical_url()
        meta_robots = self.parser.get_meta_robots()
        headings = self.parser.get_headings()
        images = self.parser.get_images()
        internal_links, external_links = self.parser.get_links()
        og = self.parser.get_open_graph()
        twitter = self.parser.get_twitter_card()
        hreflangs = self.parser.get_hreflangs()
        json_lds = self.extract_json_ld()

        _, clean_text = self.parser.get_clean_html_and_text()
        content_ratio = self.parser.calculate_content_to_html_ratio(clean_text)

        # Indexability
        x_robots = self.headers.get("x-robots-tag", "").lower()
        is_indexable = True
        if meta_robots and ("noindex" in meta_robots):
            is_indexable = False
        if "noindex" in x_robots:
            is_indexable = False
        if self.status_code >= 400:
            is_indexable = False

        # Headings count
        h1_count = sum(1 for h in headings if h.level == 1)

        # Images missing alt
        images_missing_alt = sum(1 for img in images if not img.has_alt)

        # Structured data types
        schema_types = []
        for s in json_lds:
            if isinstance(s, dict) and "@type" in s:
                stype = s["@type"]
                if isinstance(stype, list):
                    schema_types.extend(stype)
                else:
                    schema_types.append(str(stype))
        schema_types = sorted(list(set(schema_types)))

        # Canonical match
        canonical_match = True
        if canonical:
            clean_curr = self.url.rstrip("/")
            clean_canon = canonical.rstrip("/")
            canonical_match = clean_curr == clean_canon

        # Calculate Score and Recommendations
        score = 100
        recommendations = []

        if not is_indexable:
            score -= 30
            recommendations.append("Page is marked as noindex or returned HTTP error status.")

        if not meta_title:
            score -= 15
            recommendations.append(
                "Missing <title> tag. Add a descriptive title between 30 and 60 characters."
            )
        elif len(meta_title) < 30 or len(meta_title) > 65:
            score -= 5
            recommendations.append(
                f"Title length ({len(meta_title)} chars) outside optimal range (30-65 chars)."
            )

        if not meta_desc:
            score -= 10
            recommendations.append(
                "Missing meta description. Add a meta description between 120 and 160 characters."
            )
        elif len(meta_desc) < 70 or len(meta_desc) > 165:
            score -= 4
            recommendations.append(
                f"Meta description length ({len(meta_desc)} chars) outside optimal range (120-160 chars)."
            )

        if h1_count == 0:
            score -= 15
            recommendations.append(
                "Page has no <h1> heading. Ensure each page has exactly one primary <h1>."
            )
        elif h1_count > 1:
            score -= 5
            recommendations.append(
                f"Multiple <h1> headings found ({h1_count}). Best practice recommends a single primary <h1>."
            )

        if images and images_missing_alt > 0:
            pct_missing = (images_missing_alt / len(images)) * 100
            deduction = min(15, int(pct_missing * 0.15))
            score -= deduction
            recommendations.append(
                f"{images_missing_alt} of {len(images)} images are missing alt attributes."
            )

        if not canonical:
            score -= 5
            recommendations.append("Missing rel='canonical' link tag.")
        elif not canonical_match:
            score -= 3
            recommendations.append(f"Canonical URL points to a different target: {canonical}")

        if not json_lds:
            score -= 10
            recommendations.append(
                "No JSON-LD structured data detected. Implement Schema.org entities."
            )

        if not og:
            score -= 5
            recommendations.append("Missing Open Graph (og:title, og:image) social tags.")

        if content_ratio < 10.0:
            score -= 5
            recommendations.append(
                f"Low content-to-HTML ratio ({content_ratio}%). Boilerplate dominates main body."
            )

        score = max(0, min(100, score))

        return TechnicalSEOReport(
            url=self.url,
            status_code=self.status_code,
            canonical_url=canonical,
            canonical_match=canonical_match,
            meta_title=meta_title,
            meta_title_length=len(meta_title) if meta_title else 0,
            meta_description=meta_desc,
            meta_description_length=len(meta_desc) if meta_desc else 0,
            meta_robots=meta_robots,
            is_indexable=is_indexable,
            h1_count=h1_count,
            headings=headings,
            images_total=len(images),
            images_missing_alt=images_missing_alt,
            internal_links_count=len(internal_links),
            external_links_count=len(external_links),
            structured_data_types=schema_types,
            has_json_ld=bool(json_lds),
            json_ld_schemas=json_lds,
            open_graph=og,
            twitter_card=twitter,
            hreflangs=hreflangs,
            content_to_html_ratio=content_ratio,
            seo_score=score,
            recommendations=recommendations,
        )
