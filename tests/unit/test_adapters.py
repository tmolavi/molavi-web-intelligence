import pytest

from mwie.core.models import ExtractionOptions
from mwie.core.router import ExtractionRouter
from mwie.extraction.registry import AdapterRegistry


def test_adapter_registry_and_telemetry():
    reg = AdapterRegistry()
    assert "native_http" in reg.list_adapters()

    reg.record_success("native_http", 120.0)
    reg.record_success("native_http", 180.0)
    stats = reg.get_stats()

    http_stat = next(s for s in stats if s.name == "native_http")
    assert http_stat.success_count == 2
    assert http_stat.avg_latency_ms == 150.0
    assert http_stat.success_rate == 1.0


@pytest.mark.asyncio
async def test_router_selection():
    reg = AdapterRegistry()
    r = ExtractionRouter(adapter_registry=reg)

    options_default = ExtractionOptions(render_js=False)
    adapter = await r.select_adapter(options_default)
    assert adapter.name == "native_http"

    options_override = ExtractionOptions(preferred_adapter="native_http")
    adapter_over = await r.select_adapter(options_override)
    assert adapter_over.name == "native_http"
