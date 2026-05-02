# backend/__init__.py
"""
EUR/USD Signal Platform - Backend Package
"""

import os
import sys
import logging
from pathlib import Path

# Initialize __all__ as an empty list first
__all__ = []

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Package metadata
__version__ = "2.0.0"
__author__ = "EUR/USD Signal Platform"
__description__ = "Professional EUR/USD Trading Signal Platform with AI"

# ============================================================================
# PATH CONFIGURATION
# ============================================================================

BACKEND_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
MODELS_DIR = PROJECT_ROOT / "trained_models"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create necessary directories
for dir_path in [MODELS_DIR, DATA_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Add to sys.path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

logger.info(f"Project root: {PROJECT_ROOT}")
logger.info(f"Backend directory: {BACKEND_DIR}")

# ============================================================================
# EXPORT ALL MODULES
# ============================================================================

# 1. Core Configuration
try:
    from backend.config import Config
    __all__.append('Config')
    logger.info("✓ Config module loaded")
except ImportError as e:
    logger.warning(f"Config module not available: {e}")

# 2. Data Modules
try:
    from backend.data.fetch_market_data import MarketDataFetcher, TimeFrame, get_data_fetcher
    __all__.extend(['MarketDataFetcher', 'TimeFrame', 'get_data_fetcher'])
    logger.info("✓ MarketDataFetcher module loaded")
except ImportError as e:
    logger.warning(f"MarketDataFetcher not available: {e}")

try:
    from backend.data.data_preprocessor import DataPreprocessor
    __all__.append('DataPreprocessor')
    logger.info("✓ DataPreprocessor module loaded")
except ImportError as e:
    logger.warning(f"DataPreprocessor not available: {e}")

# 3. Analysis Modules
try:
    from backend.analysis.technical_analysis import TechnicalAnalyzer
    __all__.append('TechnicalAnalyzer')
    logger.info("✓ TechnicalAnalyzer module loaded")
except ImportError as e:
    logger.warning(f"TechnicalAnalyzer not available: {e}")

try:
    from backend.analysis.fundamental_analysis import FundamentalAnalyzer
    __all__.append('FundamentalAnalyzer')
    logger.info("✓ FundamentalAnalyzer module loaded")
except ImportError as e:
    logger.warning(f"FundamentalAnalyzer not available: {e}")

try:
    from backend.analysis.sentiment_analysis import SentimentAnalyzer
    __all__.append('SentimentAnalyzer')
    logger.info("✓ SentimentAnalyzer module loaded")
except ImportError as e:
    logger.warning(f"SentimentAnalyzer not available: {e}")

try:
    from backend.analysis.market_regime_detection import MarketRegimeDetector
    __all__.append('MarketRegimeDetector')
    logger.info("✓ MarketRegimeDetector module loaded")
except ImportError as e:
    logger.warning(f"MarketRegimeDetector not available: {e}")

# 4. Signal Modules
try:
    from backend.signals.signal_generator import SignalGenerator, SignalType
    __all__.extend(['SignalGenerator', 'SignalType'])
    logger.info("✓ SignalGenerator module loaded")
except ImportError as e:
    logger.warning(f"SignalGenerator not available: {e}")

try:
    from backend.signals.risk_management import RiskManager
    __all__.append('RiskManager')
    logger.info("✓ RiskManager module loaded")
except ImportError as e:
    logger.warning(f"RiskManager not available: {e}")

# 5. AI Model Modules
try:
    from backend.ai_model.price_predictor import PricePredictor, get_price_predictor
    __all__.extend(['PricePredictor', 'get_price_predictor'])
    logger.info("✓ PricePredictor module loaded")
except ImportError as e:
    logger.warning(f"PricePredictor not available: {e}")

try:
    from backend.ai_model.machine_learning import MLModelManager
    __all__.append('MLModelManager')
    logger.info("✓ MLModelManager module loaded")
except ImportError as e:
    logger.warning(f"MLModelManager not available: {e}")

try:
    from backend.ai_model.backtesting import Backtester, OrderSide
    __all__.extend(['Backtester', 'OrderSide'])
    logger.info("✓ Backtester module loaded")
except ImportError as e:
    logger.warning(f"Backtester not available: {e}")

# 6. Services
try:
    from backend.economic_calendar.calendar_manager import EconomicCalendarManager, get_calendar_manager
    __all__.extend(['EconomicCalendarManager', 'get_calendar_manager'])
    logger.info("✓ CalendarManager module loaded")
except ImportError as e:
    logger.warning(f"CalendarManager not available: {e}")

# ============================================================================
# PLATFORM CLASS
# ============================================================================

class EURUSDPlatform:
    """Main Platform Class"""
    
    def __init__(self, config=None):
        self.config = config
        self.start_time = None
        self.components = {}
        self._initialized = False
    
    def initialize(self):
        """Initialize platform components"""
        if self._initialized:
            return True
        
        try:
            from datetime import datetime
            self.start_time = datetime.now()
            
            # Initialize data fetcher
            try:
                from backend.data.fetch_market_data import get_data_fetcher
                self.components['data_fetcher'] = get_data_fetcher()
            except Exception as e:
                logger.warning(f"Data fetcher init failed: {e}")
            
            self._initialized = True
            logger.info("✅ Platform initialized")
            return True
            
        except Exception as e:
            logger.error(f"Platform init failed: {e}")
            return False
    
    def get_status(self):
        """Get platform status"""
        return {
            'initialized': self._initialized,
            'components': {k: v is not None for k, v in self.components.items()},
            'version': __version__
        }

# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_platform(config=None):
    """Create and initialize platform"""
    platform = EURUSDPlatform(config)
    platform.initialize()
    return platform

def get_platform():
    """Get or create platform singleton"""
    global _platform
    if '_platform' not in globals():
        _platform = create_platform()
    return _platform

# ============================================================================
# VERSION INFO
# ============================================================================

def get_version():
    """Get package version"""
    return __version__

def get_info():
    """Get package information"""
    return {
        'name': __name__,
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'modules': __all__
    }

logger.info(f"✅ Backend package v{__version__} loaded with {len(__all__)} modules")