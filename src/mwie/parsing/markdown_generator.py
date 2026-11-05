"""
Deterministic Markdown generator for MWIE.
Transforms HTML into clean, hierarchical, LLM-ready Markdown.
"""

import re

from bs4 import BeautifulSoup, NavigableString, Tag


class MarkdownGenerator:
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, "html.parser")

    def generate(self) -> str:
        """Converts HTML to structured Markdown."""
        lines = []
        body = self.soup.body or self.soup

        for element in body.children:
            if isinstance(element, Tag):
                res = self._convert_tag(element)
                if res.strip():
                    lines.append(res.strip())
            elif isinstance(element, NavigableString):
                text = str(element).strip()
                if text:
                    lines.append(text)

        raw_md = "\n\n".join(lines)
        # Normalize multiple blank lines
        clean_md = re.sub(r"\n{3,}", "\n\n", raw_md)
        return clean_md.strip()

    def _convert_tag(self, tag: Tag) -> str:
        name = tag.name.lower() if tag.name else ""

        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(name[1])
            text = tag.get_text(separator=" ", strip=True)
            return f"{'#' * level} {text}"

        elif name == "p":
            return self._inline_formatting(tag)

        elif name in ("ul", "ol"):
            items = []
            is_ol = name == "ol"
            for idx, li in enumerate(tag.find_all("li", recursive=False), 1):
                li_text = self._inline_formatting(li)
                prefix = f"{idx}." if is_ol else "-"
                items.append(f"{prefix} {li_text}")
            return "\n".join(items)

        elif name == "blockquote":
            text = tag.get_text(separator="\n", strip=True)
            return "\n".join(f"> {line}" for line in text.split("\n"))

        elif name == "pre":
            code = tag.find("code")
            text = code.get_text() if code else tag.get_text()
            return f"```\n{text}\n```"

        elif name == "table":
            return self._convert_table(tag)

        elif name in ("div", "section", "article", "main"):
            sub_lines = []
            for child in tag.children:
                if isinstance(child, Tag):
                    sub = self._convert_tag(child)
                    if sub.strip():
                        sub_lines.append(sub.strip())
                elif isinstance(child, NavigableString):
                    text = str(child).strip()
                    if text:
                        sub_lines.append(text)
            return "\n\n".join(sub_lines)

        else:
            return self._inline_formatting(tag)

    def _inline_formatting(self, tag: Tag) -> str:
        text = tag.get_text(separator=" ", strip=True)
        return text

    def _convert_table(self, table: Tag) -> str:
        rows = table.find_all("tr")
        if not rows:
            return ""

        table_data = []
        for tr in rows:
            cells = [c.get_text(separator=" ", strip=True) for c in tr.find_all(["th", "td"])]
            if cells:
                table_data.append(cells)

        if not table_data:
            return ""

        max_cols = max(len(r) for r in table_data)
        # Normalize row lengths
        for r in table_data:
            while len(r) < max_cols:
                r.append("")

        md_rows = []
        # Header
        header = table_data[0]
        md_rows.append("| " + " | ".join(header) + " |")
        md_rows.append("| " + " | ".join(["---"] * max_cols) + " |")

        # Body
        for row in table_data[1:]:
            md_rows.append("| " + " | ".join(row) + " |")

        return "\n".join(md_rows)
