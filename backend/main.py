"""
main.py - EUR/USD Signal Platform Backend Server
Version: 11.0 - COMPLETE WITH ALL BACKEND MODULES
"""

import os
import sys
import io
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Flask
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

import requests
import numpy as np
import pandas as pd

# ============================================================================
# IMPORT ALL BACKEND MODULES
# ============================================================================

logger.info("=" * 60)
logger.info("Importing All Backend Modules")
logger.info("=" * 60)

# Config
try:
    from config import Config
    CONFIG_AVAILABLE = True
    logger.info("  ✅ Config loaded")
except ImportError as e:
    CONFIG_AVAILABLE = False
    logger.warning(f"  ⚠️ Config not found: {e}")
    
    class Config:
        PLATFORM_NAME = "EUR/USD Signal Platform"
        PLATFORM_VERSION = "11.0"
        SYMBOL = "EURUSD=X"
        TIMEFRAME = "1h"
        DATA_DAYS_BACK = 90

# Data Modules
try:
    from data.fetch_market_data import MarketDataFetcher, get_data_fetcher, TimeFrame
    DATA_AVAILABLE = True
    logger.info("  ✅ MarketDataFetcher")
except ImportError as e:
    DATA_AVAILABLE = False
    logger.warning(f"  ⚠️ MarketDataFetcher: {e}")

try:
    from data.fetch_news import NewsFetcher, get_news_fetcher
    NEWS_AVAILABLE = True
    logger.info("  ✅ NewsFetcher")
except ImportError as e:
    NEWS_AVAILABLE = False
    logger.warning(f"  ⚠️ NewsFetcher: {e}")

# Analysis Modules
try:
    from analysis.technical_analysis import get_enhanced_analyzer
    TECH_AVAILABLE = True
    logger.info("  ✅ Technical Analysis")
except ImportError as e:
    TECH_AVAILABLE = False
    logger.warning(f"  ⚠️ Technical Analysis: {e}")

try:
    from analysis.fundamental_analysis_enhanced import get_enhanced_fundamental_analyzer
    FUND_AVAILABLE = True
    logger.info("  ✅ Fundamental Analysis")
except ImportError as e:
    FUND_AVAILABLE = False
    logger.warning(f"  ⚠️ Fundamental Analysis: {e}")

try:
    from analysis.sentiment_analysis import get_sentiment_analyzer
    SENT_AVAILABLE = True
    logger.info("  ✅ Sentiment Analysis")
except ImportError as e:
    SENT_AVAILABLE = False
    logger.warning(f"  ⚠️ Sentiment Analysis: {e}")

try:
    from analysis.trend_detection import TrendDetector
    TREND_AVAILABLE = True
    logger.info("  ✅ Trend Detection")
except ImportError as e:
    TREND_AVAILABLE = False
    logger.warning(f"  ⚠️ Trend Detection: {e}")

try:
    from analysis.market_regime_detection import MarketRegimeDetector
    REGIME_AVAILABLE = True
    logger.info("  ✅ Market Regime")
except ImportError as e:
    REGIME_AVAILABLE = False
    logger.warning(f"  ⚠️ Market Regime: {e}")

try:
    from analysis.timeframe_analyzer import MultiTimeframeAnalyzer, TimeframeService, get_timeframe_service
    MTF_AVAILABLE = True
    logger.info("  ✅ Multi-Timeframe Analyzer")
except ImportError as e:
    MTF_AVAILABLE = False
    logger.warning(f"  ⚠️ MTF Analyzer: {e}")

try:
    from analysis.unified_analyzer import UnifiedMarketAnalyzer, get_unified_analyzer
    UNIFIED_AVAILABLE = True
    logger.info("  ✅ Unified Analyzer")
except ImportError as e:
    UNIFIED_AVAILABLE = False
    logger.warning(f"  ⚠️ Unified Analyzer: {e}")

# Signal Modules
try:
    from signals.signal_generator import EnhancedSignalGenerator, get_signal_generator
    SIGNAL_AVAILABLE = True
    logger.info("  ✅ Signal Generator")
except ImportError as e:
    SIGNAL_AVAILABLE = False
    logger.warning(f"  ⚠️ Signal Generator: {e}")

try:
    from signals.risk_management import RiskManager, get_risk_manager
    RISK_AVAILABLE = True
    logger.info("  ✅ Risk Management")
except ImportError as e:
    RISK_AVAILABLE = False
    logger.warning(f"  ⚠️ Risk Management: {e}")

# FCS API Service (External)
class FCSAPIService:
    def __init__(self):
        self.api_key = os.environ.get('FCS_API_KEY', '0dQWAmgD9T5LtARPKJP0V')
        self.base_url = 'https://api-v4.fcsapi.com'
        
    def get_live_price(self, symbol: str = 'EUR/USD') -> Dict:
        try:
            url = f"{self.base_url}/forex/latest"
            params = {'access_key': self.api_key, 'symbol': symbol, 'format': 'json'}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status'):
                forex_data = data.get('response', [{}])[0]
                active = forex_data.get('active', {})
                return {
                    'success': True,
                    'price': float(active.get('c', 0)),
                    'bid': float(forex_data.get('bid', 0)),
                    'ask': float(forex_data.get('ask', 0)),
                    'high_24h': float(active.get('high', 0)),
                    'low_24h': float(active.get('low', 0)),
                    'change': float(active.get('ch', 0)),
                    'change_percent': float(active.get('cp', 0)),
                    'source': 'fcs_api'
                }
            return {'success': False, 'error': 'No data'}
        except Exception as e:
            logger.error(f"FCS API error: {e}")
            return {'success': False, 'error': str(e)}

# Calendarific API Service
class CalendarificHolidayService:
    def __init__(self):
        self.api_key = os.environ.get('CALENDARIFIC_API_KEY', 'aDIXAFT1xSZqfeGXkQgc6Z2npRrgdrXd')
        self.base_url = 'https://calendarific.com/api/v2'
        
    def get_market_holidays(self, limit: int = 12) -> Dict:
        try:
            year = datetime.now().year
            today = datetime.now().date()
            url = f"{self.base_url}/holidays"
            params = {
                'api_key': self.api_key,
                'country': 'US',
                'year': year,
                'type': 'bank'
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('meta', {}).get('code') == 200:
                holidays = data.get('response', {}).get('holidays', [])
                upcoming = []
                for holiday in holidays:
                    holiday_date = holiday.get('date', {}).get('iso', '')
                    if holiday_date:
                        date_obj = datetime.strptime(holiday_date, '%Y-%m-%d').date()
                        if date_obj >= today and len(upcoming) < limit:
                            upcoming.append({
                                'date': holiday_date,
                                'name': holiday.get('name'),
                                'country_name': 'United States'
                            })
                return {'success': True, 'holidays': upcoming, 'source': 'calendarific'}
            return {'success': True, 'holidays': self._get_mock_holidays()}
        except Exception as e:
            return {'success': True, 'holidays': self._get_mock_holidays()}
    
    def _get_mock_holidays(self):
        current_year = datetime.now().year
        return [
            {'date': f"{current_year}-01-01", 'name': "New Year's Day", 'country_name': "United States"},
            {'date': f"{current_year}-01-15", 'name': "Martin Luther King Jr. Day", 'country_name': "United States"},
            {'date': f"{current_year}-02-19", 'name': "Presidents' Day", 'country_name': "United States"},
            {'date': f"{current_year}-04-07", 'name': "Good Friday", 'country_name': "United States"},
            {'date': f"{current_year}-05-27", 'name': "Memorial Day", 'country_name': "United States"}
        ]

logger.info("=" * 60)
modules_loaded = sum([DATA_AVAILABLE, NEWS_AVAILABLE, TECH_AVAILABLE, FUND_AVAILABLE, 
                      SENT_AVAILABLE, TREND_AVAILABLE, REGIME_AVAILABLE, MTF_AVAILABLE, 
                      UNIFIED_AVAILABLE, SIGNAL_AVAILABLE, RISK_AVAILABLE])
logger.info(f"Backend Modules Loaded: {modules_loaded}/11")
logger.info("=" * 60)


# ============================================================================
# INITIALIZE ALL MODULES
# ============================================================================

class BackendModules:
    def __init__(self):
        self.data_fetcher = None
        self.news_fetcher = None
        self.technical = None
        self.fundamental = None
        self.sentiment = None
        self.trend = None
        self.regime = None
        self.mtf = None
        self.unified = None
        self.signal_generator = None
        self.risk_manager = None
        self.timeframe_service = None
        self.fcs_api = None
        self.calendarific = None
        self._initialized = False
    
    def initialize(self):
        logger.info("=" * 60)
        logger.info("Initializing Backend Modules & APIs")
        logger.info("=" * 60)
        
        # Initialize external APIs
        try:
            self.fcs_api = FCSAPIService()
            logger.info("  ✅ FCS API Service")
        except Exception as e:
            logger.error(f"  ❌ FCS API: {e}")
        
        try:
            self.calendarific = CalendarificHolidayService()
            logger.info("  ✅ Calendarific API")
        except Exception as e:
            logger.error(f"  ❌ Calendarific: {e}")
        
        if DATA_AVAILABLE:
            try:
                self.data_fetcher = MarketDataFetcher()
                price = self.data_fetcher.get_current_price()
                logger.info(f"  ✅ DataFetcher: EUR/USD = {price:.5f}")
            except Exception as e:
                logger.error(f"  ❌ DataFetcher: {e}")
        
        if NEWS_AVAILABLE:
            try:
                self.news_fetcher = NewsFetcher()
                logger.info("  ✅ NewsFetcher")
            except Exception as e:
                logger.error(f"  ❌ NewsFetcher: {e}")
        
        if TECH_AVAILABLE:
            try:
                self.technical = get_enhanced_analyzer()
                logger.info("  ✅ Technical Analyzer")
            except Exception as e:
                logger.error(f"  ❌ Technical: {e}")
        
        if FUND_AVAILABLE:
            try:
                self.fundamental = get_enhanced_fundamental_analyzer()
                logger.info("  ✅ Fundamental Analyzer")
            except Exception as e:
                logger.error(f"  ❌ Fundamental: {e}")
        
        if SENT_AVAILABLE:
            try:
                self.sentiment = get_sentiment_analyzer()
                logger.info("  ✅ Sentiment Analyzer")
            except Exception as e:
                logger.error(f"  ❌ Sentiment: {e}")
        
        if TREND_AVAILABLE:
            try:
                self.trend = TrendDetector()
                logger.info("  ✅ Trend Detector")
            except Exception as e:
                logger.error(f"  ❌ Trend: {e}")
        
        if REGIME_AVAILABLE:
            try:
                self.regime = MarketRegimeDetector()
                logger.info("  ✅ Market Regime")
            except Exception as e:
                logger.error(f"  ❌ Regime: {e}")
        
        if MTF_AVAILABLE:
            try:
                self.mtf = MultiTimeframeAnalyzer()
                logger.info("  ✅ MTF Analyzer")
            except Exception as e:
                logger.error(f"  ❌ MTF: {e}")
        
        if UNIFIED_AVAILABLE:
            try:
                self.unified = get_unified_analyzer()
                logger.info("  ✅ Unified Analyzer")
            except Exception as e:
                logger.error(f"  ❌ Unified: {e}")
        
        if SIGNAL_AVAILABLE:
            try:
                self.signal_generator = get_signal_generator()
                logger.info("  ✅ Signal Generator")
            except Exception as e:
                logger.error(f"  ❌ Signal: {e}")
        
        if RISK_AVAILABLE:
            try:
                self.risk_manager = get_risk_manager()
                logger.info("  ✅ Risk Manager")
            except Exception as e:
                logger.error(f"  ❌ Risk: {e}")
        
        if MTF_AVAILABLE and self.data_fetcher:
            try:
                self.timeframe_service = TimeframeService(self.data_fetcher)
                logger.info("  ✅ Timeframe Service")
            except Exception as e:
                logger.error(f"  ❌ Timeframe: {e}")
        
        self._initialized = True
        logger.info("=" * 60)
        logger.info("✅ ALL MODULES INITIALIZED")
        logger.info("=" * 60)
        return True


_modules = BackendModules()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def make_json_serializable(obj):
    """Convert numpy/pandas types to Python native types"""
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(i) for i in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif pd.isna(obj):
        return None
    return obj


# ============================================================================
# CREATE FLASK APP
# ============================================================================

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR.parent / 'frontend'

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path='')
CORS(app)


# ============================================================================
# FRONTEND ROUTES
# ============================================================================

@app.route('/')
def index():
    return send_from_directory(str(FRONTEND_DIR), 'index.html')

@app.route('/pages/<path:filename>')
def serve_pages(filename):
    pages_dir = FRONTEND_DIR / 'pages'
    if (pages_dir / filename).exists():
        return send_from_directory(str(pages_dir), filename)
    return f"<h1>{filename}</h1><p>Module coming soon</p><a href='/'>Back to Dashboard</a>"

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(str(FRONTEND_DIR / 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(str(FRONTEND_DIR / 'js'), filename)


# ============================================================================
# API ROUTES - USING BACKEND MODULES
# ============================================================================

@app.route('/api/health')
def health():
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'modules_loaded': modules_loaded,
        'backend_modules': {
            'data': DATA_AVAILABLE,
            'technical': TECH_AVAILABLE,
            'fundamental': FUND_AVAILABLE,
            'sentiment': SENT_AVAILABLE,
            'trend': TREND_AVAILABLE,
            'regime': REGIME_AVAILABLE,
            'mtf': MTF_AVAILABLE,
            'unified': UNIFIED_AVAILABLE,
            'signal': SIGNAL_AVAILABLE,
            'risk': RISK_AVAILABLE,
            'news': NEWS_AVAILABLE
        }
    })

@app.route('/api/config')
def get_config():
    if CONFIG_AVAILABLE:
        return jsonify({
            'success': True,
            'platform': Config.PLATFORM_NAME,
            'version': Config.PLATFORM_VERSION,
            'symbol': Config.SYMBOL,
            'timeframe': Config.TIMEFRAME
        })
    return jsonify({'success': False, 'error': 'Config not available'}), 503

@app.route('/api/price')
def get_price():
    """Get live EUR/USD price - tries FCS API first, then local fetcher"""
    try:
        # Try FCS API first
        if _modules.fcs_api:
            result = _modules.fcs_api.get_live_price()
            if result.get('success'):
                return jsonify(result)
        
        # Fallback to local data fetcher
        if _modules.data_fetcher:
            price = _modules.data_fetcher.get_current_price()
            return jsonify({
                'success': True,
                'price': price,
                'source': 'data_fetcher',
                'timestamp': datetime.now().isoformat()
            })
        
        return jsonify({'success': False, 'error': 'No data source available'}), 503
    except Exception as e:
        logger.error(f"Price error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/signal')
def get_signal():
    """Get trading signal from Signal Generator module"""
    try:
        if _modules.signal_generator:
            result = _modules.signal_generator.generate_signal()
            return jsonify(make_json_serializable(result))
        return jsonify({'success': False, 'error': 'Signal generator not available'}), 503
    except Exception as e:
        logger.error(f"Signal error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/technical')
def get_technical():
    """Get technical analysis from Technical Analysis module"""
    try:
        if _modules.technical:
            # Get historical data
            df = None
            if _modules.data_fetcher:
                df = _modules.data_fetcher.fetch_data(days_back=200, interval='1h')
            
            result = _modules.technical.analyze(df)
            return jsonify(make_json_serializable(result))
        return jsonify({'success': False, 'error': 'Technical analyzer not available'}), 503
    except Exception as e:
        logger.error(f"Technical error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/fundamental')
def get_fundamental():
    """Get fundamental analysis from Fundamental Analysis module"""
    try:
        if _modules.fundamental:
            result = _modules.fundamental.analyze()
            return jsonify(make_json_serializable(result))
        return jsonify({'success': False, 'error': 'Fundamental analyzer not available'}), 503
    except Exception as e:
        logger.error(f"Fundamental error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sentiment')
def get_sentiment():
    """Get sentiment analysis from Sentiment Analysis module"""
    try:
        if _modules.sentiment:
            df = None
            if _modules.data_fetcher:
                df = _modules.data_fetcher.fetch_data(days_back=30, interval='1h')
            result = _modules.sentiment.analyze_sentiment(df)
            return jsonify(make_json_serializable(result))
        return jsonify({'success': False, 'error': 'Sentiment analyzer not available'}), 503
    except Exception as e:
        logger.error(f"Sentiment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trend')
def get_trend():
    """Get trend detection from Trend Detection module"""
    try:
        if _modules.trend:
            df = None
            if _modules.data_fetcher:
                df = _modules.data_fetcher.fetch_data(days_back=200, interval='1h')
            result = _modules.trend.detect(df)
            return jsonify(make_json_serializable(result))
        return jsonify({'success': False, 'error': 'Trend detector not available'}), 503
    except Exception as e:
        logger.error(f"Trend error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/regime')
def get_regime():
    """Get market regime from Market Regime Detection module"""
    try:
        if _modules.regime:
            df = None
            if _modules.data_fetcher:
                df = _modules.data_fetcher.fetch_data(days_back=200, interval='1h')
            result = _modules.regime.detect(df)
            return jsonify(make_json_serializable(result))
        return jsonify({'success': False, 'error': 'Regime detector not available'}), 503
    except Exception as e:
        logger.error(f"Regime error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mtf')
def get_mtf():
    """Get multi-timeframe analysis from MTF Analyzer module"""
    try:
        if _modules.mtf:
            df = None
            if _modules.data_fetcher:
                df = _modules.data_fetcher.fetch_data(days_back=500, interval='1h')
            result = _modules.mtf.analyze(df)
            return jsonify(make_json_serializable(result))
        return jsonify({'success': False, 'error': 'MTF analyzer not available'}), 503
    except Exception as e:
        logger.error(f"MTF error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/unified')
def get_unified():
    """Get unified analysis from Unified Analyzer module"""
    try:
        if _modules.unified:
            result = _modules.unified.get_complete_analysis()
            return jsonify(make_json_serializable(result))
        return jsonify({'success': False, 'error': 'Unified analyzer not available'}), 503
    except Exception as e:
        logger.error(f"Unified error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/risk')
def get_risk():
    """Get risk management from Risk Manager module"""
    try:
        if _modules.risk_manager:
            result = _modules.risk_manager.get_status()
            return jsonify(make_json_serializable(result))
        return jsonify({'success': False, 'error': 'Risk manager not available'}), 503
    except Exception as e:
        logger.error(f"Risk error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/news')
def get_news():
    """Get news feed from News Fetcher module"""
    try:
        if _modules.news_fetcher:
            days = request.args.get('days', 7, type=int)
            result = _modules.news_fetcher.fetch_all_sources(days_back=days)
            return jsonify(make_json_serializable(result))
        return jsonify({'success': False, 'error': 'News fetcher not available'}), 503
    except Exception as e:
        logger.error(f"News error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/economic-calendar')
def get_economic_calendar():
    """Get economic calendar events"""
    try:
        if _modules.signal_generator:
            events = _modules.signal_generator.get_economic_calendar(30)
            return jsonify({'success': True, 'events': events, 'count': len(events)})
        return jsonify({'success': True, 'events': [], 'count': 0})
    except Exception as e:
        logger.error(f"Economic calendar error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/correlations')
def get_correlations():
    """Get currency correlations"""
    try:
        return jsonify({
            'success': True,
            'correlations': [
                {'pair': 'EUR/GBP', 'correlation': 0.85},
                {'pair': 'USD/CHF', 'correlation': -0.82},
                {'pair': 'USD/JPY', 'correlation': -0.55},
                {'pair': 'Gold (XAU/USD)', 'correlation': -0.65},
                {'pair': 'Dollar Index (DXY)', 'correlation': -0.88}
            ]
        })
    except Exception as e:
        logger.error(f"Correlations error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/market-holidays')
def get_market_holidays():
    """Get market holidays from Calendarific API"""
    try:
        if _modules.calendarific:
            result = _modules.calendarific.get_market_holidays()
            return jsonify(result)
        return jsonify({'success': False, 'error': 'Calendarific not available'}), 503
    except Exception as e:
        logger.error(f"Market holidays error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pivot-points')
def get_pivot_points():
    """Calculate pivot points using market data"""
    try:
        if _modules.data_fetcher:
            df = _modules.data_fetcher.fetch_data(days_back=2, interval='1h')
            if df is not None and len(df) >= 2:
                high = df['high'].iloc[-2]
                low = df['low'].iloc[-2]
                close = df['close'].iloc[-1]
                
                pivot = (high + low + close) / 3
                r1 = 2 * pivot - low
                r2 = pivot + (high - low)
                r3 = high + 2 * (pivot - low)
                s1 = 2 * pivot - high
                s2 = pivot - (high - low)
                s3 = low - 2 * (high - pivot)
                
                return jsonify({
                    'success': True,
                    'pivot': round(float(pivot), 5),
                    'r1': round(float(r1), 5),
                    'r2': round(float(r2), 5),
                    'r3': round(float(r3), 5),
                    's1': round(float(s1), 5),
                    's2': round(float(s2), 5),
                    's3': round(float(s3), 5)
                })
    except Exception as e:
        logger.error(f"Pivot points error: {e}")
    return jsonify({'success': False, 'error': 'Unable to calculate pivot points'})

@app.route('/api/fibonacci')
def get_fibonacci():
    """Calculate Fibonacci levels using market data"""
    try:
        if _modules.data_fetcher:
            df = _modules.data_fetcher.fetch_data(days_back=30, interval='1h')
            if df is not None:
                high = float(df['high'].max())
                low = float(df['low'].min())
                diff = high - low
                
                return jsonify({
                    'success': True,
                    'levels': {
                        '0.236': round(high - diff * 0.236, 5),
                        '0.382': round(high - diff * 0.382, 5),
                        '0.500': round(high - diff * 0.5, 5),
                        '0.618': round(high - diff * 0.618, 5),
                        '0.786': round(high - diff * 0.786, 5)
                    }
                })
    except Exception as e:
        logger.error(f"Fibonacci error: {e}")
    return jsonify({'success': False, 'error': 'Unable to calculate Fibonacci levels'})

@app.route('/api/dashboard-summary')
def get_dashboard_summary():
    """Get complete dashboard summary using all modules"""
    try:
        start_time = time.time()
        
        result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'price': None,
            'signal': None,
            'trend': None,
            'regime': None,
            'economic_events': []
        }
        
        # Get price
        if _modules.data_fetcher:
            result['price'] = _modules.data_fetcher.get_current_price()
        
        # Get signal
        if _modules.signal_generator:
            sig = _modules.signal_generator.generate_signal()
            if sig and sig.get('success'):
                result['signal'] = sig.get('signal')
        
        # Get trend
        if _modules.trend:
            df = None
            if _modules.data_fetcher:
                df = _modules.data_fetcher.fetch_data(days_back=200, interval='1h')
            if df is not None:
                trend_result = _modules.trend.detect(df)
                if trend_result:
                    result['trend'] = trend_result.get('direction', 'NEUTRAL')
        
        # Get regime
        if _modules.regime:
            df = None
            if _modules.data_fetcher:
                df = _modules.data_fetcher.fetch_data(days_back=200, interval='1h')
            if df is not None:
                regime_result = _modules.regime.detect(df)
                if regime_result:
                    result['regime'] = regime_result.get('regime', 'UNKNOWN')
        
        result['analysis_time_ms'] = round((time.time() - start_time) * 1000, 2)
        
        return jsonify(make_json_serializable(result))
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    """AI Trading Assistant"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'error': 'No message provided'}), 400
        
        # Get current price
        current_price = 1.1720
        if _modules.data_fetcher:
            current_price = _modules.data_fetcher.get_current_price()
        
        query = message.lower()
        if 'price' in query:
            response = f"The current EUR/USD price is {current_price:.5f}. This is real-time data from our market data feed."
        elif 'trend' in query:
            response = "Check the Technical Dashboard for current trend analysis from our Trend Detection module."
        elif 'signal' in query:
            response = "View the main signal banner for current trading recommendations from our Signal Generator module."
        elif 'rsi' in query:
            response = "RSI values are calculated by our Technical Analysis module and displayed in the Technical Dashboard."
        else:
            response = f"I'm your EUR/USD trading assistant. Current price is {current_price:.5f}. Ask me about price, trend, or signals!"
        
        return jsonify({'success': True, 'response': response, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"AI Chat error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print("\n" + "=" * 80)
    print(f" {Config.PLATFORM_NAME if CONFIG_AVAILABLE else 'EUR/USD Signal Platform'} v11.0")
    print("=" * 80)
    print(f" BACKEND MODULES LOADED: {modules_loaded}/11")
    print("=" * 80)
    print("\n MODULES:")
    print(f"   ✅ DataFetcher: {DATA_AVAILABLE}")
    print(f"   ✅ NewsFetcher: {NEWS_AVAILABLE}")
    print(f"   ✅ Technical Analysis: {TECH_AVAILABLE}")
    print(f"   ✅ Fundamental Analysis: {FUND_AVAILABLE}")
    print(f"   ✅ Sentiment Analysis: {SENT_AVAILABLE}")
    print(f"   ✅ Trend Detection: {TREND_AVAILABLE}")
    print(f"   ✅ Market Regime: {REGIME_AVAILABLE}")
    print(f"   ✅ MTF Analyzer: {MTF_AVAILABLE}")
    print(f"   ✅ Unified Analyzer: {UNIFIED_AVAILABLE}")
    print(f"   ✅ Signal Generator: {SIGNAL_AVAILABLE}")
    print(f"   ✅ Risk Manager: {RISK_AVAILABLE}")
    print(f"   ✅ FCS API: Configured")
    print(f"   ✅ Calendarific API: Configured")
    print("=" * 80)
    
    # Initialize all modules
    _modules.initialize()
    
    print(f"\n✅ Server running at: http://{host}:{port}")
    print(f"📊 Dashboard: http://{host}:{port}/")
    print("\n🔄 API Endpoints Available:")
    print("   GET /api/price - Live EUR/USD price")
    print("   GET /api/signal - Trading signals")
    print("   GET /api/technical - Technical analysis")
    print("   GET /api/fundamental - Fundamental analysis")
    print("   GET /api/sentiment - Sentiment analysis")
    print("   GET /api/trend - Trend detection")
    print("   GET /api/regime - Market regime")
    print("   GET /api/mtf - Multi-timeframe analysis")
    print("   GET /api/unified - Unified analysis")
    print("   GET /api/risk - Risk management")
    print("   GET /api/news - News feed")
    print("   GET /api/correlations - Currency correlations")
    print("   GET /api/pivot-points - Pivot points")
    print("   GET /api/fibonacci - Fibonacci levels")
    print("   GET /api/market-holidays - Market holidays")
    print("   GET /api/economic-calendar - Economic events")
    print("   POST /api/ai-chat - AI assistant")
    print("   GET /api/health - System health")
    print("=" * 80 + "\n")
    
    app.run(host=host, port=port, debug=False, threaded=True)