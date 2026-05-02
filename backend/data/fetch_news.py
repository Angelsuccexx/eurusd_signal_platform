"""
fetch_news.py - ULTIMATE REAL News Fetcher for EUR/USD
Version: 4.1.0 - REAL API Integration + Fixed JSON Serialization
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any
import os
import time
from collections import deque, Counter
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import platform configuration
import sys
sys.path.append(str(Path(__file__).parent.parent))

try:
    from backend.config import Config
    PLATFORM_AVAILABLE = True
except ImportError:
    PLATFORM_AVAILABLE = False
    Config = None

logger = logging.getLogger(__name__)


class NewsFetcher:
    """
    REAL News Fetcher v4.1 - With API Integration & Fixed JSON
    """
    
    def __init__(self):
        # Load REAL API keys from .env
        self.news_api_key = os.getenv('NEWS_API_KEY', '')
        self.gnews_api_key = os.getenv('GNEWS_API_KEY', '')
        
        # Check if API keys are configured properly
        self.has_real_api = bool(self.news_api_key and self.news_api_key != 'your_newsapi_key_here') or \
                           bool(self.gnews_api_key and self.gnews_api_key != 'your_gnews_key_here')
        
        # Platform config
        if PLATFORM_AVAILABLE and Config:
            self.symbol = getattr(Config, 'SYMBOL', "EURUSD=X")
            self.platform_name = getattr(Config, 'PLATFORM_NAME', "EUR/USD Signal Platform")
        else:
            self.symbol = "EURUSD=X"
            self.platform_name = "EUR/USD Signal Platform"
        
        # Cache
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1
        
        # Keywords for relevance
        self.keywords = {
            'high_impact': ['ecb', 'fed', 'rate', 'interest', 'fomc', 'nonfarm', 'inflation', 'gdp'],
            'medium_impact': ['eurusd', 'euro', 'dollar', 'forex', 'currency'],
            'low_impact': ['analysis', 'market', 'trading', 'outlook']
        }
        
        # Topics
        self.topics = {
            'Monetary Policy': ['ecb', 'fed', 'rate', 'interest', 'fomc', 'central bank'],
            'Economic Data': ['gdp', 'inflation', 'cpi', 'jobs', 'employment', 'manufacturing'],
            'Market Analysis': ['technical', 'analysis', 'forecast', 'outlook'],
            'Risk Sentiment': ['risk', 'safe haven', 'volatility', 'uncertainty']
        }
        
        # History
        self.sentiment_history = deque(maxlen=500)
        
        # Lazy imports
        self._vader = None
        
        self._log_status()
    
    def _log_status(self):
        """Log API status"""
        print("="*60)
        print("📡 REAL NEWS API STATUS:")
        if self.news_api_key and self.news_api_key != 'your_newsapi_key_here':
            print(f"   NewsAPI: ✓ CONFIGURED (key: {self.news_api_key[:8]}...)")
        else:
            print("   NewsAPI: ✗ NOT CONFIGURED - Add NEWS_API_KEY to .env")
        
        if self.gnews_api_key and self.gnews_api_key != 'your_gnews_key_here':
            print(f"   GNews API: ✓ CONFIGURED (key: {self.gnews_api_key[:8]}...)")
        else:
            print("   GNews API: ✗ NOT CONFIGURED - Add GNEWS_API_KEY to .env")
        
        if self.has_real_api:
            print("\n🚀 REAL NEWS MODE ACTIVE - Fetching from live APIs")
        else:
            print("\n⚠️ MOCK MODE - Add API keys to .env for real news")
        print("="*60)
    
    def fetch_all_sources(self, days_back: int = 7, use_cache: bool = True) -> Dict[str, Any]:
        """Fetch news from real APIs"""
        print(f"\n📰 Fetching REAL news for past {days_back} days...")
        
        # Check cache
        cache_key = f"news_{days_back}"
        if use_cache and cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_duration:
                print("📦 Returning cached news")
                return cache_data
        
        articles = []
        sources_used = []
        
        # Try REAL APIs first
        if self.gnews_api_key and self.gnews_api_key != 'your_gnews_key_here':
            print("🌐 Fetching from GNews API...")
            gnews_articles = self._fetch_gnews_real(days_back)
            if gnews_articles:
                articles.extend(gnews_articles)
                sources_used.append('gnews')
                print(f"   ✅ GNews: {len(gnews_articles)} articles")
        
        if self.news_api_key and self.news_api_key != 'your_newsapi_key_here' and not articles:
            print("🌐 Fetching from NewsAPI...")
            newsapi_articles = self._fetch_newsapi_real(days_back)
            if newsapi_articles:
                articles.extend(newsapi_articles)
                sources_used.append('newsapi')
                print(f"   ✅ NewsAPI: {len(newsapi_articles)} articles")
        
        # Fallback to enhanced mock if no real articles
        if not articles:
            print("⚠️ No real news available - using enhanced mock data")
            articles = self._generate_enhanced_mock()
            sources_used.append('mock')
        
        # Process articles
        articles = self._deduplicate(articles)
        articles = self._process_articles(articles)
        articles.sort(key=lambda x: x.get('published', ''), reverse=True)
        
        # Generate all data
        charts = self._generate_charts(articles)
        sentiment_summary = self._get_sentiment_summary(articles)
        topic_analysis = self._get_topic_analysis(articles)
        
        # Convert numpy types to Python native for JSON
        result = {
            'success': True,
            'articles': self._to_json(articles[:30]),
            'total': int(len(articles)),
            'sources': sources_used,
            'timestamp': datetime.now().isoformat(),
            'platform': self.platform_name,
            'has_real_data': self.has_real_api and sources_used != ['mock'],
            'sentiment_summary': self._to_json(sentiment_summary),
            'topic_analysis': self._to_json(topic_analysis),
            'charts': self._to_json(charts),
            'stats': self._to_json(self._get_stats(articles))
        }
        
        # Cache
        if use_cache:
            self.cache[cache_key] = (time.time(), result)
        
        print(f"\n✅ Total: {len(articles)} articles from {', '.join(sources_used)}")
        return result
    
    def _fetch_gnews_real(self, days_back: int) -> List[Dict]:
        """Fetch REAL news from GNews API"""
        try:
            self._rate_limit()
            
            queries = ['EURUSD', 'euro dollar', 'ECB', 'Federal Reserve']
            all_articles = []
            
            for query in queries:
                url = "https://gnews.io/api/v4/search"
                params = {
                    'q': query,
                    'lang': 'en',
                    'max': 10,
                    'apikey': self.gnews_api_key,
                    'from': (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get('articles', []):
                        all_articles.append({
                            'title': article.get('title', ''),
                            'source': article.get('source', {}).get('name', 'GNews'),
                            'published': article.get('publishedAt', ''),
                            'url': article.get('url', ''),
                            'description': article.get('description', ''),
                            'content': article.get('content', '')
                        })
                time.sleep(0.5)
            
            return all_articles
            
        except Exception as e:
            print(f"   GNews error: {e}")
            return []
    
    def _fetch_newsapi_real(self, days_back: int) -> List[Dict]:
        """Fetch REAL news from NewsAPI"""
        try:
            self._rate_limit()
            
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': 'EUR/USD OR "euro dollar" OR ECB OR "Federal Reserve"',
                'from': from_date,
                'language': 'en',
                'sortBy': 'relevancy',
                'pageSize': 30,
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                for article in data.get('articles', []):
                    articles.append({
                        'title': article.get('title', ''),
                        'source': article.get('source', {}).get('name', 'NewsAPI'),
                        'published': article.get('publishedAt', ''),
                        'url': article.get('url', ''),
                        'description': article.get('description', ''),
                        'content': article.get('content', '')
                    })
                return articles
            else:
                print(f"   NewsAPI error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   NewsAPI error: {e}")
            return []
    
    def _generate_enhanced_mock(self) -> List[Dict]:
        """Generate enhanced mock news (for testing without API keys)"""
        templates = [
            {'title': 'ECB signals potential rate cut as inflation moderates', 'sentiment': 'negative', 'relevance': 0.9, 'topic': 'Monetary Policy'},
            {'title': 'US jobs data beats expectations, dollar strengthens', 'sentiment': 'positive', 'relevance': 0.85, 'topic': 'Economic Data'},
            {'title': 'EUR/USD technical analysis: key levels to watch', 'sentiment': 'neutral', 'relevance': 0.7, 'topic': 'Market Analysis'},
            {'title': 'German industrial production falls, euro under pressure', 'sentiment': 'negative', 'relevance': 0.75, 'topic': 'Economic Data'},
            {'title': 'Fed officials divided on timing of rate cuts', 'sentiment': 'neutral', 'relevance': 0.8, 'topic': 'Monetary Policy'},
            {'title': 'Eurozone GDP revised higher, euro rallies', 'sentiment': 'positive', 'relevance': 0.85, 'topic': 'Economic Data'},
            {'title': 'US inflation data in focus for currency markets', 'sentiment': 'neutral', 'relevance': 0.9, 'topic': 'Economic Data'},
            {'title': 'ECB\'s Lagarde: progress on inflation but not done yet', 'sentiment': 'neutral', 'relevance': 0.8, 'topic': 'Monetary Policy'},
        ]
        
        import random
        articles = []
        now = datetime.now()
        sources = ['Bloomberg', 'Reuters', 'CNBC', 'Financial Times', 'WSJ']
        
        for i, template in enumerate(random.sample(templates, min(8, len(templates)))):
            articles.append({
                'title': template['title'],
                'source': random.choice(sources),
                'published': (now - timedelta(hours=random.randint(1, 168))).isoformat(),
                'url': f'https://example.com/news/{i}',
                'description': f'Analysis of {template["title"][:50]}...',
                'content': f'Full coverage of {template["title"]}...',
                'mock_topic': template['topic'],
                'mock_sentiment': template['sentiment']
            })
        
        return articles
    
    def _process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process articles with sentiment analysis"""
        processed = []
        for article in articles:
            title = article.get('title', '')
            content = article.get('content', article.get('description', ''))
            
            # Use mock sentiment if available
            if 'mock_sentiment' in article:
                sentiment = article['mock_sentiment']
            else:
                sentiment = self._analyze_sentiment(title)
            
            # Calculate relevance
            relevance = self._calculate_relevance(title)
            
            # Determine topic
            if 'mock_topic' in article:
                topics = [article['mock_topic']]
            else:
                topics = self._extract_topics(title + ' ' + content)
            
            processed.append({
                'title': title[:150],
                'source': article.get('source', 'Unknown'),
                'published': article.get('published', ''),
                'url': article.get('url', ''),
                'description': (article.get('description', '') or '')[:300],
                'sentiment': sentiment,
                'relevance': round(relevance, 2),
                'topics': topics[:2]
            })
        
        return processed
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment using keywords (fast fallback)"""
        if not text:
            return 'neutral'
        
        text_lower = text.lower()
        
        positive = ['surge', 'rally', 'gain', 'rise', 'up', 'positive', 'bull', 'strong', 'higher']
        negative = ['drop', 'fall', 'decline', 'down', 'negative', 'bear', 'weak', 'lower', 'crash']
        
        pos_count = sum(1 for w in positive if w in text_lower)
        neg_count = sum(1 for w in negative if w in text_lower)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'
    
    def _calculate_relevance(self, text: str) -> float:
        """Calculate relevance to EUR/USD"""
        text_lower = text.lower()
        score = 0.0
        
        for keyword in self.keywords['high_impact']:
            if keyword in text_lower:
                score += 0.5
                break
        
        for keyword in self.keywords['medium_impact']:
            if keyword in text_lower:
                score += 0.3
                break
        
        return min(1.0, score)
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        text_lower = text.lower()
        found = []
        
        for topic, keywords in self.topics.items():
            if any(k in text_lower for k in keywords):
                found.append(topic)
        
        return found if found else ['General']
    
    def _get_sentiment_summary(self, articles: List[Dict]) -> Dict:
        """Get sentiment summary"""
        if not articles:
            return {'overall': 'neutral', 'score': 0}
        
        sentiments = [a.get('sentiment', 'neutral') for a in articles]
        positive = sentiments.count('positive')
        negative = sentiments.count('negative')
        neutral = sentiments.count('neutral')
        total = len(articles)
        
        score = (positive - negative) / max(total, 1)
        
        return {
            'overall': 'positive' if score > 0.2 else 'negative' if score < -0.2 else 'neutral',
            'score': round(score, 3),
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'total': total,
            'positive_pct': round(positive / total * 100, 1) if total > 0 else 0,
            'negative_pct': round(negative / total * 100, 1) if total > 0 else 0,
            'neutral_pct': round(neutral / total * 100, 1) if total > 0 else 0
        }
    
    def _get_topic_analysis(self, articles: List[Dict]) -> Dict:
        """Get topic analysis"""
        all_topics = []
        for a in articles:
            all_topics.extend(a.get('topics', ['General']))
        
        topic_counts = Counter(all_topics)
        
        return {
            'top_topics': [{'topic': k, 'count': v} for k, v in topic_counts.most_common(5)],
            'unique_topics': len(topic_counts)
        }
    
    def _get_stats(self, articles: List[Dict]) -> Dict:
        """Get statistics"""
        if not articles:
            return {'total': 0}
        
        relevances = [a.get('relevance', 0) for a in articles if isinstance(a.get('relevance'), (int, float))]
        
        return {
            'total': len(articles),
            'avg_relevance': round(sum(relevances) / max(len(relevances), 1), 2),
            'sources': list(set(a.get('source', '') for a in articles))
        }
    
    def _generate_charts(self, articles: List[Dict]) -> Dict:
        """Generate chart data"""
        sentiments = [a.get('sentiment', 'neutral') for a in articles]
        sentiment_counts = Counter(sentiments)
        
        topics = []
        for a in articles:
            topics.extend(a.get('topics', ['General']))
        topic_counts = Counter(topics)
        
        return {
            'sentiment_pie': {
                'type': 'pie',
                'data': [
                    {'name': 'Positive', 'value': sentiment_counts.get('positive', 0), 'color': '#00ff88'},
                    {'name': 'Negative', 'value': sentiment_counts.get('negative', 0), 'color': '#ff4444'},
                    {'name': 'Neutral', 'value': sentiment_counts.get('neutral', 0), 'color': '#ffaa00'}
                ]
            },
            'topic_bar': {
                'type': 'bar',
                'data': [{'name': k, 'value': v} for k, v in topic_counts.most_common(5)]
            },
            'gauge': {
                'type': 'gauge',
                'value': (sentiment_counts.get('positive', 0) - sentiment_counts.get('negative', 0)) / max(len(articles), 1) * 100,
                'min': -100,
                'max': 100
            }
        }
    
    def _deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicates"""
        seen = set()
        unique = []
        for a in articles:
            url = a.get('url', '')
            if url and url not in seen:
                seen.add(url)
                unique.append(a)
        return unique
    
    def _rate_limit(self):
        """Rate limiting"""
        now = time.time()
        if now - self.last_request_time < self.min_request_interval:
            time.sleep(self.min_request_interval - (now - self.last_request_time))
        self.last_request_time = time.time()
    
    def _to_json(self, obj):
        """Convert to JSON serializable - FIXED for numpy types"""
        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {self._to_json(k): self._to_json(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._to_json(i) for i in obj]
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)
    
    def clear_cache(self):
        """Clear cache"""
        self.cache.clear()
        print("Cache cleared")


# ============================================================================
# SINGLETON
# ============================================================================

_news_fetcher = None

def get_news_fetcher() -> NewsFetcher:
    global _news_fetcher
    if _news_fetcher is None:
        _news_fetcher = NewsFetcher()
    return _news_fetcher


# ============================================================================
# TEST
# ============================================================================

def test():
    """Test the news fetcher"""
    print("\n" + "="*80)
    print("📰 REAL NEWS FETCHER v4.1 - TEST")
    print("="*80)
    
    fetcher = NewsFetcher()
    
    print("\n📡 Fetching news...")
    result = fetcher.fetch_all_sources(days_back=3, use_cache=False)
    
    print(f"\n✅ Fetch complete!")
    print(f"   Success: {result['success']}")
    print(f"   Total articles: {result['total']}")
    print(f"   Sources: {', '.join(result['sources'])}")
    print(f"   Real data: {result['has_real_data']}")
    
    print(f"\n💬 Sentiment Summary:")
    sentiment = result.get('sentiment_summary', {})
    print(f"   Overall: {sentiment.get('overall', 'N/A')}")
    print(f"   Score: {sentiment.get('score', 0)}")
    print(f"   Distribution: +{sentiment.get('positive', 0)} / -{sentiment.get('negative', 0)} / ~{sentiment.get('neutral', 0)}")
    print(f"   Positive/Negative %: {sentiment.get('positive_pct', 0)}% / {sentiment.get('negative_pct', 0)}%")
    
    print(f"\n📈 TOPICS:")
    topics = result.get('topic_analysis', {})
    for topic in topics.get('top_topics', [])[:3]:
        print(f"   {topic['topic']}: {topic['count']} articles")
    
    print(f"\n📋 Sample Articles:")
    for i, article in enumerate(result.get('articles', [])[:3], 1):
        print(f"\n   {i}. {article.get('title', '')[:70]}...")
        print(f"      Sentiment: {article.get('sentiment', 'N/A')} | Relevance: {article.get('relevance', 0)}")
        print(f"      Source: {article.get('source', 'Unknown')}")
    
    # Test JSON serialization
    import json
    try:
        json_str = json.dumps(result)
        print(f"\n✅ JSON Serialization: SUCCESS ({len(json_str)} bytes)")
    except TypeError as e:
        print(f"\n❌ JSON Serialization: FAILED - {e}")
    
    print("\n" + "="*80)
    print("✅ Test completed!")


if __name__ == "__main__":
    test()