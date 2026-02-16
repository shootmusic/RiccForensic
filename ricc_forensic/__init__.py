"""
RICC FORENSIC v1.0
Face-to-Identity Intelligence Suite
"""

__version__ = "1.0.0"
__author__ = "RICC"

from .core.face_engine import FaceEngine
from .core.reverse_search import ReverseSearch
from .core.socmed_scraper import SocmedScraper
from .core.geolocation import GeoAnalyzer
from .core.contact_extractor import ContactExtractor
from .core.enhancement import FaceEnhancer
from .core.deepfake_detect import DeepfakeDetector
from .core.report_generator import ReportGenerator

__all__ = [
    'FaceEngine',
    'ReverseSearch',
    'SocmedScraper',
    'GeoAnalyzer',
    'ContactExtractor',
    'FaceEnhancer',
    'DeepfakeDetector',
    'ReportGenerator'
]
