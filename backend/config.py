"""
config.py - Configuration Module for EUR/USD Signal Platform
Version: 8.0.0 - Added FCS API & Calendarific API Support
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """
    Configuration class for EUR/USD Signal Platform
    Clean, minimal, and production-ready with ALL API integrations
    """
    
    # ============================================
    # Base Paths
    # ============================================
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    MODELS_DIR = BASE_DIR / 'trained_models'
    LOGS_DIR = BASE_DIR / 'logs'
    CACHE_DIR = BASE_DIR / 'cache'
    NEWS_CACHE_DIR = BASE_DIR / 'news_cache'
    
    # Create directories
    for dir_path in [DATA_DIR, MODELS_DIR, LOGS_DIR, CACHE_DIR, NEWS_CACHE_DIR]:
        dir_path.mkdir(exist_ok=True, parents=True)
    
    # ============================================
    # API Keys (from environment)
    # ============================================
    # Existing APIs
    FRED_API_KEY = os.getenv('FRED_API_KEY', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    GNEWS_API_KEY = os.getenv('GNEWS_API_KEY', '')
    ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', '')
    EXCHANGERATE_API_KEY = os.getenv('EXCHANGERATE_API_KEY', '')
    
    # NEW API Keys
    FCS_API_KEY = os.getenv('FCS_API_KEY', '0dQWAmgD9T5LtARPKJP0V')
    CALENDARIFIC_API_KEY = os.getenv('CALENDARIFIC_API_KEY', 'aDIXAFT1xSZqfeGXkQgc6Z2npRrgdrXd')
    
    # ============================================
    # Platform Settings
    # ============================================
    PLATFORM_NAME = os.getenv('PLATFORM_NAME', 'EUR/USD Signal Platform')
    PLATFORM_VERSION = os.getenv('PLATFORM_VERSION', '8.0.0')
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    TIMEZONE = os.getenv('TIMEZONE', 'UTC')
    
    # ============================================
    # Trading Configuration
    # ============================================
    SYMBOL = os.getenv('SYMBOL', 'EURUSD=X')
    TIMEFRAME = os.getenv('TIMEFRAME', '1h')
    DATA_DAYS_BACK = int(os.getenv('DATA_DAYS_BACK', 90))
    
    # Risk Management
    MAX_RISK_PER_TRADE = float(os.getenv('MAX_RISK_PER_TRADE', 0.02))
    RISK_REWARD_RATIO = float(os.getenv('RISK_REWARD_RATIO', 2.0))
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 1.0))
    MIN_POSITION_SIZE = float(os.getenv('MIN_POSITION_SIZE', 0.01))
    DEFAULT_ACCOUNT_BALANCE = float(os.getenv('DEFAULT_ACCOUNT_BALANCE', 10000))
    MAX_CONCURRENT_POSITIONS = int(os.getenv('MAX_CONCURRENT_POSITIONS', 5))
    
    # ============================================
    # Technical Analysis Settings
    # ============================================
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', 14))
    BB_PERIOD = int(os.getenv('BB_PERIOD', 20))
    BB_STD = float(os.getenv('BB_STD', 2.0))
    MA_FAST = int(os.getenv('MA_FAST', 20))
    MA_SLOW = int(os.getenv('MA_SLOW', 50))
    MA_TREND = int(os.getenv('MA_TREND', 200))
    ATR_PERIOD = int(os.getenv('ATR_PERIOD', 14))
    
    # ============================================
    # Machine Learning Settings
    # ============================================
    ENABLE_ML = os.getenv('ENABLE_ML', 'true').lower() == 'true'
    ML_LOOKBACK_WINDOW = int(os.getenv('ML_LOOKBACK_WINDOW', 50))
    SEQUENCE_LENGTH = int(os.getenv('SEQUENCE_LENGTH', 60))
    FEATURE_COUNT = int(os.getenv('FEATURE_COUNT', 50))
    
    # ============================================
    # Cache Configuration
    # ============================================
    CACHE_DURATION = int(os.getenv('CACHE_DURATION', 60))
    DATA_UPDATE_INTERVAL = int(os.getenv('DATA_UPDATE_INTERVAL', 30))
    
    # ============================================
    # Data Sources
    # ============================================
    PRIMARY_DATA_SOURCE = os.getenv('PRIMARY_DATA_SOURCE', 'fcsapi')  # Changed to fcsapi
    YAHOO_FINANCE_ENABLED = os.getenv('YAHOO_FINANCE_ENABLED', 'true').lower() == 'true'
    ALPHA_VANTAGE_ENABLED = os.getenv('ALPHA_VANTAGE_ENABLED', 'true').lower() == 'true'
    FRANKFURTER_ENABLED = os.getenv('FRANKFURTER_ENABLED', 'true').lower() == 'true'
    FCS_API_ENABLED = os.getenv('FCS_API_ENABLED', 'true').lower() == 'true'
    CALENDARIFIC_ENABLED = os.getenv('CALENDARIFIC_ENABLED', 'true').lower() == 'true'
    
    # ============================================
    # Logging
    # ============================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = LOGS_DIR / os.getenv('LOG_FILE', 'eurusd_platform.log')
    LOG_TO_CONSOLE = os.getenv('LOG_TO_CONSOLE', 'true').lower() == 'true'
    LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'true').lower() == 'true'
    
    # ============================================
    # WebSocket
    # ============================================
    WEBSOCKET_ENABLED = os.getenv('WEBSOCKET_ENABLED', 'true').lower() == 'true'
    WEBSOCKET_UPDATE_INTERVAL = int(os.getenv('WEBSOCKET_UPDATE_INTERVAL', 5))
    
    # ============================================
    # Enhanced Features
    # ============================================
    ENABLE_FIBONACCI = os.getenv('ENABLE_FIBONACCI', 'true').lower() == 'true'
    ENABLE_LIQUIDITY_ANALYSIS = os.getenv('ENABLE_LIQUIDITY_ANALYSIS', 'true').lower() == 'true'
    ENABLE_ORDER_BLOCKS = os.getenv('ENABLE_ORDER_BLOCKS', 'true').lower() == 'true'
    ENABLE_CONFLUENCE = os.getenv('ENABLE_CONFLUENCE', 'true').lower() == 'true'
    ENABLE_MTF_ANALYSIS = os.getenv('ENABLE_MTF_ANALYSIS', 'true').lower() == 'true'
    ENABLE_VOLATILITY_ADAPTIVE = os.getenv('ENABLE_VOLATILITY_ADAPTIVE', 'true').lower() == 'true'
    ENABLE_PERFORMANCE_FEEDBACK = os.getenv('ENABLE_PERFORMANCE_FEEDBACK', 'true').lower() == 'true'
    ENABLE_MARKET_REGIME = os.getenv('ENABLE_MARKET_REGIME', 'true').lower() == 'true'
    
    # ============================================
    # Economic Calendar
    # ============================================
    ECONOMIC_CALENDAR_ENABLED = os.getenv('ECONOMIC_CALENDAR_ENABLED', 'true').lower() == 'true'
    ECONOMIC_CALENDAR_DAYS_AHEAD = int(os.getenv('ECONOMIC_CALENDAR_DAYS_AHEAD', 14))
    
    # ============================================
    # Sentiment Analysis
    # ============================================
    SENTIMENT_UPDATE_INTERVAL = int(os.getenv('SENTIMENT_UPDATE_INTERVAL_MINUTES', 60))
    ENABLE_NLP_SENTIMENT = os.getenv('ENABLE_NLP_SENTIMENT', 'true').lower() == 'true'
    
    # ============================================
    # Market Holidays (Calendarific)
    # ============================================
    MARKET_HOLIDAYS_COUNTRIES = os.getenv('MARKET_HOLIDAYS_COUNTRIES', 'US,GB,JP,DE,CH,AU,CA,FR,IT,ES')
    MARKET_HOLIDAYS_DAYS_AHEAD = int(os.getenv('MARKET_HOLIDAYS_DAYS_AHEAD', 90))
    
    # ============================================
    # Helper Methods
    # ============================================
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Return all configuration as dictionary - for main.py compatibility"""
        return {
            'symbol': cls.SYMBOL,
            'timeframe': cls.TIMEFRAME,
            'data_days_back': cls.DATA_DAYS_BACK,
            'max_risk_per_trade': cls.MAX_RISK_PER_TRADE,
            'risk_reward_ratio': cls.RISK_REWARD_RATIO,
            'max_position_size': cls.MAX_POSITION_SIZE,
            'min_position_size': cls.MIN_POSITION_SIZE,
            'default_account_balance': cls.DEFAULT_ACCOUNT_BALANCE,
            'rsi_period': cls.RSI_PERIOD,
            'bb_period': cls.BB_PERIOD,
            'ma_fast': cls.MA_FAST,
            'ma_slow': cls.MA_SLOW,
            'ma_trend': cls.MA_TREND,
            'sequence_length': cls.SEQUENCE_LENGTH,
            'feature_count': cls.FEATURE_COUNT,
            'cache_duration': cls.CACHE_DURATION,
            'update_interval': cls.DATA_UPDATE_INTERVAL,
            'platform_name': cls.PLATFORM_NAME,
            'platform_version': cls.PLATFORM_VERSION,
            'timezone': cls.TIMEZONE,
            'max_concurrent_positions': cls.MAX_CONCURRENT_POSITIONS,
            'enable_fibonacci': cls.ENABLE_FIBONACCI,
            'enable_liquidity_analysis': cls.ENABLE_LIQUIDITY_ANALYSIS,
            'enable_order_blocks': cls.ENABLE_ORDER_BLOCKS,
            'enable_confluence': cls.ENABLE_CONFLUENCE,
            'enable_mtf_analysis': cls.ENABLE_MTF_ANALYSIS,
            'enable_volatility_adaptive': cls.ENABLE_VOLATILITY_ADAPTIVE,
            'enable_performance_feedback': cls.ENABLE_PERFORMANCE_FEEDBACK,
            'enable_market_regime': cls.ENABLE_MARKET_REGIME,
            'economic_calendar_enabled': cls.ECONOMIC_CALENDAR_ENABLED,
            'sentiment_update_interval': cls.SENTIMENT_UPDATE_INTERVAL,
            'websocket_enabled': cls.WEBSOCKET_ENABLED,
            # New API settings
            'fcs_api_enabled': cls.FCS_API_ENABLED,
            'calendarific_enabled': cls.CALENDARIFIC_ENABLED,
            'primary_data_source': cls.PRIMARY_DATA_SOURCE,
        }
    
    @classmethod
    def get_api_keys_status(cls) -> Dict[str, Any]:
        """Get status of all API keys"""
        return {
            'FRED_API': {
                'configured': bool(cls.FRED_API_KEY),
                'has_value': bool(cls.FRED_API_KEY and len(cls.FRED_API_KEY) > 5),
                'key_preview': cls.FRED_API_KEY[:8] + '...' if cls.FRED_API_KEY else 'Not set'
            },
            'NEWS_API': {
                'configured': bool(cls.NEWS_API_KEY),
                'has_value': bool(cls.NEWS_API_KEY and len(cls.NEWS_API_KEY) > 5),
                'key_preview': cls.NEWS_API_KEY[:8] + '...' if cls.NEWS_API_KEY else 'Not set'
            },
            'GNEWS_API': {
                'configured': bool(cls.GNEWS_API_KEY),
                'has_value': bool(cls.GNEWS_API_KEY and len(cls.GNEWS_API_KEY) > 5),
                'key_preview': cls.GNEWS_API_KEY[:8] + '...' if cls.GNEWS_API_KEY else 'Not set'
            },
            'ALPHA_VANTAGE': {
                'configured': bool(cls.ALPHA_VANTAGE_KEY),
                'has_value': bool(cls.ALPHA_VANTAGE_KEY and len(cls.ALPHA_VANTAGE_KEY) > 5),
                'key_preview': cls.ALPHA_VANTAGE_KEY[:8] + '...' if cls.ALPHA_VANTAGE_KEY else 'Not set'
            },
            'EXCHANGERATE': {
                'configured': bool(cls.EXCHANGERATE_API_KEY),
                'has_value': bool(cls.EXCHANGERATE_API_KEY and len(cls.EXCHANGERATE_API_KEY) > 5),
                'key_preview': cls.EXCHANGERATE_API_KEY[:8] + '...' if cls.EXCHANGERATE_API_KEY else 'Not set'
            },
            'FCS_API': {
                'configured': bool(cls.FCS_API_KEY),
                'has_value': bool(cls.FCS_API_KEY and len(cls.FCS_API_KEY) > 5),
                'key_preview': cls.FCS_API_KEY[:8] + '...' if cls.FCS_API_KEY else 'Not set',
                'enabled': cls.FCS_API_ENABLED
            },
            'CALENDARIFIC': {
                'configured': bool(cls.CALENDARIFIC_API_KEY),
                'has_value': bool(cls.CALENDARIFIC_API_KEY and len(cls.CALENDARIFIC_API_KEY) > 5),
                'key_preview': cls.CALENDARIFIC_API_KEY[:8] + '...' if cls.CALENDARIFIC_API_KEY else 'Not set',
                'enabled': cls.CALENDARIFIC_ENABLED
            }
        }
    
    @classmethod
    def get_risk_settings(cls) -> Dict[str, Any]:
        """Return risk management settings"""
        return {
            'max_risk_per_trade': cls.MAX_RISK_PER_TRADE,
            'risk_reward_ratio': cls.RISK_REWARD_RATIO,
            'max_position_size': cls.MAX_POSITION_SIZE,
            'min_position_size': cls.MIN_POSITION_SIZE,
            'default_account_balance': cls.DEFAULT_ACCOUNT_BALANCE,
            'max_concurrent_positions': cls.MAX_CONCURRENT_POSITIONS,
        }
    
    @classmethod
    def get_technical_settings(cls) -> Dict[str, Any]:
        """Return technical analysis settings"""
        return {
            'rsi_period': cls.RSI_PERIOD,
            'bb_period': cls.BB_PERIOD,
            'bb_std': cls.BB_STD,
            'ma_fast': cls.MA_FAST,
            'ma_slow': cls.MA_SLOW,
            'ma_trend': cls.MA_TREND,
            'atr_period': cls.ATR_PERIOD,
        }
    
    @classmethod
    def get_ml_settings(cls) -> Dict[str, Any]:
        """Return machine learning settings"""
        return {
            'enabled': cls.ENABLE_ML,
            'lookback_window': cls.ML_LOOKBACK_WINDOW,
            'sequence_length': cls.SEQUENCE_LENGTH,
            'feature_count': cls.FEATURE_COUNT,
        }
    
    @classmethod
    def get_enhanced_features(cls) -> Dict[str, Any]:
        """Return enhanced features configuration"""
        return {
            'fibonacci': cls.ENABLE_FIBONACCI,
            'liquidity_analysis': cls.ENABLE_LIQUIDITY_ANALYSIS,
            'order_blocks': cls.ENABLE_ORDER_BLOCKS,
            'confluence_detection': cls.ENABLE_CONFLUENCE,
            'multi_timeframe': cls.ENABLE_MTF_ANALYSIS,
            'volatility_adaptive': cls.ENABLE_VOLATILITY_ADAPTIVE,
            'performance_feedback': cls.ENABLE_PERFORMANCE_FEEDBACK,
            'market_regime': cls.ENABLE_MARKET_REGIME,
        }
    
    @classmethod
    def validate_api_keys(cls) -> Dict[str, bool]:
        """Check which API keys are available"""
        return {
            'FRED_API': bool(cls.FRED_API_KEY and len(cls.FRED_API_KEY) > 5),
            'NEWS_API': bool(cls.NEWS_API_KEY and len(cls.NEWS_API_KEY) > 5),
            'GNEWS_API': bool(cls.GNEWS_API_KEY and len(cls.GNEWS_API_KEY) > 5),
            'ALPHA_VANTAGE': bool(cls.ALPHA_VANTAGE_KEY and len(cls.ALPHA_VANTAGE_KEY) > 5),
            'EXCHANGERATE': bool(cls.EXCHANGERATE_API_KEY and len(cls.EXCHANGERATE_API_KEY) > 5),
            'FCS_API': bool(cls.FCS_API_KEY and len(cls.FCS_API_KEY) > 5),
            'CALENDARIFIC': bool(cls.CALENDARIFIC_API_KEY and len(cls.CALENDARIFIC_API_KEY) > 5),
        }
    
    @classmethod
    def get_available_data_sources(cls) -> List[str]:
        """Return list of available data sources"""
        sources = []
        if cls.YAHOO_FINANCE_ENABLED:
            sources.append('yfinance')
        if cls.ALPHA_VANTAGE_ENABLED and cls.ALPHA_VANTAGE_KEY:
            sources.append('alphavantage')
        if cls.FRANKFURTER_ENABLED:
            sources.append('frankfurter')
        if cls.FCS_API_ENABLED and cls.FCS_API_KEY:
            sources.append('fcsapi')
        return sources
    
    @classmethod
    def display_status(cls) -> Dict[str, Any]:
        """Display configuration status"""
        return {
            'platform': cls.PLATFORM_NAME,
            'version': cls.PLATFORM_VERSION,
            'debug': cls.DEBUG_MODE,
            'symbol': cls.SYMBOL,
            'timeframe': cls.TIMEFRAME,
            'data_source': cls.PRIMARY_DATA_SOURCE,
            'available_sources': cls.get_available_data_sources(),
            'api_keys': cls.validate_api_keys(),
            'api_keys_detailed': cls.get_api_keys_status(),
            'risk_settings': cls.get_risk_settings(),
            'enhanced_features': cls.get_enhanced_features(),
            'directories': {
                'data': str(cls.DATA_DIR),
                'models': str(cls.MODELS_DIR),
                'logs': str(cls.LOGS_DIR),
                'cache': str(cls.CACHE_DIR),
            }
        }


# Create config instance for easy access
config = Config

logger.info(f"✅ Configuration module v{Config.PLATFORM_VERSION} loaded")
logger.info(f"   - FCS API: {'✅' if Config.FCS_API_KEY else '❌'}")
logger.info(f"   - Calendarific API: {'✅' if Config.CALENDARIFIC_API_KEY else '❌'}")
logger.info(f"   - Primary Data Source: {Config.PRIMARY_DATA_SOURCE}")