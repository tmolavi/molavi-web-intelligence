"""
Molavi Web Intelligence Engine (MWIE)
One Engine. Complete Web Intelligence.
Author: Taqi Molavi (https://molavi.pro)
License: Apache-2.0
"""

__version__ = "0.1.0"
__author__ = "Taqi Molavi"
__license__ = "Apache-2.0"

from mwie.core.models import (
    CrawlRequest,
    CrawlResult,
    ExtractionResult,
    GEOReport,
    SEOReport,
)

__all__ = [
    "CrawlRequest",
    "CrawlResult",
    "ExtractionResult",
    "GEOReport",
    "SEOReport",
    "__author__",
    "__license__",
    "__version__",
]
