/**
 * API Service for EUR/USD Platform
 * Version: 3.1 - Added FCS API & Calendarific API support for market holidays and correlations
 */

const API_BASE = '/api';

class ApiService {
    // Cache storage
    static cache = new Map();
    static cacheDuration = 30000; // 30 seconds cache
    
    // Retry configuration
    static maxRetries = 3;
    static retryDelay = 1000;
    
    // Connection status
    static isOnline = navigator.onLine;
    static pendingRequests = new Map();
    static eventSource = null;
    static webSocket = null;
    
    // Helper to get cache key
    static getCacheKey(endpoint, params = {}) {
        return `${endpoint}_${JSON.stringify(params)}`;
    }
    
    // Check if cache is valid
    static isCacheValid(cacheEntry) {
        return cacheEntry && (Date.now() - cacheEntry.timestamp) < this.cacheDuration;
    }
    
    // Generic GET with caching and retry
    static async get(endpoint, options = { useCache: true, retries: 3 }) {
        const cacheKey = this.getCacheKey(endpoint);
        
        // Check cache
        if (options.useCache !== false) {
            const cached = this.cache.get(cacheKey);
            if (this.isCacheValid(cached)) {
                console.log(`📦 Cache hit: ${endpoint}`);
                return { success: true, data: cached.data, cached: true, fromCache: true };
            }
        }
        
        // Retry logic
        let lastError = null;
        for (let attempt = 1; attempt <= (options.retries || this.maxRetries); attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 15000);
                
                const startTime = performance.now();
                const response = await fetch(`${API_BASE}${endpoint}`, {
                    signal: controller.signal
                });
                clearTimeout(timeoutId);
                
                const fetchTime = performance.now() - startTime;
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                
                // Store in cache
                if (options.useCache !== false && data && !data.error) {
                    this.cache.set(cacheKey, {
                        data: data,
                        timestamp: Date.now(),
                        fetchTime: fetchTime
                    });
                }
                
                console.log(`✅ API Success: ${endpoint} (${fetchTime.toFixed(0)}ms)`);
                return { success: true, data, fetchTime, cached: false };
                
            } catch (error) {
                lastError = error;
                console.warn(`⚠️ API Attempt ${attempt} failed: ${endpoint} - ${error.message}`);
                
                if (attempt < (options.retries || this.maxRetries)) {
                    await this.delay(this.retryDelay * attempt);
                }
            }
        }
        
        console.error(`❌ API Error: ${endpoint}`, lastError);
        
        // Try to return stale cache if available
        const staleCache = this.cache.get(this.getCacheKey(endpoint));
        if (staleCache) {
            console.log(`📦 Returning stale cache for: ${endpoint}`);
            return { success: true, data: staleCache.data, cached: true, stale: true };
        }
        
        return { success: false, error: lastError.message };
    }
    
    // Generic POST
    static async post(endpoint, body, options = {}) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 15000);
            
            const startTime = performance.now();
            const response = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            
            const fetchTime = performance.now() - startTime;
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log(`✅ API POST Success: ${endpoint} (${fetchTime.toFixed(0)}ms)`);
            return { success: true, data, fetchTime };
            
        } catch (error) {
            console.error(`❌ API POST Error: ${endpoint}`, error);
            return { success: false, error: error.message };
        }
    }
    
    // Delay helper for retries
    static delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // Clear cache for specific endpoint or all
    static clearCache(endpoint = null) {
        if (endpoint) {
            for (const key of this.cache.keys()) {
                if (key.startsWith(endpoint)) {
                    this.cache.delete(key);
                }
            }
            console.log(`🗑️ Cache cleared for: ${endpoint}`);
        } else {
            this.cache.clear();
            console.log(`🗑️ All cache cleared`);
        }
    }
    
    // Check connection status
    static checkConnection() {
        this.isOnline = navigator.onLine;
        if (!this.isOnline) {
            console.warn('⚠️ Network connection lost');
        }
        return this.isOnline;
    }
    
    // Setup online/offline listeners
    static setupNetworkListeners() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            console.log('🟢 Network connection restored');
            this.clearCache();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            console.log('🔴 Network connection lost');
        });
    }
    
    // ============================================================
    // MARKET DATA ENDPOINTS (FCS API Integration)
    // ============================================================
    
    static getPrice() {
        return this.get('/price');
    }
    
    static getCurrentPrice() {
        return this.get('/current-price');
    }
    
    static getMarketData(days = 30) {
        return this.get(`/market-data?days=${days}`);
    }
    
    // Get real-time price with shorter cache (FCS API)
    static getRealTimePrice() {
        return this.get('/price', { useCache: false });
    }
    
    // Get 24h stats from FCS API
    static get24hStats() {
        return this.get('/price/24h-stats');
    }
    
    // Get historical candlestick data
    static getHistoricalData(interval = '1h', limit = 100) {
        return this.get(`/price/historical?interval=${interval}&limit=${limit}`);
    }
    
    // ============================================================
    // MARKET HOLIDAYS (Calendarific API)
    // ============================================================
    
    static getMarketHolidays(year = null, limit = 12) {
        let url = '/market-holidays';
        const params = [];
        if (year) params.push(`year=${year}`);
        if (limit) params.push(`limit=${limit}`);
        if (params.length) url += '?' + params.join('&');
        return this.get(url);
    }
    
    static getUpcomingHolidays(daysAhead = 90) {
        return this.get(`/market-holidays/upcoming?days=${daysAhead}`);
    }
    
    static getHolidaysByCountry(countryCode) {
        return this.get(`/market-holidays?country=${countryCode}`);
    }
    
    // ============================================================
    // CORRELATIONS (FCS API + Calculated)
    // ============================================================
    
    static getCorrelations() {
        return this.get('/correlations');
    }
    
    static getPairCorrelation(pair1, pair2, days = 30) {
        return this.get(`/correlations/${pair1}/${pair2}?days=${days}`);
    }
    
    // ============================================================
    // ANALYSIS ENDPOINTS
    // ============================================================
    
    static getTechnical() {
        return this.get('/technical');
    }
    
    static getFundamental() {
        return this.get('/fundamental');
    }
    
    static getSentiment() {
        return this.get('/sentiment');
    }
    
    static getTrend() {
        return this.get('/trend');
    }
    
    static getRegime() {
        return this.get('/regime');
    }
    
    static getMTF() {
        return this.get('/mtf');
    }
    
    static getUnified() {
        return this.get('/unified');
    }
    
    // ============================================================
    // SIGNAL & RISK ENDPOINTS
    // ============================================================
    
    static getSignal() {
        return this.get('/signal');
    }
    
    static getQuickSignal() {
        return this.get('/quick-signal');
    }
    
    static getRisk() {
        return this.get('/risk');
    }
    
    // ============================================================
    // NEWS & CALENDAR ENDPOINTS
    // ============================================================
    
    static getNews(days = 7) {
        return this.get(`/news?days=${days}`);
    }
    
    static getEconomicCalendar(days = 30) {
        return this.get(`/economic-calendar?days=${days}`);
    }
    
    static getHighImpactEvents() {
        return this.get('/economic-calendar?impact=HIGH');
    }
    
    // ============================================================
    // DASHBOARD & SYSTEM ENDPOINTS
    // ============================================================
    
    static getDashboardSummary() {
        return this.get('/dashboard-summary');
    }
    
    static getHealth() {
        return this.get('/health');
    }
    
    static getConfig() {
        return this.get('/config');
    }
    
    // Get API status (FCS, Calendarific, etc.)
    static getAPIStatus() {
        return this.get('/api-status');
    }
    
    // ============================================================
    // AI CHAT ENDPOINTS
    // ============================================================
    
    static async sendChatMessage(message) {
        return this.post('/ai-chat', { message });
    }
    
    static getChatContext() {
        return this.get('/ai-chat/context');
    }
    
    // ============================================================
    // BATCH REQUESTS (Parallel fetching)
    // ============================================================
    
    static async getAllMarketData() {
        const endpoints = ['/price', '/technical', '/signal', '/news?days=3', '/regime', '/correlations', '/market-holidays'];
        const results = await Promise.all(endpoints.map(ep => this.get(ep)));
        
        return {
            success: results.every(r => r.success),
            price: results[0]?.data,
            technical: results[1]?.data,
            signal: results[2]?.data,
            news: results[3]?.data,
            regime: results[4]?.data,
            correlations: results[5]?.data,
            marketHolidays: results[6]?.data,
            timestamp: new Date().toISOString()
        };
    }
    
    static async getAnalysisSuite() {
        const endpoints = ['/technical', '/fundamental', '/sentiment', '/trend', '/regime', '/risk'];
        const results = await Promise.all(endpoints.map(ep => this.get(ep)));
        
        return {
            success: results.every(r => r.success),
            technical: results[0]?.data,
            fundamental: results[1]?.data,
            sentiment: results[2]?.data,
            trend: results[3]?.data,
            regime: results[4]?.data,
            risk: results[5]?.data,
            timestamp: new Date().toISOString()
        };
    }
    
    static async getWeekendAnalysis() {
        const [priceData, technicalData, regimeData, holidayData] = await Promise.all([
            this.getPrice(),
            this.getTechnical(),
            this.getRegime(),
            this.getMarketHolidays()
        ]);
        
        return {
            success: true,
            price: priceData.data?.price || 1.1750,
            technical: technicalData.data,
            regime: regimeData.data,
            marketHolidays: holidayData.data?.holidays || [],
            timestamp: new Date().toISOString()
        };
    }
    
    static async getFullDashboard() {
        const [price, signal, technical, sentiment, regime, correlations, holidays, events] = await Promise.all([
            this.getPrice(),
            this.getSignal(),
            this.getTechnical(),
            this.getSentiment(),
            this.getRegime(),
            this.getCorrelations(),
            this.getMarketHolidays(),
            this.getEconomicCalendar()
        ]);
        
        return {
            success: price.success && signal.success,
            price: price.data,
            signal: signal.data,
            technical: technical.data,
            sentiment: sentiment.data,
            regime: regime.data,
            correlations: correlations.data,
            marketHolidays: holidays.data,
            economicEvents: events.data,
            timestamp: new Date().toISOString()
        };
    }
    
    // ============================================================
    // REAL-TIME UPDATES (Server-Sent Events)
    // ============================================================
    
    static connectEventSource(onMessage, onError) {
        if (typeof EventSource === 'undefined') {
            console.warn('EventSource not supported');
            return null;
        }
        
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        this.eventSource = new EventSource(`${API_BASE}/events`);
        
        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (onMessage) onMessage(data);
            } catch (e) {
                console.error('Event parse error:', e);
            }
        };
        
        this.eventSource.onerror = (error) => {
            console.error('EventSource error:', error);
            if (onError) onError(error);
        };
        
        return this.eventSource;
    }
    
    static disconnectEventSource() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
            console.log('EventSource disconnected');
        }
    }
    
    // ============================================================
    // WEBSOCKET CONNECTION (for real-time price updates)
    // ============================================================
    
    static connectWebSocket(onMessage, onOpen, onClose, onError) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        if (this.webSocket && this.webSocket.readyState === WebSocket.OPEN) {
            console.log('WebSocket already connected');
            return this.webSocket;
        }
        
        this.webSocket = new WebSocket(wsUrl);
        
        this.webSocket.onopen = () => {
            console.log('✅ WebSocket connected');
            if (onOpen) onOpen();
        };
        
        this.webSocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (onMessage) onMessage(data);
            } catch (e) {
                console.error('WebSocket message parse error:', e);
            }
        };
        
        this.webSocket.onclose = () => {
            console.log('WebSocket disconnected');
            if (onClose) onClose();
            // Attempt to reconnect after 5 seconds
            setTimeout(() => {
                if (this.webSocket && this.webSocket.readyState !== WebSocket.OPEN) {
                    console.log('Attempting WebSocket reconnection...');
                    this.connectWebSocket(onMessage, onOpen, onClose, onError);
                }
            }, 5000);
        };
        
        this.webSocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            if (onError) onError(error);
        };
        
        return this.webSocket;
    }
    
    static disconnectWebSocket() {
        if (this.webSocket) {
            this.webSocket.close();
            this.webSocket = null;
            console.log('WebSocket disconnected');
        }
    }
    
    static sendWebSocketMessage(message) {
        if (this.webSocket && this.webSocket.readyState === WebSocket.OPEN) {
            this.webSocket.send(JSON.stringify(message));
            return true;
        }
        return false;
    }
    
    // ============================================================
    // HELPER METHODS
    // ============================================================
    
    // Format price for display
    static formatPrice(price, decimals = 5) {
        if (!price && price !== 0) return '--';
        if (isNaN(price) || !isFinite(price)) return '--';
        return price.toFixed(decimals);
    }
    
    // Format percentage
    static formatPercent(value, decimals = 2, showSign = true) {
        if (!value && value !== 0) return '--';
        if (isNaN(value) || !isFinite(value)) return '--';
        const sign = showSign && value > 0 ? '+' : '';
        return `${sign}${value.toFixed(decimals)}%`;
    }
    
    // Format pips
    static formatPips(value) {
        if (!value && value !== 0) return '--';
        if (isNaN(value) || !isFinite(value)) return '--';
        return `${value.toFixed(1)} pips`;
    }
    
    // Format large numbers
    static formatNumber(num, decimals = 0) {
        if (!num && num !== 0) return '--';
        if (isNaN(num) || !isFinite(num)) return '--';
        if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
        if (num >= 1e3) return `${(num / 1e3).toFixed(1)}K`;
        return num.toFixed(decimals);
    }
    
    // Format currency
    static formatCurrency(value, currency = '$', decimals = 2) {
        if (!value && value !== 0) return '--';
        if (isNaN(value) || !isFinite(value)) return '--';
        return `${currency}${value.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`;
    }
    
    // Format date for holidays
    static formatHolidayDate(dateString) {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }
    
    // Get signal color class
    static getSignalColor(signal) {
        const colors = {
            'STRONG_BUY': '#00ff88',
            'BUY': '#00ff88',
            'CONSIDER_BUY': '#88ff88',
            'NEUTRAL': '#ffaa00',
            'CONSIDER_SELL': '#ff8888',
            'SELL': '#ff4444',
            'STRONG_SELL': '#ff4444',
            'HOLD': '#ffaa00'
        };
        return colors[signal] || '#ffffff';
    }
    
    // Get signal icon
    static getSignalIcon(signal) {
        const icons = {
            'STRONG_BUY': 'fa-arrow-up',
            'BUY': 'fa-arrow-up',
            'CONSIDER_BUY': 'fa-arrow-up',
            'NEUTRAL': 'fa-minus',
            'CONSIDER_SELL': 'fa-arrow-down',
            'SELL': 'fa-arrow-down',
            'STRONG_SELL': 'fa-arrow-down',
            'HOLD': 'fa-pause'
        };
        return icons[signal] || 'fa-question';
    }
    
    // Get trend icon
    static getTrendIcon(trend) {
        if (trend === 'BULLISH') return 'fa-arrow-trend-up';
        if (trend === 'BEARISH') return 'fa-arrow-trend-down';
        return 'fa-minus';
    }
    
    // Get trend color
    static getTrendColor(trend) {
        if (trend === 'BULLISH') return '#00ff88';
        if (trend === 'BEARISH') return '#ff4444';
        return '#ffaa00';
    }
    
    // Format correlation value
    static formatCorrelation(value) {
        if (!value && value !== 0) return '--';
        const num = parseFloat(value);
        if (isNaN(num)) return '--';
        const sign = num > 0 ? '+' : '';
        return `${sign}${num.toFixed(3)}`;
    }
    
    // Get correlation class
    static getCorrelationClass(value) {
        const num = parseFloat(value);
        if (isNaN(num)) return 'neutral';
        if (num > 0.5) return 'positive';
        if (num < -0.5) return 'negative';
        return 'neutral';
    }
    
    // Format timestamp to relative time
    static getRelativeTime(timestamp) {
        if (!timestamp) return 'Unknown';
        const now = new Date();
        const then = new Date(timestamp);
        const diffMs = now - then;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} min ago`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)} hours ago`;
        return `${Math.floor(diffMins / 1440)} days ago`;
    }
    
    // Get session based on time
    static getTradingSession() {
        const now = new Date();
        const utcHour = now.getUTCHours();
        
        if (utcHour >= 0 && utcHour < 8) return 'Asia (Tokyo)';
        if (utcHour >= 8 && utcHour < 12) return 'London Open';
        if (utcHour >= 12 && utcHour < 16) return 'London-New York Overlap';
        if (utcHour >= 16 && utcHour < 20) return 'New York';
        return 'Pacific';
    }
    
    // Check if market is open
    static isMarketOpen() {
        const now = new Date();
        const day = now.getDay();
        const hour = now.getUTCHours();
        
        if (day === 0 || day === 6) return false;
        if (hour < 22 && hour > 22) return false;
        return true;
    }
}

// Auto-refresh helper
class AutoRefreshManager {
    constructor(interval = 30000) {
        this.interval = interval;
        this.timer = null;
        this.callbacks = [];
        this.isRunning = false;
    }
    
    addCallback(callback) {
        this.callbacks.push(callback);
    }
    
    removeCallback(callback) {
        const index = this.callbacks.indexOf(callback);
        if (index > -1) this.callbacks.splice(index, 1);
    }
    
    start() {
        if (this.timer) this.stop();
        this.timer = setInterval(() => {
            if (ApiService.checkConnection()) {
                this.callbacks.forEach(cb => cb());
            }
        }, this.interval);
        this.isRunning = true;
        console.log(`Auto-refresh started (${this.interval / 1000}s interval)`);
    }
    
    stop() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
            this.isRunning = false;
            console.log('Auto-refresh stopped');
        }
    }
    
    setInterval(interval) {
        this.interval = interval;
        if (this.isRunning) {
            this.stop();
            this.start();
        }
    }
    
    triggerNow() {
        if (this.callbacks.length > 0) {
            Promise.all(this.callbacks.map(cb => cb())).catch(console.error);
        }
    }
}

// Export for use
window.ApiService = ApiService;
window.AutoRefreshManager = AutoRefreshManager;

// Initialize auto-refresh by default
const autoRefresh = new AutoRefreshManager(30000);
window.autoRefresh = autoRefresh;

// Setup network listeners
ApiService.setupNetworkListeners();

console.log('✅ API Service v3.1 loaded with FCS API & Calendarific support');