"""
Molavi Web Intelligence Engine (MWIE)
One Engine. Complete Web Intelligence.
Author: Taqi Molavi (https://molavi.pro)
License: Apache-2.0
"""

__version__ = "0.1.0"
__author__ = "Taqi Molavi"
__license__ = "Apache-2.0"

from mwie.citations.citation_evidence_probe import CitationEvidenceProbe
from mwie.engines.multi_engine_probe import MultiEngineProbe
from mwie.telemetry_correlator import TelemetryCorrelator, telemetry_correlator
from mwie.core.models import (
    CitationEvidenceReport,
    CrawlRequest,
    CrawlResult,
    EngineMatrixReport,
    ExtractionResult,
    GEOReport,
    SEOReport,
)

__all__ = [
    "CitationEvidenceProbe",
    "CitationEvidenceReport",
    "CrawlRequest",
    "CrawlResult",
    "EngineMatrixReport",
    "ExtractionResult",
    "GEOReport",
    "MultiEngineProbe",
    "SEOReport",
    "TelemetryCorrelator",
    "telemetry_correlator",
    "__author__",
    "__license__",
    "__version__",
]
