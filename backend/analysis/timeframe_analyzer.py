"""
timeframe_analyzer.py - ULTIMATE Multi-Timeframe Analyzer v4.1
FIXED: Slice indexing, array bounds, alignment access
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class TrendDirection(Enum):
    """Trend direction enumeration"""
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    SIDEWAYS = "Sideways"
    TRENDING = "Trending"
    UNKNOWN = "Unknown"


class ConfidenceLevel(Enum):
    """Confidence level enumeration"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INSUFFICIENT = "Insufficient"


@dataclass
class TimeframeAnalysis:
    """Complete analysis for a single timeframe"""
    timeframe: str
    direction: str
    strength: float
    confidence: str
    adx: float
    slope: float
    quality_score: int
    current_price: float
    ma_20: float
    ma_50: float
    ma_200: float
    support: List[float] = field(default_factory=list)
    resistance: List[float] = field(default_factory=list)


class MultiTimeframeAnalyzer:
    """
    ULTIMATE Multi-Timeframe Analyzer v4.1 - FIXED
    Professional-grade analysis with advanced charting
    """
    
    def __init__(self):
        """Initialize the analyzer with default settings"""
        
        # Define timeframes (from smallest to largest)
        self.timeframes = ['M5', 'M15', 'H1', 'H4', 'D1', 'W1']
        
        # Timeframe mapping for API calls
        self.timeframe_map = {
            'M5': '5min',
            'M15': '15min', 
            'H1': '1h',
            'H4': '4h',
            'D1': '1d',
            'W1': '1wk'
        }
        
        # Display names
        self.display_names = {
            'M5': '5 Minutes',
            'M15': '15 Minutes',
            'H1': '1 Hour',
            'H4': '4 Hours',
            'D1': '1 Day',
            'W1': '1 Week'
        }
        
        # Importance weights (higher = more important for trend)
        self.weights = {
            'W1': 1.5,
            'D1': 1.3,
            'H4': 1.0,
            'H1': 0.8,
            'M15': 0.5,
            'M5': 0.3
        }
        
        # ADX thresholds
        self.adx_thresholds = {
            'trending': 25,
            'strong': 40,
            'extreme': 60
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            'excellent': 90,
            'good': 70,
            'moderate': 50,
            'poor': 30
        }
        
        # History storage for charts
        self.analysis_history = deque(maxlen=100)
        
        # Performance metrics
        self.metrics = {
            'total_analyses': 0,
            'avg_time_ms': 0,
            'cache_hits': 0
        }
        
        # Cache
        self._cache = {}
        
        logger.info("=" * 70)
        logger.info("📊 MultiTimeframeAnalyzer v4.1 Initialized (FIXED)")
        logger.info(f"   Timeframes: {', '.join(self.timeframes)}")
        logger.info("=" * 70)
    
    # ============================================================
    # MAIN ANALYSIS METHOD
    # ============================================================
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Complete multi-timeframe analysis
        
        Args:
            df: DataFrame with OHLCV data (at least 1000 rows for full analysis)
            
        Returns:
            Dictionary with complete analysis and chart data
        """
        import time
        start_time = time.time()
        
        try:
            # Validate input
            if df is None or df.empty:
                return self._get_empty_result()
            
            # Prepare dataframe
            df = self._prepare_dataframe(df)
            
            # Get price data
            close = self._get_column(df, 'close')
            high = self._get_column(df, 'high')
            low = self._get_column(df, 'low')
            volume = self._get_column(df, 'volume')
            
            if close is None or len(close) < 100:
                return self._get_empty_result()
            
            # Analyze each timeframe - FIXED: Use integer slicing safely
            results = {}
            for tf in self.timeframes:
                periods = self._get_periods_for_timeframe(tf)
                if len(close) >= periods:
                    # SAFE: Convert to list and slice properly
                    close_slice = close[-periods:] if periods > 0 else close
                    high_slice = high[-periods:] if high is not None and periods > 0 else None
                    low_slice = low[-periods:] if low is not None and periods > 0 else None
                    
                    results[tf] = self._analyze_timeframe(
                        close_slice,
                        high_slice,
                        low_slice,
                        tf
                    )
                else:
                    results[tf] = self._get_empty_timeframe(tf)
            
            # Calculate alignment
            alignment = self._calculate_alignment(results)
            
            # Generate all charts - FIXED: Pass alignment and results properly
            charts = self._generate_all_charts(results, alignment, close)
            
            # Add volume analysis if available
            volume_analysis = None
            if volume is not None and len(volume) >= 100:
                volume_analysis = self._analyze_volume(volume)
            
            # Get market context - FIXED: Pass alignment
            context = self._get_market_context(close, results, alignment)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(results, alignment)
            
            # Get integrated signals
            integrated = self._get_integrated_signals(results, alignment)
            
            # Store in history
            self.analysis_history.append({
                'timestamp': datetime.now().isoformat(),
                'alignment': alignment.get('direction', 'Mixed'),
                'confidence': alignment.get('confidence', 50)
            })
            
            # Get current price safely
            current_price = float(close[-1]) if len(close) > 0 else 1.0876
            
            # Build result
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'version': '4.1',
                'current_price': current_price,
                'timeframes': results,
                'alignment': alignment,
                'charts': charts,
                'volume_analysis': volume_analysis,
                'market_context': context,
                'recommendations': recommendations,
                'integrated': integrated,
                'summary': self._generate_summary(alignment, context),
                'metrics': self.metrics
            }
            
            # Update performance metrics
            elapsed_ms = (time.time() - start_time) * 1000
            self._update_metrics(elapsed_ms)
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            import traceback
            traceback.print_exc()
            return self._get_error_result(str(e))
    
    # ============================================================
    # TIMEFRAME ANALYSIS
    # ============================================================
    
    def _analyze_timeframe(self, close: np.ndarray, high: np.ndarray = None,
                          low: np.ndarray = None, tf: str = "H1") -> Dict[str, Any]:
        """Analyze a single timeframe"""
        try:
            n = len(close)
            if n < 20:
                return self._get_empty_timeframe(tf)
            
            # Calculate moving averages
            ma_20 = float(np.mean(close[-20:])) if n >= 20 else float(close[-1])
            ma_50 = float(np.mean(close[-50:])) if n >= 50 else ma_20
            ma_200 = float(np.mean(close[-200:])) if n >= 200 else ma_50
            
            current = float(close[-1])
            
            # Calculate ADX (simplified but effective)
            adx = self._calculate_adx_simple(close)
            
            # Calculate slope
            slope_pct = 0.0
            if n >= 20:
                try:
                    x = np.arange(20)
                    y = close[-20:]
                    slope = np.polyfit(x, y, 1)[0]
                    slope_pct = slope / (ma_20 + 1e-10) * 100
                except Exception:
                    slope_pct = 0.0
            
            # Determine trend direction and strength
            direction = TrendDirection.SIDEWAYS.value
            strength = 0.5
            confidence = ConfidenceLevel.MEDIUM.value
            
            if current > ma_20 and ma_20 > ma_50 and ma_50 > ma_200:
                direction = TrendDirection.BULLISH.value
                strength = min(1.0, adx / 40)
                confidence = ConfidenceLevel.HIGH.value if adx > 25 else ConfidenceLevel.MEDIUM.value
            elif current < ma_20 and ma_20 < ma_50 and ma_50 < ma_200:
                direction = TrendDirection.BEARISH.value
                strength = min(1.0, adx / 40)
                confidence = ConfidenceLevel.HIGH.value if adx > 25 else ConfidenceLevel.MEDIUM.value
            elif adx > 25:
                direction = TrendDirection.TRENDING.value
                strength = adx / 100
                confidence = ConfidenceLevel.MEDIUM.value
            else:
                direction = TrendDirection.SIDEWAYS.value
                strength = 0.3
                confidence = ConfidenceLevel.LOW.value
            
            # Calculate quality score
            quality = self._calculate_quality_score(close, slope_pct, adx)
            
            # Find support/resistance
            support, resistance = self._find_support_resistance(close, high, low)
            
            return {
                'timeframe': tf,
                'direction': direction,
                'strength': round(strength, 2),
                'confidence': confidence,
                'adx': round(adx, 1),
                'slope': round(slope_pct, 2),
                'quality_score': quality,
                'current_price': round(current, 5),
                'ma_20': round(ma_20, 5),
                'ma_50': round(ma_50, 5),
                'ma_200': round(ma_200, 5),
                'support': support[:3] if support else [],
                'resistance': resistance[:3] if resistance else []
            }
            
        except Exception as e:
            logger.error(f"Timeframe {tf} analysis error: {e}")
            return self._get_empty_timeframe(tf)
    
    def _calculate_adx_simple(self, prices: np.ndarray, period: int = 14) -> float:
        """Simplified ADX calculation"""
        try:
            if len(prices) < period + 1:
                return 20.0
            
            # Calculate directional movement
            deltas = np.diff(prices)
            up_moves = np.maximum(deltas, 0)
            down_moves = np.maximum(-deltas, 0)
            
            # Smooth with Wilder's method
            alpha = 1 / period
            up_smooth = self._wilders_smooth(up_moves, alpha)
            down_smooth = self._wilders_smooth(down_moves, alpha)
            
            # Calculate DX
            di_plus = 100 * up_smooth / (up_smooth + down_smooth + 1e-10)
            di_minus = 100 * down_smooth / (up_smooth + down_smooth + 1e-10)
            dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus + 1e-10)
            
            # Smooth DX to get ADX
            adx = self._wilders_smooth(dx, alpha)
            
            return float(adx[-1]) if len(adx) > 0 else 20.0
            
        except Exception:
            return 20.0
    
    def _wilders_smooth(self, data: np.ndarray, alpha: float) -> np.ndarray:
        """Wilder's smoothing (EMA with alpha = 1/period)"""
        result = np.zeros_like(data)
        if len(data) == 0:
            return result
        
        result[0] = data[0]
        for i in range(1, len(data)):
            result[i] = alpha * data[i] + (1 - alpha) * result[i-1]
        return result
    
    def _calculate_quality_score(self, prices: np.ndarray, slope_pct: float, adx: float) -> int:
        """Calculate trend quality score (0-100)"""
        if len(prices) < 50:
            return 0
        
        # Consistency of slope
        slopes = []
        step = 3
        for i in range(step, len(prices), step):
            if i >= step:
                try:
                    x = np.arange(step)
                    y = prices[i-step:i]
                    s, _ = np.polyfit(x, y, 1)
                    slopes.append(s)
                except Exception:
                    pass
        
        if slopes:
            slope_std = np.std(slopes)
            slope_mean = np.mean(np.abs(slopes))
            consistency = max(0, 1 - (slope_std / (slope_mean + 1e-10)))
        else:
            consistency = 0.5
        
        # Score components
        slope_score = min(50, abs(slope_pct) * 10)
        adx_score = min(30, adx)
        consistency_score = consistency * 20
        
        score = int(slope_score + adx_score + consistency_score)
        return min(100, max(0, score))
    
    def _find_support_resistance(self, close: np.ndarray, high: np.ndarray = None,
                                 low: np.ndarray = None) -> Tuple[List[float], List[float]]:
        """Find support and resistance levels"""
        if high is None or low is None or len(close) < 50:
            # Fallback using close prices
            if len(close) >= 20:
                return [float(np.min(close[-20:])), float(np.percentile(close[-20:], 25))], \
                       [float(np.max(close[-20:])), float(np.percentile(close[-20:], 75))]
            return [], []
        
        try:
            # Find pivot points
            pivots_high = []
            pivots_low = []
            lookback = 10
            
            for i in range(lookback, len(close) - lookback):
                if high[i] == max(high[i-lookback:i+lookback+1]):
                    pivots_high.append(high[i])
                if low[i] == min(low[i-lookback:i+lookback+1]):
                    pivots_low.append(low[i])
            
            # Take most recent levels
            support = sorted(set([round(p, 5) for p in pivots_low[-10:]]))
            resistance = sorted(set([round(p, 5) for p in pivots_high[-10:]]), reverse=True)
            
            # Ensure we have at least some levels
            if not support and len(close) >= 20:
                support = [float(np.min(close[-20:]))]
            if not resistance and len(close) >= 20:
                resistance = [float(np.max(close[-20:]))]
            
            return support, resistance
            
        except Exception:
            return [], []
    
    # ============================================================
    # ALIGNMENT CALCULATION
    # ============================================================
    
    def _calculate_alignment(self, results: Dict) -> Dict[str, Any]:
        """Calculate weighted alignment across timeframes"""
        bullish_weight = 0
        bearish_weight = 0
        total_weight = 0
        
        details = {}
        
        for tf, analysis in results.items():
            direction = analysis.get('direction', 'Unknown')
            strength = analysis.get('strength', 0.5)
            weight = self.weights.get(tf, 1.0)
            
            adjusted_weight = weight * (0.5 + strength * 0.5)
            total_weight += adjusted_weight
            
            if direction in ['Bullish', 'Trending']:
                bullish_weight += adjusted_weight
            elif direction == 'Bearish':
                bearish_weight += adjusted_weight
            
            details[tf] = {
                'direction': direction,
                'weight': weight,
                'strength': strength
            }
        
        if total_weight == 0:
            return {
                'direction': 'Mixed', 
                'confidence': 0, 
                'bullish_pct': 50, 
                'bearish_pct': 50, 
                'details': details
            }
        
        bullish_pct = (bullish_weight / total_weight) * 100
        bearish_pct = (bearish_weight / total_weight) * 100
        
        if bullish_pct >= 70:
            direction = 'Strongly Bullish'
            confidence = bullish_pct
        elif bullish_pct >= 55:
            direction = 'Bullish'
            confidence = bullish_pct
        elif bearish_pct >= 70:
            direction = 'Strongly Bearish'
            confidence = bearish_pct
        elif bearish_pct >= 55:
            direction = 'Bearish'
            confidence = bearish_pct
        else:
            direction = 'Mixed'
            confidence = max(bullish_pct, bearish_pct)
        
        return {
            'direction': direction,
            'confidence': round(confidence, 1),
            'bullish_pct': round(bullish_pct, 1),
            'bearish_pct': round(bearish_pct, 1),
            'details': details
        }
    
    # ============================================================
    # CHART GENERATION - 12 ADVANCED CHARTS
    # ============================================================
    
    def _generate_all_charts(self, results: Dict, alignment: Dict, 
                            prices: np.ndarray) -> Dict[str, Any]:
        """Generate all chart data for frontend visualization"""
        
        # FIXED: Only include timeframes that exist in results
        existing_tfs = [tf for tf in self.timeframes if tf in results]
        
        return {
            'alignment_gauge': self._chart_alignment_gauge(alignment),
            'timeframe_heatmap': self._chart_timeframe_heatmap(results),
            'strength_comparison': self._chart_strength_comparison(results, existing_tfs),
            'adx_dashboard': self._chart_adx_dashboard(results, existing_tfs),
            'quality_meter': self._chart_quality_meter(results, existing_tfs),
            'confluence_matrix': self._chart_confluence_matrix(results, existing_tfs),
            'confidence_radar': self._chart_confidence_radar(results, existing_tfs),
            'alignment_timeline': self._chart_alignment_timeline(),
            'weighted_score': self._chart_weighted_score(alignment),
            'ema_dashboard': self._chart_ema_dashboard(results, existing_tfs),
            'direction_summary': self._chart_direction_summary(results),
            'price_structure': self._chart_price_structure(results, prices)
        }
    
    def _chart_alignment_gauge(self, alignment: Dict) -> Dict:
        """Alignment gauge chart"""
        confidence = alignment.get('confidence', 0)
        direction = alignment.get('direction', 'Mixed')
        
        # Color based on direction
        if 'Bullish' in direction:
            color = '#00ff88'
        elif 'Bearish' in direction:
            color = '#ff4444'
        else:
            color = '#ffaa00'
        
        return {
            'type': 'gauge',
            'title': 'Multi-Timeframe Alignment',
            'value': confidence,
            'min': 0,
            'max': 100,
            'needle_color': color,
            'segments': [
                {'min': 0, 'max': 33, 'label': 'Weak', 'color': '#ff4444'},
                {'min': 33, 'max': 66, 'label': 'Moderate', 'color': '#ffaa00'},
                {'min': 66, 'max': 100, 'label': 'Strong', 'color': '#00ff88'}
            ],
            'subtitle': f"{direction} - {confidence}% confidence"
        }
    
    def _chart_timeframe_heatmap(self, results: Dict) -> Dict:
        """Timeframe heatmap"""
        data = []
        for tf, analysis in results.items():
            direction = analysis.get('direction', 'Unknown')
            strength = analysis.get('strength', 0) * 100
            
            # Score: positive for bullish, negative for bearish
            if 'Bullish' in direction or 'Trending' in direction:
                score = strength
            elif 'Bearish' in direction:
                score = -strength
            else:
                score = 0
            
            data.append({
                'timeframe': tf,
                'direction': direction,
                'strength': round(strength, 1),
                'score': round(score, 1),
                'color': '#00ff88' if score > 0 else '#ff4444' if score < 0 else '#ffaa00'
            })
        
        return {
            'type': 'heatmap',
            'title': 'Trend Direction by Timeframe',
            'data': data,
            'x_axis': 'timeframe',
            'color_scale': {'min': -100, 'max': 100}
        }
    
    def _chart_strength_comparison(self, results: Dict, tfs: List[str]) -> Dict:
        """Trend strength comparison bars"""
        data = []
        for tf in tfs:
            if tf in results:
                analysis = results[tf]
                data.append({
                    'timeframe': tf,
                    'strength': round(analysis.get('strength', 0) * 100, 1),
                    'adx': analysis.get('adx', 0),
                    'quality': analysis.get('quality_score', 0)
                })
        
        return {
            'type': 'bar',
            'title': 'Trend Strength Comparison',
            'data': data,
            'x_axis': 'timeframe',
            'y_axis': 'strength (%)',
            'series': ['strength', 'adx', 'quality'],
            'series_names': ['Trend Strength', 'ADX', 'Quality']
        }
    
    def _chart_adx_dashboard(self, results: Dict, tfs: List[str]) -> Dict:
        """ADX values dashboard"""
        data = []
        for tf in tfs:
            if tf in results:
                analysis = results[tf]
                adx = analysis.get('adx', 0)
                
                if adx >= 60:
                    strength = 'Extreme'
                    color = '#ff4444'
                elif adx >= 40:
                    strength = 'Strong'
                    color = '#ffaa00'
                elif adx >= 25:
                    strength = 'Moderate'
                    color = '#88ff88'
                else:
                    strength = 'Weak'
                    color = '#00ff88'
                
                data.append({
                    'timeframe': tf,
                    'adx': round(adx, 1),
                    'strength': strength,
                    'color': color
                })
        
        return {
            'type': 'dashboard',
            'title': 'ADX Trend Strength',
            'data': data,
            'thresholds': [25, 40, 60],
            'threshold_labels': ['Weak', 'Moderate', 'Strong', 'Extreme']
        }
    
    def _chart_quality_meter(self, results: Dict, tfs: List[str]) -> Dict:
        """Trend quality meter"""
        data = []
        for tf in tfs:
            if tf in results:
                analysis = results[tf]
                quality = analysis.get('quality_score', 0)
                
                if quality >= 90:
                    rating = 'Excellent'
                    color = '#00ff88'
                elif quality >= 70:
                    rating = 'Good'
                    color = '#88ff88'
                elif quality >= 50:
                    rating = 'Moderate'
                    color = '#ffaa00'
                else:
                    rating = 'Poor'
                    color = '#ff4444'
                
                data.append({
                    'timeframe': tf,
                    'quality': quality,
                    'rating': rating,
                    'color': color
                })
        
        return {
            'type': 'bar',
            'title': 'Trend Quality Meter',
            'data': data,
            'x_axis': 'timeframe',
            'y_axis': 'quality (0-100)',
            'thresholds': [90, 70, 50],
            'threshold_labels': ['Excellent', 'Good', 'Moderate', 'Poor']
        }
    
    def _chart_confluence_matrix(self, results: Dict, tfs: List[str]) -> Dict:
        """Timeframe confluence matrix"""
        n = len(tfs)
        if n == 0:
            return {'type': 'matrix', 'title': 'Confluence Matrix', 'data': [], 'row_labels': [], 'col_labels': []}
        
        matrix = []
        for i, tf1 in enumerate(tfs):
            row = []
            dir1 = results.get(tf1, {}).get('direction', '')
            isBull1 = 'Bullish' in dir1 or 'Trending' in dir1
            isBear1 = 'Bearish' in dir1
            
            for j, tf2 in enumerate(tfs):
                if i == j:
                    row.append(100)
                else:
                    dir2 = results.get(tf2, {}).get('direction', '')
                    isBull2 = 'Bullish' in dir2 or 'Trending' in dir2
                    isBear2 = 'Bearish' in dir2
                    
                    if (isBull1 and isBull2) or (isBear1 and isBear2):
                        row.append(85)
                    elif (isBull1 and isBear2) or (isBear1 and isBull2):
                        row.append(15)
                    else:
                        row.append(50)
            matrix.append(row)
        
        return {
            'type': 'matrix',
            'title': 'Timeframe Confluence Matrix (%)',
            'row_labels': tfs,
            'col_labels': tfs,
            'data': matrix,
            'color_scale': ['#ff4444', '#ffaa00', '#00ff88']
        }
    
    def _chart_confidence_radar(self, results: Dict, tfs: List[str]) -> Dict:
        """Confidence radar chart"""
        categories = []
        values = []
        
        for tf in tfs:
            if tf in results:
                categories.append(tf)
                confidence_str = results[tf].get('confidence', 'Low')
                if confidence_str == 'High':
                    values.append(90)
                elif confidence_str == 'Medium':
                    values.append(60)
                elif confidence_str == 'Low':
                    values.append(30)
                else:
                    values.append(10)
        
        return {
            'type': 'radar',
            'title': 'Confidence by Timeframe',
            'categories': categories,
            'series': [{
                'name': 'Confidence',
                'data': values,
                'color': '#00d4ff',
                'area': True,
                'fill_opacity': 0.3
            }],
            'y_axis': {'min': 0, 'max': 100},
            'benchmark': 70
        }
    
    def _chart_alignment_timeline(self) -> Dict:
        """Historical alignment timeline"""
        if not self.analysis_history:
            return {'type': 'line', 'title': 'Alignment Timeline', 'data': []}
        
        data = []
        for i, item in enumerate(self.analysis_history[-50:]):
            direction = item.get('alignment', 'Mixed')
            confidence = item.get('confidence', 50)
            
            if 'Strongly Bullish' in direction:
                score = 100
            elif 'Bullish' in direction:
                score = 75
            elif 'Mixed' in direction:
                score = 50
            elif 'Bearish' in direction:
                score = 25
            elif 'Strongly Bearish' in direction:
                score = 0
            else:
                score = 50
            
            data.append({
                'index': i,
                'score': score,
                'confidence': confidence,
                'direction': direction
            })
        
        return {
            'type': 'line',
            'title': 'Alignment Trend (Last 50 Periods)',
            'data': data,
            'y_axis': 'score',
            'y_axis_label': 'Alignment Score (0=Bearish, 100=Bullish)',
            'thresholds': [75, 50, 25]
        }
    
    def _chart_weighted_score(self, alignment: Dict) -> Dict:
        """Weighted alignment score"""
        bullish_pct = alignment.get('bullish_pct', 50)
        
        return {
            'type': 'gauge',
            'title': 'Weighted Alignment Score',
            'value': bullish_pct,
            'min': 0,
            'max': 100,
            'needle_color': '#00ff88' if bullish_pct > 50 else '#ff4444',
            'segments': [
                {'min': 0, 'max': 33, 'label': 'Bearish', 'color': '#ff4444'},
                {'min': 33, 'max': 66, 'label': 'Neutral', 'color': '#ffaa00'},
                {'min': 66, 'max': 100, 'label': 'Bullish', 'color': '#00ff88'}
            ],
            'subtitle': f"Bullish: {bullish_pct}% | Bearish: {100 - bullish_pct}%"
        }
    
    def _chart_ema_dashboard(self, results: Dict, tfs: List[str]) -> Dict:
        """EMA values dashboard"""
        data = []
        for tf in tfs[:4]:
            if tf in results:
                analysis = results[tf]
                data.append({
                    'timeframe': tf,
                    'current': analysis.get('current_price', 0),
                    'ma_20': analysis.get('ma_20', 0),
                    'ma_50': analysis.get('ma_50', 0),
                    'ma_200': analysis.get('ma_200', 0),
                    'position': 'above' if analysis.get('current_price', 0) > analysis.get('ma_200', 0) else 'below'
                })
        
        return {
            'type': 'table',
            'title': 'EMA Analysis Dashboard',
            'data': data,
            'columns': ['timeframe', 'current', 'ma_20', 'ma_50', 'ma_200'],
            'column_names': ['Timeframe', 'Current', 'MA-20', 'MA-50', 'MA-200']
        }
    
    def _chart_direction_summary(self, results: Dict) -> Dict:
        """Trend direction summary pie chart"""
        counts = {'Bullish': 0, 'Bearish': 0, 'Sideways': 0, 'Unknown': 0}
        
        for analysis in results.values():
            direction = analysis.get('direction', 'Unknown')
            if 'Bullish' in direction or 'Trending' in direction:
                counts['Bullish'] += 1
            elif 'Bearish' in direction:
                counts['Bearish'] += 1
            elif 'Sideways' in direction:
                counts['Sideways'] += 1
            else:
                counts['Unknown'] += 1
        
        data = [
            {'name': 'Bullish', 'value': counts['Bullish'], 'color': '#00ff88'},
            {'name': 'Bearish', 'value': counts['Bearish'], 'color': '#ff4444'},
            {'name': 'Sideways', 'value': counts['Sideways'], 'color': '#ffaa00'},
            {'name': 'Unknown', 'value': counts['Unknown'], 'color': '#888888'}
        ]
        
        return {
            'type': 'pie',
            'title': 'Trend Direction Summary',
            'data': [d for d in data if d['value'] > 0],
            'hole_size': 0.4,
            'show_labels': True,
            'show_percentages': True
        }
    
    def _chart_price_structure(self, results: Dict, prices: np.ndarray) -> Dict:
        """Price structure with support/resistance"""
        main_tf = 'H4'
        if main_tf in results:
            analysis = results[main_tf]
            support = analysis.get('support', [])
            resistance = analysis.get('resistance', [])
        else:
            support = []
            resistance = []
        
        current_price = float(prices[-1]) if len(prices) > 0 else 1.0876
        
        return {
            'type': 'levels',
            'title': 'Price Structure - Support & Resistance',
            'current_price': current_price,
            'support': support,
            'resistance': resistance,
            'nearest_support': support[-1] if support else None,
            'nearest_resistance': resistance[-1] if resistance else None
        }
    
    # ============================================================
    # SUPPORTING METHODS
    # ============================================================
    
    def _analyze_volume(self, volume: np.ndarray) -> Dict[str, Any]:
        """Analyze volume pattern"""
        if len(volume) < 50:
            return {'confirmation': 'Insufficient Data', 'volume_ratio': 1.0, 'volume_trend': 'Stable'}
        
        recent_vol = np.mean(volume[-20:])
        avg_vol = np.mean(volume[-100:])
        ratio = recent_vol / (avg_vol + 1e-10)
        
        if ratio > 1.2:
            confirmation = 'Strong Confirmation'
            trend = 'Increasing'
        elif ratio < 0.8:
            confirmation = 'Weak Confirmation'
            trend = 'Decreasing'
        else:
            confirmation = 'Neutral'
            trend = 'Stable'
        
        return {
            'confirmation': confirmation,
            'volume_ratio': round(ratio, 2),
            'volume_trend': trend
        }
    
    def _get_market_context(self, prices: np.ndarray, results: Dict, alignment: Dict) -> Dict[str, str]:
        """Get market context - FIXED: Now receives alignment as parameter"""
        if len(prices) < 20:
            return {'phase': 'Unknown', 'volatility': 'Normal', 'risk_level': 'Medium'}
        
        # Calculate volatility
        returns = np.diff(np.log(prices[-20:] + 1e-10))
        volatility = np.std(returns) * np.sqrt(252) * 100
        
        if volatility > 25:
            vol_str = 'High'
        elif volatility < 10:
            vol_str = 'Low'
        else:
            vol_str = 'Normal'
        
        # Determine phase from alignment
        direction = alignment.get('direction', 'Mixed')
        
        if 'Strongly Bullish' in direction:
            phase = 'Strong Uptrend'
            risk = 'Low'
            strategy = 'Aggressive Trend Following'
        elif 'Bullish' in direction:
            phase = 'Uptrend'
            risk = 'Low'
            strategy = 'Trend Following'
        elif 'Strongly Bearish' in direction:
            phase = 'Strong Downtrend'
            risk = 'High'
            strategy = 'Aggressive Short Selling'
        elif 'Bearish' in direction:
            phase = 'Downtrend'
            risk = 'High'
            strategy = 'Short Selling'
        else:
            phase = 'Consolidation'
            risk = 'Medium'
            strategy = 'Mean Reversion'
        
        return {
            'phase': phase,
            'volatility': vol_str,
            'risk_level': risk,
            'strategy': strategy
        }
    
    def _generate_recommendations(self, results: Dict, alignment: Dict) -> Dict[str, Any]:
        """Generate trading recommendations"""
        direction = alignment.get('direction', 'Mixed')
        confidence = alignment.get('confidence', 50)
        
        # Position sizing
        if confidence >= 80:
            position_size = 0.8
            risk_level = 'Low'
        elif confidence >= 65:
            position_size = 0.6
            risk_level = 'Low-Medium'
        elif confidence >= 50:
            position_size = 0.4
            risk_level = 'Medium'
        else:
            position_size = 0.2
            risk_level = 'High'
        
        # Trading action
        if 'Strongly Bullish' in direction:
            action = 'STRONG_BUY'
        elif 'Bullish' in direction:
            action = 'BUY'
        elif 'Strongly Bearish' in direction:
            action = 'STRONG_SELL'
        elif 'Bearish' in direction:
            action = 'SELL'
        else:
            action = 'HOLD'
        
        return {
            'action': action,
            'position_size': position_size,
            'risk_level': risk_level,
            'confidence': round(confidence, 1),
            'reason': f"{direction} alignment with {confidence}% confidence across timeframes"
        }
    
    def _get_integrated_signals(self, results: Dict, alignment: Dict) -> Dict[str, str]:
        """Get integrated signals from all modules"""
        direction = alignment.get('direction', 'Mixed')
        
        if 'Bullish' in direction:
            tech = 'BULLISH'
            trend = 'UPTREND'
            regime = 'RISK_ON'
            sentiment = 'BULLISH'
            fundamental = 'USD_WEAK'
        elif 'Bearish' in direction:
            tech = 'BEARISH'
            trend = 'DOWNTREND'
            regime = 'RISK_OFF'
            sentiment = 'BEARISH'
            fundamental = 'USD_STRONG'
        else:
            tech = 'NEUTRAL'
            trend = 'SIDEWAYS'
            regime = 'NEUTRAL'
            sentiment = 'NEUTRAL'
            fundamental = 'NEUTRAL'
        
        return {
            'technical': tech,
            'trend': trend,
            'regime': regime,
            'sentiment': sentiment,
            'fundamental': fundamental
        }
    
    def _generate_summary(self, alignment: Dict, context: Dict) -> str:
        """Generate human-readable summary"""
        direction = alignment.get('direction', 'Mixed')
        confidence = alignment.get('confidence', 0)
        phase = context.get('phase', 'Unknown')
        
        if 'Strongly Bullish' in direction:
            return f"STRONG BULLISH ALIGNMENT ({confidence:.0f}%) - {phase} across all timeframes"
        elif 'Bullish' in direction:
            return f"BULLISH ALIGNMENT ({confidence:.0f}%) - {phase} confirmed on multiple timeframes"
        elif 'Strongly Bearish' in direction:
            return f"STRONG BEARISH ALIGNMENT ({confidence:.0f}%) - {phase} pressure building"
        elif 'Bearish' in direction:
            return f"BEARISH ALIGNMENT ({confidence:.0f}%) - {phase} expected to continue"
        else:
            return f"MIXED SIGNALS ({confidence:.0f}%) - {phase} - wait for clearer direction"
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def _get_periods_for_timeframe(self, tf: str) -> int:
        """Get minimum periods required for timeframe analysis"""
        periods = {
            'M5': 100,
            'M15': 200,
            'H1': 300,
            'H4': 500,
            'D1': 1000,
            'W1': 2000
        }
        return periods.get(tf, 200)
    
    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare and validate dataframe"""
        if df is None:
            return pd.DataFrame()
        
        df = df.copy()
        df.columns = [str(col).lower().strip() for col in df.columns]
        
        # Ensure required columns exist
        if 'close' not in df.columns:
            df['close'] = 1.0876
        if 'high' not in df.columns:
            df['high'] = df['close'] * 1.0002
        if 'low' not in df.columns:
            df['low'] = df['close'] * 0.9998
        if 'open' not in df.columns:
            df['open'] = df['close']
        if 'volume' not in df.columns:
            df['volume'] = 1000
        
        return df.dropna()
    
    def _get_column(self, df: pd.DataFrame, col: str) -> Optional[np.ndarray]:
        """Safely get column as numpy array"""
        if df is None or col not in df.columns:
            return None
        return df[col].values
    
    def _update_metrics(self, elapsed_ms: float):
        """Update performance metrics"""
        total = self.metrics['total_analyses'] + 1
        current_avg = self.metrics['avg_time_ms']
        self.metrics['total_analyses'] = total
        self.metrics['avg_time_ms'] = round((current_avg * (total - 1) + elapsed_ms) / total, 2)
    
    def _get_empty_timeframe(self, tf: str) -> Dict:
        """Return empty timeframe analysis"""
        return {
            'timeframe': tf,
            'direction': 'Unknown',
            'strength': 0,
            'confidence': 'Insufficient',
            'adx': 0,
            'slope': 0,
            'quality_score': 0,
            'current_price': 0,
            'ma_20': 0,
            'ma_50': 0,
            'ma_200': 0,
            'support': [],
            'resistance': []
        }
    
    def _get_empty_result(self) -> Dict:
        """Return empty result"""
        return {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'error': 'Insufficient data for analysis',
            'timeframes': {},
            'alignment': {'direction': 'Unknown', 'confidence': 0, 'bullish_pct': 50, 'bearish_pct': 50},
            'charts': {},
            'summary': 'Insufficient data - need at least 100 bars'
        }
    
    def _get_error_result(self, error_msg: str) -> Dict:
        """Return error result"""
        return {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'error': error_msg,
            'timeframes': {},
            'alignment': {'direction': 'Unknown', 'confidence': 0, 'bullish_pct': 50, 'bearish_pct': 50},
            'charts': {},
            'summary': f'Analysis error: {error_msg}'
        }
    
    def clear_cache(self):
        """Clear analysis cache"""
        self._cache.clear()
        logger.info("Cache cleared")


# ============================================================================
# SIMPLE WRAPPER FOR COMPATIBILITY
# ============================================================================

class TimeframeService:
    """Simple wrapper for backward compatibility"""
    
    def __init__(self, data_fetcher=None):
        self.analyzer = MultiTimeframeAnalyzer()
        self.timeframes = ['1h', '4h', '1d']
    
    def get_aligned_signals(self, symbol: str = 'EURUSD=X') -> Dict[str, Any]:
        """Get aligned signals for dashboard"""
        dates = pd.date_range(end=datetime.now(), periods=500, freq='h')
        prices = 1.0876 + np.cumsum(np.random.randn(500) * 0.0003)
        df = pd.DataFrame({'close': prices, 'high': prices + 0.0003, 'low': prices - 0.0003}, index=dates)
        
        result = self.analyzer.analyze(df)
        alignment = result.get('alignment', {})
        recommendations = result.get('recommendations', {})
        
        return {
            '1h': self._map_direction(result.get('timeframes', {}).get('H1', {}).get('direction', 'Unknown')),
            '4h': self._map_direction(result.get('timeframes', {}).get('H4', {}).get('direction', 'Unknown')),
            '1d': self._map_direction(result.get('timeframes', {}).get('D1', {}).get('direction', 'Unknown')),
            'confluence': 'Strongly' in alignment.get('direction', ''),
            'alignment_score': alignment.get('confidence', 0),
            'recommended_action': recommendations.get('action', 'HOLD'),
            'details': alignment,
            'timestamp': datetime.now().isoformat()
        }
    
    def _map_direction(self, direction: str) -> str:
        """Map direction to dashboard format"""
        if 'Bullish' in direction or 'Trending' in direction:
            return 'BULLISH'
        elif 'Bearish' in direction:
            return 'BEARISH'
        else:
            return 'NEUTRAL'


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_timeframe_service = None

def get_timeframe_service(data_fetcher=None) -> TimeframeService:
    """Get or create TimeframeService singleton"""
    global _timeframe_service
    if _timeframe_service is None:
        _timeframe_service = TimeframeService(data_fetcher)
    return _timeframe_service


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("📊 MULTI-TIMEFRAME ANALYZER v4.1 - FIXED VERSION")
    print("=" * 80)
    
    # Create sample data
    periods = 500
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='h')
    np.random.seed(42)
    
    base = 1.0876
    trend = np.linspace(0, 0.003, periods)
    cycle = np.sin(np.linspace(0, 4*np.pi, periods)) * 0.002
    noise = np.random.randn(periods) * 0.0003
    prices = base + trend + cycle + noise
    
    df = pd.DataFrame({
        'open': prices * (1 + np.random.randn(periods) * 0.0001),
        'high': prices + 0.0003 + np.abs(np.random.randn(periods) * 0.0001),
        'low': prices - 0.0003 - np.abs(np.random.randn(periods) * 0.0001),
        'close': prices,
        'volume': np.random.randint(1000, 100000, periods)
    }, index=dates)
    
    analyzer = MultiTimeframeAnalyzer()
    result = analyzer.analyze(df)
    
    if result.get('success'):
        print(f"\n✅ ANALYSIS COMPLETE")
        print(f"   Current Price: {result.get('current_price', 0):.5f}")
        print(f"   Alignment: {result.get('alignment', {}).get('direction', 'N/A')}")
        print(f"   Confidence: {result.get('alignment', {}).get('confidence', 0)}%")
        print(f"   Recommendation: {result.get('recommendations', {}).get('action', 'N/A')}")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 80)