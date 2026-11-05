# Molavi Web Intelligence Engine (MWIE)

<div align="center">

**One Engine. Complete Web Intelligence.**  
**Tek Motor. Eksiksiz Web İstihbaratı.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](pyproject.toml)
[![Tests](https://img.shields.io/badge/Tests-23%20Passed-brightgreen)](tests/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![MCP](https://img.shields.io/badge/MCP-Native%20Server-purple.svg)](https://modelcontextprotocol.io)
[![Author](https://img.shields.io/badge/Author-Taqi%20Molavi-orange.svg)](https://molavi.pro)

**[English](README.md) | [فارسی](README.fa.md) | [Türkçe](README.tr.md) | [Azərbaycan](README.az.md) | [العربية](README.ar.md)**

<br/>

> 🚀 **Canlı Çevrimiçi Web Aracı:** Ücretsiz ve kararlı [Molavi Web İstihbaratı ve SEO / GEO Analiz Aracını](https://molavi.pro/tr/tools/web-intelligence) doğrudan [molavi.pro](https://molavi.pro/tr) üzerinde tarayıcınızda deneyin.

</div>

---

## 1. Proje Tanıtımı

**Molavi Web Intelligence Engine (MWIE)**; **Teknik SEO**, **Üretken Arama Optimizasyonu (GEO - Generative Engine Optimization)**, **Yapay Zeka Arama İndeksleme** ve **Otonom Yapay Zeka Ajanları** için özel olarak tasarlanmış açık kaynaklı, bağımsız barındırılabilir (self-hosted) bir web zekası platformudur.

Modern arama motorları klasik anahtar kelime eşleştirmesinden üretken yapay zeka motorlarına (Perplexity, ChatGPT Search, Google Gemini Grounding) evrilmiştir. Geleneksel web kazıma araçları yalnızca ham HTML elde etmeye odaklanırken anlamsal varlık ilişkilerini (Entities), alıntıları (Citations) veya teknik SEO sağlığını analiz edememektedir.

MWIE; yüksek performanslı HTTP tarama, başsız (headless) Playwright JavaScript çalıştırma, dayanıklı DOM ayrıştırma, teknik SEO karnesi ve yapay zeka hazırlık analizini modüler bir yapıda birleştirir. Tüm yeteneklere **REST API** ve yerel **Model Context Protocol (MCP)** üzerinden erişilebilir.

---

## 2. Temel Özellikler

- **Birleşik Çoklu Adaptör Mimarisi:**
  - *Yerel Asenkron HTTP Adaptörü:* Tarayıcı yükü olmadan 20 ms altında ultra hızlı kazıma.
  - *Playwright Başsız Tarayıcı Adaptörü:* İstemci taraflı dinamik JavaScript tek sayfa uygulamalarını (SPA) tam olarak işler.
  - *Firecrawl Bağımsız Adaptörü:* Harici veya yerel Firecrawl kümelerine temiz arayüz bağlantısı.
- **Akıllı ve Öğrenen Yönlendirici (Intelligent Router):**
  - Sayfa karmaşıklığına, JS ihtiyacına ve geçmiş kararlılık metriklerine göre en uygun adaptörü otomatik seçer.
  - Hata durumunda alternatif adaptörlere otomatik geri dönüş (fallback) sağlar.
- **Gürültüden Arındırılmış İçerik ve Markdown Üretimi:**
  - Üstbilgi, altbilgi, gezinme menüleri ve çerez bildirimleri gibi gereksiz öğeleri otomatik filtreler.
  - LLM modelleri ve RAG vektör sistemleri için hiyerarşik temiz Markdown üretir.
- **Yerel Model Context Protocol (MCP) Sunucusu:**
  - Otonom ajan sistemleri (Hermes, Hamzad, Claude Desktop, Cursor) için 12 yerel araç sunar.
- **Maliyet ve Kaynak Verimliliği:**
  - %100 açık kaynak ve yerel çalışabilir. Ticari veya ücretli API zorunluluğu yoktur.

---

## 3. Yerel Teknik SEO Yetenekleri

- **İndekslenebilirlik ve Tarama Denetimi:** Meta robots (`noindex`, `nofollow`), `X-Robots-Tag` ve HTTP durum kodları denetimi.
- **Meta Veri Denetimi:** Başlık (`<title>`) ve meta açıklama uzunluklarının arama motoru standartlarına göre değerlendirilmesi.
- **Kanonik Bağlantı Uyumluluğu:** `rel="canonical"` etiketinin hedef URL ile tutarlılığı.
- **Başlık Hiyerarşisi:** H1–H6 yapısı, tek birincil H1 kuralı ve anlamsal sıralama denetimi.
- **Görsel Erişilebilirliği:** Toplam görsel sayısı, Alt metin varlığı ve eksik Alt bildirimleri.
- **Bağlantı Grafiği:** Dahili (Internal) ve harici (External) bağlantıların ayrıştırılması ve sayımı.
- **Yapılandırılmış Veri:** JSON-LD scriptlerinden Schema.org veri türlerinin tam olarak çıkarılması.
- **Sosyal Medya Kartları:** Open Graph ve Twitter Cards etiketlerinin doğrulanması.
- **Uluslararasılaşma:** Hreflang etiketleri ve hedef dil kodlarının ayrıştırılması.
- **Metin / HTML Oranı:** Temiz metin hacminin toplam kod boyutuna oranının kalite göstergesi olarak hesaplanması.
- **Teknik SEO Karnesi:** 0–100 arası ağırlıklı puanlama ve eyleme dönüştürülebilir teşhis önerileri.

---

## 4. Yerel GEO (Üretken Arama Optimizasyonu) Yetenekleri

- **Marka ve Varlık Tespiti (Entity Intelligence):** JSON-LD ve metin gövdesinden Marka, Kuruluş, Kişi ve Ürün varlıklarını çıkarır.
- **Alıntı ve Kaynak Zekası (Citation Intelligence):** Dış kaynak referanslarını, alıntı bloklarını (`blockquote`) ve yazar atıflarını haritalandırır.
- **Soru-Cevap Bilgi Blokları:** SSS şemalarını ve soru başlıklı paragrafları otomatik tespit eder.
- **Anlamsal Parçalama (Semantic Chunking):** Vektör tabanlı RAG indeksleri için karakter ve token tahminli temiz parçalar oluşturur.
- **Yapay Zeka Hazırlık Puanı (AI-Readiness Score):** İçeriğin üretken arama motorları (Perplexity, ChatGPT vb.) tarafından anlaşılabilirlik düzeyini 0–100 arasında puanlar.

---

## 5. Mimari Genel Bakış

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Yapay Zeka Ajanları ve İstemciler               │
│           (Hermes, Hamzad, Claude Desktop, Cursor, REST Clients)       │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │ MCP (Stdio/SSE)                 │ REST API (HTTP)
┌──────────────────▼─────────────────────────────────▼───────────────────┐
│               Molavi Web Intelligence Engine (MWIE) Çekirdeği          │
├────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────┐    ┌────────────────────────────────────┐ │
│ │     Akıllı Yönlendirici   │    │  İstek Kuyruğu ve Robots Yöneticisi │ │
│ └────────────┬─────────────┘    └────────────────────────────────────┘ │
│              │                                                         │
│ ┌────────────▼───────────────────────────────────────────────────────┐ │
│ │                     Birleşik Kazıma Adaptörleri                     │ │
│ │  • Native HTTP Adaptörü    • Playwright Adaptörü  • Firecrawl API   │ │
│ └────────────┬───────────────────────────────────────────────────────┘ │
│              │ Ham HTML                                                │
│ ┌────────────▼───────────────────────────────────────────────────────┐ │
│ │                   İçerik Arındırma ve Ayrıştırma                     │ │
│ │  • Gürültü Filtresi    • HTML Parser      • Markdown Oluşturucu    │ │
│ └────────────┬───────────────────────────────────────────────────────┘ │
│              │ Temiz DOM ve Metin                                      │
│ ┌────────────▼────────────────────────┬──────────────────────────────┐ │
│ │         Teknik SEO Analizcisi        │      GEO ve Varlık Analizcisi│ │
│ │  • Kanonik ve Meta Veriler          │  • Marka Varlıkları Çıkarımı │ │
│ │  • Başlıklar ve Görsel Altları      │  • Kaynak ve Alıntı Haritası │ │
│ │  • JSON-LD Yapılandırılmış Veri     │  • Soru-Cevap Bilgi Blokları │ │
│ │  • 0-100 Ağırlıklı SEO Puanı        │  • Yapay Zeka Hazırlık Puanı │ │
│ └─────────────────────────────────────┴──────────────────────────────┘ │
│                                                                        │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │   TTL Önbellek (Bellek/Redis)   •   SSRF Güvenlik ve İzin Listesi  │ │
│ └────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Kurulum ve Hızlı Başlangıç

### Gereksinimler
- Python 3.10 veya üzeri
- Linux, macOS veya Windows

### Kurulum
```bash
git clone https://github.com/tmolavi/molavi-web-intelligence.git
cd molavi-web-intelligence
python3 -m pip install -e .
```

Geliştirme ve test araçları dahil:
```bash
python3 -m pip install -e ".[dev]"
```

### Python SDK Örneği
```python
import asyncio
from mwie.crawler.engine import crawl_engine
from mwie.core.models import ExtractionOptions


async def main():
    options = ExtractionOptions(render_js=False, extract_seo=True, extract_geo=True)
    result = await crawl_engine.extract_single("https://molavi.pro", options)

    print(f"Sayfa Başlığı: {result.seo.meta_title}")
    print(f"SEO Puanı: {result.seo.seo_score}/100")
    print(f"Yapay Zeka Hazırlığı: {result.geo.ai_readiness_score}/100")
    print(f"Tespit Edilen Varlıklar: {[e.name for e in result.geo.entities]}")


asyncio.run(main())
```

---

## 7. REST API Kullanımı

Sunucuyu başlatın:
```bash
uvicorn mwie.api.app:app --host 0.0.0.0 --port 8000
```
Etkileşimli Swagger belgeleri: `http://localhost:8000/docs`

### Örnek Çağrı: Sayfa Analizi
```bash
curl -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://molavi.pro"}'
```

### Örnek Çağrı: Rakip Sayfaları Karşılaştırma
```bash
curl -X POST http://localhost:8000/api/v1/compare \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://molavi.pro", "https://example.com"]}'
```

---

## 8. Model Context Protocol (MCP) Entegrasyonu

MWIE, yapay zeka ajanları için 12 yerel araç sunar:

| Araç Adı | Açıklama |
| :--- | :--- |
| `crawl_url` | Tek URL için tam çıkarma, SEO ve GEO denetimi |
| `crawl_domain` | Alan adı genelinde özyinelemeli tarama |
| `extract_page_content` | Arındırılmış metin ve Markdown çıkarımı |
| `analyze_seo` | Teknik SEO karnesi ve optimizasyon önerileri |
| `analyze_geo` | Üretken Arama Optimizasyonu ve AI hazırlığı |
| `extract_entities` | Marka, kişi, kurum ve ürün varlıkları çıkarımı |
| `extract_structured_data` | Schema.org JSON-LD şemaları çıkarımı |
| `analyze_sitemap` | Site haritasından (sitemap.xml) URL keşfi |
| `compare_pages` | Rakip sayfaları yan yana SEO/GEO karşılaştırması |
| `batch_process_urls` | Çoklu URL listesini eşzamanlı işleme |
| `get_job_status` | Motor durumu ve önbellek sağlığı |
| `get_extraction_metadata`| Canlı adaptör gecikme ve başarı oranları |

---

## 9. Docker Kurulumu

```bash
docker build -t molavi-web-intelligence .
docker run -p 8000:8000 molavi-web-intelligence
```

Veya Docker Compose ile:
```bash
docker compose up -d
```

---

## 10. Güvenlik ve Sorumlu Tarama

- **SSRF Koruması:** Varsayılan olarak RFC 1918 özel IP adresleri (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) ve localhost engellenir.
- **Robots.txt Uyumu:** Web yöneticilerinin kısıtlamalarına tam uyum sağlanır.
- **Alan Adı İzin Listesi:** Kurumsal ağlarda güvenli hedefler için yapılandırılabilir.

---

## 11. Performans ve Kıyaslama (Benchmark)

Linux ARM64 üzerinde bileşen başına 100 yinelemeli gerçek ölçümler:
- **HTML Ayrıştırma ve Temizleme:** 13.10 ms ortalama gecikme (76.4 işlem/sn, 4.7 MB bellek)
- **Markdown Üretimi:** 2.56 ms ortalama gecikme (390.7 işlem/sn, 2.6 MB bellek)
- **Teknik SEO Analizcisi:** 11.25 ms ortalama gecikme (88.9 işlem/sn, 2.4 MB bellek)
- **GEO ve Varlık Grafiği:** 8.56 ms ortalama gecikme (116.8 işlem/sn, 6.4 MB bellek)

Ayrıntılı rapor için: [docs/BENCHMARKS.md](docs/BENCHMARKS.md)

---

## 12. Lisans ve Telif Hakkı

- **Apache License 2.0** kapsamında yayınlanmıştır. Ayrıntılar: [LICENSE](LICENSE).
- **Taqi Molavi** tarafından bağımsız olarak geliştirilmiştir.
- Üçüncü taraf açık kaynak referansları [CREDITS.md](CREDITS.md) ve [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) dosyalarında listelenmiştir.

---

## 13. Yazar ve Ekosistem

**Yazar:** Taqi Molavi  
**Resmi Web Sitesi:** [https://molavi.pro](https://molavi.pro)  
**Ekosistem Entegrasyonları:** [Hermes Ajanı](integrations/hermes/) | [Hamzad Dijital İkizleri](integrations/hamzad/)
