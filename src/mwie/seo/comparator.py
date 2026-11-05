"""
Competitor and Multi-Page SEO/GEO Comparison Engine for MWIE.
"""

from mwie.core.models import (
    ExtractionResult,
    PageComparisonItem,
    PageComparisonResult,
)


class PageComparator:
    @staticmethod
    def compare(results: list[ExtractionResult]) -> PageComparisonResult:
        items: list[PageComparisonItem] = []
        insights: list[str] = []

        for res in results:
            seo_score = res.seo.seo_score if res.seo else 0
            geo_score = res.geo.ai_readiness_score if res.geo else 0
            words = len(res.clean_text.split()) if res.clean_text else 0
            h1 = None
            if res.seo and res.seo.headings:
                h1_list = [h.text for h in res.seo.headings if h.level == 1]
                if h1_list:
                    h1 = h1_list[0]
            has_schema = bool(res.seo.has_json_ld) if res.seo else False
            meta_title = res.seo.meta_title if res.seo else None

            items.append(
                PageComparisonItem(
                    url=res.url,
                    seo_score=seo_score,
                    ai_readiness_score=geo_score,
                    content_words=words,
                    h1=h1,
                    has_schema=has_schema,
                    meta_title=meta_title,
                )
            )

        # Generate comparative insights
        if len(items) >= 2:
            sorted_by_seo = sorted(items, key=lambda x: x.seo_score, reverse=True)
            top_seo = sorted_by_seo[0]
            insights.append(f"Highest Technical SEO Score: {top_seo.url} ({top_seo.seo_score}/100)")

            sorted_by_geo = sorted(items, key=lambda x: x.ai_readiness_score, reverse=True)
            top_geo = sorted_by_geo[0]
            insights.append(
                f"Highest AI / GEO Readiness Score: {top_geo.url} ({top_geo.ai_readiness_score}/100)"
            )

            sorted_by_words = sorted(items, key=lambda x: x.content_words, reverse=True)
            top_words = sorted_by_words[0]
            insights.append(
                f"Most comprehensive content depth: {top_words.url} ({top_words.content_words} words)"
            )

            schema_missing = [item.url for item in items if not item.has_schema]
            if schema_missing:
                insights.append(
                    f"{len(schema_missing)} pages are missing JSON-LD schema markup: {', '.join(schema_missing)}"
                )

        return PageComparisonResult(pages=items, insights=insights)
