# Molavi Web Intelligence Engine (MWIE)

<div align="center">

**One Engine. Complete Web Intelligence.**  
**Vahid Mühərrik. Tam Veb Kəşfiyyatı.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](pyproject.toml)
[![Tests](https://img.shields.io/badge/Tests-23%20Passed-brightgreen)](tests/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![MCP](https://img.shields.io/badge/MCP-Native%20Server-purple.svg)](https://modelcontextprotocol.io)
[![Author](https://img.shields.io/badge/Author-Taqi%20Molavi-orange.svg)](https://molavi.pro)

**[English](README.md) | [فارسی](README.fa.md) | [Türkçe](README.tr.md) | [Azərbaycan](README.az.md) | [العربية](README.ar.md)**

<br/>

> 🚀 **Canlı Onlayn Veb Aləti (100% Pulsuz və Modeldən Asılı Olmayan):**  
> Mühərriki 5 dildə birbaşa brauzerinizdə canlı sınaqdan keçirin:  
> [🇮🇷 فارسی (Fars)](https://molavi.pro/fa/tools/web-intelligence) • [🇬🇧 English](https://molavi.pro/en/tools/web-intelligence) • [🇹🇷 Türkçe](https://molavi.pro/tr/tools/web-intelligence) • [🇦🇿 Azərbaycanca](https://molavi.pro/az/tools/web-intelligence) • [🇸🇦 العربية](https://molavi.pro/ar/tools/web-intelligence)

<br/>

[![Molavi Web Intelligence Mühərriki İzah Videosu](docs/assets/poster.jpg)](https://molavi.pro/videos/web-intelligence/explainer.mp4)

*🎬 Vizual Memarlıq və Video İzahı — [Yüksək Keyfiyyətdə İzlə](https://molavi.pro/videos/web-intelligence/explainer.mp4) və ya depoda: [`docs/assets/mwie-explainer.mp4`](docs/assets/mwie-explainer.mp4)*

</div>

---

## 1. Layihənin Təqdimatı

**Molavi Web Intelligence Engine (MWIE)** — **Texniki SEO**, **Generativ Axtarış Optimizasiyası (GEO - Generative Engine Optimization)**, **Süni İntellekt Axtarış İndekslənməsi** və **Müstəqil Süni İntellekt Agentləri** üçün xüsusi olaraq dizayn edilmiş açıq mənbəli, öz-özünə yerləşdirilə bilən (self-hosted) veb kəşfiyyat platformasıdır.

Müasir axtarış sistemləri ənənəvi açar söz uyğunluğundan generativ süni intellekt axtarış sistemlərinə (Perplexity, ChatGPT Search, Google Gemini Grounding) doğru inkişaf etmişdir. Ənənəvi veb skreypinq vasitələri yalnız xam HTML çıxarışına diqqət yetirir, lakin semantik varlıq münasibətlərini (Entities), istinadları (Citations) və ya texniki SEO vəziyyətini dərk edə bilmirlər.

MWIE yüksək sürətli HTTP dırmaşma, JavaScript icrası üçün başsız Playwright brauzeri, davamlı DOM təmizlənməsi, texniki SEO hesabatı və süni intellekt hazırlığı analizini vahid modulyar arxitekturada birləşdirir. Bütün imkanlar **REST API** və yerli **Model Context Protocol (MCP)** vasitəsilə əlçatandır.

---

## 2. Əsas Xüsusiyyətlər

- **Vahid Çox-Adaptorlu İnteqrasiya:**
  - *Native Async HTTP Adaptoru:* Brauzer resursu tələb etmədən 20 ms-dən aşağı sürətli çıxarış.
  - *Playwright Başsız Brauzer Adaptoru:* Dinamik JavaScript tək-səhifəli tətbiqlərinin (SPA) tam emalı.
  - *Firecrawl Müstəqil Adaptoru:* Xarici və ya yerli Firecrawl klasterləri ilə tam hüquqi təcrid olunmuş əlaqə.
- **Ağıllı Marşrutlaşdırıcı (Intelligent Router):**
  - Səhifənin növünə, JS tələbinə və real zaman performansına əsasən optimal adaptoru avtomatik seçir.
  - Xəta baş verdikdə ehtiyat adaptora avtomatik keçid (fallback) təmin edir.
- **Təmiz Məzmun və Markdown İstehsalı:**
  - Sayt başlıqları, altlıqlar, naviqasiya menyuları və kuki bannerləri kimi lüzumsuz məlumatları kənarlaşdırır.
  - LLM və RAG sistemləri üçün iyerarxik təmiz Markdown sənədi formalaşdırır.
- **Doğma Model Context Protocol (MCP) Serveri:**
  - Süni intellekt agentləri (Hermes, Hamzad, Claude Desktop, Cursor) üçün 12 doğma alət təqdim edir.
- **Sıfır Xərc və Tam Sərbəstlik:**
  - 100% açıq mənbəli və yerli icra. Heç bir ödənişli API açarına ehtiyac yoxdur.

---

## 3. Texniki SEO İmkanları

- **İndeksləşmə və İcazə Nəzarəti:** Meta robots (`noindex`, `nofollow`), `X-Robots-Tag` və HTTP status kodlarının yoxlanılması.
- **Meta Məlumatların Auditi:** Başlıq (`<title>`) və təsvir (`meta description`) uzunluqlarının beynəlxalq standartlara uyğunluğu.
- **Kanonik Link Uyğunluğu:** `rel="canonical"` etiketinin sorğu olunan URL ilə uyğunluğunun təyini.
- **Başlıq İyerarxiyası:** H1–H6 strukturunun analizi və yeganə əsas H1 tələbi.
- **Şəkillərin Əlçatanlığı:** Şəkillərin ümumi sayı, Alt mətninin mövcudluğu və çatışmayan Alt etiketləri.
- **Keçidlərin Analizi:** Daxili (Internal) və xarici (External) keçidlərin sayılması və ayrılması.
- **Strukturlaşdırılmış Məlumatlar:** JSON-LD skriptlərindən Schema.org tiplərinin çıxarılması.
- **Sosial Şəbəkə Kartları:** Open Graph və Twitter Cards tamlığının yoxlanılması.
- **Çoxdillilik Dəstəyi:** Hreflang etiketlərinin və dil kodlarının doğrulanması.
- **Mətn / HTML Nisbəti:** Təmiz mətnin ümumi koda nisbətinin hesablanması.
- **Çəkili SEO Hesabatı:** 0–100 bal arasında qiymətləndirmə və çatışmazlıqların aradan qaldırılması üçün tövsiyələr.

---

## 4. GEO (Generativ Axtarış Optimizasiyası) İmkanları

- **Brend və Varlıq Təyini (Entity Intelligence):** JSON-LD və mətn daxilindən Brend, Təşkilat, Şəxs və Məhsul varlıqlarının aşkarlanması.
- **İstinad və Mənbə İntellekti (Citation Intelligence):** Xarici istinad keçidləri, sitat blokları (`blockquote`) və müəllif aidiyyətinin xəritələnməsi.
- **Sual-Cavab Bilik Blokları:** FAQPage strukturlarının və sual başlıqlı paraqrafların avtomatik aşkarlanması.
- **Semantik Parçalama (Semantic Chunking):** Vektor RAG bazaları üçün simvol və token həcminə uyğun təmiz mətn hissələrinin yaradılması.
- **Süni İntellekt Hazırlıq Balı (AI-Readiness Score):** Məzmunun generativ axtarış sistemləri (Perplexity, ChatGPT və s.) tərəfindən dərk olunma dərəcəsinin 0–100 arasında qiymətləndirilməsi.

---

## 5. Arxitektura Baxışı

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      Süni İntellekt Agentləri və Müştərilər            │
│           (Hermes, Hamzad, Claude Desktop, Cursor, REST Clients)       │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │ MCP (Stdio/SSE)                 │ REST API (HTTP)
┌──────────────────▼─────────────────────────────────▼───────────────────┐
│              Molavi Web Intelligence Engine (MWIE) Nüvəsi              │
├────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────┐    ┌────────────────────────────────────┐ │
│ │   Ağıllı Marşrutlaşdırıcı│    │  Sorğu Növbəsi və Robots İdarəçisi │ │
│ └────────────┬─────────────┘    └────────────────────────────────────┘ │
│              │                                                         │
│ ┌────────────▼───────────────────────────────────────────────────────┐ │
│ │                    Vahid Çıxarış Adaptorları                       │ │
│ │  • Native HTTP Adaptoru    • Playwright Adaptoru  • Firecrawl API   │ │
│ └────────────┬───────────────────────────────────────────────────────┘ │
│              │ Xam HTML                                                │
│ ┌────────────▼───────────────────────────────────────────────────────┐ │
│ │                  Məzmunun Təmizlənməsi və Emalı                      │ │
│ │  • Kənarlaşdırma       • HTML Parser      • Markdown Generator     │ │
│ └────────────┬───────────────────────────────────────────────────────┘ │
│              │ Təmiz DOM və Mətn                                       │
│ ┌────────────▼────────────────────────┬──────────────────────────────┐ │
│ │         Texniki SEO Analizçisi       │       GEO və Varlıq Analizçisi │ │
│ │  • Kanonik və Meta Məlumatlar       │  • Brend Varlıqlarının Təyini│ │
│ │  • Başlıqlar və Şəkil Altları       │  • Mənbə və İstinad Xəritəsi │ │
│ │  • JSON-LD Strukturlaşmış Data      │  • Sual-Cavab Bilik Blokları │ │
│ │  • 0-100 Çəkili Bal                 │  • Süni İntellekt Hazırlıq   │ │
│ └─────────────────────────────────────┴──────────────────────────────┘ │
│                                                                        │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │   TTL Keş Yaddaş (Yaddaş/Redis)  •   SSRF Təhlükəsizlik Filtrləri  │ │
│ └────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Quraşdırma və Başlanğıc

### Tələblər
- Python 3.10 və ya daha yüksək versiya
- Linux, macOS və ya Windows

### Quraşdırma
```bash
git clone https://github.com/tmolavi/molavi-web-intelligence.git
cd molavi-web-intelligence
python3 -m pip install -e .
```

Test və tərtibat alətləri daxil:
```bash
python3 -m pip install -e ".[dev]"
```

### Python SDK Nümunəsi
```python
import asyncio
from mwie.crawler.engine import crawl_engine
from mwie.core.models import ExtractionOptions


async def main():
    options = ExtractionOptions(render_js=False, extract_seo=True, extract_geo=True)
    result = await crawl_engine.extract_single("https://molavi.pro", options)

    print(f"Səhifə Başlığı: {result.seo.meta_title}")
    print(f"SEO Balı: {result.seo.seo_score}/100")
    print(f"Süni İntellekt Hazırlığı: {result.geo.ai_readiness_score}/100")
    print(f"Aşkarlanmış Varlıqlar: {[e.name for e in result.geo.entities]}")


asyncio.run(main())
```

---

## 7. REST API İstifadəsi

Serveri işə salın:
```bash
uvicorn mwie.api.app:app --host 0.0.0.0 --port 8000
```
İnteraktiv Swagger sənədləşməsi: `http://localhost:8000/docs`

### Nümunə Sorğu: Səhifənin Analizi
```bash
curl -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://molavi.pro"}'
```

### Nümunə Sorğu: Rəqiblərin Müqayisəsi
```bash
curl -X POST http://localhost:8000/api/v1/compare \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://molavi.pro", "https://example.com"]}'
```

---

## 8. Model Context Protocol (MCP) İnteqrasiyası

MWIE sistemi süni intellekt agentləri üçün 12 yerli alət təqdim edir:

| Alət Adı | Təyinatı |
| :--- | :--- |
| `crawl_url` | Tək URL üçün tam çıxarış, SEO və GEO auditi |
| `crawl_domain` | Domen üzrə dərin rekursiv axtarış |
| `extract_page_content` | Təmiz mətn və Markdown çıxarışı |
| `analyze_seo` | Texniki SEO hesabatı və tövsiyələr |
| `analyze_geo` | Generativ axtarış optimizasiyası və AI hazırlığı |
| `extract_entities` | Brend, təşkilat, şəxs və məhsul varlıqları |
| `extract_structured_data` | Schema.org JSON-LD sxemlərinin çıxarılması |
| `analyze_sitemap` | Sayt xəritəsindən (sitemap.xml) URL kəşfi |
| `compare_pages` | Rəqib səhifələrin yan-yana SEO/GEO müqayisəsi |
| `batch_process_urls` | Səhifələrin paralel emalı |
| `get_job_status` | Sistem və keş yaddaşının vəziyyəti |
| `get_extraction_metadata`| Canlı adaptor gecikmələri və uğur faizləri |

---

## 9. Docker İlə İşə Salınma

```bash
docker build -t molavi-web-intelligence .
docker run -p 8000:8000 molavi-web-intelligence
```

Və ya Docker Compose vasitəsilə:
```bash
docker compose up -d
```

---

## 10. Təhlükəsizlik Qaydaları

- **SSRF Müdafiəsi:** RFC 1918 daxili şəbəkə IP-ləri (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) və daxili hostlar avtomatik bloklanır.
- **Robots.txt Qaydaları:** Sayt sahiblərinin məhdudiyyətlərinə tam riayət edilir.
- **İcazə Verilmiş Domenlər:** Korporativ şəbəkələrdə hədəf domenlərin müəyyənləşdirilməsi mümkündür.

---

## 11. Testlər, Real Göstəricilər və İcma Telemetriyası

Linux ARM64 mühitində 100 təkrar üzrə ölçülmüş real göstəricilər:
- **HTML Ayrıştırma və Təmizləmə:** 13.10 ms orta gecikmə (76.4 əməliyyat/san, 4.7 MB yaddaş)
- **Markdown İstehsalı:** 2.56 ms orta gecikmə (390.7 əməliyyat/san, 2.6 MB yaddaş)
- **Texniki SEO Analizçisi:** 11.25 ms orta gecikmə (88.9 əməliyyat/san, 2.4 MB yaddaş)
- **GEO və Varlıq Qrafı:** 8.56 ms orta gecikmə (116.8 əməliyyat/san, 6.4 MB yaddaş)

### İcma Bençmark Telemetriyası və Repozitoriyə Göndəriş
`molavi.pro` veb aləti könüllü iştirak əsasında sürət və audit nəticələrini açıq repozitori məlumat bazasına göndərir. Qeydlər [`https://molavi.pro/data/benchmark-records.json`](https://molavi.pro/data/benchmark-records.json) ünvanında saxlanılır. Bu məlumatları lokal mühitinizdə sinxronlaşdırmaq üçün:

```bash
python3 scripts/sync_benchmarks.py
```

Ətraflı məlumat və metodologiya: [docs/BENCHMARKS.md](docs/BENCHMARKS.md)

---

## 12. Lisenziya və Müəlliflik Hüququ

- **Apache License 2.0** altında yayımlanmışdır. Ətraflı: [LICENSE](LICENSE).
- Arxitektura müstəqil şəkildə **Taqi Molavi** tərəfindən hazırlanmışdır.
- Tədqiqat zamanı istinad edilmiş üçüncü tərəf layihələri [CREDITS.md](CREDITS.md) və [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) sənədlərində qeyd olunmuşdur.

---

## 13. Müəllif və Ekosistem

**Müəllif:** Taqi Molavi  
**Rəsmi Sayt:** [https://molavi.pro](https://molavi.pro)  
**Ekosistem İnteqrasiyaları:** [Hermes Agent](integrations/hermes/) | [Hamzad Digital Twins](integrations/hamzad/)
