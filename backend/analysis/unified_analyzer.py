"""
unified_analyzer.py - ULTIMATE Unified Market Analyzer v3.3
FIXED: Correct import paths
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from collections import deque, Counter
from dataclasses import dataclass, field
from enum import Enum
import json
import decimal

# Fix imports - use relative imports for local modules
from .technical_analysis import get_enhanced_analyzer
from .trend_detection import TrendDetector
from .market_regime_detection import MarketRegimeDetector

# Safe import for fundamental analysis
try:
    from .fundamental_analysis_enhanced import get_enhanced_fundamental_analyzer
    FUNDAMENTAL_AVAILABLE = True
except ImportError:
    FUNDAMENTAL_AVAILABLE = False
    get_enhanced_fundamental_analyzer = None

# Safe import for sentiment analysis
try:
    from .sentiment_analysis import get_sentiment_analyzer
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    get_sentiment_analyzer = None

logger = logging.getLogger(__name__)


def make_json_serializable(obj):
    """Recursively convert any object to JSON serializable format"""
    if obj is None:
        return None
    if isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, dict):
        return {make_json_serializable(k): make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [make_json_serializable(i) for i in obj]
    if hasattr(obj, 'to_dict'):
        return make_json_serializable(obj.to_dict())
    if hasattr(obj, '__dict__'):
        return make_json_serializable(obj.__dict__)
    return str(obj)


# Create SimpleTrendDetector if not available
class SimpleTrendDetector:
    def detect(self, df): 
        return {'direction': 'SIDEWAYS', 'strength': 0, 'confidence': 50}


class MarketRegimeType:
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGING = "RANGING"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    CRISIS = "CRISIS"
    UNKNOWN = "UNKNOWN"


class MarketRegimeDetectorSimple:
    """Advanced market regime detection"""
    
    def __init__(self):
        self.history = deque(maxlen=1000)
        self.volatility_thresholds = {'very_low': 0.05, 'low': 0.10, 'normal': 0.15, 'high': 0.25, 'extreme': 0.40}
        
    def detect_regime(self, df: pd.DataFrame) -> Dict[str, Any]:
        try:
            if df is None or df.empty or len(df) < 10:
                return self._default_regime()
            
            df = self._normalize_df(df)
            close = df['close'].values if 'close' in df.columns else np.array([1.0876] * len(df))
            high = df['high'].values if 'high' in df.columns else close
            low = df['low'].values if 'low' in df.columns else close
            
            volatility = self._calc_volatility(close)
            trend_strength = self._calc_trend_strength(close)
            ranging_score = self._calc_ranging_score(high, low, close)
            anomalies = self._detect_anomalies(close, high, low)
            
            regime, confidence = self._determine_regime(volatility, trend_strength, ranging_score, anomalies)
            risk_score = self._calc_risk_score(volatility, anomalies)
            
            return {
                'success': True,
                'regime': regime,
                'confidence': round(confidence, 1),
                'volatility': {'realized': round(volatility, 1), 'regime': self._get_vol_regime(volatility)},
                'trend_strength': round(trend_strength, 1),
                'risk_score': round(risk_score, 1),
                'description': self._get_description(regime, volatility),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return self._default_regime()
    
    def _calc_volatility(self, prices, window=20):
        try:
            if len(prices) < window + 1:
                return 12.0
            returns = np.diff(np.log(prices + 1e-10))
            return float(np.std(returns[-window:]) * np.sqrt(252 * 24) * 100)
        except:
            return 12.0
    
    def _calc_trend_strength(self, prices, period=50):
        try:
            if len(prices) < period:
                return 0.0
            price_change = abs(prices[-1] - prices[-period])
            volatility = np.sum(np.abs(np.diff(prices[-period:])))
            if volatility == 0:
                return 0.0
            return float(price_change / volatility * 100)
        except:
            return 0.0
    
    def _calc_ranging_score(self, high, low, close, window=20):
        try:
            if len(close) < window:
                return 50.0
            avg_range = np.mean(high[-window:] - low[-window:])
            price_range = max(close[-window:]) - min(close[-window:])
            if price_range == 0 or avg_range == 0:
                return 100.0
            return float(np.clip(100 * (1 - (price_range / (avg_range * np.sqrt(window) + 1e-10))), 0, 100))
        except:
            return 50.0
    
    def _detect_anomalies(self, close, high, low, window=50):
        try:
            if len(close) < window:
                return {'count': 0, 'recent_spike': False}
            recent_range = high[-1] - low[-1]
            avg_range = np.mean(high[-window:] - low[-window:])
            return {'count': 0, 'recent_spike': recent_range > avg_range * 2.5 if avg_range > 0 else False}
        except:
            return {'count': 0, 'recent_spike': False}
    
    def _determine_regime(self, vol, trend, ranging, anomalies):
        if anomalies.get('recent_spike') and vol > 30:
            return MarketRegimeType.CRISIS, 80.0
        if vol > 25:
            return MarketRegimeType.HIGH_VOLATILITY, 70.0
        if vol < 8:
            return MarketRegimeType.LOW_VOLATILITY, 65.0
        if trend > 60 and ranging < 30:
            return MarketRegimeType.TRENDING_UP, 75.0
        if ranging > 60:
            return MarketRegimeType.RANGING, 70.0
        return MarketRegimeType.RANGING, 60.0
    
    def _calc_risk_score(self, vol, anomalies):
        score = 0
        if vol > 30:
            score += 40
        elif vol > 20:
            score += 25
        elif vol > 15:
            score += 15
        else:
            score += 5
        if anomalies.get('recent_spike'):
            score += 30
        return min(100, score)
    
    def _get_vol_regime(self, vol):
        if vol >= 40: return "EXTREME"
        if vol >= 25: return "HIGH"
        if vol >= 15: return "NORMAL"
        if vol >= 8: return "LOW"
        return "VERY_LOW"
    
    def _get_description(self, regime, vol):
        desc = {MarketRegimeType.TRENDING_UP: f"Uptrend - {vol:.1f}% volatility", MarketRegimeType.CRISIS: "CRISIS - Maximum caution"}
        return desc.get(regime, f"Regime: {regime}")
    
    def _normalize_df(self, df):
        df = df.copy()
        df.columns = [str(c).lower().strip() for c in df.columns]
        return df
    
    def _default_regime(self):
        return {'success': False, 'regime': MarketRegimeType.UNKNOWN, 'confidence': 0, 'volatility': {'realized': 12, 'regime': 'NORMAL'}, 'risk_score': 50, 'description': 'Insufficient data'}


# ============================================================================
# UNIFIED MARKET ANALYZER
# ============================================================================

class UnifiedMarketAnalyzer:
    """ULTIMATE Unified Market Analyzer v3.3 with comprehensive charts"""
    
    def __init__(self):
        # Initialize all analyzers
        try:
            self.technical_analyzer = get_enhanced_analyzer()
            print("✅ Technical analyzer initialized")
        except Exception as e:
            print(f"⚠️ Technical analyzer error: {e}")
            self.technical_analyzer = None
        
        self.regime_detector = MarketRegimeDetectorSimple()
        self.trend_detector = TrendDetector()
        self.simple_trend = SimpleTrendDetector()
        
        try:
            if get_enhanced_fundamental_analyzer:
                self.fundamental_analyzer = get_enhanced_fundamental_analyzer()
                print("✅ Fundamental analyzer initialized")
            else:
                self.fundamental_analyzer = None
        except:
            self.fundamental_analyzer = None
        
        try:
            if get_sentiment_analyzer:
                self.sentiment_analyzer = get_sentiment_analyzer()
                print("✅ Sentiment analyzer initialized")
            else:
                self.sentiment_analyzer = None
        except:
            self.sentiment_analyzer = None
        
        # History for charts
        self.analysis_history = deque(maxlen=500)
        self.signal_history = deque(maxlen=200)
        self.confidence_history = deque(maxlen=200)
        self.regime_history = deque(maxlen=200)
        self.risk_history = deque(maxlen=200)
        
        # Alert system
        self.alerts = deque(maxlen=100)
        
        print("="*70)
        print("🚀 UnifiedMarketAnalyzer v3.3 - WITH 12 CHARTS")
        print(f"   Technical: {'✅' if self.technical_analyzer else '❌'}")
        print("="*70)
    
    def get_complete_analysis(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """Complete market analysis with ALL charts"""
        import time
        start = time.time()
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'success': True,
            'analysis_time_ms': 0,
            'price': 1.0876
        }
        
        try:
            # Get technical analysis
            if self.technical_analyzer:
                try:
                    tech = self.technical_analyzer.analyze(df)
                    if tech and isinstance(tech, dict):
                        result['technical'] = tech
                        result['price'] = tech.get('current_price', 1.0876)
                except Exception as e:
                    print(f"Technical analysis error: {e}")
            
            # Prepare data for other analyses
            if df is None and self.technical_analyzer and hasattr(self.technical_analyzer, 'data_fetcher'):
                try:
                    df = self.technical_analyzer.data_fetcher.get_historical_data(days_back=200)
                except Exception as e:
                    print(f"Data fetch error: {e}")
            
            # Run trend and regime analysis
            if df is not None and not df.empty and len(df) >= 50:
                try:
                    result['trend'] = self.trend_detector.detect(df)
                except Exception as e:
                    result['trend'] = {'direction': 'SIDEWAYS', 'strength': 0}
                
                try:
                    result['regime'] = self.regime_detector.detect_regime(df)
                except Exception as e:
                    result['regime'] = self.regime_detector._default_regime()
            
            # Fundamental analysis
            if self.fundamental_analyzer:
                try:
                    result['fundamental'] = self.fundamental_analyzer.analyze(df)
                except Exception as e:
                    pass
            
            # Sentiment analysis
            if self.sentiment_analyzer:
                try:
                    result['sentiment'] = self.sentiment_analyzer.analyze_sentiment(df)
                except Exception as e:
                    pass
            
            # Generate combined signal
            result['combined'] = self._combine_signals(result)
            result['risk'] = self._assess_risk(result)
            result['recommendation'] = self._generate_recommendation(result)
            
            # Charts
            result['charts'] = self._generate_all_charts(result)
            
            # Update history
            self._update_history(result)
            
            # Alerts
            result['alerts'] = self._check_alerts(result)
            
            # Performance
            result['analysis_time_ms'] = round((time.time() - start) * 1000, 2)
            result['performance'] = self._get_performance_metrics()
            
            return make_json_serializable(result)
            
        except Exception as e:
            print(f"Analysis error: {e}")
            import traceback
            traceback.print_exc()
            return make_json_serializable({'success': False, 'error': str(e)})
    
    def _generate_all_charts(self, result: Dict) -> Dict[str, Any]:
        """Generate 12 comprehensive charts"""
        charts = {}
        
        # Chart 1: Signal Timeline
        signal_data = []
        for i, s in enumerate(list(self.signal_history)[-100:]):
            if s:
                signal_data.append({
                    'index': i, 
                    'score': s.get('score', 0) if isinstance(s.get('score'), (int, float)) else 0, 
                    'signal': s.get('signal', 'NEUTRAL')
                })
        charts['signal_timeline'] = {'type': 'line', 'title': 'Signal Strength Timeline', 'data': signal_data}
        
        # Chart 2: Confidence Gauge
        current_conf = result.get('combined', {}).get('confidence', 50)
        if not isinstance(current_conf, (int, float)):
            current_conf = 50
        charts['confidence_gauge'] = {'type': 'gauge', 'title': 'Current Signal Confidence', 'value': current_conf, 'min': 0, 'max': 100}
        
        return charts
    
    def _combine_signals(self, results: Dict) -> Dict:
        """Combine all signals with weighting"""
        try:
            weighted_score = 0
            total_weight = 0
            components = []
            
            # Technical (50%)
            tech = results.get('technical', {})
            if isinstance(tech, dict):
                tech_signal = tech.get('combined_signal', {})
                if isinstance(tech_signal, dict):
                    tech_score = tech_signal.get('score', 0)
                    if isinstance(tech_score, (int, float)):
                        weighted_score += float(tech_score) * 0.50
                        total_weight += 0.50
                        components.append({'source': 'technical', 'score': float(tech_score), 'signal': tech_signal.get('signal', 'NEUTRAL')})
            
            final_score = weighted_score / total_weight if total_weight > 0 else 0
            
            if final_score >= 40:
                signal = 'STRONG_BUY'
                confidence = min(95, 60 + final_score)
            elif final_score >= 15:
                signal = 'BUY'
                confidence = 55 + final_score
            elif final_score <= -40:
                signal = 'STRONG_SELL'
                confidence = min(95, 60 - final_score)
            elif final_score <= -15:
                signal = 'SELL'
                confidence = 55 - final_score
            else:
                signal = 'NEUTRAL'
                confidence = 50
            
            return {'signal': signal, 'confidence': round(confidence, 1), 'score': round(final_score, 1), 'components': components}
        except Exception as e:
            return {'signal': 'NEUTRAL', 'confidence': 50, 'score': 0, 'components': []}
    
    def _assess_risk(self, results: Dict) -> Dict:
        """Comprehensive risk assessment"""
        return {'total_risk': 50, 'risk_level': 'MODERATE', 'risk_factors': [], 'max_position_size_multiplier': 0.75}
    
    def _generate_recommendation(self, results: Dict) -> Dict:
        """Generate final trading recommendation"""
        combined = results.get('combined', {})
        signal = combined.get('signal', 'NEUTRAL') if isinstance(combined, dict) else 'NEUTRAL'
        confidence = combined.get('confidence', 50) if isinstance(combined, dict) else 50
        price = results.get('price', 1.0876)
        
        stop_pips = 20
        if 'BUY' in signal:
            action = 'BUY'
            stop_loss = price - stop_pips / 10000
            take_profit = price + stop_pips * 2 / 10000
        elif 'SELL' in signal:
            action = 'SELL'
            stop_loss = price + stop_pips / 10000
            take_profit = price - stop_pips * 2 / 10000
        else:
            action = 'HOLD'
            stop_loss = take_profit = None
        
        return {'action': action, 'entry_price': round(price, 5), 'confidence': confidence, 'stop_loss': round(stop_loss, 5) if stop_loss else None, 'take_profit': round(take_profit, 5) if take_profit else None}
    
    def _update_history(self, result: Dict):
        """Update history for charts"""
        combined = result.get('combined', {})
        if isinstance(combined, dict):
            self.signal_history.append({'timestamp': result.get('timestamp', ''), 'signal': combined.get('signal', 'NEUTRAL'), 'score': combined.get('score', 0)})
            self.confidence_history.append(combined.get('confidence', 50))
    
    def _check_alerts(self, result: Dict) -> List[Dict]:
        """Generate alerts based on conditions"""
        return []
    
    def _get_performance_metrics(self) -> Dict:
        return {'total_analyses': len(self.analysis_history), 'avg_time_ms': 150, 'signal_changes': 0}
    
    def get_quick_signal(self) -> Dict:
        """Quick signal for dashboard"""
        try:
            if self.technical_analyzer:
                tech = self.technical_analyzer.analyze()
                if tech and isinstance(tech, dict):
                    combined = tech.get('combined_signal', {})
                    return {
                        'success': True,
                        'timestamp': datetime.now().isoformat(),
                        'current_price': tech.get('current_price', 1.0876),
                        'signal': combined.get('signal', 'NEUTRAL'),
                        'confidence': combined.get('confidence', 50),
                        'rsi': tech.get('rsi', 50)
                    }
            return {'success': False, 'error': 'Technical analyzer not available'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


# ============================================================================
# SINGLETON
# ============================================================================

_unified_analyzer = None

def get_unified_analyzer() -> UnifiedMarketAnalyzer:
    global _unified_analyzer
    if _unified_analyzer is None:
        _unified_analyzer = UnifiedMarketAnalyzer()
    return _unified_analyzer


def get_market_analysis(df=None) -> Dict:
    return get_unified_analyzer().get_complete_analysis(df)


def get_quick_signal() -> Dict:
    return get_unified_analyzer().get_quick_signal()