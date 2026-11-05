"""
Generative Engine Optimization (GEO) Analyzer for MWIE.
Extracts entities, citations, Q&A knowledge blocks, semantic chunks, and calculates AI-readiness.
"""

import re
from typing import Any

from bs4 import BeautifulSoup

from mwie.core.models import (
    CitationItem,
    ContentChunk,
    EntityItem,
    GEOReport,
    QAItem,
)
from mwie.parsing.html_parser import HTMLParser


class GEOAnalyzer:
    COMMON_ENTITIES = {
        "Brand": [
            "google",
            "microsoft",
            "apple",
            "amazon",
            "meta",
            "openai",
            "anthropic",
            "molavi",
        ],
        "Organization": [
            "foundation",
            "inc",
            "corp",
            "ltd",
            "gmbh",
            "university",
            "institute",
            "consortium",
        ],
        "Product": ["engine", "sdk", "api", "platform", "model", "suite", "cloud", "framework"],
    }

    def __init__(
        self,
        raw_html: str,
        clean_text: str,
        url: str,
        json_ld_schemas: list[dict[str, Any]] | None = None,
    ):
        self.raw_html = raw_html or ""
        self.clean_text = clean_text or ""
        self.url = url
        self.json_ld_schemas = json_ld_schemas or []
        self.soup = BeautifulSoup(self.raw_html, "html.parser")
        self.parser = HTMLParser(self.raw_html, self.url)

    def extract_entities(self) -> list[EntityItem]:
        entities: dict[str, EntityItem] = {}

        # 1. From JSON-LD schemas
        for schema in self.json_ld_schemas:
            stype = schema.get("@type", "")
            if isinstance(stype, list):
                stype = "/".join(stype)

            name = schema.get("name") or schema.get("legalName")
            if name and isinstance(name, str):
                ename = name.strip()
                cat = (
                    "Organization"
                    if "Organization" in stype
                    else "Product"
                    if "Product" in stype
                    else "Brand"
                )
                entities[ename.lower()] = EntityItem(
                    name=ename,
                    entity_type=cat,
                    frequency=3,
                    context=f"JSON-LD Schema {stype}",
                    confidence=0.98,
                )

            author = schema.get("author")
            if isinstance(author, dict) and "name" in author:
                aname = str(author["name"]).strip()
                entities[aname.lower()] = EntityItem(
                    name=aname,
                    entity_type="Person",
                    frequency=2,
                    context="Author metadata in JSON-LD",
                    confidence=0.95,
                )

        # 2. Extract brand from meta author / site_name
        site_name_tag = self.soup.find("meta", property="og:site_name")
        if site_name_tag and site_name_tag.get("content"):
            bname = site_name_tag["content"].strip()
            if bname.lower() not in entities:
                entities[bname.lower()] = EntityItem(
                    name=bname,
                    entity_type="Brand",
                    frequency=2,
                    context="og:site_name metadata",
                    confidence=0.92,
                )

        # 3. Text-level entity extraction (Capitalized n-grams and proper nouns)
        proper_noun_pattern = re.compile(r"\b([A-Z][a-z0-9]+(?:\s+[A-Z][a-z0-9]+)*)\b")
        words = proper_noun_pattern.findall(self.clean_text)

        frequency_map: dict[str, int] = {}
        for w in words:
            if len(w) > 3 and w.lower() not in (
                "this",
                "that",
                "there",
                "these",
                "those",
                "when",
                "what",
                "where",
            ):
                frequency_map[w] = frequency_map.get(w, 0) + 1

        for phrase, freq in frequency_map.items():
            if freq >= 2 and phrase.lower() not in entities:
                # Classify heuristic
                etype = "Concept"
                for cat, keywords in self.COMMON_ENTITIES.items():
                    if any(k in phrase.lower() for k in keywords):
                        etype = cat
                        break
                entities[phrase.lower()] = EntityItem(
                    name=phrase,
                    entity_type=etype,
                    frequency=freq,
                    context="Discovered in body text",
                    confidence=0.75,
                )

        return list(entities.values())

    def extract_citations(self) -> list[CitationItem]:
        citations: list[CitationItem] = []
        _, external_links = self.parser.get_links()

        # Find blockquotes and citations
        for bq in self.soup.find_all("blockquote"):
            quote_text = bq.get_text(separator=" ", strip=True)
            if quote_text:
                cite_source = bq.get("cite")
                citations.append(
                    CitationItem(
                        source_url=cite_source,
                        citation_text=quote_text,
                        context_sentence="Blockquote citation element",
                    )
                )

        # Check external reference links
        for ext in external_links[:15]:
            citations.append(
                CitationItem(
                    source_url=ext.url,
                    citation_text=ext.text,
                    anchor_text=ext.text,
                    context_sentence=f"External reference link in body: {ext.url}",
                )
            )

        return citations

    def extract_qa_blocks(self) -> list[QAItem]:
        qa_list: list[QAItem] = []

        # 1. From JSON-LD FAQPage
        for schema in self.json_ld_schemas:
            if schema.get("@type") == "FAQPage" and "mainEntity" in schema:
                for q in schema["mainEntity"]:
                    question = q.get("name", "")
                    answer = q.get("acceptedAnswer", {}).get("text", "")
                    if question and answer:
                        qa_list.append(QAItem(question=question, answer=answer))

        # 2. Text heuristics: headings containing ? followed by paragraph
        for heading in self.soup.find_all(["h2", "h3", "h4"]):
            htext = heading.get_text(separator=" ", strip=True)
            if "?" in htext or any(
                htext.lower().startswith(q) for q in ["how", "what", "why", "when", "can", "is"]
            ):
                # Look for next sibling paragraph
                next_p = heading.find_next_sibling(["p", "div"])
                if next_p:
                    ptext = next_p.get_text(separator=" ", strip=True)
                    if ptext and len(ptext) > 15:
                        qa_list.append(QAItem(question=htext, answer=ptext))

        return qa_list

    def create_semantic_chunks(self, max_chunk_chars: int = 1000) -> list[ContentChunk]:
        chunks: list[ContentChunk] = []
        sections = re.split(r"\n{2,}", self.clean_text)

        current_heading = "Overview"
        current_buffer = []
        curr_chars = 0
        idx = 0

        for sec in sections:
            sec_clean = sec.strip()
            if not sec_clean:
                continue

            if len(sec_clean) < 80 and not sec_clean.endswith("."):
                current_heading = sec_clean
                continue

            if curr_chars + len(sec_clean) > max_chunk_chars and current_buffer:
                combined = "\n\n".join(current_buffer)
                chunks.append(
                    ContentChunk(
                        index=idx,
                        heading=current_heading,
                        text=combined,
                        char_count=len(combined),
                        token_estimate=int(len(combined) / 4),
                    )
                )
                idx += 1
                current_buffer = [sec_clean]
                curr_chars = len(sec_clean)
            else:
                current_buffer.append(sec_clean)
                curr_chars += len(sec_clean)

        if current_buffer:
            combined = "\n\n".join(current_buffer)
            chunks.append(
                ContentChunk(
                    index=idx,
                    heading=current_heading,
                    text=combined,
                    char_count=len(combined),
                    token_estimate=int(len(combined) / 4),
                )
            )

        return chunks

    def analyze(self) -> GEOReport:
        entities = self.extract_entities()
        citations = self.extract_citations()
        qa_blocks = self.extract_qa_blocks()
        chunks = self.create_semantic_chunks()

        # Entity counts by type
        type_counts: dict[str, int] = {}
        for e in entities:
            type_counts[e.entity_type] = type_counts.get(e.entity_type, 0) + 1

        # Primary brand identification
        primary_brand = None
        brand_entities = [e for e in entities if e.entity_type == "Brand"]
        if brand_entities:
            brand_entities.sort(key=lambda x: (x.frequency, x.confidence), reverse=True)
            primary_brand = brand_entities[0].name

        # Calculate AI Readiness Score (0-100)
        score = 100
        breakdown = {}
        recommendations = []

        # 1. Answer & Q&A readiness
        if len(qa_blocks) == 0:
            score -= 15
            recommendations.append(
                "No explicit Q&A or FAQ structures detected. Generative engines favor direct Q&A formats."
            )
            breakdown["qa_structure"] = 0
        else:
            breakdown["qa_structure"] = min(20, len(qa_blocks) * 5)

        # 2. Entity density & clarity
        if len(entities) < 3:
            score -= 20
            recommendations.append(
                "Low entity density. Disclose brand, author, organization, or product entities clearly."
            )
            breakdown["entity_clarity"] = 5
        else:
            breakdown["entity_clarity"] = 25

        # 3. Citation & Source Attribution
        if len(citations) == 0:
            score -= 15
            recommendations.append(
                "No external citations, references, or source attributions found. Generative models heavily rely on verifiable citations."
            )
            breakdown["citations_grounding"] = 0
        else:
            breakdown["citations_grounding"] = min(25, len(citations) * 5)

        # 4. Semantic Chunkability
        if len(chunks) == 0 or len(self.clean_text) < 150:
            score -= 25
            recommendations.append(
                "Content length is insufficient for semantic chunking and RAG ingestion."
            )
            breakdown["semantic_chunks"] = 0
        else:
            breakdown["semantic_chunks"] = 30

        score = max(0, min(100, score))

        return GEOReport(
            url=self.url,
            primary_brand=primary_brand,
            entities=entities,
            entity_types_count=type_counts,
            citations=citations,
            qa_knowledge_blocks=qa_blocks,
            semantic_chunks=chunks,
            ai_readiness_score=score,
            ai_readiness_breakdown=breakdown,
            recommendations=recommendations,
        )
