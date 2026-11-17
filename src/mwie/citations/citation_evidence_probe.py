"""
Citation Evidence, Quote Density & Offer Transparency Probe for MWIE.
Detects attributed expert quotations, verifiable statistical claims,
outbound academic/research citations, and commercial offer transparency.
"""

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from mwie.core.models import (
    CitationEvidenceReport,
    ExpertQuoteItem,
    OfferTransparencyReport,
    StatisticalClaimItem,
)
from mwie.parsing.html_parser import HTMLParser


class CitationEvidenceProbe:
    """Probe for evaluating quotation density, verifiable evidence, and offer transparency."""

    RESEARCH_DOMAINS = {
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
        "semanticscholar.org",
        "researchgate.net",
        "github.com",
        "huggingface.co",
        "wikipedia.org",
        "wikidata.org",
        "orcid.org",
    }

    COMMERCIAL_PATH_KEYWORDS = [
        "pricing",
        "service",
        "services",
        "plans",
        "packages",
        "tariffs",
        "fiyat",
        "fiyatlar",
        "ucretler",
        "xidmet",
        "xidmetler",
        "qiymet",
        "qiymetler",
        "products",
        "solutions",
        "consulting",
        "تعرفه",
        "قیمت",
        "خدمات",
        "باقات",
        "أسعار",
        "اسعار",
    ]

    COMMERCIAL_BODY_KEYWORDS = [
        "pricing",
        "subscription",
        "monthly plan",
        "annual plan",
        "our services",
        "package includes",
        "deliverables",
        "fiyat listesi",
        "paket içeriği",
        "xidmət paketi",
        "qiymət cədvəli",
        "تعرفه خدمات",
        "پلن‌های اشتراک",
        "هزینه اجرای",
        "باقات الاشتراك",
        "جدول الأسعار",
    ]

    CURRENCY_SYMBOLS = ["$", "€", "£", "¥", "₺", "تومان", "ریال", "USD", "EUR", "TRY", "IRR", "AZN", "GBP", "AED"]

    def __init__(
        self,
        raw_html: str,
        clean_text: str,
        url: str,
        status_code: int = 200,
    ):
        self.raw_html = raw_html or ""
        self.clean_text = clean_text or ""
        self.url = url or ""
        self.status_code = status_code
        self.soup = BeautifulSoup(self.raw_html, "html.parser")
        self.parser = HTMLParser(self.raw_html, self.url)

    def extract_expert_quotes(self) -> list[ExpertQuoteItem]:
        """Extracts blockquotes, inline quotes, and text patterns with attribution."""
        quotes: list[ExpertQuoteItem] = []
        seen_texts: set[str] = set()

        # 1. <blockquote> elements
        for bq in self.soup.find_all("blockquote"):
            quote_text = bq.get_text(separator=" ", strip=True)
            if not quote_text or len(quote_text) < 15:
                continue

            cleaned_key = re.sub(r"\s+", " ", quote_text).lower()[:100]
            if cleaned_key in seen_texts:
                continue
            seen_texts.add(cleaned_key)

            cite_source = bq.get("cite")
            author = None

            # Look for author in cite tag or footer/figcaption inside blockquote
            cite_tag = bq.find(["cite", "footer", "figcaption", "small"])
            if cite_tag:
                author = cite_tag.get_text(separator=" ", strip=True)
            else:
                # Check for attribution dash pattern: -- Name or — Name
                dash_match = re.search(r"[\u2014\u2013-]{1,2}\s*([A-Z\u0600-\u06FF][^\n,\.]{2,40})", quote_text)
                if dash_match:
                    author = dash_match.group(1).strip()

            quotes.append(
                ExpertQuoteItem(
                    quote=quote_text,
                    author=author,
                    source=cite_source,
                    element_type="blockquote",
                )
            )

        # 2. <q> inline elements
        for q_tag in self.soup.find_all("q"):
            q_text = q_tag.get_text(separator=" ", strip=True)
            if not q_text or len(q_text) < 15:
                continue

            cleaned_key = re.sub(r"\s+", " ", q_text).lower()[:100]
            if cleaned_key in seen_texts:
                continue
            seen_texts.add(cleaned_key)

            quotes.append(
                ExpertQuoteItem(
                    quote=q_text,
                    author=q_tag.get("cite"),
                    source=q_tag.get("cite"),
                    element_type="q",
                )
            )

        # 3. Attribution patterns in clean text (English, Persian, Arabic, Turkish, Azerbaijani)
        # e.g., "quoted sentence" said Author, or «نقل‌قول» به گفته فلانی
        text_quote_patterns = [
            # Persian / Arabic «...» with attribution
            re.compile(r"«([^»]{15,300})»(?:\s*(?:به گفته|به نقل از|اظهار داشت|تصریح کرد|قال|صرح)\s+([^\n\.،]{3,35}))?"),
            # Latin / English / Turkish “...” with attribution
            re.compile(r'["“]([^"”]{15,300})["”]\s*(?:said|stated|noted|explained|according to|reports|dedi|belirtti|görə)\s+([A-ZÇĞİÖŞÜ][A-Za-zÇĞİÖŞÜçğıöşü\s]{2,35})', re.IGNORECASE),
        ]

        for pat in text_quote_patterns:
            for match in pat.finditer(self.clean_text):
                q_body = match.group(1).strip()
                cleaned_key = re.sub(r"\s+", " ", q_body).lower()[:100]
                if cleaned_key in seen_texts:
                    continue
                seen_texts.add(cleaned_key)

                author = match.group(2).strip() if len(match.groups()) >= 2 and match.group(2) else None
                quotes.append(
                    ExpertQuoteItem(
                        quote=q_body,
                        author=author,
                        source=None,
                        element_type="inline_pattern",
                    )
                )

        return quotes

    def detect_statistical_claims(self) -> tuple[list[StatisticalClaimItem], list[str]]:
        """Detects verifiable percentages, year-stamped metrics, and primary academic/research outbound citations."""
        claims: list[StatisticalClaimItem] = []
        research_domains: list[str] = []
        seen_claims: set[str] = set()

        # 1. Percentages
        pct_regex = re.compile(r"(?:[^\.\n;]{0,40}\b\d+(?:\.\d+)?%(?:\s*(?:increase|decrease|growth|share|confidence|rate|درصد|yüzde|faiz))?[^\.\n;]{0,50})", re.IGNORECASE)
        for m in pct_regex.finditer(self.clean_text):
            txt = m.group(0).strip()
            if len(txt) >= 8 and txt.lower() not in seen_claims:
                seen_claims.add(txt.lower())
                claims.append(
                    StatisticalClaimItem(
                        claim_text=txt,
                        claim_type="percentage",
                    )
                )
            if len(claims) >= 6:
                break

        # 2. Year-stamped figures / benchmarks (e.g., 2024 report, by 2026, 1403 شمسی)
        year_regex = re.compile(
            r"(?:(?:in|by|since|year|report|survey|benchmark|سال|گزارش|tarihinde|ilində|عام|سنة)\s*(?:19\d{2}|20\d{2}|۱[۳۴]\d{2})[^\.\n;]{5,60})",
            re.IGNORECASE,
        )
        for m in year_regex.finditer(self.clean_text):
            txt = m.group(0).strip()
            if len(txt) >= 12 and txt.lower() not in seen_claims:
                seen_claims.add(txt.lower())
                claims.append(
                    StatisticalClaimItem(
                        claim_text=txt,
                        claim_type="year_figure",
                    )
                )
            if len(claims) >= 10:
                break

        # 3. Outbound academic / research links (.edu, .org, arXiv, DOI, journals)
        _, external_links = self.parser.get_links()
        seen_domains = set()

        for ext in external_links:
            try:
                parsed = urlparse(ext.url)
                netloc = parsed.netloc.lower()
                is_edu = netloc.endswith(".edu") or ".edu." in netloc
                is_org = netloc.endswith(".org") or ".org." in netloc
                is_research = any(netloc == rd or netloc.endswith("." + rd) for rd in self.RESEARCH_DOMAINS)

                if is_edu or is_research or (is_org and "wikipedia" not in netloc):
                    matched_label = netloc
                    if matched_label not in seen_domains:
                        seen_domains.add(matched_label)
                        research_domains.append(matched_label)
                        claims.append(
                            StatisticalClaimItem(
                                claim_text=f"Primary research/authority citation ({netloc}): {ext.text or ext.url}",
                                claim_type="research_citation",
                                source_url=ext.url,
                            )
                        )
            except Exception:
                continue

        return claims, research_domains

    def evaluate_offer_transparency(self) -> OfferTransparencyReport:
        """Evaluates commercial pages for explicit pricing, scope tables, and structured deliverables."""
        url_lower = self.url.lower()
        parsed_path = urlparse(self.url).path.lower()
        text_lower = self.clean_text.lower()

        # Determine if URL is commercial / service offering
        is_path_commercial = any(k in parsed_path for k in self.COMMERCIAL_PATH_KEYWORDS)
        is_body_commercial = any(k in text_lower for k in self.COMMERCIAL_BODY_KEYWORDS)
        is_commercial = is_path_commercial or is_body_commercial

        if not is_commercial:
            return OfferTransparencyReport(
                is_commercial_url=False,
                has_pricing_table=False,
                has_structured_deliverables=False,
                detected_currencies=[],
                deliverables_count=0,
                transparency_score=100,  # Non-commercial pages are not penalized
            )

        # 1. Check for Pricing Tables or Grids
        has_table = bool(self.soup.find("table"))
        has_price_grid = bool(
            self.soup.find(
                lambda tag: tag.name in ["div", "section", "article"]
                and any(
                    cls_kw in " ".join(tag.get("class", [])).lower()
                    for cls_kw in ["pricing", "price", "plans", "tier", "tarif", "paket"]
                )
            )
        )
        has_pricing_table = has_table or has_price_grid

        # 2. Check for Currency Disclosures
        detected_currencies = []
        for curr in self.CURRENCY_SYMBOLS:
            if curr in self.raw_html or curr.lower() in text_lower:
                if curr not in detected_currencies:
                    detected_currencies.append(curr)

        # 3. Check for Structured Deliverables (lists with deliverables/checkmarks)
        deliverables_count = 0
        deliverable_patterns = [
            re.compile(r"[\u2713\u2714\u2611\u2022\u25cf\u2705]"),  # checkmark or bullet symbols
            re.compile(r"\b(included|deliverable|deliverables|feature|sla|timeline|تحویل|ضمانت|تعهد|teslimat|daxildir)\b", re.IGNORECASE),
        ]

        for li in self.soup.find_all("li"):
            li_text = li.get_text(separator=" ", strip=True)
            if any(p.search(li_text) for p in deliverable_patterns) and len(li_text) > 8:
                deliverables_count += 1

        has_structured_deliverables = deliverables_count >= 3

        # Compute transparency score
        t_score = 0
        if has_pricing_table:
            t_score += 40
        if len(detected_currencies) > 0:
            t_score += 30
        if has_structured_deliverables:
            t_score += 30

        return OfferTransparencyReport(
            is_commercial_url=True,
            has_pricing_table=has_pricing_table,
            has_structured_deliverables=has_structured_deliverables,
            detected_currencies=detected_currencies,
            deliverables_count=deliverables_count,
            transparency_score=min(100, t_score),
        )

    def analyze(self) -> CitationEvidenceReport:
        """Executes full Citation Evidence, Quote Density & Offer Transparency audit."""
        expert_quotes = self.extract_expert_quotes()
        statistical_claims, research_domains = self.detect_statistical_claims()
        offer_transparency = self.evaluate_offer_transparency()

        # Scoring weights & breakdown
        # 1. Expert Quotes & Attributions (up to 30 pts)
        quote_score = 0
        if len(expert_quotes) >= 3:
            quote_score = 30
        elif len(expert_quotes) == 2:
            quote_score = 25
        elif len(expert_quotes) == 1:
            quote_score = 20
        else:
            quote_score = 0

        # 2. Verifiable Statistical Claims & Empirical Grounding (up to 40 pts)
        # 20 pts from percentage/figures + 20 pts from primary research citations
        stat_points = min(20, len([c for c in statistical_claims if c.claim_type in ["percentage", "year_figure"]]) * 5)
        research_points = min(20, len(research_domains) * 10)
        empirical_score = stat_points + research_points

        # 3. Offer Transparency / Context Grounding (up to 30 pts)
        if offer_transparency.is_commercial_url:
            transparency_points = int(offer_transparency.transparency_score * 0.3)
        else:
            # For informational / editorial URLs, credit citation depth & word density
            word_count = len(self.clean_text.split())
            if word_count > 600 and (len(expert_quotes) > 0 or len(research_domains) > 0):
                transparency_points = 30
            elif word_count > 300:
                transparency_points = 20
            else:
                transparency_points = 10

        total_score = max(0, min(100, quote_score + empirical_score + transparency_points))

        # Generate up to 3 prioritized remediation tips
        remediation_tips: list[str] = []

        if len(expert_quotes) < 2:
            remediation_tips.append(
                "Embed attributed expert quotes (`<blockquote>`, `<q>`, or author citations) to elevate domain authority and quotation density."
            )

        if len(research_domains) == 0 or len(statistical_claims) < 2:
            remediation_tips.append(
                "Incorporate verifiable statistical claims, date-stamped figures, and primary research links (.edu, .org, arXiv, DOI)."
            )

        if offer_transparency.is_commercial_url and offer_transparency.transparency_score < 70:
            remediation_tips.append(
                "Publish transparent pricing tables, clearly defined scope deliverables, and SLA timelines for commercial offerings."
            )
        elif len(remediation_tips) < 3 and total_score < 75:
            remediation_tips.append(
                "Anchor factual claims with explicit source attribution and contextual citations to reinforce AI Search answer engines."
            )

        return CitationEvidenceReport(
            evidence_citability_score=total_score,
            expert_quotes_count=len(expert_quotes),
            expert_quotes=expert_quotes[:10],
            statistical_claims_count=len(statistical_claims),
            statistical_claims=statistical_claims[:10],
            research_links_count=len(research_domains),
            research_domains=research_domains,
            offer_transparency=offer_transparency,
            remediation_tips=remediation_tips[:3],
        )
