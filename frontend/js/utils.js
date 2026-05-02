/**
 * Utility Functions for EUR/USD Platform
 * Version: 3.1 - Added Market Holidays, Correlations & API Status Helpers
 */

class Utils {
    // ============================================================
    // NUMBER FORMATTING
    // ============================================================
    
    // Format number with decimals
    static formatNumber(num, decimals = 5) {
        if (num === undefined || num === null) return '--';
        if (isNaN(num) || !isFinite(num)) return '--';
        return Number(num).toFixed(decimals);
    }

    // Format percentage
    static formatPercent(value, decimals = 2, showSign = true) {
        if (value === undefined || value === null) return '--';
        if (isNaN(value) || !isFinite(value)) return '--';
        const sign = showSign && value > 0 ? '+' : '';
        return `${sign}${Number(value).toFixed(decimals)}%`;
    }

    // Format pips
    static formatPips(value, decimals = 1) {
        if (value === undefined || value === null) return '--';
        if (isNaN(value) || !isFinite(value)) return '--';
        return `${Number(value).toFixed(decimals)} pips`;
    }

    // Format price movement in pips
    static formatPriceMovement(price, previousPrice) {
        if (!price || !previousPrice) return '--';
        const pips = Math.abs(price - previousPrice) * 10000;
        const direction = price > previousPrice ? '▲' : price < previousPrice ? '▼' : '●';
        return `${direction} ${pips.toFixed(1)} pips`;
    }

    // Format large numbers (K, M, B)
    static formatLargeNumber(num, decimals = 1) {
        if (num === undefined || num === null) return '--';
        if (isNaN(num) || !isFinite(num)) return '--';
        if (num >= 1e9) return `${(num / 1e9).toFixed(decimals)}B`;
        if (num >= 1e6) return `${(num / 1e6).toFixed(decimals)}M`;
        if (num >= 1e3) return `${(num / 1e3).toFixed(decimals)}K`;
        return num.toString();
    }

    // Format currency
    static formatCurrency(value, currency = '$', decimals = 2) {
        if (value === undefined || value === null) return '--';
        if (isNaN(value) || !isFinite(value)) return '--';
        return `${currency}${Math.abs(value).toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`;
    }

    // Format number with + sign for positive values
    static formatSignedNumber(value, decimals = 2) {
        if (value === undefined || value === null) return '--';
        if (isNaN(value) || !isFinite(value)) return '--';
        const sign = value > 0 ? '+' : '';
        return `${sign}${value.toFixed(decimals)}`;
    }

    // ============================================================
    // NEW: CORRELATION FORMATTING
    // ============================================================
    
    // Format correlation value
    static formatCorrelation(value, decimals = 3) {
        if (value === undefined || value === null) return '--';
        if (isNaN(value) || !isFinite(value)) return '--';
        const sign = value > 0 ? '+' : '';
        return `${sign}${Number(value).toFixed(decimals)}`;
    }
    
    // Get correlation strength label
    static getCorrelationStrength(value) {
        const abs = Math.abs(value);
        if (abs >= 0.7) return 'Strong';
        if (abs >= 0.4) return 'Moderate';
        if (abs >= 0.2) return 'Weak';
        return 'Very Weak';
    }
    
    // Get correlation class for styling
    static getCorrelationClass(value) {
        if (value === undefined || value === null) return 'neutral';
        const num = parseFloat(value);
        if (isNaN(num)) return 'neutral';
        if (num > 0.5) return 'positive';
        if (num < -0.5) return 'negative';
        return 'neutral';
    }
    
    // Get correlation icon
    static getCorrelationIcon(value) {
        if (value === undefined || value === null) return 'fa-chart-line';
        const num = parseFloat(value);
        if (isNaN(num)) return 'fa-chart-line';
        if (num > 0.3) return 'fa-arrow-trend-up';
        if (num < -0.3) return 'fa-arrow-trend-down';
        return 'fa-minus';
    }
    
    // Get correlation description
    static getCorrelationDescription(value) {
        const num = parseFloat(value);
        if (isNaN(num)) return 'No correlation detected';
        if (num > 0.7) return 'Strong positive correlation - moves together';
        if (num > 0.4) return 'Moderate positive correlation';
        if (num > 0.2) return 'Weak positive correlation';
        if (num > -0.2) return 'No meaningful correlation';
        if (num > -0.4) return 'Weak negative correlation';
        if (num > -0.7) return 'Moderate negative correlation';
        return 'Strong negative correlation - moves opposite';
    }

    // ============================================================
    // NEW: MARKET HOLIDAY FORMATTING
    // ============================================================
    
    // Format holiday date nicely
    static formatHolidayDate(dateString, format = 'short') {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return dateString;
        
        if (format === 'short') {
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        }
        if (format === 'full') {
            return date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
        }
        if (format === 'relative') {
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const diffDays = Math.ceil((date - today) / (1000 * 60 * 60 * 24));
            
            if (diffDays === 0) return 'Today';
            if (diffDays === 1) return 'Tomorrow';
            if (diffDays < 7) return `${diffDays} days away`;
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        }
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }
    
    // Get holiday badge class based on type
    static getHolidayClass(holiday) {
        const types = holiday.types || [];
        if (types.includes('Bank') || types.includes('Financial')) return 'bank-holiday';
        if (types.includes('National') || types.includes('Public')) return 'public-holiday';
        if (types.includes('Local')) return 'local-holiday';
        return 'standard-holiday';
    }
    
    // Check if a date is a market holiday
    static isMarketHoliday(date, holidays) {
        if (!holidays || !holidays.length) return false;
        const checkDate = new Date(date);
        checkDate.setHours(0, 0, 0, 0);
        return holidays.some(h => {
            const holidayDate = new Date(h.date);
            holidayDate.setHours(0, 0, 0, 0);
            return holidayDate.getTime() === checkDate.getTime();
        });
    }
    
    // Get upcoming holidays within days
    static getUpcomingHolidays(holidays, daysAhead = 30) {
        if (!holidays || !holidays.length) return [];
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const future = new Date(today);
        future.setDate(today.getDate() + daysAhead);
        
        return holidays.filter(h => {
            const holidayDate = new Date(h.date);
            holidayDate.setHours(0, 0, 0, 0);
            return holidayDate >= today && holidayDate <= future;
        }).sort((a, b) => new Date(a.date) - new Date(b.date));
    }

    // ============================================================
    // NEW: API STATUS HELPERS
    // ============================================================
    
    // Get API status color
    static getAPIStatusColor(status) {
        if (status === 'online' || status === 'connected' || status === 'active') return '#00ff88';
        if (status === 'degraded' || status === 'slow') return '#ffaa00';
        if (status === 'offline' || status === 'error' || status === 'disconnected') return '#ff4444';
        return '#8a8fa8';
    }
    
    // Get API status icon
    static getAPIStatusIcon(status) {
        if (status === 'online' || status === 'connected' || status === 'active') return 'fa-check-circle';
        if (status === 'degraded' || status === 'slow') return 'fa-exclamation-triangle';
        if (status === 'offline' || status === 'error' || status === 'disconnected') return 'fa-times-circle';
        return 'fa-question-circle';
    }
    
    // Get API status class
    static getAPIStatusClass(status) {
        if (status === 'online' || status === 'connected' || status === 'active') return 'status-online';
        if (status === 'degraded' || status === 'slow') return 'status-degraded';
        if (status === 'offline' || status === 'error' || status === 'disconnected') return 'status-offline';
        return 'status-unknown';
    }

    // ============================================================
    // DATE & TIME FORMATTING
    // ============================================================
    
    // Format date with multiple options
    static formatDate(date, format = 'relative') {
        if (!date) return '--';
        const d = new Date(date);
        if (isNaN(d.getTime())) return '--';
        
        if (format === 'relative') {
            const now = new Date();
            const diff = Math.floor((now - d) / 1000);
            
            if (diff < 60) return 'just now';
            if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
            if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
            if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
            return d.toLocaleDateString();
        }
        
        if (format === 'time') {
            return d.toLocaleTimeString();
        }
        
        if (format === 'datetime') {
            return `${d.toLocaleDateString()} ${d.toLocaleTimeString()}`;
        }
        
        return d.toLocaleDateString();
    }

    // Get current trading session with detailed info
    static getTradingSession() {
        const now = new Date();
        const utcHour = now.getUTCHours();
        const utcMinute = now.getUTCMinutes();
        const timeInMinutes = utcHour * 60 + utcMinute;
        
        const sessions = [
            { name: 'Sydney', start: 22 * 60, end: 7 * 60, active: false, liquidity: 'Low', volatility: 'Low' },
            { name: 'Tokyo', start: 0, end: 9 * 60, active: false, liquidity: 'Medium', volatility: 'Low' },
            { name: 'London', start: 8 * 60, end: 17 * 60, active: false, liquidity: 'High', volatility: 'Medium' },
            { name: 'New York', start: 13 * 60, end: 22 * 60, active: false, liquidity: 'High', volatility: 'High' },
            { name: 'London-New York Overlap', start: 13 * 60, end: 17 * 60, active: false, liquidity: 'Very High', volatility: 'High' }
        ];
        
        for (const session of sessions) {
            if (session.start <= session.end) {
                if (timeInMinutes >= session.start && timeInMinutes < session.end) {
                    session.active = true;
                    return session;
                }
            } else {
                if (timeInMinutes >= session.start || timeInMinutes < session.end) {
                    session.active = true;
                    return session;
                }
            }
        }
        
        return { name: 'Closed', active: false, liquidity: 'None', volatility: 'None' };
    }

    // Check if market is open
    static isMarketOpen() {
        const session = this.getTradingSession();
        return session.active;
    }

    // Get next market open time
    static getNextMarketOpen() {
        const now = new Date();
        const day = now.getDay();
        const hour = now.getHours();
        
        // If weekend, next open is Sunday 22:00 UTC
        if (day === 6 || (day === 0 && hour < 22)) {
            const nextOpen = new Date(now);
            nextOpen.setUTCDate(now.getUTCDate() + (7 - day) % 7);
            nextOpen.setUTCHours(22, 0, 0, 0);
            return nextOpen;
        }
        
        // If weekday but after 22:00, next open is next day 22:00
        if (hour >= 22) {
            const nextOpen = new Date(now);
            nextOpen.setUTCDate(now.getUTCDate() + 1);
            nextOpen.setUTCHours(22, 0, 0, 0);
            return nextOpen;
        }
        
        // If before 22:00, same day at 22:00
        const nextOpen = new Date(now);
        nextOpen.setUTCHours(22, 0, 0, 0);
        return nextOpen;
    }

    // ============================================================
    // SIGNAL & TRADING HELPERS
    // ============================================================
    
    // Get signal color
    static getSignalColor(signal) {
        const colors = {
            'STRONG_BUY': '#00ff88',
            'BUY': '#00ff88',
            'CONSIDER_BUY': '#88ff88',
            'NEUTRAL': '#ffaa00',
            'CONSIDER_SELL': '#ff8888',
            'SELL': '#ff4444',
            'STRONG_SELL': '#ff4444',
            'HOLD': '#ffaa00',
            'LONG': '#00ff88',
            'SHORT': '#ff4444'
        };
        return colors[signal] || '#ffffff';
    }

    // Get signal class
    static getSignalClass(signal) {
        if (!signal) return 'signal-neutral';
        const s = signal.toUpperCase();
        if (s === 'STRONG_BUY' || s === 'BUY' || s === 'LONG') return 'signal-bullish';
        if (s === 'STRONG_SELL' || s === 'SELL' || s === 'SHORT') return 'signal-bearish';
        return 'signal-neutral';
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
            'HOLD': 'fa-pause',
            'LONG': 'fa-arrow-up',
            'SHORT': 'fa-arrow-down'
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

    // Calculate risk/reward ratio
    static calculateRiskReward(entry, stopLoss, takeProfit) {
        const risk = Math.abs(entry - stopLoss);
        const reward = Math.abs(takeProfit - entry);
        if (risk === 0) return 0;
        return reward / risk;
    }

    // Calculate position size
    static calculatePositionSize(accountBalance, riskPercent, stopLossPips, pipValue = 10) {
        const riskAmount = accountBalance * (riskPercent / 100);
        const positionSize = riskAmount / (stopLossPips * pipValue);
        return Math.min(1.0, Math.max(0.01, positionSize));
    }

    // Calculate pip value for given lot size
    static calculatePipValue(lotSize, pair = 'EURUSD') {
        // Standard pip value for 1 standard lot (100,000 units) is $10
        return lotSize * 10;
    }

    // ============================================================
    // TECHNICAL INDICATOR HELPERS
    // ============================================================
    
    // Get RSI status text
    static getRSIStatus(rsi) {
        if (rsi >= 70) return 'Overbought';
        if (rsi <= 30) return 'Oversold';
        return 'Neutral';
    }

    // Get RSI color
    static getRSIColor(rsi) {
        if (rsi >= 70) return '#ff4444';
        if (rsi <= 30) return '#00ff88';
        return '#ffaa00';
    }

    // Get ADX status text
    static getADXStatus(adx) {
        if (adx >= 40) return 'Strong Trend';
        if (adx >= 25) return 'Trending';
        return 'No Trend';
    }

    // Get ATR interpretation
    static getATRInterpretation(atr, averageATR = 20) {
        if (atr > averageATR * 1.5) return 'High Volatility';
        if (atr < averageATR * 0.7) return 'Low Volatility';
        return 'Normal Volatility';
    }

    // ============================================================
    // VOLATILITY & RISK HELPERS
    // ============================================================
    
    // Calculate volatility from price array
    static calculateVolatility(prices, period = 20) {
        if (prices.length < period + 1) return 0;
        const returns = [];
        for (let i = prices.length - period; i < prices.length; i++) {
            returns.push(Math.log(prices[i] / prices[i - 1]));
        }
        const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
        const variance = returns.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / returns.length;
        return Math.sqrt(variance) * Math.sqrt(365 * 24) * 100;
    }

    // Get risk level from score
    static getRiskLevel(score) {
        if (score >= 70) return { text: 'HIGH', color: '#ff4444', class: 'risk-high' };
        if (score >= 40) return { text: 'MEDIUM', color: '#ffaa00', class: 'risk-medium' };
        return { text: 'LOW', color: '#00ff88', class: 'risk-low' };
    }

    // ============================================================
    // VALIDATION & SANITIZATION
    // ============================================================
    
    // Safe value handler
    static safeValue(value, defaultValue = '--') {
        if (value === undefined || value === null) return defaultValue;
        if (typeof value === 'number' && (isNaN(value) || !isFinite(value))) return defaultValue;
        if (value === 'Infinity' || value === '-Infinity') return defaultValue;
        if (value === 'NaN') return defaultValue;
        return value;
    }

    // Validate price
    static isValidPrice(price) {
        return price && typeof price === 'number' && isFinite(price) && price > 0;
    }

    // Clamp value between min and max
    static clamp(value, min, max) {
        return Math.min(max, Math.max(min, value));
    }

    // ============================================================
    // STRING MANIPULATION
    // ============================================================
    
    // Capitalize first letter
    static capitalize(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    }

    // Truncate string
    static truncate(str, length = 50) {
        if (!str) return '';
        if (str.length <= length) return str;
        return str.substring(0, length) + '...';
    }

    // Convert to title case
    static toTitleCase(str) {
        if (!str) return '';
        return str.replace(/\w\S*/g, txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
    }

    // ============================================================
    // DEBOUNCE & THROTTLE
    // ============================================================
    
    // Debounce function
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Throttle function
    static throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // ============================================================
    // OBJECT & ARRAY HELPERS
    // ============================================================
    
    // Deep clone object
    static deepClone(obj) {
        return JSON.parse(JSON.stringify(obj));
    }

    // Check if object is empty
    static isEmpty(obj) {
        return obj && Object.keys(obj).length === 0 && obj.constructor === Object;
    }

    // Generate random ID
    static generateId() {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    // Group array by key
    static groupBy(array, key) {
        return array.reduce((result, item) => {
            const groupKey = item[key];
            if (!result[groupKey]) result[groupKey] = [];
            result[groupKey].push(item);
            return result;
        }, {});
    }

    // ============================================================
    // NOTIFICATION & ALERTS
    // ============================================================
    
    // Show notification
    static showNotification(message, type = 'info', duration = 3000) {
        const colors = {
            success: '#00ff88',
            error: '#ff4444',
            warning: '#ffaa00',
            info: '#00d4ff'
        };
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <i class="fas ${icons[type]}"></i>
                <span>${message}</span>
            </div>
        `;
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${colors[type]};
            color: white;
            border-radius: 8px;
            font-size: 14px;
            z-index: 10000;
            animation: slideIn 0.3s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
        `;
        
        document.body.appendChild(notification);
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }

    // Show toast message (shorter duration)
    static toast(message, type = 'info') {
        this.showNotification(message, type, 2000);
    }

    // ============================================================
    // LOCAL STORAGE
    // ============================================================
    
    static storage = {
        set(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (e) {
                console.error('Storage set error:', e);
                return false;
            }
        },
        get(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (e) {
                console.error('Storage get error:', e);
                return defaultValue;
            }
        },
        remove(key) {
            localStorage.removeItem(key);
        },
        clear() {
            localStorage.clear();
        },
        has(key) {
            return localStorage.getItem(key) !== null;
        }
    };

    // ============================================================
    // TIMEFRAME HELPERS
    // ============================================================
    
    // Get timeframe display name
    static getTimeframeName(tf) {
        const names = {
            '1m': '1 Minute',
            '5m': '5 Minutes',
            '15m': '15 Minutes',
            '30m': '30 Minutes',
            '1h': '1 Hour',
            '2h': '2 Hours',
            '4h': '4 Hours',
            '1d': '1 Day',
            '1w': '1 Week',
            '1M': '1 Month'
        };
        return names[tf] || tf;
    }

    // Get timeframe in minutes
    static getTimeframeMinutes(tf) {
        const minutes = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '30m': 30,
            '1h': 60,
            '2h': 120,
            '4h': 240,
            '1d': 1440,
            '1w': 10080
        };
        return minutes[tf] || 60;
    }

    // ============================================================
    // COLOR HELPERS
    // ============================================================
    
    // Get color for value (gradient)
    static getGradientColor(value, min = 0, max = 100) {
        const percent = this.clamp((value - min) / (max - min), 0, 1);
        if (percent < 0.33) return '#ff4444';
        if (percent < 0.66) return '#ffaa00';
        return '#00ff88';
    }

    // Get opacity for value
    static getOpacity(value, min = 0, max = 100) {
        return this.clamp((value - min) / (max - min), 0.1, 1);
    }

    // ============================================================
    // DOM HELPERS
    // ============================================================
    
    // Safely get element
    static getElement(id) {
        const el = document.getElementById(id);
        if (!el) console.warn(`Element not found: ${id}`);
        return el;
    }

    // Safely set text content
    static setText(id, text) {
        const el = this.getElement(id);
        if (el) el.textContent = text;
    }

    // Safely set HTML
    static setHTML(id, html) {
        const el = this.getElement(id);
        if (el) el.innerHTML = html;
    }

    // Toggle element visibility
    static toggleVisibility(id, show) {
        const el = this.getElement(id);
        if (el) el.style.display = show ? 'flex' : 'none';
    }

    // ============================================================
    // SESSION TIME HELPERS
    // ============================================================
    
    // Get session progress percentage
    static getSessionProgress() {
        const session = this.getTradingSession();
        if (!session.active) return 0;
        
        const now = new Date();
        const utcHour = now.getUTCHours();
        const utcMinute = now.getUTCMinutes();
        const currentMinutes = utcHour * 60 + utcMinute;
        
        let startMinutes, endMinutes;
        if (session.name === 'London-New York Overlap') {
            startMinutes = 13 * 60;
            endMinutes = 17 * 60;
        } else {
            switch (session.name) {
                case 'Sydney': startMinutes = 22 * 60; endMinutes = 7 * 60 + 60; break;
                case 'Tokyo': startMinutes = 0; endMinutes = 9 * 60; break;
                case 'London': startMinutes = 8 * 60; endMinutes = 17 * 60; break;
                case 'New York': startMinutes = 13 * 60; endMinutes = 22 * 60; break;
                default: return 0;
            }
        }
        
        let progress;
        if (startMinutes <= endMinutes) {
            progress = (currentMinutes - startMinutes) / (endMinutes - startMinutes);
        } else {
            if (currentMinutes >= startMinutes) {
                progress = (currentMinutes - startMinutes) / ((24 * 60 - startMinutes) + endMinutes);
            } else {
                progress = ((24 * 60 - startMinutes) + currentMinutes) / ((24 * 60 - startMinutes) + endMinutes);
            }
        }
        
        return this.clamp(progress * 100, 0, 100);
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 5px currentColor; }
        50% { text-shadow: 0 0 20px currentColor; }
    }
    
    .blink {
        animation: blink 1s ease infinite;
    }
    
    .shake {
        animation: shake 0.5s ease;
    }
    
    .glow {
        animation: glow 2s ease infinite;
    }
    
    /* Signal classes */
    .signal-bullish { color: #00ff88; }
    .signal-bearish { color: #ff4444; }
    .signal-neutral { color: #ffaa00; }
    
    /* Correlation classes */
    .correlation-positive { color: #00ff88; }
    .correlation-negative { color: #ff4444; }
    .correlation-neutral { color: #ffaa00; }
    
    /* Holiday classes */
    .bank-holiday { border-left-color: #ff4444; }
    .public-holiday { border-left-color: #ffaa00; }
    .local-holiday { border-left-color: #00d4ff; }
    .standard-holiday { border-left-color: #8a8fa8; }
    
    /* API Status classes */
    .status-online { color: #00ff88; }
    .status-degraded { color: #ffaa00; }
    .status-offline { color: #ff4444; }
    .status-unknown { color: #8a8fa8; }
    
    /* Risk classes */
    .risk-high { color: #ff4444; background: rgba(255,68,68,0.1); border-color: #ff4444; }
    .risk-medium { color: #ffaa00; background: rgba(255,170,0,0.1); border-color: #ffaa00; }
    .risk-low { color: #00ff88; background: rgba(0,255,136,0.1); border-color: #00ff88; }
`;
document.head.appendChild(style);

// Export for use
window.Utils = Utils;

console.log('✅ Utils v3.1 loaded with Market Holidays, Correlations & API Status helpers');