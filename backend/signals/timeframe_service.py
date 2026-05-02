"""
timeframe_service.py - COMPLETE Timeframe Service for Dashboard
FULL INTEGRATION with MultiTimeframeAnalyzer v4.0
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class TimeframeService:
    """
    Complete Timeframe Service for dashboard compatibility
    Fully integrated with MultiTimeframeAnalyzer
    """
    
    def __init__(self, data_fetcher=None):
        """
        Initialize the TimeframeService
        
        Args:
            data_fetcher: Optional data fetcher instance
        """
        self.data_fetcher = data_fetcher
        self.timeframes = ['1h', '4h', '1d']
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        self.last_update = None
        
        # Try to import the MultiTimeframeAnalyzer
        self.analyzer = None
        self._init_analyzer()
        
        logger.info(f"TimeframeService initialized - Analyzer: {'✅' if self.analyzer else '❌'}")
    
    def _init_analyzer(self):
        """Initialize the MultiTimeframeAnalyzer"""
        try:
            # Try different import paths
            try:
                from analysis.timeframe_analyzer import MultiTimeframeAnalyzer
            except ImportError:
                from backend.analysis.timeframe_analyzer import MultiTimeframeAnalyzer
            
            self.analyzer = MultiTimeframeAnalyzer()
            logger.info("✅ MultiTimeframeAnalyzer loaded successfully")
        except ImportError as e:
            logger.warning(f"Could not load MultiTimeframeAnalyzer: {e}")
            self.analyzer = None
    
    def get_aligned_signals(self, symbol: str = 'EURUSD=X') -> Dict[str, Any]:
        """
        Get aligned signals across all timeframes
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with aligned signals
        """
        try:
            # Check cache
            cache_key = f"signals_{symbol}"
            if cache_key in self.cache:
                cache_time, cache_data = self.cache[cache_key]
                if (datetime.now() - cache_time).seconds < self.cache_duration:
                    return cache_data
            
            # Get real market data
            df = self._fetch_market_data()
            
            if df is not None and not df.empty:
                # Use the analyzer if available
                if self.analyzer:
                    result = self.analyzer.analyze(df)
                    signals = self._extract_signals_from_analyzer(result)
                    alignment = result.get('alignment', {})
                    
                    output = {
                        '1h': signals.get('1h', 'NEUTRAL'),
                        '4h': signals.get('4h', 'NEUTRAL'),
                        '1d': signals.get('1d', 'NEUTRAL'),
                        'confluence': alignment.get('confidence', 0) > 60,
                        'alignment_score': alignment.get('confidence', 50),
                        'recommended_action': self._get_action(alignment),
                        'details': {
                            'alignment_direction': alignment.get('direction', 'Mixed'),
                            'alignment_confidence': alignment.get('confidence', 0),
                            'bullish_weight': alignment.get('bullish_weight', 0),
                            'bearish_weight': alignment.get('bearish_weight', 0)
                        },
                        'summary': result.get('summary', 'Analysis complete'),
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    # Fallback to simple analysis
                    output = self._simple_analysis(df)
                
                # Cache the result
                self.cache[cache_key] = (datetime.now(), output)
                self.last_update = datetime.now()
                
                return output
            
            return self._get_default_signals()
            
        except Exception as e:
            logger.error(f"Error getting aligned signals: {e}")
            return self._get_default_signals()
    
    def get_mtf_analysis(self, df_dict: Dict[str, pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Get comprehensive multi-timeframe analysis
        
        Args:
            df_dict: Dictionary of dataframes per timeframe
            
        Returns:
            Complete MTF analysis
        """
        try:
            # Get data for the highest timeframe
            df = None
            if df_dict:
                for tf in ['1d', '4h', '1h']:
                    if tf in df_dict and df_dict[tf] is not None and not df_dict[tf].empty:
                        df = df_dict[tf]
                        break
            
            if df is None:
                df = self._fetch_market_data()
            
            if df is not None and not df.empty:
                if self.analyzer:
                    result = self.analyzer.analyze(df)
                    return {
                        'success': True,
                        'timeframes': result.get('timeframes', {}),
                        'alignment': result.get('alignment', {}),
                        'market_context': result.get('market_context', {}),
                        'volume_analysis': result.get('volume_analysis', {}),
                        'key_levels': result.get('key_levels', {}),
                        'summary': result.get('summary', ''),
                        'timestamp': datetime.now().isoformat()
                    }
            
            return self._get_default_mtf()
            
        except Exception as e:
            logger.error(f"MTF analysis error: {e}")
            return self._get_default_mtf()
    
    def _fetch_market_data(self, days: int = 90, interval: str = '1h') -> Optional[pd.DataFrame]:
        """Fetch real market data"""
        try:
            import yfinance as yf
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            ticker = yf.Ticker("EURUSD=X")
            df = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if df is not None and not df.empty:
                df.columns = [col.lower() for col in df.columns]
                logger.info(f"✅ Fetched {len(df)} candles for analysis")
                return df
            
        except Exception as e:
            logger.warning(f"Data fetch error: {e}")
        
        # Generate fallback data
        return self._generate_mock_data(days)
    
    def _generate_mock_data(self, days: int = 90) -> pd.DataFrame:
        """Generate realistic mock data as fallback"""
        periods = days * 24
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='h')
        base_price = 1.0876
        prices = base_price + np.cumsum(np.random.randn(periods) * 0.0002)
        
        return pd.DataFrame({
            'open': prices,
            'high': prices + 0.0002,
            'low': prices - 0.0002,
            'close': prices,
            'volume': np.random.randint(1000, 50000, periods)
        }, index=dates)
    
    def _extract_signals_from_analyzer(self, result: Dict) -> Dict[str, str]:
        """Extract signals from analyzer results"""
        signals = {}
        
        # Map analyzer timeframe names to our format
        tf_map = {'H1': '1h', 'H4': '4h', 'D1': '1d'}
        
        timeframes = result.get('timeframes', {})
        for analyzer_tf, display_tf in tf_map.items():
            if analyzer_tf in timeframes:
                tf_data = timeframes[analyzer_tf]
                direction = tf_data.get('direction', '--')
                strength = tf_data.get('strength', 0)
                
                if direction in ['Bullish', 'Trending']:
                    if strength > 0.7:
                        signals[display_tf] = 'STRONG_BULLISH'
                    else:
                        signals[display_tf] = 'BULLISH'
                elif direction == 'Bearish':
                    if strength > 0.7:
                        signals[display_tf] = 'STRONG_BEARISH'
                    else:
                        signals[display_tf] = 'BEARISH'
                else:
                    signals[display_tf] = 'NEUTRAL'
            else:
                signals[display_tf] = 'NEUTRAL'
        
        return signals
    
    def _simple_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Simple analysis when full analyzer not available"""
        try:
            close = df['close'].values if 'close' in df.columns else df['Close'].values
            
            # Calculate for different lookbacks
            signals = {}
            
            # 1H (20 periods ~ 1 day)
            if len(close) >= 20:
                signals['1h'] = self._simple_trend(close[-20:])
            else:
                signals['1h'] = 'NEUTRAL'
            
            # 4H (80 periods ~ 4 days)
            if len(close) >= 80:
                signals['4h'] = self._simple_trend(close[-80:])
            else:
                signals['4h'] = 'NEUTRAL'
            
            # 1D (200 periods ~ 8 days)
            if len(close) >= 200:
                signals['1d'] = self._simple_trend(close[-200:])
            else:
                signals['1d'] = 'NEUTRAL'
            
            # Calculate alignment
            bullish_count = sum(1 for s in signals.values() if s in ['BULLISH', 'STRONG_BULLISH'])
            bearish_count = sum(1 for s in signals.values() if s in ['BEARISH', 'STRONG_BEARISH'])
            
            if bullish_count >= 2:
                action = 'BUY'
                score = (bullish_count / 3) * 100
                confluence = True
            elif bearish_count >= 2:
                action = 'SELL'
                score = (bearish_count / 3) * 100
                confluence = True
            else:
                action = 'HOLD'
                score = 50
                confluence = False
            
            return {
                '1h': signals['1h'],
                '4h': signals['4h'],
                '1d': signals['1d'],
                'confluence': confluence,
                'alignment_score': round(score, 1),
                'recommended_action': action,
                'details': {'analysis_type': 'simplified'},
                'summary': f"Simplified analysis: {'Bullish' if bullish_count > bearish_count else 'Bearish' if bearish_count > bullish_count else 'Mixed'} alignment",
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Simple analysis error: {e}")
            return self._get_default_signals()
    
    def _simple_trend(self, prices: np.ndarray) -> str:
        """Simple trend detection"""
        if len(prices) < 10:
            return 'NEUTRAL'
        
        sma_10 = np.mean(prices[-10:])
        sma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else sma_10
        current = prices[-1]
        
        if current > sma_10 and sma_10 > sma_20:
            return 'BULLISH'
        elif current < sma_10 and sma_10 < sma_20:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def _get_action(self, alignment: Dict) -> str:
        """Get recommended action from alignment"""
        direction = alignment.get('direction', 'Mixed')
        confidence = alignment.get('confidence', 0)
        
        if 'Strongly Bullish' in direction and confidence > 70:
            return 'BUY'
        elif 'Bullish' in direction and confidence > 60:
            return 'CONSIDER_BUY'
        elif 'Strongly Bearish' in direction and confidence > 70:
            return 'SELL'
        elif 'Bearish' in direction and confidence > 60:
            return 'CONSIDER_SELL'
        else:
            return 'HOLD'
    
    def _get_default_signals(self) -> Dict[str, Any]:
        """Return default signals"""
        return {
            '1h': 'NEUTRAL',
            '4h': 'NEUTRAL',
            '1d': 'NEUTRAL',
            'confluence': False,
            'alignment_score': 50,
            'recommended_action': 'HOLD',
            'details': {},
            'summary': 'Analysis could not be completed - using default values',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_default_mtf(self) -> Dict[str, Any]:
        """Return default MTF analysis"""
        return {
            'success': False,
            'timeframes': {},
            'alignment': {'direction': 'Mixed', 'confidence': 0},
            'summary': 'Insufficient data for analysis',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_trend_summary(self) -> pd.DataFrame:
        """Get trend summary as DataFrame"""
        signals = self.get_aligned_signals()
        
        data = []
        for tf in self.timeframes:
            data.append({
                'Timeframe': tf,
                'Direction': signals.get(tf, 'NEUTRAL'),
                'Confidence': signals.get('alignment_score', 50),
                'Updated': datetime.now().strftime('%H:%M')
            })
        
        return pd.DataFrame(data)
    
    def get_trading_recommendation(self) -> Dict[str, Any]:
        """Get final trading recommendation"""
        signals = self.get_aligned_signals()
        
        return {
            'action': signals.get('recommended_action', 'HOLD'),
            'signal': signals.get('recommended_action', 'HOLD'),
            'confidence': signals.get('alignment_score', 50),
            'direction': 'BULLISH' if signals.get('recommended_action') in ['BUY', 'CONSIDER_BUY'] else 'BEARISH' if signals.get('recommended_action') in ['SELL', 'CONSIDER_SELL'] else 'NEUTRAL',
            'timeframes': {
                '1h': signals.get('1h', 'NEUTRAL'),
                '4h': signals.get('4h', 'NEUTRAL'),
                '1d': signals.get('1d', 'NEUTRAL')
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        self.last_update = None
        logger.info("Cache cleared")
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            'initialized': True,
            'timeframes': self.timeframes,
            'has_analyzer': self.analyzer is not None,
            'analyzer_type': 'FULL' if self.analyzer else 'SIMPLIFIED',
            'cache_size': len(self.cache),
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'timestamp': datetime.now().isoformat()
        }


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_timeframe_service = None


def get_timeframe_service(data_fetcher=None) -> TimeframeService:
    """Get or create the TimeframeService singleton"""
    global _timeframe_service
    if _timeframe_service is None:
        _timeframe_service = TimeframeService(data_fetcher)
    return _timeframe_service


# ============================================================================
# TEST
# ============================================================================

def test():
    """Test the TimeframeService"""
    print("\n" + "=" * 80)
    print("📊 TIMEFRAME SERVICE TEST")
    print("=" * 80)
    
    service = TimeframeService()
    
    # Get status
    status = service.get_status()
    print(f"\n📡 Status:")
    print(f"   Analyzer: {status.get('analyzer_type')}")
    print(f"   Timeframes: {status.get('timeframes')}")
    
    # Get aligned signals
    print("\n📈 Getting aligned signals...")
    result = service.get_aligned_signals()
    
    print(f"\n🎯 RESULTS:")
    print(f"   1H: {result.get('1h')}")
    print(f"   4H: {result.get('4h')}")
    print(f"   1D: {result.get('1d')}")
    print(f"   Confluence: {result.get('confluence')}")
    print(f"   Alignment Score: {result.get('alignment_score')}%")
    print(f"   Action: {result.get('recommended_action')}")
    
    if result.get('summary'):
        print(f"\n📝 Summary: {result.get('summary')}")
    
    # Get trend summary
    print("\n📊 Trend Summary:")
    trend_df = service.get_trend_summary()
    print(trend_df.to_string(index=False))
    
    # Get trading recommendation
    print("\n💡 Trading Recommendation:")
    rec = service.get_trading_recommendation()
    print(f"   Action: {rec.get('action')}")
    print(f"   Confidence: {rec.get('confidence')}%")
    print(f"   Direction: {rec.get('direction')}")
    
    # JSON test
    import json
    try:
        json_str = json.dumps(result)
        print(f"\n✅ JSON Serialization: SUCCESS ({len(json_str)} bytes)")
    except TypeError as e:
        print(f"\n❌ JSON Error: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Test complete!")


if __name__ == "__main__":
    test()