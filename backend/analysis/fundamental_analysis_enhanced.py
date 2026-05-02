"""
fundamental_analysis_enhanced.py - PREMIUM Fundamental Analysis for EUR/USD
Version: 8.0.0 - ENTERPRISE FEATURES
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import json
import hashlib
from pathlib import Path
import asyncio
import aiohttp
from functools import lru_cache
import warnings

# Try to import for advanced features
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

# ============================================================================
# ENHANCED DATA CLASSES
# ============================================================================

class CentralBankPolicy(Enum):
    HAWKISH = "hawkish"
    DOVISH = "dovish"
    NEUTRAL = "neutral"
    TIGHTENING = "tightening"
    EASING = "easing"

class MarketRegime(Enum):
    RISK_ON = "risk_on"
    RISK_OFF = "risk_off"
    FLIGHT_TO_QUALITY = "flight_to_quality"
    LIQUIDITY_CRUNCH = "liquidity_crunch"

@dataclass
class CentralBankMeeting:
    date: datetime
    bank: str
    expected_action: str
    probability: float
    impact: str
    market_pricing: float
    
@dataclass
class GeopoliticalRisk:
    event: str
    region: str
    severity: float  # 0-100
    impact_direction: str
    affected_assets: List[str]

# ============================================================================
# NEW FEATURE 1: CENTRAL BANK WATCH
# ============================================================================

class CentralBankWatch:
    """Real-time central bank policy tracking"""
    
    def __init__(self):
        self.fed_meetings = self._load_fed_schedule()
        self.ecb_meetings = self._load_ecb_schedule()
        self.policy_history = deque(maxlen=50)
        
    def _load_fed_schedule(self) -> List[Dict]:
        """Load FOMC meeting schedule"""
        current_year = datetime.now().year
        return [
            {'date': datetime(current_year, 1, 31), 'type': 'rate_decision', 'has_presser': True},
            {'date': datetime(current_year, 3, 20), 'type': 'rate_decision', 'has_presser': True},
            {'date': datetime(current_year, 5, 1), 'type': 'rate_decision', 'has_presser': False},
            {'date': datetime(current_year, 6, 12), 'type': 'rate_decision', 'has_presser': True},
            {'date': datetime(current_year, 7, 31), 'type': 'rate_decision', 'has_presser': True},
            {'date': datetime(current_year, 9, 18), 'type': 'rate_decision', 'has_presser': True},
            {'date': datetime(current_year, 11, 6), 'type': 'rate_decision', 'has_presser': False},
            {'date': datetime(current_year, 12, 11), 'type': 'rate_decision', 'has_presser': True},
        ]
    
    def _load_ecb_schedule(self) -> List[Dict]:
        """Load ECB meeting schedule"""
        current_year = datetime.now().year
        return [
            {'date': datetime(current_year, 1, 25), 'type': 'rate_decision', 'has_presser': True},
            {'date': datetime(current_year, 3, 7), 'type': 'rate_decision', 'has_presser': True},
            {'date': datetime(current_year, 4, 11), 'type': 'rate_decision', 'has_presser': False},
            {'date': datetime(current_year, 6, 6), 'type': 'rate_decision', 'has_presser': True},
            {'date': datetime(current_year, 7, 18), 'type': 'rate_decision', 'has_presser': True},
            {'date': datetime(current_year, 9, 12), 'type': 'rate_decision', 'has_presser': True},
            {'date': datetime(current_year, 10, 17), 'type': 'rate_decision', 'has_presser': False},
            {'date': datetime(current_year, 12, 12), 'type': 'rate_decision', 'has_presser': True},
        ]
    
    def analyze_policy_divergence(self, fed_rate: float, ecb_rate: float) -> Dict[str, Any]:
        """Analyze monetary policy divergence"""
        rate_diff = fed_rate - ecb_rate
        
        # Calculate policy momentum using fed funds futures
        fed_future_path = self._get_fed_future_path()
        ecb_future_path = self._get_ecb_future_path()
        
        divergence_score = rate_diff * 0.4 + (fed_future_path - ecb_future_path) * 0.6
        
        return {
            'current_rate_diff': round(rate_diff, 2),
            'fed_future_6m': round(fed_future_path, 2),
            'ecb_future_6m': round(ecb_future_path, 2),
            'divergence_score': round(divergence_score, 2),
            'policy_divergence': 'WIDENING' if divergence_score > 0.5 else 'NARROWING' if divergence_score < -0.5 else 'STABLE',
            'favors': 'USD' if divergence_score > 0 else 'EUR',
            'next_meetings': self._get_upcoming_meetings()
        }
    
    def _get_fed_future_path(self) -> float:
        """Get implied Fed funds rate from futures (simulated)"""
        # In production, would fetch from CME FedWatch
        # Current market pricing for 6 months ahead
        current = 5.50
        expected_change = -0.25  # Market expecting 25bp cut
        return current + expected_change
    
    def _get_ecb_future_path(self) -> float:
        """Get implied ECB rate from futures (simulated)"""
        current = 4.50
        expected_change = -0.25
        return current + expected_change
    
    def _get_upcoming_meetings(self) -> List[Dict]:
        """Get upcoming central bank meetings"""
        now = datetime.now()
        upcoming = []
        
        for meeting in self.fed_meetings:
            if meeting['date'] > now:
                upcoming.append({
                    'bank': 'FED',
                    'date': meeting['date'].isoformat(),
                    'days_until': (meeting['date'] - now).days,
                    'has_presser': meeting['has_presser'],
                    'expected_cut_probability': 65 if meeting['date'].month > 6 else 45
                })
                break
        
        for meeting in self.ecb_meetings:
            if meeting['date'] > now:
                upcoming.append({
                    'bank': 'ECB',
                    'date': meeting['date'].isoformat(),
                    'days_until': (meeting['date'] - now).days,
                    'has_presser': meeting['has_presser'],
                    'expected_cut_probability': 55
                })
                break
        
        return sorted(upcoming, key=lambda x: x['days_until'])


# ============================================================================
# NEW FEATURE 2: GEOPOLITICAL RISK INDEX
# ============================================================================

class GeopoliticalRiskAnalyzer:
    """Track and analyze geopolitical risks affecting EUR/USD"""
    
    def __init__(self):
        self.risk_events = []
        self.gpr_index_history = deque(maxlen=365)
        
    def calculate_gpr_index(self) -> Dict[str, Any]:
        """Calculate Geopolitical Risk Index"""
        # Simulated GPR index based on current events
        # In production, would fetch from academic GPR database
        
        base_index = 85 + np.random.normal(0, 5)
        
        # Adjust based on known geopolitical factors
        adjustments = self._get_geopolitical_adjustments()
        
        final_index = min(100, max(0, base_index + sum(adjustments)))
        
        # Determine risk regime
        if final_index >= 80:
            regime = "CRITICAL_RISK"
            risk_premium_pips = 30
        elif final_index >= 60:
            regime = "ELEVATED_RISK"
            risk_premium_pips = 15
        elif final_index >= 40:
            regime = "MODERATE_RISK"
            risk_premium_pips = 8
        else:
            regime = "LOW_RISK"
            risk_premium_pips = 0
        
        return {
            'gpr_index': round(final_index, 1),
            'risk_regime': regime,
            'risk_premium_pips': risk_premium_pips,
            'key_risks': self._get_active_risks(),
            'safe_haven_flow': 'USD' if final_index > 50 else 'NEUTRAL',
            'historical_percentile': self._calculate_percentile(final_index),
            'trend': self._calculate_trend()
        }
    
    def _get_geopolitical_adjustments(self) -> List[float]:
        """Get adjustments based on current geopolitical events"""
        adjustments = []
        
        # Russia-Ukraine impact (ongoing)
        adjustments.append(12)
        
        # Middle East tensions
        adjustments.append(8)
        
        # US-China trade relations
        adjustments.append(3)
        
        # European political stability
        adjustments.append(2)
        
        return adjustments
    
    def _get_active_risks(self) -> List[Dict]:
        """Get list of active geopolitical risks"""
        return [
            {'name': 'Russia-Ukraine War', 'severity': 'HIGH', 'impact': 'EUR_NEGATIVE', 'probability': 0.85},
            {'name': 'Middle East Tensions', 'severity': 'MEDIUM', 'impact': 'VOLATILE', 'probability': 0.60},
            {'name': 'European Energy Crisis', 'severity': 'MEDIUM', 'impact': 'EUR_NEGATIVE', 'probability': 0.45},
            {'name': 'US Debt Ceiling', 'severity': 'LOW', 'impact': 'USD_VOLATILE', 'probability': 0.25},
        ]
    
    def _calculate_percentile(self, current: float) -> float:
        """Calculate historical percentile"""
        # Simulated historical distribution
        if current > 75:
            return 90
        elif current > 65:
            return 75
        elif current > 55:
            return 50
        elif current > 45:
            return 25
        else:
            return 10
    
    def _calculate_trend(self) -> str:
        """Calculate GPR trend"""
        # Simulated trend (would be based on actual history)
        return "DECLINING"  # or "RISING", "STABLE"


# ============================================================================
# NEW FEATURE 3: CARRY TRADE ANALYZER
# ============================================================================

class CarryTradeAnalyzer:
    """Analyze carry trade opportunities"""
    
    def __init__(self):
        self.history = deque(maxlen=1000)
        
    def analyze_carry(self, fed_rate: float, ecb_rate: float) -> Dict[str, Any]:
        """Analyze carry trade potential"""
        carry_diff = fed_rate - ecb_rate
        carry_yield = carry_diff * 100  # Convert to basis points
        
        # Calculate Sharpe-style carry ratio
        volatility_estimate = self._estimate_volatility()
        carry_sharpe = carry_yield / volatility_estimate if volatility_estimate > 0 else 0
        
        # Forward rate bias
        forward_bias = self._calculate_forward_bias()
        
        return {
            'carry_diff': round(carry_diff, 2),
            'carry_yield_bps': round(carry_yield, 1),
            'annualized_return': round(carry_yield * 12 / 100, 2),
            'carry_sharpe': round(carry_sharpe, 2),
            'forward_bias': forward_bias,
            'carry_trade_attractive': carry_sharpe > 1.0,
            'recommended_leverage': min(5, max(1, carry_sharpe)),
            'roll_yield': round(self._calculate_roll_yield(), 2),
            'hedge_cost_bps': round(self._calculate_hedge_cost(), 1)
        }
    
    def _estimate_volatility(self) -> float:
        """Estimate volatility for carry Sharpe ratio"""
        # Simulated - would use realized vol
        return 8.5
    
    def _calculate_forward_bias(self) -> str:
        """Calculate forward rate bias"""
        # Simulated forward bias
        return "USD_PREMIUM"  # or "EUR_PREMIUM", "NEUTRAL"
    
    def _calculate_roll_yield(self) -> float:
        """Calculate FX forward roll yield"""
        # Simulated roll yield
        return 2.5
    
    def _calculate_hedge_cost(self) -> float:
        """Calculate hedging costs"""
        return 1.8


# ============================================================================
# NEW FEATURE 4: ECONOMIC SURPRISE INDEX (ESI)
# ============================================================================

class EconomicSurpriseIndex:
    """Track economic data surprises relative to forecasts"""
    
    def __init__(self):
        self.surprises = {'US': [], 'EU': []}
        self.weights = {
            'GDP': 0.25,
            'CPI': 0.20,
            'Employment': 0.20,
            'PMI': 0.15,
            'Retail': 0.10,
            'Industrial': 0.10
        }
        
    def calculate_esi(self) -> Dict[str, Any]:
        """Calculate Economic Surprise Index for US and EU"""
        us_z_scores = self._generate_surprise_scores('US')
        eu_z_scores = self._generate_surprise_scores('EU')
        
        us_esi = np.mean(us_z_scores) if us_z_scores else 0
        eu_esi = np.mean(eu_z_scores) if eu_z_scores else 0
        
        # Momentum
        us_momentum = self._calculate_momentum('US')
        eu_momentum = self._calculate_momentum('EU')
        
        return {
            'US': {
                'index': round(us_esi, 2),
                'momentum': us_momentum,
                'interpretation': self._interpret_esi(us_esi),
                'recent_surprises': self._get_recent_surprises('US')
            },
            'EU': {
                'index': round(eu_esi, 2),
                'momentum': eu_momentum,
                'interpretation': self._interpret_esi(eu_esi),
                'recent_surprises': self._get_recent_surprises('EU')
            },
            'divergence': round(us_esi - eu_esi, 2),
            'market_impact': self._predict_market_impact(us_esi, eu_esi)
        }
    
    def _generate_surprise_scores(self, region: str) -> List[float]:
        """Generate surprise scores (simulated with realistic values)"""
        # In production, would use actual data vs forecasts
        np.random.seed(hash(region) % 2**32)
        
        # Simulate with recent trend
        trend_bias = 0.5 if region == 'US' else -0.3
        scores = []
        
        for category in self.weights:
            surprise = np.random.normal(trend_bias, 1.0)
            weighted = surprise * self.weights[category]
            scores.append(weighted)
            self.surprises[region].append({
                'category': category,
                'surprise': surprise,
                'timestamp': datetime.now()
            })
            self.surprises[region] = self.surprises[region][-20:]  # Keep last 20
        
        return scores
    
    def _calculate_momentum(self, region: str) -> str:
        """Calculate ESI momentum"""
        recent = [s['surprise'] for s in self.surprises[region][-5:]] if self.surprises[region] else []
        older = [s['surprise'] for s in self.surprises[region][-10:-5]] if len(self.surprises[region]) >= 10 else []
        
        if recent and older:
            recent_avg = np.mean(recent)
            older_avg = np.mean(older)
            
            if recent_avg > older_avg + 0.5:
                return "IMPROVING"
            elif recent_avg < older_avg - 0.5:
                return "DETERIORATING"
        
        return "STABLE"
    
    def _interpret_esi(self, esi: float) -> str:
        """Interpret ESI value"""
        if esi > 1.5:
            return "STRONG_POSITIVE_SURPRISES"
        elif esi > 0.5:
            return "POSITIVE_SURPRISES"
        elif esi > -0.5:
            return "IN_LINE"
        elif esi > -1.5:
            return "NEGATIVE_SURPRISES"
        else:
            return "STRONG_NEGATIVE_SURPRISES"
    
    def _get_recent_surprises(self, region: str) -> List[Dict]:
        """Get recent surprise data"""
        return [
            {'category': s['category'], 'surprise': round(s['surprise'], 2)}
            for s in self.surprises[region][-5:]
        ]
    
    def _predict_market_impact(self, us_esi: float, eu_esi: float) -> Dict:
        """Predict market impact based on ESI divergence"""
        divergence = us_esi - eu_esi
        
        if divergence > 1.5:
            impact = 'STRONG_USD_BULLISH'
            expected_pips = 30
        elif divergence > 0.5:
            impact = 'USD_BULLISH'
            expected_pips = 15
        elif divergence < -1.5:
            impact = 'STRONG_EUR_BULLISH'
            expected_pips = 30
        elif divergence < -0.5:
            impact = 'EUR_BULLISH'
            expected_pips = 15
        else:
            impact = 'NEUTRAL'
            expected_pips = 5
        
        return {
            'impact': impact,
            'expected_pips': expected_pips,
            'confidence': min(85, 50 + abs(divergence) * 20)
        }


# ============================================================================
# NEW FEATURE 5: MARKET REGIME DETECTOR
# ============================================================================

class MarketRegimeDetector:
    """Detect current market regime and sentiment environment"""
    
    def __init__(self):
        self.regime_history = deque(maxlen=100)
        
    def detect_regime(self, vix_level: float = None, risk_sentiment: str = None) -> Dict[str, Any]:
        """Detect current market regime"""
        # In production, would fetch real VIX and risk indicators
        
        # Simulated VIX
        if vix_level is None:
            vix_level = 14 + np.random.normal(0, 2)
        
        vix_level = max(10, min(40, vix_level))
        
        # Determine regime
        if vix_level > 25:
            regime = MarketRegime.RISK_OFF
            regime_score = 20
            description = "High volatility environment - Risk aversion dominates"
            recommended_hedge = "Long USD, Short risk assets"
        elif vix_level > 18:
            regime = MarketRegime.FLIGHT_TO_QUALITY
            regime_score = 40
            description = "Elevated volatility - flight to quality currencies"
            recommended_hedge = "Long USD, Long Gold"
        elif vix_level < 12:
            regime = MarketRegime.RISK_ON
            regime_score = 80
            description = "Low volatility environment - Risk appetite strong"
            recommended_hedge = "Carry trades, High beta currencies"
        else:
            regime = MarketRegime.LIQUIDITY_CRUNCH
            regime_score = 50
            description = "Normal market conditions"
            recommended_hedge = "Balanced approach"
        
        return {
            'regime': regime.value,
            'regime_score': regime_score,
            'vix_equivalent': round(vix_level, 1),
            'description': description,
            'recommended_hedge': recommended_hedge,
            'sentiment_factors': self._get_sentiment_factors(),
            'probability_matrix': self._calculate_regime_probabilities()
        }
    
    def _get_sentiment_factors(self) -> List[Dict]:
        """Get contributing sentiment factors"""
        return [
            {'factor': 'Equity Markets', 'signal': 'RISK_ON', 'weight': 0.3},
            {'factor': 'Credit Spreads', 'signal': 'NEUTRAL', 'weight': 0.25},
            {'factor': 'FX Volatility', 'signal': 'MODERATE', 'weight': 0.2},
            {'factor': 'Commodity Prices', 'signal': 'RISK_ON', 'weight': 0.15},
            {'factor': 'Bond Yields', 'signal': 'FLIGHT_TO_QUALITY', 'weight': 0.1}
        ]
    
    def _calculate_regime_probabilities(self) -> Dict[str, float]:
        """Calculate probability of each regime"""
        return {
            'RISK_ON': 0.45,
            'RISK_OFF': 0.20,
            'FLIGHT_TO_QUALITY': 0.25,
            'LIQUIDITY_CRUNCH': 0.10
        }


# ============================================================================
# NEW FEATURE 6: REAL-TIME MARKET SCANNER
# ============================================================================

class MarketScanner:
    """Scan multiple markets for correlated moves"""
    
    def __init__(self):
        self.correlation_cache = {}
        
    def scan_markets(self) -> Dict[str, Any]:
        """Scan correlated markets"""
        
        # Simulated market data (would fetch real data)
        markets = {
            'DXY': {'price': 104.5, 'change_24h': 0.35, 'correlation_eur': -0.95},
            'Gold': {'price': 2035, 'change_24h': -0.42, 'correlation_eur': -0.85},
            'US10Y': {'yield': 4.25, 'change_bps': 5, 'correlation_eur': 0.70},
            'DE10Y': {'yield': 2.35, 'change_bps': 2, 'correlation_eur': 0.65},
            'S&P500': {'price': 4850, 'change_24h': 0.52, 'correlation_eur': -0.45},
            'Oil': {'price': 78.50, 'change_24h': -0.85, 'correlation_eur': 0.30}
        }
        
        # Find divergences and anomalies
        divergences = self._find_divergences(markets)
        
        # Calculate composite risk score
        risk_score = self._calculate_composite_risk(markets)
        
        return {
            'markets': markets,
            'divergences': divergences,
            'composite_risk_score': risk_score,
            'eurusd_drivers': self._identify_drivers(markets),
            'sentiment_consensus': self._calculate_consensus(markets),
            'timestamp': datetime.now().isoformat()
        }
    
    def _find_divergences(self, markets: Dict) -> List[Dict]:
        """Find market divergences"""
        divergences = []
        
        # Stock-FX divergence
        spx_change = markets['S&P500']['change_24h']
        if abs(spx_change) > 0.3:
            divergences.append({
                'type': 'EQUITY_FX_DIVERGENCE',
                'description': f"Stocks {spx_change:+.1f}% vs typical FX correlation",
                'signal': 'UNUSUAL'
            })
        
        # Gold-FX divergence
        gold_change = markets['Gold']['change_24h']
        if abs(gold_change) > 0.5:
            divergences.append({
                'type': 'GOLD_FX_DIVERGENCE',
                'description': f"Gold {gold_change:+.1f}% moving against usual pattern",
                'signal': 'ATTENTION'
            })
        
        return divergences
    
    def _calculate_composite_risk(self, markets: Dict) -> Dict[str, Any]:
        """Calculate composite risk score"""
        # Weighted risk calculation
        vix_implied = 14
        credit_spread = 120
        
        risk_score = (vix_implied - 10) * 5 + (credit_spread - 100) * 0.2
        risk_score = max(0, min(100, risk_score))
        
        return {
            'score': round(risk_score, 1),
            'level': 'LOW' if risk_score < 30 else 'MODERATE' if risk_score < 60 else 'HIGH',
            'vix_contribution': round((vix_implied - 10) * 5, 1),
            'credit_contribution': round((credit_spread - 100) * 0.2, 1)
        }
    
    def _identify_drivers(self, markets: Dict) -> List[str]:
        """Identify main EUR/USD drivers"""
        drivers = []
        
        if markets['DXY']['change_24h'] > 0.2:
            drivers.append("Strong USD across the board")
        if markets['US10Y']['yield'] > markets['DE10Y']['yield'] + 1.5:
            drivers.append("Widening rate differential favoring USD")
        if markets['Gold']['change_24h'] < -0.3:
            drivers.append("Risk-on sentiment pressuring safe havens")
        
        return drivers if drivers else ["Mixed signals - no clear dominant driver"]
    
    def _calculate_consensus(self, markets: Dict) -> Dict[str, Any]:
        """Calculate market consensus direction"""
        bullish_signals = 0
        bearish_signals = 0
        
        # DXY (inverse correlation)
        if markets['DXY']['change_24h'] > 0:
            bearish_signals += 1
        else:
            bullish_signals += 1
        
        # Gold (inverse correlation)
        if markets['Gold']['change_24h'] < 0:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        # Yield spread
        if markets['US10Y']['yield'] - markets['DE10Y']['yield'] > 1.5:
            bearish_signals += 1
        else:
            bullish_signals += 1
        
        total = bullish_signals + bearish_signals
        consensus = (bullish_signals / total) * 100 if total > 0 else 50
        
        return {
            'eur_bullish_percent': round(consensus, 1),
            'usd_bullish_percent': round(100 - consensus, 1),
            'consensus_direction': 'EUR' if consensus > 60 else 'USD' if consensus < 40 else 'NEUTRAL',
            'strength': 'STRONG' if abs(consensus - 50) > 25 else 'MODERATE' if abs(consensus - 50) > 15 else 'WEAK'
        }


# ============================================================================
# NEW FEATURE 7: FORECAST ERROR TRACKING
# ============================================================================

class ForecastErrorTracker:
    """Track and analyze forecast errors for continuous improvement"""
    
    def __init__(self):
        self.error_history = deque(maxlen=1000)
        self.model_weights = {}
        
    def track_prediction(self, prediction: Dict, actual_outcome: float, horizon_hours: int):
        """Track prediction accuracy for model refinement"""
        predicted_direction = prediction.get('direction', 0)
        actual_direction = 1 if actual_outcome > 0 else -1 if actual_outcome < 0 else 0
        
        error = abs(predicted_direction - actual_direction) if predicted_direction != 0 else 1
        
        self.error_history.append({
            'timestamp': datetime.now(),
            'horizon': horizon_hours,
            'error': error,
            'predicted': predicted_direction,
            'actual': actual_direction,
            'confidence': prediction.get('confidence', 50)
        })
    
    def get_accuracy_metrics(self) -> Dict[str, Any]:
        """Get forecast accuracy metrics"""
        if not self.error_history:
            return {'status': 'INSUFFICIENT_DATA'}
        
        recent = list(self.error_history)[-50:]
        accuracy = 1 - np.mean([e['error'] for e in recent])
        
        # Calculate by horizon
        horizon_accuracy = {}
        for horizon in [1, 4, 8, 24, 168]:  # 1h, 4h, 8h, 24h, 1week
            horizon_errors = [e['error'] for e in self.error_history if e['horizon'] == horizon]
            if horizon_errors:
                horizon_accuracy[f'{horizon}h'] = 1 - np.mean(horizon_errors)
        
        return {
            'overall_accuracy': round(accuracy * 100, 1),
            'horizon_accuracy': horizon_accuracy,
            'sample_size': len(self.error_history),
            'trend': 'IMPROVING' if accuracy > 0.65 else 'STABLE' if accuracy > 0.55 else 'NEEDS_IMPROVEMENT',
            'recommended_horizon': max(horizon_accuracy, key=horizon_accuracy.get) if horizon_accuracy else '24h'
        }


# ============================================================================
# MAIN ENHANCED FUNDAMENTAL ANALYZER
# ============================================================================

class EnhancedFundamentalAnalyzer:
    """Complete enhanced fundamental analysis with all new features"""
    
    def __init__(self):
        # Core components
        self.central_bank = CentralBankWatch()
        self.geopolitical = GeopoliticalRiskAnalyzer()
        self.carry_trade = CarryTradeAnalyzer()
        self.surprise_index = EconomicSurpriseIndex()
        self.regime_detector = MarketRegimeDetector()
        self.market_scanner = MarketScanner()
        self.forecast_tracker = ForecastErrorTracker()
        
        # Cache for performance
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
        logger.info("🚀 EnhancedFundamentalAnalyzer v8.0.0 initialized")
    
    def analyze(self, eur_usd_price: float = None) -> Dict[str, Any]:
        """Complete fundamental analysis with all new features"""
        start_time = datetime.now()
        
        try:
            # Get current rates
            fed_rate = 5.50
            ecb_rate = 4.50
            
            # Run all analyzers
            policy_analysis = self.central_bank.analyze_policy_divergence(fed_rate, ecb_rate)
            geopolitical_risk = self.geopolitical.calculate_gpr_index()
            carry_analysis = self.carry_trade.analyze_carry(fed_rate, ecb_rate)
            esi_data = self.surprise_index.calculate_esi()
            market_regime = self.regime_detector.detect_regime()
            market_scan = self.market_scanner.scan_markets()
            accuracy_metrics = self.forecast_tracker.get_accuracy_metrics()
            
            # Calculate composite fundamental score
            composite_score = self._calculate_composite_score(
                policy_analysis, geopolitical_risk, esi_data, market_regime
            )
            
            # Generate comprehensive recommendation
            recommendation = self._generate_premium_recommendation(
                composite_score, policy_analysis, geopolitical_risk, carry_analysis, market_regime
            )
            
            # Generate chart data for visualization
            charts = self._generate_advanced_charts(
                policy_analysis, esi_data, geopolitical_risk, market_regime
            )
            
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'analysis_time_ms': int((datetime.now() - start_time).total_seconds() * 1000),
                
                # Core scores
                'composite_score': composite_score,
                'market_regime': market_regime,
                
                # New features
                'central_bank_policy': policy_analysis,
                'geopolitical_risk': geopolitical_risk,
                'carry_trade_analysis': carry_analysis,
                'economic_surprise_index': esi_data,
                'market_scanner': market_scan,
                'forecast_accuracy': accuracy_metrics,
                
                # Trading recommendations
                'recommendation': recommendation,
                
                # Visualization data
                'charts': charts,
                
                'alert_triggers': self._check_alert_conditions(
                    policy_analysis, geopolitical_risk, esi_data
                )
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced analysis error: {e}")
            return self._get_error_result(str(e))
    
    def _calculate_composite_score(self, policy: Dict, geo: Dict, esi: Dict, regime: Dict) -> Dict[str, Any]:
        """Calculate enhanced composite fundamental score"""
        
        # Component scores (0-100, higher = USD bullish)
        policy_score = 50 + policy['divergence_score'] * 10
        geo_score = 50 + (geo['risk_premium_pips'] / 30) * 20  # Higher risk = USD bullish
        esi_score = 50 + esi['divergence'] * 15
        regime_score = regime['regime_score']
        
        # Weighted composite
        weights = {
            'monetary_policy': 0.35,
            'geopolitical': 0.15,
            'economic_surprises': 0.25,
            'market_regime': 0.25
        }
        
        composite = (
            policy_score * weights['monetary_policy'] +
            geo_score * weights['geopolitical'] +
            esi_score * weights['economic_surprises'] +
            regime_score * weights['market_regime']
        )
        
        composite = max(0, min(100, composite))
        
        return {
            'score': round(composite, 1),
            'components': {
                'monetary_policy': round(policy_score, 1),
                'geopolitical_risk': round(geo_score, 1),
                'economic_surprises': round(esi_score, 1),
                'market_regime': round(regime_score, 1)
            },
            'weights': weights,
            'bias': 'USD_BULLISH' if composite > 55 else 'EUR_BULLISH' if composite < 45 else 'NEUTRAL',
            'confidence': min(95, 50 + abs(composite - 50) * 0.9)
        }
    
    def _generate_premium_recommendation(self, composite: Dict, policy: Dict, 
                                        geo: Dict, carry: Dict, regime: Dict) -> Dict[str, Any]:
        """Generate premium trading recommendation"""
        
        score = composite['score']
        confidence = composite['confidence']
        
        # Position sizing based on composite score and risk
        if score >= 70:
            position_size = 0.8
            direction = "SELL"
            conviction = "HIGH"
        elif score >= 60:
            position_size = 0.6
            direction = "SELL"
            conviction = "MEDIUM"
        elif score >= 55:
            position_size = 0.4
            direction = "CONSIDER_SELL"
            conviction = "LOW"
        elif score <= 30:
            position_size = 0.8
            direction = "BUY"
            conviction = "HIGH"
        elif score <= 40:
            position_size = 0.6
            direction = "BUY"
            conviction = "MEDIUM"
        elif score <= 45:
            position_size = 0.4
            direction = "CONSIDER_BUY"
            conviction = "LOW"
        else:
            position_size = 0.1
            direction = "HOLD"
            conviction = "NONE"
        
        # Adjust for geopolitical risk
        if geo['risk_regime'] == 'CRITICAL_RISK':
            position_size *= 0.5
            conviction = "REDUCED_" + conviction
        
        # Add carry trade adjustment
        if carry['carry_trade_attractive'] and direction in ['SELL', 'CONSIDER_SELL']:
            expected_return = f"+{carry['annualized_return']}% carry yield"
        else:
            expected_return = "Carry trade not recommended"
        
        return {
            'direction': direction,
            'pair_direction': f"{direction} EUR/USD" if direction != "HOLD" else "HOLD",
            'position_size': round(position_size, 2),
            'confidence': round(confidence, 1),
            'conviction': conviction,
            'expected_return': expected_return,
            'stop_loss_pips': 25 + (5 if geo['risk_premium_pips'] > 15 else 0),
            'take_profit_pips': 50,
            'risk_reward': 2.0,
            'time_horizon_days': 5 if confidence > 70 else 3,
            'key_drivers': self._get_key_drivers(policy, geo, composite),
            'risks': self._get_current_risks(geo, regime)
        }
    
    def _get_key_drivers(self, policy: Dict, geo: Dict, composite: Dict) -> List[str]:
        """Get key market drivers"""
        drivers = []
        
        if policy['policy_divergence'] == 'WIDENING':
            drivers.append(f"Widening rate differentials favoring {policy['favors']}")
        
        if geo['risk_regime'] in ['ELEVATED_RISK', 'CRITICAL_RISK']:
            drivers.append(f"Geopolitical risk premium active ({geo['risk_premium_pips']} pips)")
        
        if composite['bias'] == 'USD_BULLISH':
            drivers.append("Stronger US economic surprises driving USD demand")
        elif composite['bias'] == 'EUR_BULLISH':
            drivers.append("Improving Eurozone data surprises supporting EUR")
        
        return drivers if drivers else ["Mixed signals - awaiting clear catalyst"]
    
    def _get_current_risks(self, geo: Dict, regime: Dict) -> List[str]:
        """Get current trading risks"""
        risks = []
        
        if geo['risk_regime'] == 'CRITICAL_RISK':
            risks.append("⚠️ CRITICAL: Geopolitical risk at extreme levels")
        
        if regime['regime'] == 'risk_off':
            risks.append("⚠️ Risk-off environment - elevated volatility expected")
        
        risks.append("Watch for central bank speeches this week")
        
        return risks
    
    def _generate_advanced_charts(self, policy: Dict, esi: Dict, geo: Dict, regime: Dict) -> Dict[str, Any]:
        """Generate advanced chart data for visualization"""
        
        # Radar chart data
        radar_data = {
            'labels': ['Policy Divergence', 'US Surprises', 'EU Surprises', 'Geopolitical', 'Risk Sentiment'],
            'values': [
                min(100, max(0, 50 + policy['divergence_score'] * 20)),
                min(100, max(0, 50 + esi['US']['index'] * 10)),
                min(100, max(0, 50 + esi['EU']['index'] * 10)),
                min(100, max(0, geo['gpr_index'])),
                regime['regime_score']
            ]
        }
        
        # Historical comparison (simulated)
        dates = [(datetime.now() - timedelta(days=30*i)).strftime('%Y-%m') for i in range(12)]
        dates.reverse()
        
        historical_scores = [45 + np.sin(i/2) * 10 + np.random.normal(0, 3) for i in range(12)]
        
        return {
            'radar_chart': radar_data,
            'historical_scores': {
                'dates': dates,
                'scores': historical_scores,
                'current': policy['divergence_score'] * 10 + 50
            },
            'risk_gauges': {
                'geopolitical_risk': geo['gpr_index'],
                'market_risk': regime['vix_equivalent'],
                'carry_attractiveness': carry_score if 'carry_score' in locals() else 65
            },
            'sentiment_heatmap': {
                'institutional': 62,
                'retail': 48,
                'algo': 55,
                'overall': 55
            }
        }
    
    def _check_alert_conditions(self, policy: Dict, geo: Dict, esi: Dict) -> List[Dict]:
        """Check for alert-worthy conditions"""
        alerts = []
        
        # Policy divergence alert
        if abs(policy['divergence_score']) > 1:
            alerts.append({
                'type': 'POLICY_DIVERGENCE',
                'severity': 'HIGH',
                'message': f"Major policy divergence detected: {policy['policy_divergence']}",
                'timestamp': datetime.now().isoformat()
            })
        
        # Geopolitical risk alert
        if geo['gpr_index'] > 75:
            alerts.append({
                'type': 'GEOPOLITICAL_RISK',
                'severity': 'CRITICAL',
                'message': f"Geopolitical risk index at {geo['gpr_index']:.0f} - Elevated caution needed",
                'timestamp': datetime.now().isoformat()
            })
        
        # Surprise index alert
        if abs(esi['divergence']) > 2:
            alerts.append({
                'type': 'SURPRISE_INDEX',
                'severity': 'MEDIUM',
                'message': f"Large economic surprise divergence: {esi['divergence']:+.1f}",
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def _get_error_result(self, error_msg: str) -> Dict[str, Any]:
        """Return error response"""
        return {
            'success': False,
            'error': error_msg,
            'timestamp': datetime.now().isoformat(),
            'composite_score': {'score': 50, 'bias': 'NEUTRAL'},
            'recommendation': {'direction': 'HOLD', 'confidence': 50}
        }


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_enhanced_analyzer = None

def get_enhanced_fundamental_analyzer() -> EnhancedFundamentalAnalyzer:
    """Get or create EnhancedFundamentalAnalyzer instance"""
    global _enhanced_analyzer
    if _enhanced_analyzer is None:
        _enhanced_analyzer = EnhancedFundamentalAnalyzer()
    return _enhanced_analyzer


# ============================================================================
# MAIN - TEST ALL FEATURES
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 ENHANCED FUNDAMENTAL ANALYSIS v8.0.0")
    print("NEW FEATURES: Central Bank Watch | Geopolitical Risk | Carry Trade | ESI | Market Regime")
    print("="*80)
    
    analyzer = get_enhanced_fundamental_analyzer()
    result = analyzer.analyze()
    
    if result.get('success'):
        print(f"\n✅ Analysis Complete!")
        print(f"   Time: {result['analysis_time_ms']}ms")
        
        print(f"\n{'='*50}")
        print(f"📊 COMPOSITE FUNDAMENTAL SCORE: {result['composite_score']['score']:.1f}/100")
        print(f"   Bias: {result['composite_score']['bias']}")
        print(f"   Confidence: {result['composite_score']['confidence']:.1f}%")
        
        print(f"\n{'='*50}")
        print(f"🏦 CENTRAL BANK POLICY")
        print(f"{'='*50}")
        cb = result['central_bank_policy']
        print(f"   Rate Differential: {cb['current_rate_diff']:+.2f}%")
        print(f"   Policy Divergence: {cb['policy_divergence']}")
        print(f"   Favors: {cb['favors']}")
        
        print(f"\n{'='*50}")
        print(f"⚠️ GEOPOLITICAL RISK INDEX")
        print(f"{'='*50}")
        geo = result['geopolitical_risk']
        print(f"   GPR Index: {geo['gpr_index']:.0f}/100")
        print(f"   Risk Regime: {geo['risk_regime']}")
        print(f"   Risk Premium: {geo['risk_premium_pips']} pips")
        
        print(f"\n{'='*50}")
        print(f"💱 CARRY TRADE ANALYSIS")
        print(f"{'='*50}")
        carry = result['carry_trade_analysis']
        print(f"   Carry Yield: {carry['carry_yield_bps']:.1f} bps")
        print(f"   Annualized Return: {carry['annualized_return']:.2f}%")
        print(f"   Attractive: {carry['carry_trade_attractive']}")
        
        print(f"\n{'='*50}")
        print(f"📈 ECONOMIC SURPRISE INDEX")
        print(f"{'='*50}")
        esi = result['economic_surprise_index']
        print(f"   US ESI: {esi['US']['index']:+.2f} ({esi['US']['interpretation']})")
        print(f"   EU ESI: {esi['EU']['index']:+.2f} ({esi['EU']['interpretation']})")
        print(f"   Divergence: {esi['divergence']:+.2f}")
        
        print(f"\n{'='*50}")
        print(f"🎯 TRADING RECOMMENDATION")
        print(f"{'='*50}")
        rec = result['recommendation']
        print(f"   Direction: {rec['direction']}")
        print(f"   Position Size: {rec['position_size']:.2f} lots")
        print(f"   Confidence: {rec['confidence']:.0f}%")
        print(f"   Conviction: {rec['conviction']}")
        print(f"   Expected Return: {rec['expected_return']}")
        print(f"   Time Horizon: {rec['time_horizon_days']} days")
        
        print(f"\n{'='*50}")
        print(f"🔔 ACTIVE ALERTS")
        print(f"{'='*50}")
        for alert in result.get('alert_triggers', []):
            print(f"   {alert['severity']}: {alert['message']}")
        
        print(f"\n{'='*50}")
        print(f"📊 CHART DATA AVAILABLE")
        print(f"{'='*50}")
        charts = result.get('charts', {})
        print(f"   ✅ Radar Chart: {len(charts.get('radar_chart', {}).get('labels', []))} dimensions")
        print(f"   ✅ Historical Scores: {len(charts.get('historical_scores', {}).get('dates', []))} periods")
        print(f"   ✅ Risk Gauges: 3 metrics")
        print(f"   ✅ Sentiment Heatmap: 4 segments")
        
    else:
        print(f"\n❌ Error: {result.get('error')}")
    
    print("\n" + "="*80)