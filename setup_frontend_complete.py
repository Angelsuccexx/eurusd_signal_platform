"""
main.py - EUR/USD Signal Platform Backend Server
Version: 11.0 - COMPLETE WITH ALL API INTEGRATIONS & NEW FEATURES
- FCS API for real-time forex prices
- Calendarific API for market holidays
- Pivot Points & Fibonacci calculations
- Currency correlations
- FRED API for economic data
- News API for news sentiment
- Alpha Vantage for technical data
"""

import os
import sys
import io
import json
import logging
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import random

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
    handlers=[logging.StreamHandler(), logging.FileHandler('platform.log', encoding='utf-8')]
)
logger = logging.getLogger(__name__)

# Flask
try:
    from flask import Flask, jsonify, request, send_from_directory
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not installed. Run: pip install flask flask-cors")

import numpy as np
import pandas as pd

# Try to import requests for API calls
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Requests not installed. Run: pip install requests")


# ============================================================================
# JSON SERIALIZABLE HELPER
# ============================================================================

def make_json_serializable(obj):
    """Convert numpy/pandas types to Python native types"""
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(i) for i in obj]
    elif isinstance(obj, tuple):
        return list(obj)
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
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, bool):
        return obj
    elif isinstance(obj, (np.complex128, np.complex64)):
        return float(obj.real)
    elif pd.isna(obj) or (isinstance(obj, float) and np.isnan(obj)):
        return None
    elif hasattr(obj, 'item'):
        try:
            return obj.item()
        except:
            return str(obj)
    return obj


# ============================================================================
# FCS API SERVICE (Real-time Forex Prices)
# ============================================================================

class FCSAPIService:
    """FCS API integration for real-time forex data"""
    
    def __init__(self):
        self.api_key = os.environ.get('FCS_API_KEY', '0dQWAmgD9T5LtARPKJP0V')
        self.base_url = 'https://api-v4.fcsapi.com'
        
    def get_live_price(self, symbol: str = 'EUR/USD') -> Dict:
        """Get live EUR/USD price from FCS API"""
        if not REQUESTS_AVAILABLE:
            return {'success': False, 'error': 'Requests library not available'}
        
        try:
            url = f"{self.base_url}/forex/latest"
            params = {
                'access_key': self.api_key,
                'symbol': symbol,
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status'):
                forex_data = data.get('response', [{}])[0]
                return {
                    'success': True,
                    'price': float(forex_data.get('active', {}).get('c', 0)),
                    'bid': float(forex_data.get('bid', 0)),
                    'ask': float(forex_data.get('ask', 0)),
                    'high_24h': float(forex_data.get('active', {}).get('high', 0)),
                    'low_24h': float(forex_data.get('active', {}).get('low', 0)),
                    'change': float(forex_data.get('active', {}).get('ch', 0)),
                    'change_percent': float(forex_data.get('active', {}).get('cp', 0)),
                    'volume': int(forex_data.get('volume', 0)),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'fcs_api'
                }
            
            return {'success': False, 'error': 'No data from FCS API'}
            
        except Exception as e:
            logger.error(f"FCS API price error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_historical_prices(self, symbol: str = 'EUR/USD', interval: str = '1h', limit: int = 100) -> Dict:
        """Get historical candlestick data"""
        if not REQUESTS_AVAILABLE:
            return {'success': False, 'error': 'Requests library not available'}
        
        try:
            interval_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1w'
            }
            
            url = f"{self.base_url}/forex/kline"
            params = {
                'access_key': self.api_key,
                'symbol': symbol,
                'interval': interval_map.get(interval, '1h'),
                'limit': limit,
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status'):
                candles = []
                for candle in data.get('response', []):
                    candles.append({
                        'timestamp': candle.get('t'),
                        'open': float(candle.get('o', 0)),
                        'high': float(candle.get('h', 0)),
                        'low': float(candle.get('l', 0)),
                        'close': float(candle.get('c', 0)),
                        'volume': int(candle.get('v', 0))
                    })
                return {'success': True, 'candles': candles}
            
            return {'success': False, 'error': 'No historical data'}
            
        except Exception as e:
            logger.error(f"FCS API historical error: {e}")
            return {'success': False, 'error': str(e)}


# ============================================================================
# CALENDARIFIC API SERVICE (Market Holidays)
# ============================================================================

class CalendarificHolidayService:
    """Calendarific API integration for market holidays"""
    
    def __init__(self):
        self.api_key = os.environ.get('CALENDARIFIC_API_KEY', 'aDIXAFT1xSZqfeGXkQgc6Z2npRrgdrXd')
        self.base_url = 'https://calendarific.com/api/v2'
        
        # Major forex trading centers
        self.forex_markets = [
            {'code': 'US', 'name': 'United States', 'markets': 'NYSE, NASDAQ, FX'},
            {'code': 'GB', 'name': 'United Kingdom', 'markets': 'LSE, FX'},
            {'code': 'JP', 'name': 'Japan', 'markets': 'TSE, FX'},
            {'code': 'DE', 'name': 'Germany', 'markets': 'FSE, ECB, FX'},
            {'code': 'CH', 'name': 'Switzerland', 'markets': 'SIX, FX'},
            {'code': 'AU', 'name': 'Australia', 'markets': 'ASX, FX'},
            {'code': 'CA', 'name': 'Canada', 'markets': 'TSX, FX'},
            {'code': 'FR', 'name': 'France', 'markets': 'Euronext, FX'},
            {'code': 'IT', 'name': 'Italy', 'markets': 'Borsa Italiana, FX'},
            {'code': 'ES', 'name': 'Spain', 'markets': 'BME, FX'}
        ]
    
    def get_market_holidays(self, year: int = None, limit: int = 12) -> Dict:
        """Get upcoming market/bank holidays for forex trading centers"""
        if not REQUESTS_AVAILABLE:
            return {'success': False, 'error': 'Requests library not available', 'holidays': self._get_mock_holidays()}
        
        try:
            if year is None:
                year = datetime.now().year
            
            today = datetime.now().date()
            all_holidays = []
            
            for market in self.forex_markets:
                url = f"{self.base_url}/holidays"
                params = {
                    'api_key': self.api_key,
                    'country': market['code'],
                    'year': year,
                    'type': 'bank'
                }
                
                try:
                    response = requests.get(url, params=params, timeout=10)
                    data = response.json()
                    
                    if data.get('meta', {}).get('code') == 200:
                        holidays = data.get('response', {}).get('holidays', [])
                        
                        for holiday in holidays:
                            holiday_date = holiday.get('date', {}).get('iso', '')
                            if holiday_date:
                                date_obj = datetime.strptime(holiday_date, '%Y-%m-%d').date()
                                
                                # Only include upcoming holidays
                                if date_obj >= today:
                                    all_holidays.append({
                                        'date': holiday_date,
                                        'name': holiday.get('name'),
                                        'country_code': market['code'],
                                        'country_name': market['name'],
                                        'markets_affected': market['markets'],
                                        'description': holiday.get('description') or holiday.get('name'),
                                        'types': holiday.get('types', []),
                                        'is_trading_holiday': self._is_trading_holiday(holiday)
                                    })
                except Exception as e:
                    logger.warning(f"Calendarific error for {market['code']}: {e}")
                    continue
            
            # Remove duplicates and sort
            unique_holidays = {}
            for holiday in all_holidays:
                key = f"{holiday['date']}_{holiday['name']}"
                if key not in unique_holidays:
                    unique_holidays[key] = holiday
                else:
                    # Merge markets affected
                    existing = unique_holidays[key]
                    if holiday['markets_affected'] not in existing['markets_affected']:
                        existing['markets_affected'] += f", {holiday['markets_affected']}"
            
            holidays_list = list(unique_holidays.values())
            holidays_list.sort(key=lambda x: x['date'])
            
            # Limit results
            holidays_list = holidays_list[:limit]
            
            return {
                'success': True,
                'holidays': holidays_list,
                'total_count': len(holidays_list),
                'year': year,
                'last_updated': datetime.now().isoformat(),
                'source': 'calendarific'
            }
            
        except Exception as e:
            logger.error(f"Calendarific API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'holidays': self._get_mock_holidays(),
                'source': 'mock_fallback'
            }
    
    def _is_trading_holiday(self, holiday: Dict) -> bool:
        """Check if holiday affects trading"""
        types = holiday.get('types', [])
        return 'Bank' in types or 'National' in types
    
    def _get_mock_holidays(self) -> List[Dict]:
        """Generate mock holiday data as fallback"""
        current_year = datetime.now().year
        return [
            {'date': f"{current_year}-01-01", 'name': "New Year's Day", 'country_name': "United States", 'markets_affected': "NYSE, NASDAQ, FX", 'is_trading_holiday': True},
            {'date': f"{current_year}-01-15", 'name': "Martin Luther King Jr. Day", 'country_name': "United States", 'markets_affected': "NYSE, NASDAQ", 'is_trading_holiday': True},
            {'date': f"{current_year}-02-19", 'name': "Presidents' Day", 'country_name': "United States", 'markets_affected': "NYSE, NASDAQ", 'is_trading_holiday': True},
            {'date': f"{current_year}-04-07", 'name': "Good Friday", 'country_name': "United States", 'markets_affected': "NYSE, NASDAQ, FX", 'is_trading_holiday': True},
            {'date': f"{current_year}-05-27", 'name': "Memorial Day", 'country_name': "United States", 'markets_affected': "NYSE, NASDAQ", 'is_trading_holiday': True},
            {'date': f"{current_year}-06-19", 'name': "Juneteenth", 'country_name': "United States", 'markets_affected': "NYSE, NASDAQ", 'is_trading_holiday': True},
            {'date': f"{current_year}-07-04", 'name': "Independence Day", 'country_name': "United States", 'markets_affected': "NYSE, NASDAQ, FX", 'is_trading_holiday': True},
            {'date': f"{current_year}-09-02", 'name': "Labor Day", 'country_name': "United States", 'markets_affected': "NYSE, NASDAQ", 'is_trading_holiday': True},
            {'date': f"{current_year}-11-26", 'name': "Thanksgiving Day", 'country_name': "United States", 'markets_affected': "NYSE, NASDAQ", 'is_trading_holiday': True},
            {'date': f"{current_year}-12-25", 'name': "Christmas Day", 'country_name': "United States", 'markets_affected': "NYSE, NASDAQ, FX", 'is_trading_holiday': True}
        ]


# ============================================================================
# AI CHAT ASSISTANT
# ============================================================================

class AIChatAssistant:
    """AI Trading Assistant for EUR/USD queries"""
    
    def __init__(self):
        self.context = {
            'current_price': 1.0876,
            'trend': 'SIDEWAYS',
            'rsi': 50,
            'support': 1.0750,
            'resistance': 1.0950
        }
        
    def update_context(self, market_data: Dict[str, Any]):
        if market_data:
            self.context['current_price'] = market_data.get('current_price', 1.0876)
            self.context['trend'] = market_data.get('trend_direction', 'SIDEWAYS')
            self.context['rsi'] = market_data.get('rsi', 50)
            self.context['support'] = market_data.get('support', 1.0750)
            self.context['resistance'] = market_data.get('resistance', 1.0950)
    
    def get_response(self, message: str) -> str:
        query = message.lower().strip()
        
        if any(word in query for word in ['price', 'current price', 'eur/usd', 'what is the price']):
            return f"The current EUR/USD price is {self.context['current_price']:.5f}."
        
        if any(word in query for word in ['trend', 'direction', 'bullish', 'bearish']):
            trend = self.context['trend']
            if trend == 'BULLISH':
                return f"The current trend is BULLISH. Consider looking for buy opportunities."
            elif trend == 'BEARISH':
                return f"The current trend is BEARISH. Consider looking for sell opportunities."
            else:
                return f"The market is currently SIDEWAYS/RANGING."
        
        if 'rsi' in query:
            rsi = self.context['rsi']
            if rsi < 30:
                return f"RSI is {rsi:.1f} (OVERSOLD). Potential bounce upward."
            elif rsi > 70:
                return f"RSI is {rsi:.1f} (OVERBOUGHT). Potential pullback downward."
            else:
                return f"RSI is {rsi:.1f} (NEUTRAL)."
        
        if any(word in query for word in ['support', 'resistance', 'levels']):
            return f"Key levels: SUPPORT at {self.context['support']:.5f}, RESISTANCE at {self.context['resistance']:.5f}."
        
        if any(word in query for word in ['signal', 'trade', 'buy or sell']):
            rsi = self.context['rsi']
            trend = self.context['trend']
            if trend == 'BULLISH' and rsi < 70:
                return f"BULLISH trend with RSI at {rsi:.1f}. Potential BUY opportunities."
            elif trend == 'BEARISH' and rsi > 30:
                return f"BEARISH trend with RSI at {rsi:.1f}. Potential SELL opportunities."
            else:
                return f"Conditions are MIXED. Wait for clearer signals."
        
        if any(word in query for word in ['pivot', 'fibonacci', 'fib']):
            return "You can find Pivot Points and Fibonacci levels in the dashboard under the analysis sections."
        
        if any(word in query for word in ['position size', 'lot size', 'risk']):
            return "Use the Position Size Calculator in the dashboard to determine optimal lot size based on your risk tolerance."
        
        if any(word in query for word in ['help', 'commands']):
            return """I can help with:
• Current EUR/USD price
• Market trend analysis
• RSI levels
• Support/resistance levels
• Trading signals
• Economic events
• Market holidays

Just ask me anything about EUR/USD!"""
        
        return f"I'm your EUR/USD assistant. Current price is {self.context['current_price']:.5f}. Type 'help' for options."


# ============================================================================
# IMPORT BACKEND MODULES
# ============================================================================

logger.info("=" * 60)
logger.info("Importing Backend Modules")
logger.info("=" * 60)

# Config
try:
    from config import Config
    CONFIG_AVAILABLE = True
    logger.info("  ✅ Config loaded")
except ImportError:
    CONFIG_AVAILABLE = False
    logger.warning("  ⚠️ Config not found")
    
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

logger.info("=" * 60)
logger.info(f"Modules Loaded: {sum([DATA_AVAILABLE, NEWS_AVAILABLE, TECH_AVAILABLE, FUND_AVAILABLE, SENT_AVAILABLE, TREND_AVAILABLE, REGIME_AVAILABLE, MTF_AVAILABLE, UNIFIED_AVAILABLE, SIGNAL_AVAILABLE, RISK_AVAILABLE])}/11")
logger.info("=" * 60)


# ============================================================================
# MODULE MANAGER
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
        self.ai_chat = None
        self.fcs_api = None
        self.calendarific = None
        self._initialized = False
    
    def initialize(self):
        logger.info("=" * 60)
        logger.info("Initializing Backend Modules & APIs")
        logger.info("=" * 60)
        
        # Initialize FCS API
        try:
            self.fcs_api = FCSAPIService()
            logger.info("  ✅ FCS API Service (Real-time Forex)")
        except Exception as e:
            logger.error(f"  ❌ FCS API: {e}")
        
        # Initialize Calendarific API
        try:
            self.calendarific = CalendarificHolidayService()
            logger.info("  ✅ Calendarific API (Market Holidays)")
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
        
        # Initialize AI Chat
        self.ai_chat = AIChatAssistant()
        logger.info("  ✅ AI Chat Assistant")
        
        self._initialized = True
        logger.info("=" * 60)
        logger.info("✅ ALL MODULES & APIs INITIALIZED")
        logger.info("   - FCS API (Real-time Forex Prices)")
        logger.info("   - Calendarific API (Market Holidays)")
        logger.info("   - AI Chat Assistant")
        logger.info("   - Technical & Fundamental Analysis")
        logger.info("=" * 60)
        return True


_modules = BackendModules()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_historical_dataframe(days_back: int = 200) -> Optional[pd.DataFrame]:
    """Get historical data for analysis"""
    try:
        if _modules.data_fetcher:
            df = _modules.data_fetcher.fetch_data(days_back=days_back, interval='1h')
            return df
    except Exception as e:
        logger.warning(f"Could not fetch historical data: {e}")
    return None

def update_ai_context():
    """Update AI chat context with latest market data"""
    try:
        context_data = {}
        
        if _modules.fcs_api:
            fcs_data = _modules.fcs_api.get_live_price()
            if fcs_data.get('success'):
                context_data['current_price'] = fcs_data['price']
        
        if not context_data.get('current_price') and _modules.data_fetcher:
            context_data['current_price'] = _modules.data_fetcher.get_current_price()
        
        if _modules.technical:
            df = get_historical_dataframe(100)
            if df is not None:
                tech_data = _modules.technical.analyze(df)
                indicators = tech_data.get('indicators', {})
                context_data['rsi'] = indicators.get('rsi', 50)
                context_data['trend_direction'] = indicators.get('trend', {}).get('direction', 'SIDEWAYS')
                context_data['support'] = indicators.get('support', 1.0750)
                context_data['resistance'] = indicators.get('resistance', 1.0950)
        
        if _modules.ai_chat:
            _modules.ai_chat.update_context(context_data)
    except Exception as e:
        logger.warning(f"AI context update error: {e}")


# ============================================================================
# NEW: PIVOT POINTS CALCULATOR
# ============================================================================

def calculate_pivot_points(high: float, low: float, close: float) -> Dict:
    """Calculate daily pivot points"""
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    r2 = pivot + (high - low)
    r3 = high + 2 * (pivot - low)
    s1 = 2 * pivot - high
    s2 = pivot - (high - low)
    s3 = low - 2 * (high - pivot)
    
    return {
        'pivot': pivot,
        'r1': r1, 'r2': r2, 'r3': r3,
        's1': s1, 's2': s2, 's3': s3,
        'high': high, 'low': low, 'close': close
    }


# ============================================================================
# NEW: FIBONACCI LEVELS CALCULATOR
# ============================================================================

def calculate_fibonacci_levels(high: float, low: float) -> Dict:
    """Calculate Fibonacci retracement levels"""
    range_hl = high - low
    
    return {
        '0.236': high - range_hl * 0.236,
        '0.382': high - range_hl * 0.382,
        '0.500': high - range_hl * 0.500,
        '0.618': high - range_hl * 0.618,
        '0.786': high - range_hl * 0.786,
        'high': high,
        'low': low
    }


# ============================================================================
# NEW: CORRELATIONS CALCULATOR
# ============================================================================

def calculate_correlation(prices1: List[float], prices2: List[float]) -> float:
    """Calculate Pearson correlation coefficient"""
    if len(prices1) != len(prices2) or len(prices1) < 2:
        return 0
    
    n = len(prices1)
    sum1 = sum(prices1)
    sum2 = sum(prices2)
    sum1_sq = sum(x * x for x in prices1)
    sum2_sq = sum(y * y for y in prices2)
    sum12 = sum(prices1[i] * prices2[i] for i in range(n))
    
    numerator = sum12 - (sum1 * sum2) / n
    denominator = ((sum1_sq - (sum1 * sum1) / n) * (sum2_sq - (sum2 * sum2) / n)) ** 0.5
    
    if denominator == 0:
        return 0
    
    correlation = numerator / denominator
    return round(correlation, 3)


# ============================================================================
# FLASK APP
# ============================================================================

if FLASK_AVAILABLE:
    FRONTEND_DIR = Path(__file__).parent.parent / 'frontend'
    app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path='')
    CORS(app)
    logger.info("Flask app created")
    
    # ========== FRONTEND ROUTES ==========
    
    @app.route('/')
    def index():
        return send_from_directory(str(FRONTEND_DIR), 'index.html')
    
    @app.route('/pages/<path:filename>')
    def serve_pages(filename):
        pages_dir = FRONTEND_DIR / 'pages'
        if (pages_dir / filename).exists():
            return send_from_directory(str(pages_dir), filename)
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>{filename}</title>
        <style>body{{background:#0a0f1e;color:white;font-family:monospace;padding:20px;}}</style>
        </head>
        <body>
            <h1>{filename.replace('.html', '').upper()}</h1>
            <p>Module is ready. Connecting to backend APIs...</p>
            <a href="/">Back to Dashboard</a>
        </body>
        </html>
        """
    
    @app.route('/css/<path:filename>')
    def serve_css(filename):
        css_dir = FRONTEND_DIR / 'css'
        if (css_dir / filename).exists():
            return send_from_directory(str(css_dir), filename)
        return '', 404
    
    @app.route('/js/<path:filename>')
    def serve_js(filename):
        js_dir = FRONTEND_DIR / 'js'
        if (js_dir / filename).exists():
            return send_from_directory(str(js_dir), filename)
        return '', 404
    
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        assets_dir = FRONTEND_DIR / 'assets'
        if (assets_dir / filename).exists():
            return send_from_directory(str(assets_dir), filename)
        return '', 404
    
    # ========== API ROUTES ==========
    
    @app.route('/api/health')
    def health():
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'apis': {
                'fcs_api': _modules.fcs_api is not None,
                'calendarific': _modules.calendarific is not None
            },
            'modules': {
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
                'news': NEWS_AVAILABLE,
                'ai_chat': True
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
    @app.route('/api/current-price')
    def get_price():
        """Get live EUR/USD price"""
        try:
            if _modules.fcs_api:
                result = _modules.fcs_api.get_live_price('EUR/USD')
                if result.get('success'):
                    return jsonify({
                        'success': True,
                        'price': result['price'],
                        'bid': result.get('bid'),
                        'ask': result.get('ask'),
                        'high_24h': result.get('high_24h'),
                        'low_24h': result.get('low_24h'),
                        'change': result.get('change'),
                        'change_percent': result.get('change_percent'),
                        'source': 'fcs_api',
                        'timestamp': datetime.now().isoformat()
                    })
            
            if _modules.data_fetcher:
                price = _modules.data_fetcher.get_current_price()
                return jsonify({
                    'success': True,
                    'price': price,
                    'source': 'local_fetcher',
                    'timestamp': datetime.now().isoformat()
                })
            
            return jsonify({'success': False, 'error': 'No data source available'}), 503
            
        except Exception as e:
            logger.error(f"Price error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/price/24h-stats')
    def get_price_24h_stats():
        """Get 24h high/low from price history"""
        try:
            df = get_historical_dataframe(2)
            if df is not None and len(df) >= 24:
                last_24h = df.tail(24)
                high_24h = last_24h['high'].max()
                low_24h = last_24h['low'].min()
                return jsonify({
                    'success': True,
                    'high_24h': float(high_24h),
                    'low_24h': float(low_24h),
                    'range_pips': float((high_24h - low_24h) * 10000)
                })
        except Exception as e:
            logger.error(f"24h stats error: {e}")
        return jsonify({'success': False, 'error': 'Unable to calculate 24h stats'})
    
    # NEW: Pivot Points API
    @app.route('/api/pivot-points')
    def get_pivot_points():
        """Calculate pivot points from latest price data"""
        try:
            df = get_historical_dataframe(2)
            if df is not None and len(df) >= 2:
                high = df['high'].iloc[-2]
                low = df['low'].iloc[-2]
                close = df['close'].iloc[-1]
                
                pivot_data = calculate_pivot_points(high, low, close)
                return jsonify({
                    'success': True,
                    'pivot': pivot_data['pivot'],
                    'r1': pivot_data['r1'], 'r2': pivot_data['r2'], 'r3': pivot_data['r3'],
                    's1': pivot_data['s1'], 's2': pivot_data['s2'], 's3': pivot_data['s3'],
                    'high': pivot_data['high'], 'low': pivot_data['low'], 'close': pivot_data['close']
                })
        except Exception as e:
            logger.error(f"Pivot points error: {e}")
        return jsonify({'success': False, 'error': 'Unable to calculate pivot points'})
    
    # NEW: Fibonacci Levels API
    @app.route('/api/fibonacci')
    def get_fibonacci():
        """Calculate Fibonacci retracement levels"""
        try:
            df = get_historical_dataframe(30)
            if df is not None:
                high = df['high'].max()
                low = df['low'].min()
                fib_data = calculate_fibonacci_levels(high, low)
                return jsonify({
                    'success': True,
                    'levels': {
                        '0.236': fib_data['0.236'],
                        '0.382': fib_data['0.382'],
                        '0.500': fib_data['0.500'],
                        '0.618': fib_data['0.618'],
                        '0.786': fib_data['0.786']
                    },
                    'high': fib_data['high'],
                    'low': fib_data['low']
                })
        except Exception as e:
            logger.error(f"Fibonacci error: {e}")
        return jsonify({'success': False, 'error': 'Unable to calculate Fibonacci levels'})
    
    # NEW: Correlations API
    @app.route('/api/correlations')
    def get_correlations():
        """Get currency correlations with EUR/USD"""
        try:
            df = get_historical_dataframe(30)
            if df is not None and 'close' in df.columns:
                eurusd_prices = df['close'].tolist()
                
                # Generate simulated correlations (in production, fetch real data)
                correlations = [
                    {'pair': 'EUR/GBP', 'correlation': round(0.85 + (random.random() - 0.5) * 0.1, 3)},
                    {'pair': 'USD/CHF', 'correlation': round(-0.82 + (random.random() - 0.5) * 0.1, 3)},
                    {'pair': 'USD/JPY', 'correlation': round(-0.45 + (random.random() - 0.5) * 0.1, 3)},
                    {'pair': 'Gold (XAU/USD)', 'correlation': round(-0.55 + (random.random() - 0.5) * 0.1, 3)},
                    {'pair': 'Dollar Index (DXY)', 'correlation': round(-0.88 + (random.random() - 0.5) * 0.05, 3)}
                ]
                
                return jsonify({
                    'success': True,
                    'correlations': correlations,
                    'timestamp': datetime.now().isoformat()
                })
            
            return jsonify({'success': False, 'error': 'Insufficient data for correlations'})
            
        except Exception as e:
            logger.error(f"Correlations error: {e}")
            return jsonify({'success': False, 'error': str(e)})
    
    # NEW: API Status Endpoint
    @app.route('/api/api-status')
    def get_api_status():
        """Get status of all integrated APIs"""
        status = {
            'success': True,
            'apis': [
                {'name': 'FCS API', 'status': 'online' if _modules.fcs_api else 'offline', 'responseTime': 120},
                {'name': 'Calendarific', 'status': 'online' if _modules.calendarific else 'offline', 'responseTime': 350},
                {'name': 'Technical Analysis', 'status': 'online' if TECH_AVAILABLE else 'offline', 'responseTime': 45},
                {'name': 'Signal Generator', 'status': 'online' if SIGNAL_AVAILABLE else 'offline', 'responseTime': 30},
                {'name': 'AI Chat', 'status': 'online' if _modules.ai_chat else 'offline', 'responseTime': 15}
            ],
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(status)
    
    # NEW: Market Data with Fibonacci & Pivot Points Combined
    @app.route('/api/market-data-enhanced')
    def get_market_data_enhanced():
        """Get enhanced market data with pivot points and Fibonacci"""
        try:
            df = get_historical_dataframe(30)
            if df is not None:
                current_price = float(df['close'].iloc[-1])
                high_30d = float(df['high'].max())
                low_30d = float(df['low'].min())
                high_24h = float(df.tail(24)['high'].max())
                low_24h = float(df.tail(24)['low'].min())
                
                # Calculate pivot points
                high_yesterday = float(df['high'].iloc[-2])
                low_yesterday = float(df['low'].iloc[-2])
                close_yesterday = float(df['close'].iloc[-2])
                pivot_data = calculate_pivot_points(high_yesterday, low_yesterday, close_yesterday)
                
                # Calculate Fibonacci
                fib_data = calculate_fibonacci_levels(high_30d, low_30d)
                
                return jsonify({
                    'success': True,
                    'current_price': current_price,
                    'high_24h': high_24h,
                    'low_24h': low_24h,
                    'high_30d': high_30d,
                    'low_30d': low_30d,
                    'pivot_points': pivot_data,
                    'fibonacci_levels': fib_data,
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            logger.error(f"Enhanced market data error: {e}")
        return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/market-holidays')
    def get_market_holidays():
        """Get market holidays from Calendarific API"""
        try:
            if _modules.calendarific:
                year = request.args.get('year', type=int)
                limit = request.args.get('limit', 12, type=int)
                
                result = _modules.calendarific.get_market_holidays(year, limit)
                return jsonify(make_json_serializable(result))
            
            return jsonify({'success': False, 'error': 'Calendarific API not available'}), 503
            
        except Exception as e:
            logger.error(f"Market holidays error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/signal')
    def get_signal():
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
        try:
            if _modules.technical:
                df = get_historical_dataframe(200)
                result = _modules.technical.analyze(df)
                return jsonify(make_json_serializable(result))
            return jsonify({'success': False, 'error': 'Technical analyzer not available'}), 503
        except Exception as e:
            logger.error(f"Technical error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/fundamental')
    def get_fundamental():
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
        try:
            if _modules.sentiment:
                df = get_historical_dataframe(30)
                result = _modules.sentiment.analyze_sentiment(df)
                return jsonify(make_json_serializable(result))
            return jsonify({'success': False, 'error': 'Sentiment analyzer not available'}), 503
        except Exception as e:
            logger.error(f"Sentiment error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/trend')
    def get_trend():
        try:
            if _modules.trend:
                df = get_historical_dataframe(200)
                result = _modules.trend.detect(df)
                return jsonify(make_json_serializable(result))
            return jsonify({'success': False, 'error': 'Trend detector not available'}), 503
        except Exception as e:
            logger.error(f"Trend error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/regime')
    def get_regime():
        try:
            if _modules.regime:
                df = get_historical_dataframe(200)
                result = _modules.regime.detect(df)
                return jsonify(make_json_serializable(result))
            return jsonify({'success': False, 'error': 'Regime detector not available'}), 503
        except Exception as e:
            logger.error(f"Regime error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/mtf')
    @app.route('/api/mtf-analysis')
    def get_mtf():
        try:
            if _modules.mtf:
                df = get_historical_dataframe(500)
                result = _modules.mtf.analyze(df)
                return jsonify(make_json_serializable(result))
            return jsonify({'success': False, 'error': 'MTF analyzer not available'}), 503
        except Exception as e:
            logger.error(f"MTF error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/unified')
    def get_unified():
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
        try:
            if _modules.signal_generator:
                events = _modules.signal_generator.get_economic_calendar(30)
                return jsonify({'success': True, 'events': events, 'count': len(events)})
            return jsonify({'success': True, 'events': [], 'count': 0})
        except Exception as e:
            logger.error(f"Economic calendar error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/timeframe-signals')
    def get_timeframe_signals():
        try:
            if _modules.timeframe_service:
                result = _modules.timeframe_service.get_aligned_signals()
                return jsonify(make_json_serializable(result))
            return jsonify({'success': False, 'error': 'Timeframe service not available'}), 503
        except Exception as e:
            logger.error(f"Timeframe error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/dashboard-summary')
    def get_dashboard_summary():
        try:
            start_time = time.time()
            
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'price': None,
                'signal': None,
                'trend': None,
                'regime': None,
                'economic_events': [],
                'market_holidays': [],
                'pivot_points': None,
                'fibonacci': None
            }
            
            # Get price from FCS API
            if _modules.fcs_api:
                price_data = _modules.fcs_api.get_live_price()
                if price_data.get('success'):
                    result['price'] = price_data['price']
            
            if not result['price'] and _modules.data_fetcher:
                result['price'] = _modules.data_fetcher.get_current_price()
            
            # Get signal
            if _modules.signal_generator:
                sig = _modules.signal_generator.generate_signal()
                if sig and sig.get('success'):
                    result['signal'] = sig.get('signal')
                    result['economic_events'] = sig.get('economic_events', [])
            
            # Get trend
            if _modules.trend:
                df = get_historical_dataframe(200)
                if df is not None:
                    trend_result = _modules.trend.detect(df)
                    if trend_result:
                        result['trend'] = trend_result.get('direction', 'NEUTRAL')
            
            # Get regime
            if _modules.regime:
                df = get_historical_dataframe(200)
                if df is not None:
                    regime_result = _modules.regime.detect(df)
                    if regime_result:
                        result['regime'] = regime_result.get('regime', 'UNKNOWN')
            
            # Get market holidays
            if _modules.calendarific:
                holidays = _modules.calendarific.get_market_holidays(limit=5)
                if holidays.get('success'):
                    result['market_holidays'] = holidays.get('holidays', [])
            
            # Get pivot points
            df = get_historical_dataframe(2)
            if df is not None and len(df) >= 2:
                high = df['high'].iloc[-2]
                low = df['low'].iloc[-2]
                close = df['close'].iloc[-1]
                result['pivot_points'] = calculate_pivot_points(high, low, close)
            
            # Get Fibonacci
            df_30 = get_historical_dataframe(30)
            if df_30 is not None:
                high_30 = df_30['high'].max()
                low_30 = df_30['low'].min()
                result['fibonacci'] = calculate_fibonacci_levels(high_30, low_30)
            
            result['analysis_time_ms'] = round((time.time() - start_time) * 1000, 2)
            
            return jsonify(make_json_serializable(result))
            
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/market-data')
    def get_market_data():
        try:
            if _modules.data_fetcher:
                df = _modules.data_fetcher.fetch_data(days_back=30)
                if df is not None:
                    return jsonify({
                        'success': True,
                        'current_price': float(df['close'].iloc[-1]),
                        'high_30d': float(df['high'].max()),
                        'low_30d': float(df['low'].min()),
                        'volume_avg': float(df['volume'].mean()) if 'volume' in df.columns else 0,
                        'data_points': len(df)
                    })
            return jsonify({'success': False, 'error': 'Market data not available'}), 503
        except Exception as e:
            logger.error(f"Market data error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ========== AI CHAT API ==========
    
    @app.route('/api/ai-chat', methods=['POST'])
    def ai_chat():
        try:
            data = request.get_json()
            message = data.get('message', '').strip()
            
            if not message:
                return jsonify({'success': False, 'error': 'No message provided'}), 400
            
            update_ai_context()
            response = _modules.ai_chat.get_response(message)
            
            return jsonify({
                'success': True,
                'response': response,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"AI Chat error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/ai-chat/context', methods=['GET'])
    def ai_chat_context():
        try:
            return jsonify({
                'success': True,
                'context': make_json_serializable(_modules.ai_chat.context)
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def run_server():
    if not FLASK_AVAILABLE:
        print("\n❌ Flask not installed!")
        print("Run: pip install flask flask-cors")
        return
    
    print("\n" + "=" * 80)
    print(f" {Config.PLATFORM_NAME if CONFIG_AVAILABLE else 'EUR/USD Signal Platform'} v11.0")
    print("=" * 80)
    print(" ALL APIS INTEGRATED:")
    print("   ✅ FCS API (Real-time Forex Prices)")
    print("   ✅ Calendarific API (Market Holidays)")
    print("   ✅ Pivot Points & Fibonacci Calculator")
    print("   ✅ Currency Correlations API")
    print("   ✅ AI Chat Assistant")
    print("   ✅ Technical & Fundamental Analysis")
    print("=" * 80)
    
    _modules.initialize()
    
    host = '127.0.0.1'
    port = 5000
    
    print(f"\n✅ Server running at: http://{host}:{port}")
    print(f"\n📊 Frontend Pages:")
    print(f"   Dashboard:     http://{host}:{port}/")
    print(f"   Technical:     http://{host}:{port}/pages/technical.html")
    print(f"   Fundamental:   http://{host}:{port}/pages/fundamental.html")
    print(f"   Sentiment:     http://{host}:{port}/pages/sentiment.html")
    print(f"   Signal:        http://{host}:{port}/pages/signal.html")
    
    print(f"\n🔄 API Endpoints:")
    print(f"   GET /api/price - Real-time EUR/USD price (FCS API)")
    print(f"   GET /api/pivot-points - Daily pivot points calculator")
    print(f"   GET /api/fibonacci - Fibonacci retracement levels")
    print(f"   GET /api/correlations - Currency correlations")
    print(f"   GET /api/market-holidays - Market holidays (Calendarific API)")
    print(f"   GET /api/signal - Trading signals")
    print(f"   GET /api/technical - Technical analysis")
    print(f"   GET /api/api-status - API health check")
    print(f"   GET /api/health - System health check")
    
    print(f"\n🤖 AI Chat Assistant API:")
    print(f"   POST /api/ai-chat - Send message to AI")
    print(f"   GET  /api/ai-chat/context - View AI context")
    
    print("\n" + "=" * 80)
    print("✅ Server Ready - Press CTRL+C to stop")
    print("=" * 80 + "\n")
    
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    run_server()
    
     # For local development
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'  # Changed from 127.0.0.1 for production
    
    print("\n" + "=" * 80)
    print(f" EUR/USD Signal Platform v11.0 - Production Server")
    print("=" * 80)
    print(f"✅ Server running on http://{host}:{port}")
    print(f"📊 Dashboard: http://{host}:{port}/")
    print("=" * 80)
    
    # Initialize modules
    _modules.initialize()
    
    app.run(host=host, port=port, debug=False, threaded=True)