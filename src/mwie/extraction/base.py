"""
Base Extraction Adapter Interface for MWIE.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel

from mwie.core.models import ExtractionOptions


class RawExtraction(BaseModel):
    url: str
    final_url: str
    status_code: int
    html: str
    headers: dict[str, str] = {}
    rendered_js: bool = False
    adapter_name: str = ""
    execution_time_ms: float = 0.0


class BaseExtractionAdapter(ABC):
    name: str = "base"
    cost_weight: float = 1.0  # Relative cost indicator (1.0 = baseline local http)
    supports_js: bool = False

    @abstractmethod
    async def extract(self, url: str, options: ExtractionOptions) -> RawExtraction:
        """Fetch and extract raw HTML and metadata for the given URL."""

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if adapter dependencies and runtime environment are healthy."""
