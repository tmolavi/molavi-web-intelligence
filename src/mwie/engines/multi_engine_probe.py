"""
Multi-Engine Shortlist & Branded-Query Defense Probe for MWIE.
Evaluates divergent engine readiness across ChatGPT (GPT-5.6), Google AI Mode,
and Perplexity Sonar based on DOM analysis, JSON-LD schemas, and passage architecture.
"""

import json
import re
from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from mwie.core.models import (
    CitationEvidenceReport,
    EngineMatrixReport,
    GEOReport,
    TechnicalSEOReport,
)
from mwie.parsing.html_parser import HTMLParser


class MultiEngineProbe:
    """Evaluates multi-engine shortlist readiness and branded-query defense posture."""

    DISAMBIGUATION_DOMAINS = {
        "wikipedia.org",
        "wikidata.org",
        "linkedin.com",
        "github.com",
        "crunchbase.com",
        "twitter.com",
        "x.com",
        "youtube.com",
        "orcid.org",
    }

    PRIMARY_RESEARCH_DOMAINS = {
        "arxiv.org",
        "doi.org",
        "nih.gov",
        "ncbi.nlm.nih.gov",
        "nature.com",
        "science.org",
        "springer.com",
        "ieee.org",
        "acm.org",
        "w3.org",
        "ietf.org",
        "github.com",
        "wikipedia.org",
        "wikidata.org",
    }

    QUESTION_STEMS = [
        # English
        r"\bwhat\b", r"\bhow\b", r"\bwhy\b", r"\bwho\b", r"\bwhich\b",
        r"\bwhere\b", r"\bwhen\b", r"\bcan\b", r"\bis\b", r"\bare\b",
        r"\bdoes\b", r"\bshould\b",
        # Persian
        r"چگونه", r"چیست", r"کدام", r"آیا", r"چرا", r"چه کسی", r"کجا",
        r"چه زمانی", r"چطور",
        # Arabic
        r"ما هو", r"ما هي", r"كيف", r"لماذا", r"هل", r"أين", r"متى", r"من هو",
        # Turkish
        r"\bnedir\b", r"\bnasıl\b", r"\bnasil\b", r"\bneden\b",
        r"\bkimdir\b", r"\bhangi\b", r"\bnerede\b", r"\bne zaman\b",
        # Azerbaijani
        r"\bnədir\b", r"\bnece\b", r"\bnecə\b", r"\bnədən\b",
        r"\bhansı\b", r"\bhansi\b", r"\bharada\b", r"\bnə vaxt\b",
    ]

    DEFINITION_MARKERS = [
        # English
        r"\bis an?\b", r"\brefers to\b", r"\bprovides\b", r"\boffers\b",
        r"\bdelivers\b", r"\bspecializes in\b", r"\bdesigned to\b",
        # Persian
        r"یک (?:پلتفرم|ابزار|سیستم|سرویس|مجموعه|شرکت|مرجع)",
        r"ارائه (?:دهنده|می‌دهد|میدهد)",
        r"عبارت است از",
        # Arabic
        r"عبارة عن", r"يقدم", r"تعتبر", r"يعد", r"منصة",
        # Turkish / Azerbaijani
        r"bir (?:platformdur|araçtır|hizmettir|şirkettir)",
        r"hizmeti sunar", r"sağlar", r"təqdim edir",
    ]

    def __init__(
        self,
        raw_html: str,
        clean_text: str,
        url: str,
        status_code: int = 200,
        json_ld_schemas: list[dict[str, Any]] | None = None,
        seo_report: TechnicalSEOReport | None = None,
        geo_report: GEOReport | None = None,
        evidence_report: CitationEvidenceReport | None = None,
    ):
        self.raw_html = raw_html or ""
        self.clean_text = clean_text or ""
        self.url = url
        self.status_code = status_code
        self.soup = BeautifulSoup(self.raw_html, "html.parser")
        self.parser = HTMLParser(self.raw_html, self.url)

        # Inferred reports or defaults
        self.seo_report = seo_report
        self.geo_report = geo_report
        self.evidence_report = evidence_report

        # JSON-LD schemas
        self.schemas = json_ld_schemas or self._extract_json_ld()
        self.parsed_url = urlparse(self.url)
        self.domain = self.parsed_url.netloc.lower()
        self.brand_slug = self._extract_brand_slug()

    def _extract_brand_slug(self) -> str:
        parts = self.domain.split(".")
        if len(parts) >= 2:
            return parts[-2] if parts[-2] not in ("com", "org", "net", "co", "ac") else parts[0]
        return self.domain

    def _extract_json_ld(self) -> list[dict[str, Any]]:
        schemas: list[dict[str, Any]] = []
        for script in self.soup.find_all("script", type="application/ld+json"):
            content = script.string
            if not content:
                continue
            try:
                data = json.loads(content.strip())
                if isinstance(data, list):
                    schemas.extend([item for item in data if isinstance(item, dict)])
                elif isinstance(data, dict):
                    if "@graph" in data and isinstance(data["@graph"], list):
                        schemas.extend([item for item in data["@graph"] if isinstance(item, dict)])
                    else:
                        schemas.append(data)
            except Exception:
                continue
        return schemas

    def _flatten_schema_types(self) -> list[str]:
        types: list[str] = []
        for s in self.schemas:
            t = s.get("@type")
            if isinstance(t, str):
                types.append(t)
            elif isinstance(t, list):
                types.extend([str(x) for x in t])
        return types

    def _extract_same_as_links(self) -> list[str]:
        links: set[str] = set()
        # From schemas
        for s in self.schemas:
            same_as = s.get("sameAs")
            if isinstance(same_as, str):
                links.add(same_as)
            elif isinstance(same_as, list):
                for item in same_as:
                    if isinstance(item, str):
                        links.add(item)
        # From DOM profile links
        for a in self.soup.find_all("a", href=True):
            href = a["href"].strip()
            try:
                p = urlparse(href)
                domain = p.netloc.lower()
                if any(base in domain for base in self.DISAMBIGUATION_DOMAINS):
                    links.add(href)
            except Exception:
                continue
        return list(links)

    def _has_structured_facts(self) -> tuple[bool, int]:
        tables = len(self.soup.find_all("table"))
        dls = len(self.soup.find_all("dl"))
        uls_with_colons = 0
        for li in self.soup.find_all("li"):
            text = li.get_text()
            if ":" in text or "：" in text or "—" in text or "-" in text:
                uls_with_colons += 1

        schema_facts = 0
        for s in self.schemas:
            for key in ("offers", "price", "description", "foundingDate", "founder", "author", "knowsAbout"):
                if key in s:
                    schema_facts += 1

        total_facts = tables * 3 + dls * 2 + min(uls_with_colons, 10) + schema_facts * 2
        return (total_facts > 0, total_facts)

    def _evaluate_chatgpt_readiness(self) -> tuple[int, dict[str, Any]]:
        """
        ChatGPT (GPT-5.6) evaluates entity graph stability, sameAs disambiguation,
        and structured brand/product facts.
        """
        types = self._flatten_schema_types()
        brand_schemas = {"Organization", "Corporation", "LocalBusiness", "Person", "Brand", "Product", "Service", "WebSite"}
        has_brand_schema = any(t in brand_schemas for t in types)
        has_graph = any("@id" in s or "@graph" in str(s) for s in self.schemas)

        # 1. Schema & Graph Stability (max 35 pts)
        schema_score = 0
        if has_brand_schema:
            schema_score += 25
        if has_graph:
            schema_score += 10

        # 2. sameAs Disambiguation Profiles (max 25 pts)
        same_as_links = self._extract_same_as_links()
        disambig_count = len(same_as_links)
        if disambig_count >= 3:
            disambig_score = 25
        elif disambig_count >= 1:
            disambig_score = 15
        else:
            disambig_score = 0

        # 3. Structured Brand/Product Facts (max 25 pts)
        has_facts, facts_count = self._has_structured_facts()
        if facts_count >= 6:
            facts_score = 25
        elif facts_count >= 2:
            facts_score = 15
        elif has_facts:
            facts_score = 10
        else:
            facts_score = 0

        # 4. Identity Anchor Consistency (max 15 pts)
        title_text = (self.soup.title.string or "").lower() if self.soup.title else ""
        h1_tags = [h.get_text().strip().lower() for h in self.soup.find_all("h1")]
        brand_in_title = self.brand_slug in title_text
        brand_in_h1 = any(self.brand_slug in h for h in h1_tags)
        identity_score = 0
        if brand_in_title:
            identity_score += 8
        if brand_in_h1:
            identity_score += 7

        total_score = min(100, schema_score + disambig_score + facts_score + identity_score)
        breakdown = {
            "has_brand_schema": has_brand_schema,
            "has_graph_network": has_graph,
            "same_as_count": disambig_count,
            "disambiguation_profiles": same_as_links[:5],
            "structured_facts_detected": facts_count,
            "brand_in_title": brand_in_title,
            "brand_in_h1": brand_in_h1,
        }
        return total_score, breakdown

    def _evaluate_google_ai_mode_readiness(self) -> tuple[int, dict[str, Any]]:
        """
        Google AI Mode evaluates conversational 3x-long query coverage,
        FAQ/H2 question alignment, top-30% answer clarity, and branded entity defense.
        """
        # 1. Conversational Query Headings (max 35 pts)
        headings = [h.get_text().strip() for h in self.soup.find_all(["h2", "h3", "h4"])]
        question_headings: list[str] = []
        for h in headings:
            is_q = False
            if "?" in h or "؟" in h:
                is_q = True
            else:
                for pattern in self.QUESTION_STEMS:
                    if re.search(pattern, h, re.IGNORECASE):
                        is_q = True
                        break
            if is_q:
                question_headings.append(h)

        faq_schemas = any(t in ("FAQPage", "Question", "Answer") for t in self._flatten_schema_types())
        q_count = len(question_headings)
        if faq_schemas:
            q_count += 3

        if q_count >= 3:
            query_coverage_score = 35
        elif q_count >= 1:
            query_coverage_score = 20
        else:
            query_coverage_score = 5

        # 2. Top-30% Answer Clarity (max 35 pts)
        words = self.clean_text.split()
        top_30_len = max(30, int(len(words) * 0.3))
        top_30_text = " ".join(words[:top_30_len])

        has_direct_definition = False
        for marker in self.DEFINITION_MARKERS:
            if re.search(marker, top_30_text, re.IGNORECASE):
                has_direct_definition = True
                break

        # Check concise opening paragraph under main heading
        first_p = self.soup.find("p")
        first_p_words = len(first_p.get_text().split()) if first_p else 0
        has_concise_snippet = 25 <= first_p_words <= 85

        clarity_score = 0
        if has_direct_definition:
            clarity_score += 25
        if has_concise_snippet:
            clarity_score += 10
        elif first_p_words > 0:
            clarity_score += 5

        # 3. Branded Entity Defense (max 30 pts)
        title_text = (self.soup.title.string or "").lower() if self.soup.title else ""
        canonical_link = self.soup.find("link", rel=lambda r: r and "canonical" in r)
        has_canonical = bool(canonical_link and canonical_link.get("href"))
        brand_in_title = self.brand_slug in title_text

        defense_score = 0
        if brand_in_title:
            defense_score += 15
        if has_canonical:
            defense_score += 8
        if any(t in ("Organization", "Person", "Brand") for t in self._flatten_schema_types()):
            defense_score += 7

        total_score = min(100, query_coverage_score + clarity_score + defense_score)
        breakdown = {
            "conversational_questions_count": len(question_headings),
            "sample_question_headings": question_headings[:3],
            "has_faq_schema": faq_schemas,
            "has_direct_definition_top30": has_direct_definition,
            "has_concise_snippet_opening": has_concise_snippet,
            "branded_defense_anchor": brand_in_title and has_canonical,
        }
        return total_score, breakdown

    def _evaluate_perplexity_readiness(self) -> tuple[int, dict[str, Any]]:
        """
        Perplexity evaluates numeric/statistical density, outbound primary citations,
        and extractable quotes/blocks.
        """
        # 1. Statistical & Numeric Density (max 40 pts)
        # Match percentages, years, multipliers, metrics
        stats_matches = re.findall(
            r"(?:\b\d+(?:\.\d+)?%|\b202[0-9]\b|\b\d+(?:\.\d+)?x\b|\$\d+[\d,]*|\b\d+\s*(?:ms|gb|mb|users|clients|projects|kb|tb)\b)",
            self.clean_text,
            re.IGNORECASE,
        )
        stats_count = len(stats_matches)
        if self.evidence_report:
            stats_count = max(stats_count, self.evidence_report.statistical_claims_count)

        if stats_count >= 5:
            stats_score = 40
        elif stats_count >= 3:
            stats_score = 25
        elif stats_count >= 1:
            stats_score = 15
        else:
            stats_score = 0

        # 2. Outbound Primary Citations (max 30 pts)
        primary_links: set[str] = set()
        for a in self.soup.find_all("a", href=True):
            href = a["href"].strip()
            try:
                p = urlparse(href)
                domain = p.netloc.lower()
                if (
                    any(rd in domain for rd in self.PRIMARY_RESEARCH_DOMAINS)
                    or domain.endswith(".edu")
                    or domain.endswith(".gov")
                    or domain.endswith(".org")
                ):
                    if domain != self.domain:
                        primary_links.add(href)
            except Exception:
                continue

        primary_count = len(primary_links)
        if self.evidence_report:
            primary_count = max(primary_count, self.evidence_report.research_links_count)

        if primary_count >= 2:
            citation_score = 30
        elif primary_count >= 1:
            citation_score = 18
        else:
            citation_score = 0

        # 3. Quote Extractability & Semantic Blocks (max 30 pts)
        quotes = self.soup.find_all(["blockquote", "q"])
        quotes_count = len(quotes)
        if self.evidence_report:
            quotes_count = max(quotes_count, self.evidence_report.expert_quotes_count)

        paragraphs = [p.get_text().strip() for p in self.soup.find_all("p")]
        optimal_passages = [p for p in paragraphs if 80 <= len(p.split()) <= 180]

        quote_score = 0
        if quotes_count >= 2:
            quote_score += 20
        elif quotes_count >= 1:
            quote_score += 12

        if len(optimal_passages) >= 2:
            quote_score += 10
        elif len(optimal_passages) >= 1:
            quote_score += 6

        total_score = min(100, stats_score + citation_score + quote_score)
        breakdown = {
            "statistical_claims_count": stats_count,
            "outbound_primary_citations_count": primary_count,
            "sample_primary_citations": list(primary_links)[:3],
            "quote_blocks_count": quotes_count,
            "optimal_length_passages_count": len(optimal_passages),
        }
        return total_score, breakdown

    def _determine_branded_defense(
        self, chatgpt_score: int, google_score: int, chatgpt_bd: dict[str, Any], google_bd: dict[str, Any]
    ) -> str:
        defense_points = 0
        if chatgpt_bd.get("brand_in_title"):
            defense_points += 25
        if chatgpt_bd.get("has_brand_schema"):
            defense_points += 25
        if google_bd.get("has_direct_definition_top30"):
            defense_points += 25
        if chatgpt_bd.get("same_as_count", 0) >= 1:
            defense_points += 25

        if defense_points >= 75 and google_score >= 60:
            return "defended"
        elif defense_points >= 40:
            return "adequate"
        return "vulnerable"

    def _generate_remediation_tips(
        self,
        chatgpt_score: int,
        google_score: int,
        perplexity_score: int,
        branded_defense: str,
        chatgpt_bd: dict[str, Any],
        google_bd: dict[str, Any],
        perplexity_bd: dict[str, Any],
    ) -> list[str]:
        tips: list[str] = []

        if branded_defense == "vulnerable" or not chatgpt_bd.get("has_brand_schema"):
            tips.append(
                "Add Schema.org Organization/Person with sameAs disambiguation links (Wikidata, LinkedIn) to fortify ChatGPT GPT-5.6 knowledge graph."
            )

        if google_score < 70 or google_bd.get("conversational_questions_count", 0) < 2:
            tips.append(
                "Incorporate conversational question-based H2 headings and direct answer definitions in the top 30% of content to capture Google AI Mode queries."
            )

        if perplexity_score < 70 or perplexity_bd.get("statistical_claims_count", 0) < 3:
            tips.append(
                "Increase verifiable numeric/statistical claim density and link to primary research sources (.edu/.org/arxiv) for Perplexity citation extraction."
            )

        return tips[:3]

    def analyze(self) -> EngineMatrixReport:
        chatgpt_score, chatgpt_bd = self._evaluate_chatgpt_readiness()
        google_score, google_bd = self._evaluate_google_ai_mode_readiness()
        perplexity_score, perplexity_bd = self._evaluate_perplexity_readiness()

        branded_defense = self._determine_branded_defense(
            chatgpt_score, google_score, chatgpt_bd, google_bd
        )

        tips = self._generate_remediation_tips(
            chatgpt_score,
            google_score,
            perplexity_score,
            branded_defense,
            chatgpt_bd,
            google_bd,
            perplexity_bd,
        )

        return EngineMatrixReport(
            chatgpt_score=chatgpt_score,
            google_ai_mode_score=google_score,
            perplexity_score=perplexity_score,
            branded_defense_status=branded_defense,
            chatgpt_breakdown=chatgpt_bd,
            google_breakdown=google_bd,
            perplexity_breakdown=perplexity_bd,
            remediation_tips=tips,
        )
