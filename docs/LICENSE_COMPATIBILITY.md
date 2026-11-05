# License Compatibility & Clean-Room Architecture Analysis

This document provides a formal legal and architectural review of the licenses governing the 10 reference projects, explains the licensing boundary strategy for **Molavi Web Intelligence Engine (MWIE)**, and confirms full compliance with open-source legal standards.

---

## 1. Reference Projects License Audit

| Project | License Type | SPDX Identifier | Permissive / Copyleft | Linking & Distribution Obligations |
| :--- | :--- | :--- | :--- | :--- |
| **01. Firecrawl** | AGPL-3.0 | `AGPL-3.0-only` | Strong Network Copyleft | Cannot be linked, embedded, or modified within proprietary or Apache-2.0 core code without triggering copyleft requirements across network usage. |
| **02. Camoufox** | MPL-2.0 | `MPL-2.0` | Weak File-level Copyleft | Permits integration and Apache-2.0 distribution as long as modifications to Camoufox's own source files remain under MPL-2.0. |
| **03. Scrapling** | BSD-3-Clause | `BSD-3-Clause` | Permissive | Fully compatible with Apache-2.0. Requires retention of copyright notice and disclaimer. |
| **04. Crawl4AI** | Apache-2.0 | `Apache-2.0` | Permissive with Patent Grant | Directly compatible with MWIE under Apache-2.0. |
| **05. ScrapeGraphAI** | MIT | `MIT` | Permissive | Fully compatible with Apache-2.0. Requires copyright attribution. |
| **06. Apify MCP Server** | MIT | `MIT` | Permissive | Fully compatible with Apache-2.0. Requires copyright attribution. |
| **07. Nanobrowser** | Apache-2.0 | `Apache-2.0` | Permissive with Patent Grant | Directly compatible with MWIE under Apache-2.0. |
| **08. Agent Desktop** | Apache-2.0 | `Apache-2.0` | Permissive with Patent Grant | Directly compatible with MWIE under Apache-2.0. |
| **09. Maxun** | AGPL-3.0 | `AGPL-3.0-only` | Strong Network Copyleft | Cannot be bundled or imported directly into Apache-2.0 codebase. Requires clean-room implementation or decoupled HTTP integration. |
| **10. Crawlee** | Apache-2.0 | `Apache-2.0` | Permissive with Patent Grant | Directly compatible with MWIE under Apache-2.0. |

---

## 2. Chosen License for MWIE

The **Molavi Web Intelligence Engine (MWIE)** is released under the **Apache License 2.0**:
- **Why Apache-2.0?**
  1. Grants explicit patent rights from contributors to users.
  2. Protects trademarks while ensuring open collaboration.
  3. Enables enterprise adoption without friction.
  4. Fully compatible with permissive licenses (MIT, BSD-3-Clause, Apache-2.0).
  5. Provides crystal-clear terms for redistribution and derivative works.

---

## 3. Clean-Room Boundary Strategy for Copyleft Projects

Two projects in the research audit are governed by **AGPL-3.0** (`Firecrawl` and `Maxun`):
1. **Zero Code Copying:** Not a single line of code, template, or script from Firecrawl or Maxun has been copied, pasted, or directly translated into MWIE.
2. **Clean-Room Independent Implementation:** MWIE's crawler, scheduler, markdown generator, and API architecture are written 100% from scratch in idiomatic Python using independent design patterns.
3. **Decoupled Network Boundaries:** If users wish to route scraping tasks through an existing self-hosted Firecrawl instance, MWIE provides an independent client adapter (`FirecrawlAdapter`) that communicates strictly over HTTP standard REST JSON APIs. Under FSF and OSI guidelines, communicating with an AGPL service over an independent network API does not contaminate the caller's Apache-2.0 license.
4. **MPL-2.0 Compliance (Camoufox):** Camoufox is supported as an optional external browser engine module. No modifications are made to upstream Camoufox source files, adhering cleanly to MPL-2.0 Section 3.3.

---

## 4. Verification & Attributions

All referenced conceptual inspirations are openly and transparently acknowledged in [CREDITS.md](../CREDITS.md) and [THIRD_PARTY_LICENSES.md](../THIRD_PARTY_LICENSES.md).
