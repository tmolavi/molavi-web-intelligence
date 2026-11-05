# Third-Party Licenses & Legal Notices

The **Molavi Web Intelligence Engine (MWIE)** utilizes or interacts with several open-source libraries and frameworks. Below is a summary of the relevant licenses:

---

### Python Standard & Third-Party Dependencies

- **FastAPI** (`tiangolo/fastapi`)  
  License: MIT  
  Copyright (c) 2018 Sebastián Ramírez

- **Pydantic** (`pydantic/pydantic`)  
  License: MIT  
  Copyright (c) 2017 Samuel Colvin

- **Playwright for Python** (`microsoft/playwright-python`)  
  License: Apache-2.0  
  Copyright (c) Microsoft Corporation

- **HTTPX** (`encode/httpx`)  
  License: BSD-3-Clause  
  Copyright (c) 2019 Encode OSS Ltd.

- **BeautifulSoup4** (`Leonard Richardson`)  
  License: MIT  
  Copyright (c) 2004-2024 Leonard Richardson

- **Model Context Protocol Python SDK (`mcp`)** (`Anthropic, PBC`)  
  License: MIT  
  Copyright (c) 2024 Anthropic, PBC

- **Uvicorn** (`encode/uvicorn`)  
  License: BSD-3-Clause  
  Copyright (c) 2017-present, Encode OSS Ltd.

- **Pytest** (`pytest-dev`)  
  License: MIT  
  Copyright (c) 2004-2024 Holger Krekel and others

- **Ruff** (`astral-sh/ruff`)  
  License: MIT / Apache-2.0  
  Copyright (c) 2023 Astral Software Inc.

---

### Reference Projects Inspected Under Clean-Room Research

The following projects were studied as architectural and research references under clean-room engineering rules (see [docs/SOURCE_PROJECT_ANALYSIS.md](docs/SOURCE_PROJECT_ANALYSIS.md) and [docs/LICENSE_COMPATIBILITY.md](docs/LICENSE_COMPATIBILITY.md)):

- **Crawl4AI** — Apache-2.0 (unclecode)
- **Crawlee** — Apache-2.0 (Apify Technologies s.r.o.)
- **Scrapling** — BSD-3-Clause (D4Vinci)
- **ScrapeGraphAI** — MIT (ScrapeGraphAI)
- **Apify MCP Server** — MIT (Apify Technologies s.r.o.)
- **Nanobrowser** — Apache-2.0 (Nanobrowser)
- **Agent Desktop** — Apache-2.0 (Vercel, Inc.)
- **Camoufox** — MPL-2.0 (daijro)
- **Firecrawl** — AGPL-3.0 (Mendable AI / Firecrawl) [Clean-room decoupled HTTP adapter only; no AGPL code copied or linked]
- **Maxun** — AGPL-3.0 (GetMaxun) [Clean-room decoupled architecture only; no AGPL code copied or linked]
