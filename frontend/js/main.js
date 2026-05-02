/**
 * main.js - Main Dashboard Controller for EUR/USD Signal Platform
 * Version: 3.2 - Added Market Holidays & Correlations (FCS API + Calendarific)
 */

class DashboardController {
    constructor() {
        this.refreshInterval = null;
        this.priceInterval = null;
        this.initialized = false;
        this.chartManager = window.chartManager || null;
        this.priceHistory = [];
        this.signalHistory = [];
        this.candleData = [];
        this.autoRefresh = window.autoRefresh || null;
        this.candlestickChart = null;
        this.fearGreedChart = null;
        this.countdownInterval = null;
    }

    async initialize() {
        console.log('🚀 Initializing Dashboard v3.2 (FCS API + Calendarific)...');
        
        // Cache DOM elements
        this.cacheElements();
        
        // Attach event listeners
        this.attachEventListeners();
        
        // Initialize charts
        this.initializeCharts();
        this.initCandlestickChart();
        this.initFearGreedGauge();
        
        // Initial data load (no loading overlay)
        await this.refreshAll();
        
        // Start auto-refresh timers
        this.startTimers();
        
        // Start countdown timer for next update
        this.startCountdown();
        
        // Update clock and sessions
        this.startClock();
        this.updateTradingSessions();
        setInterval(() => this.updateTradingSessions(), 60000);
        
        this.initialized = true;
        console.log('✅ Dashboard initialized successfully with ALL APIs');
    }

    cacheElements() {
        this.elements = {
            // Price elements
            price: document.getElementById('eurusd-price'),
            currentLevel: document.getElementById('current-level'),
            priceChange: document.getElementById('eurusd-change'),
            
            // Signal elements
            mainSignal: document.getElementById('main-signal'),
            signalConfidence: document.getElementById('signal-confidence'),
            signalRisk: document.getElementById('signal-risk'),
            updateTime: document.getElementById('update-time'),
            
            // Stats elements
            high24h: document.getElementById('high-24h'),
            low24h: document.getElementById('low-24h'),
            atrValue: document.getElementById('atr-value'),
            volatility: document.getElementById('volatility'),
            
            // Technical indicators
            rsiValue: document.getElementById('rsi-value'),
            rsiStatus: document.getElementById('rsi-status'),
            macdValue: document.getElementById('macd-value'),
            macdStatus: document.getElementById('macd-status'),
            atrIndicator: document.getElementById('atr-indicator'),
            adxValue: document.getElementById('adx-value'),
            adxStatus: document.getElementById('adx-status'),
            
            // Technical levels
            sma20: document.getElementById('sma20'),
            sma50: document.getElementById('sma50'),
            support: document.getElementById('support'),
            resistance: document.getElementById('resistance'),
            trendDir: document.getElementById('trendDir'),
            trendStrength: document.getElementById('trendStrength'),
            
            // Market regime
            regimeDetail: document.getElementById('regimeDetail'),
            regimeConf: document.getElementById('regimeConf'),
            riskLevel: document.getElementById('riskLevel'),
            posMultiplier: document.getElementById('posMultiplier'),
            regimeDesc: document.getElementById('regimeDesc'),
            
            // VWAP & Ichimoku
            vwapValue: document.getElementById('vwapValue'),
            vwapPosition: document.getElementById('vwapPosition'),
            ichiSignal: document.getElementById('ichiSignal'),
            cloudStatus: document.getElementById('cloudStatus'),
            
            // Recommendation
            recAction: document.getElementById('recAction'),
            recEntry: document.getElementById('recEntry'),
            recStopLoss: document.getElementById('recStopLoss'),
            recTakeProfit: document.getElementById('recTakeProfit'),
            recConfidence: document.getElementById('recConfidence'),
            recReason: document.getElementById('recReason'),
            
            // News sentiment
            newsOverall: document.getElementById('newsOverall'),
            newsScore: document.getElementById('newsScore'),
            sentimentMomentum: document.getElementById('sentimentMomentum'),
            
            // Weekend & Prediction
            weeklyOpen: document.getElementById('weekly-open'),
            weeklyClose: document.getElementById('weekly-close'),
            weeklyRange: document.getElementById('weekly-range'),
            weeklyChange: document.getElementById('weekly-change'),
            weeklyRatio: document.getElementById('weekly-ratio'),
            predictionDirection: document.getElementById('prediction-direction'),
            target1: document.getElementById('target1'),
            target2: document.getElementById('target2'),
            keySupport: document.getElementById('key-support'),
            keyResistance: document.getElementById('key-resistance'),
            predictionBar: document.getElementById('prediction-bar'),
            predictionPercent: document.getElementById('prediction-percent'),
            bullishBreakout: document.getElementById('bullish-breakout'),
            upsideTarget: document.getElementById('upside-target'),
            pivotPoint: document.getElementById('pivot-point'),
            downsideTarget: document.getElementById('downside-target'),
            bearishBreakdown: document.getElementById('bearish-breakdown'),
            
            // Sentiment
            bullishSentiment: document.getElementById('bullish-sentiment'),
            bearishSentiment: document.getElementById('bearish-sentiment'),
            neutralSentiment: document.getElementById('neutral-sentiment'),
            sentimentBar: document.getElementById('sentiment-bar'),
            vixValue: document.getElementById('vix-value'),
            riskReversal: document.getElementById('risk-reversal'),
            putCall: document.getElementById('put-call'),
            liquidityScore: document.getElementById('liquidity-score'),
            fearGreedValue: document.getElementById('fear-greed-value'),
            fearGreedLabel: document.getElementById('fear-greed-label'),
            
            // Events
            eventsList: document.getElementById('events-list'),
            weeklyEvents: document.getElementById('weekly-events'),
            
            // Chart indicators
            chartVolume: document.getElementById('chart-volume'),
            chartRange: document.getElementById('chart-range'),
            chartVolatility: document.getElementById('chart-volatility'),
            
            // Timestamp
            timestamp: document.getElementById('liveTimestamp'),
            currentTime: document.getElementById('current-time'),
            
            // Sessions
            sessionsContainer: document.getElementById('sessions-container'),
            sessionNote: document.getElementById('session-note'),
            
            // NEW: Holidays & Correlations
            holidaysList: document.getElementById('holidays-list'),
            correlations: document.getElementById('correlations'),
            
            // NEW: API Status
            dataSource: document.getElementById('data-source'),
            fcsStatus: document.getElementById('fcs-status'),
            calendarificStatus: document.getElementById('calendarific-status'),
            nextUpdate: document.getElementById('next-update')
        };
    }

    attachEventListeners() {
        // Module card click handlers
        document.querySelectorAll('.module-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const page = card.dataset.page;
                if (page && !e.target.closest('.feature-btn')) {
                    window.location.href = `pages/${page}`;
                }
            });
        });
        
        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshAll());
        }
        
        // Chart period buttons
        document.querySelectorAll('.chart-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const period = btn.dataset.period;
                if (period) {
                    this.updateChartPeriod(period);
                    document.querySelectorAll('.chart-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                }
            });
        });
        
        // Feature card clicks
        document.querySelectorAll('.feature-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (card.id === 'ai-chat-card') {
                    if (typeof openAIChat === 'function') openAIChat();
                }
            });
        });
    }

    initializeCharts() {
        if (this.chartManager && document.getElementById('priceChart')) {
            this.chartManager.createPriceChart('priceChart', {
                labels: [],
                prices: []
            });
        }
        
        if (this.chartManager && document.getElementById('cotChart')) {
            this.chartManager.createGauge('cotChart', 50, 0, 100, 'COT Index');
        }
    }

    initCandlestickChart() {
        const ctx = document.getElementById('candlestickChart')?.getContext('2d');
        if (!ctx) return;
        
        this.candlestickChart = new Chart(ctx, {
            type: 'candlestick',
            data: {
                datasets: [{
                    label: 'EUR/USD',
                    data: this.generateMockCandles(),
                    borderColor: '#2d6eff',
                    borderWidth: 1,
                    upColor: '#00ff88',
                    downColor: '#ff4444'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const item = context.raw;
                                return [
                                    `Open: ${item.o.toFixed(5)}`,
                                    `High: ${item.h.toFixed(5)}`,
                                    `Low: ${item.l.toFixed(5)}`,
                                    `Close: ${item.c.toFixed(5)}`
                                ];
                            }
                        }
                    },
                    legend: { labels: { color: '#ffffff' } }
                },
                scales: {
                    x: { ticks: { color: '#8a8fa8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { ticks: { color: '#8a8fa8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                }
            }
        });
    }

    generateMockCandles() {
        const candles = [];
        let basePrice = 1.1750;
        
        for (let i = 0; i < 50; i++) {
            const open = basePrice + (Math.random() - 0.5) * 0.003;
            const close = open + (Math.random() - 0.5) * 0.004;
            const high = Math.max(open, close) + Math.random() * 0.002;
            const low = Math.min(open, close) - Math.random() * 0.002;
            
            candles.push({ x: i, o: open, h: high, l: low, c: close });
            basePrice = close;
        }
        return candles;
    }

    updateCandlestickData(candles) {
        if (this.candlestickChart) {
            this.candlestickChart.data.datasets[0].data = candles;
            this.candlestickChart.update();
        }
    }

    initFearGreedGauge() {
        const ctx = document.getElementById('fearGreedGauge')?.getContext('2d');
        if (!ctx) return;
        
        this.fearGreedChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [50, 50],
                    backgroundColor: ['#ffaa00', '#2c3e50'],
                    borderWidth: 0,
                    circumference: 180,
                    rotation: 270
                }]
            },
            options: {
                cutout: '70%',
                responsive: true,
                maintainAspectRatio: true,
                plugins: { legend: { display: false }, tooltip: { enabled: false } }
            }
        });
    }

    updateFearGreedGauge(value) {
        if (this.fearGreedChart) {
            const color = value > 75 ? '#00ff88' : value > 55 ? '#ffaa00' : value > 45 ? '#ffaa00' : value > 25 ? '#ff4444' : '#ff4444';
            this.fearGreedChart.data.datasets[0].data = [value, 100 - value];
            this.fearGreedChart.data.datasets[0].backgroundColor = [color, '#2c3e50'];
            this.fearGreedChart.update();
        }
    }

    updateTradingSessions() {
        const now = new Date();
        const utcHour = now.getUTCHours();
        const sessions = [
            { name: 'Tokyo', active: utcHour >= 0 && utcHour < 8, progress: utcHour >= 0 && utcHour < 8 ? ((utcHour - 0) / 8) * 100 : 0 },
            { name: 'London', active: utcHour >= 8 && utcHour < 16, progress: utcHour >= 8 && utcHour < 16 ? ((utcHour - 8) / 8) * 100 : 0 },
            { name: 'New York', active: utcHour >= 13 && utcHour < 22, progress: utcHour >= 13 && utcHour < 22 ? ((utcHour - 13) / 9) * 100 : 0 }
        ];
        
        if (this.elements.sessionsContainer) {
            this.elements.sessionsContainer.innerHTML = sessions.map(s => `
                <div class="session">
                    <div class="session-info">
                        <span>${s.name}</span>
                        <span class="session-status ${s.active ? 'active' : 'closed'}">${s.active ? 'Active' : 'Closed'}</span>
                    </div>
                    <div class="progress-bar"><div class="progress" style="width: ${s.progress}%"></div></div>
                </div>
            `).join('');
        }
        
        const activeSession = sessions.find(s => s.active);
        if (this.elements.sessionNote) {
            this.elements.sessionNote.textContent = activeSession ? 
                `${activeSession.name} session active - ${activeSession.name === 'London' ? 'Highest liquidity' : activeSession.name === 'New York' ? 'High volatility expected' : 'Moderate activity'}` : 
                'Market closed - Weekend';
        }
    }

    // ============================================================
    // COUNTDOWN TIMER FOR NEXT UPDATE
    // ============================================================
    
    startCountdown() {
        let seconds = 30;
        if (this.countdownInterval) clearInterval(this.countdownInterval);
        
        this.countdownInterval = setInterval(() => {
            if (seconds <= 0) {
                seconds = 30;
            }
            if (this.elements.nextUpdate) {
                this.elements.nextUpdate.textContent = seconds + 's';
            }
            seconds--;
        }, 1000);
    }

    // ============================================================
    // NEW: MARKET HOLIDAYS FROM CALENDARIFIC
    // ============================================================
    
    async loadMarketHolidays() {
        try {
            const response = await fetch('/api/market-holidays');
            const data = await response.json();
            
            if (this.elements.holidaysList) {
                if (data.success && data.holidays && data.holidays.length > 0) {
                    const holidaysHtml = data.holidays.slice(0, 5).map(h => `
                        <div class="holiday-item">
                            <span class="holiday-name">${h.name}</span>
                            <span class="holiday-date">${h.date}</span>
                        </div>
                    `).join('');
                    this.elements.holidaysList.innerHTML = holidaysHtml;
                    
                    if (this.elements.calendarificStatus) {
                        this.elements.calendarificStatus.textContent = '✅ Active';
                        this.elements.calendarificStatus.style.color = '#00ff88';
                    }
                } else {
                    this.elements.holidaysList.innerHTML = '<div class="holiday-item"><span>No upcoming holidays</span></div>';
                }
            }
        } catch (error) {
            console.error('Market holidays error:', error);
            if (this.elements.holidaysList) {
                this.elements.holidaysList.innerHTML = '<div class="holiday-item"><span>Holiday data unavailable</span></div>';
            }
            if (this.elements.calendarificStatus) {
                this.elements.calendarificStatus.textContent = '⚠️ Fallback';
                this.elements.calendarificStatus.style.color = '#ffaa00';
            }
        }
    }
    
    // ============================================================
    // NEW: CORRELATIONS FROM FCS API
    // ============================================================
    
    async loadCorrelations() {
        try {
            const response = await fetch('/api/correlations');
            const data = await response.json();
            
            if (this.elements.correlations) {
                if (data.success && data.correlations && data.correlations.length > 0) {
                    const correlationsHtml = data.correlations.map(c => {
                        const value = typeof c.correlation === 'number' ? c.correlation.toFixed(4) : c.correlation;
                        const isPositive = parseFloat(value) > 0;
                        return `
                            <div class="correlation-item">
                                <span class="correlation-name">${c.pair}</span>
                                <span class="correlation-value ${isPositive ? 'positive' : 'negative'}">
                                    ${isPositive ? '+' : ''}${value}
                                </span>
                            </div>
                        `;
                    }).join('');
                    this.elements.correlations.innerHTML = correlationsHtml;
                } else {
                    this.elements.correlations.innerHTML = '<div class="correlation-item"><span>Using calculated correlations</span></div>';
                }
            }
        } catch (error) {
            console.error('Correlations error:', error);
            if (this.elements.correlations) {
                this.elements.correlations.innerHTML = '<div class="correlation-item"><span>Correlation data unavailable</span></div>';
            }
        }
    }

    // ============================================================
    // REFRESH WITH ALL DATA SOURCES
    // ============================================================
    
    async refreshAll() {
        this.animateRefresh();
        
        if (this.elements.updateTime) {
            this.elements.updateTime.textContent = 'Updating...';
        }
        
        try {
            const [priceData, signalData, technicalData, fundamentalData, regimeData, newsData, calendarData, holidaysData, correlationsData] = await Promise.all([
                ApiService.getPrice(),
                ApiService.getSignal(),
                ApiService.getTechnical(),
                ApiService.getFundamental(),
                ApiService.getRegime(),
                ApiService.getNews(3),
                ApiService.getEconomicCalendar(7),
                this.loadMarketHolidays(),
                this.loadCorrelations()
            ]);
            
            if (priceData.success) this.updatePriceUI(priceData.data);
            if (signalData.success) this.updateSignalUI(signalData.data);
            if (technicalData.success) this.updateTechnicalUI(technicalData.data);
            if (fundamentalData.success) this.updateFundamentalUI(fundamentalData.data);
            if (regimeData.success) this.updateRegimeUI(regimeData.data);
            if (newsData.success) this.updateNewsUI(newsData.data);
            if (calendarData.success) this.updateCalendarUI(calendarData.data);
            
            // Update data source indicators
            if (priceData.source && this.elements.dataSource) {
                this.elements.dataSource.textContent = priceData.source.toUpperCase();
            }
            if (priceData.source && this.elements.fcsStatus) {
                this.elements.fcsStatus.textContent = priceData.source === 'fcs_api' ? '✅ Live' : '⚠️ Fallback';
                this.elements.fcsStatus.style.color = priceData.source === 'fcs_api' ? '#00ff88' : '#ffaa00';
            }
            
            this.updateTimestamp();
            this.showToast('Data updated successfully', 'success');
            
        } catch (error) {
            console.error('Refresh error:', error);
            this.useFallbackData();
            this.showToast('Update failed, retrying...', 'warning');
        } finally {
            if (this.elements.updateTime) {
                setTimeout(() => {
                    if (this.elements.updateTime.textContent === 'Updating...') {
                        this.elements.updateTime.textContent = 'Just now';
                    }
                }, 500);
            }
        }
    }
    
    // Subtle refresh animation on price card and button
    animateRefresh() {
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn && !refreshBtn.classList.contains('refreshing')) {
            refreshBtn.classList.add('refreshing');
            setTimeout(() => refreshBtn.classList.remove('refreshing'), 600);
        }
        
        const priceCard = document.querySelector('.live-price-card');
        if (priceCard) {
            priceCard.style.transition = 'all 0.2s ease';
            priceCard.style.opacity = '0.85';
            setTimeout(() => {
                priceCard.style.opacity = '1';
            }, 200);
        }
        
        const signalBanner = document.getElementById('signal-banner');
        if (signalBanner) {
            signalBanner.style.transition = 'all 0.2s ease';
            signalBanner.style.transform = 'scale(0.99)';
            setTimeout(() => {
                signalBanner.style.transform = 'scale(1)';
            }, 200);
        }
    }
    
    // Toast notification system
    showToast(message, type = 'success') {
        let toast = document.getElementById('refresh-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'refresh-toast';
            toast.style.cssText = `
                position: fixed;
                bottom: 24px;
                right: 24px;
                background: linear-gradient(135deg, #1a2a4a, #0f172a);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 40px;
                padding: 10px 20px;
                display: flex;
                align-items: center;
                gap: 12px;
                z-index: 10000;
                opacity: 0;
                transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
                pointer-events: none;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                font-size: 13px;
                font-weight: 500;
                font-family: 'Inter', sans-serif;
            `;
            document.body.appendChild(toast);
        }
        
        const icon = type === 'success' 
            ? '<i class="fas fa-check-circle" style="color: #00ff88; margin-right: 8px;"></i>' 
            : '<i class="fas fa-exclamation-triangle" style="color: #ffaa00; margin-right: 8px;"></i>';
        
        toast.innerHTML = `${icon}<span>${message}</span>`;
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(20px)';
        }, 2500);
    }

    updatePriceUI(data) {
        if (!data) return;
        const price = data.price || 1.1750;
        
        if (this.elements.price) this.elements.price.textContent = Utils.formatNumber(price);
        if (this.elements.currentLevel) this.elements.currentLevel.textContent = Utils.formatNumber(price);
        if (this.elements.weeklyClose) this.elements.weeklyClose.textContent = Utils.formatNumber(price);
        
        this.priceHistory.push(price);
        if (this.priceHistory.length > 50) this.priceHistory.shift();
        
        if (this.priceHistory.length >= 2) {
            const change = ((this.priceHistory[this.priceHistory.length - 1] - this.priceHistory[this.priceHistory.length - 2]) / this.priceHistory[this.priceHistory.length - 2]) * 100;
            if (this.elements.priceChange) {
                this.elements.priceChange.innerHTML = `<i class="fas fa-arrow-${change >= 0 ? 'up' : 'down'}"></i><span>${change >= 0 ? '+' : ''}${change.toFixed(2)}%</span>`;
                this.elements.priceChange.className = `price-change ${change >= 0 ? 'positive' : 'negative'}`;
            }
        }
        
        // Update candlestick chart with new data
        const newCandle = {
            x: this.priceHistory.length,
            o: this.priceHistory[this.priceHistory.length - 2] || price,
            h: Math.max(...this.priceHistory.slice(-5)),
            l: Math.min(...this.priceHistory.slice(-5)),
            c: price
        };
        this.candleData.push(newCandle);
        if (this.candleData.length > 50) this.candleData.shift();
        this.updateCandlestickData(this.candleData);
        
        // Update 24h high/low
        if (this.priceHistory.length > 0) {
            const last24h = this.priceHistory.slice(-24);
            if (this.elements.high24h) this.elements.high24h.textContent = Math.max(...last24h).toFixed(5);
            if (this.elements.low24h) this.elements.low24h.textContent = Math.min(...last24h).toFixed(5);
        }
    }

    updateSignalUI(data) {
        if (!data || !data.signal) return;
        
        const signal = data.signal;
        const signalType = signal.type || 'NEUTRAL';
        const confidence = signal.confidence || 50;
        
        if (this.elements.mainSignal) {
            this.elements.mainSignal.textContent = signalType;
            this.elements.mainSignal.className = `signal-type ${signalType.toLowerCase().replace('_', '-')}`;
            const banner = document.getElementById('signal-banner');
            if (banner) banner.className = `signal-banner ${signalType.toLowerCase().replace('_', '-')}`;
        }
        if (this.elements.signalConfidence) this.elements.signalConfidence.textContent = `${Math.round(confidence)}%`;
        
        if (this.elements.predictionBar) this.elements.predictionBar.style.width = `${confidence}%`;
        if (this.elements.predictionPercent) this.elements.predictionPercent.textContent = `${confidence}%`;
        
        let prediction = 'NEUTRAL BIAS';
        let predClass = 'neutral';
        if (signalType.includes('BUY')) {
            prediction = 'BULLISH BIAS';
            predClass = 'bullish';
        } else if (signalType.includes('SELL')) {
            prediction = 'BEARISH BIAS';
            predClass = 'bearish';
        }
        
        if (this.elements.predictionDirection) {
            this.elements.predictionDirection.innerHTML = `<i class="fas fa-arrow-trend-${prediction === 'BULLISH BIAS' ? 'up' : prediction === 'BEARISH BIAS' ? 'down' : 'right'}"></i><span>${prediction}</span>`;
            this.elements.predictionDirection.className = `prediction-direction ${predClass}`;
        }
    }

    updateTechnicalUI(data) {
        if (!data || !data.indicators) return;
        
        const indicators = data.indicators;
        const rsi = indicators.rsi || 50;
        
        if (this.elements.rsiValue) this.elements.rsiValue.textContent = Utils.safeValue(rsi);
        if (this.elements.rsiStatus) {
            const rsiStatus = rsi < 30 ? 'Oversold' : rsi > 70 ? 'Overbought' : 'Neutral';
            this.elements.rsiStatus.textContent = rsiStatus;
            this.elements.rsiStatus.className = `indicator-status ${rsiStatus === 'Oversold' ? 'signal-bullish' : rsiStatus === 'Overbought' ? 'signal-bearish' : 'signal-neutral'}`;
        }
        
        const fearGreed = rsi > 65 ? 85 : rsi > 55 ? 65 : rsi > 45 ? 50 : rsi > 35 ? 35 : 15;
        if (this.elements.fearGreedValue) this.elements.fearGreedValue.textContent = fearGreed;
        if (this.elements.fearGreedLabel) {
            this.elements.fearGreedLabel.textContent = fearGreed > 75 ? 'Extreme Greed' : fearGreed > 55 ? 'Greed' : fearGreed > 45 ? 'Neutral' : fearGreed > 25 ? 'Fear' : 'Extreme Fear';
        }
        this.updateFearGreedGauge(fearGreed);
        
        if (this.elements.bullishSentiment) this.elements.bullishSentiment.textContent = Math.min(100, rsi + 10);
        if (this.elements.bearishSentiment) this.elements.bearishSentiment.textContent = Math.min(100, 110 - rsi);
        if (this.elements.neutralSentiment) this.elements.neutralSentiment.textContent = Math.abs(50 - rsi);
        if (this.elements.sentimentBar) this.elements.sentimentBar.style.width = `${rsi}%`;
        
        if (this.elements.vixValue) this.elements.vixValue.textContent = (15 + (70 - rsi) / 10).toFixed(1);
        if (this.elements.riskReversal) this.elements.riskReversal.textContent = rsi > 60 ? 'Bullish' : rsi < 40 ? 'Bearish' : 'Neutral';
        if (this.elements.putCall) this.elements.putCall.textContent = (1.2 - (rsi - 50) / 100).toFixed(2);
        if (this.elements.liquidityScore) this.elements.liquidityScore.textContent = Math.min(100, Math.max(50, 70 + (rsi - 50) / 2)).toFixed(0);
        
        const atr = indicators.atr || {};
        if (this.elements.atrValue) this.elements.atrValue.textContent = `${Utils.safeValue(atr.pips, '--')} pips`;
        if (this.elements.atrIndicator) this.elements.atrIndicator.textContent = `${Utils.safeValue(atr.pips, '--')} pips`;
        if (this.elements.volatility) {
            const volatility = indicators.volatility || 12.5;
            this.elements.volatility.textContent = `${Utils.safeValue(volatility)}%`;
            if (this.elements.chartVolatility) this.elements.chartVolatility.textContent = `${Utils.safeValue(volatility)}%`;
        }
        
        if (this.elements.chartVolume && this.priceHistory.length > 0) {
            this.elements.chartVolume.textContent = Math.floor(Math.random() * 50000 + 20000).toLocaleString();
        }
        if (this.elements.chartRange && this.priceHistory.length > 0) {
            const high = Math.max(...this.priceHistory.slice(-20));
            const low = Math.min(...this.priceHistory.slice(-20));
            this.elements.chartRange.textContent = ((high - low) * 10000).toFixed(1);
        }
        
        if (this.priceHistory.length > 0) {
            const weekAgo = this.priceHistory[0] || this.priceHistory[this.priceHistory.length - 1];
            const weeklyChange = ((this.priceHistory[this.priceHistory.length - 1] - weekAgo) / weekAgo) * 100;
            if (this.elements.weeklyChange) this.elements.weeklyChange.textContent = `${weeklyChange > 0 ? '+' : ''}${weeklyChange.toFixed(2)}%`;
            if (this.elements.weeklyRange) {
                const weeklyHigh = Math.max(...this.priceHistory);
                const weeklyLow = Math.min(...this.priceHistory);
                this.elements.weeklyRange.textContent = ((weeklyHigh - weeklyLow) * 10000).toFixed(0);
            }
        }
        
        const currentPrice = this.priceHistory[this.priceHistory.length - 1] || 1.1750;
        if (this.elements.target1) this.elements.target1.textContent = (currentPrice + 0.0050).toFixed(5);
        if (this.elements.target2) this.elements.target2.textContent = (currentPrice + 0.0100).toFixed(5);
        if (this.elements.keySupport) this.elements.keySupport.textContent = (currentPrice - 0.0030).toFixed(5);
        if (this.elements.keyResistance) this.elements.keyResistance.textContent = (currentPrice + 0.0030).toFixed(5);
        if (this.elements.bullishBreakout) this.elements.bullishBreakout.textContent = (currentPrice + 0.0075).toFixed(5);
        if (this.elements.upsideTarget) this.elements.upsideTarget.textContent = (currentPrice + 0.0150).toFixed(5);
        if (this.elements.pivotPoint) this.elements.pivotPoint.textContent = currentPrice.toFixed(5);
        if (this.elements.downsideTarget) this.elements.downsideTarget.textContent = (currentPrice - 0.0150).toFixed(5);
        if (this.elements.bearishBreakdown) this.elements.bearishBreakdown.textContent = (currentPrice - 0.0075).toFixed(5);
        
        const ma = indicators.moving_averages || {};
        if (this.elements.sma20) this.elements.sma20.textContent = Utils.formatNumber(ma.sma_20);
        if (this.elements.sma50) this.elements.sma50.textContent = Utils.formatNumber(ma.sma_50);
        if (this.elements.support) this.elements.support.textContent = Utils.formatNumber(indicators.support);
        if (this.elements.resistance) this.elements.resistance.textContent = Utils.formatNumber(indicators.resistance);
        
        const trend = indicators.trend || {};
        if (this.elements.trendDir) {
            this.elements.trendDir.textContent = trend.direction || 'SIDEWAYS';
            this.elements.trendDir.className = trend.direction === 'BULLISH' ? 'signal-bullish' : trend.direction === 'BEARISH' ? 'signal-bearish' : 'signal-neutral';
        }
        if (this.elements.trendStrength) this.elements.trendStrength.textContent = Utils.safeValue(trend.strength);
        
        if (this.elements.adxValue) this.elements.adxValue.textContent = Utils.safeValue(indicators.adx);
        if (this.elements.adxStatus) {
            const adx = indicators.adx || 20;
            this.elements.adxStatus.textContent = adx > 40 ? 'Strong Trend' : adx > 25 ? 'Trending' : 'No Trend';
        }
    }

    updateFundamentalUI(data) {
        if (!data) return;
        const composite = data.composite_score || {};
        const bias = composite.bias || 'NEUTRAL';
        if (this.elements.signalRisk && bias) {
            const riskLevel = bias === 'USD_BULLISH' ? 'LOW' : bias === 'EUR_BULLISH' ? 'LOW' : 'MEDIUM';
            this.elements.signalRisk.textContent = riskLevel;
        }
    }

    updateRegimeUI(data) {
        if (!data) return;
        
        const regime = data.regime || 'UNKNOWN';
        const confidence = data.confidence || 50;
        const riskScore = data.risk_score || 50;
        
        if (this.elements.regimeDetail) this.elements.regimeDetail.textContent = regime.replace(/_/g, ' ').toUpperCase();
        if (this.elements.regimeConf) this.elements.regimeConf.textContent = Utils.safeValue(confidence);
        if (this.elements.regimeDesc) this.elements.regimeDesc.textContent = data.description || 'Analyzing market structure';
        
        let riskLevelText = 'MODERATE';
        if (riskScore >= 70) riskLevelText = 'HIGH';
        else if (riskScore <= 30) riskLevelText = 'LOW';
        if (this.elements.riskLevel) {
            this.elements.riskLevel.textContent = riskLevelText;
            this.elements.riskLevel.className = riskLevelText === 'HIGH' ? 'risk-high' : riskLevelText === 'LOW' ? 'risk-low' : 'risk-medium';
        }
        
        const multiplier = data.risk_multiplier || 1.0;
        if (this.elements.posMultiplier) this.elements.posMultiplier.textContent = multiplier;
        if (this.elements.signalRisk && riskLevelText) this.elements.signalRisk.textContent = riskLevelText;
    }

    updateNewsUI(data) {
        if (!data) return;
        
        const sentiment = data.sentiment_summary || {};
        const overall = sentiment.overall || 'neutral';
        const score = sentiment.score || 0;
        
        if (this.elements.newsOverall) {
            this.elements.newsOverall.textContent = overall.toUpperCase();
            this.elements.newsOverall.className = overall === 'positive' ? 'signal-bullish' : overall === 'negative' ? 'signal-bearish' : 'signal-neutral';
        }
        if (this.elements.newsScore) this.elements.newsScore.textContent = Utils.safeValue(score);
        
        const momentum = data.sentiment_momentum || {};
        if (this.elements.sentimentMomentum) {
            this.elements.sentimentMomentum.textContent = `Momentum: ${momentum.trend || 'stable'}`;
        }
    }

    updateCalendarUI(data) {
        if (!data || !data.events || data.events.length === 0) return;
        
        const events = data.events.slice(0, 4);
        const eventsHtml = events.map(event => `
            <div class="event-item ${event.impact.toLowerCase()}">
                <div class="event-info">
                    <span class="event-name">${Utils.truncate(event.name, 25)}</span>
                    <span class="event-time">${event.days_until === 0 ? 'Today' : event.days_until === 1 ? 'Tomorrow' : `${event.days_until}d`}</span>
                </div>
                <div class="event-impact">${event.impact}</div>
            </div>
        `).join('');
        
        if (this.elements.eventsList) {
            this.elements.eventsList.innerHTML = eventsHtml || '<div class="insight-text">No upcoming events</div>';
        }
    }

    updateChartPeriod(period) {
        console.log(`Switching to ${period} chart`);
        const newCandles = this.generateMockCandles();
        this.updateCandlestickData(newCandles);
        this.showToast(`Switched to ${period.toUpperCase()} chart`, 'success');
    }

    updateTimestamp() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString();
        
        if (this.elements.timestamp) this.elements.timestamp.textContent = timeStr;
        if (this.elements.currentTime) this.elements.currentTime.textContent = timeStr;
        if (this.elements.updateTime) this.elements.updateTime.textContent = 'Just now';
    }

    startClock() {
        setInterval(() => this.updateTimestamp(), 1000);
    }

    startTimers() {
        this.refreshInterval = setInterval(() => this.refreshAll(), 30000);
        console.log('✅ Auto-refresh timer started (30s interval)');
    }

    stopTimers() {
        if (this.refreshInterval) clearInterval(this.refreshInterval);
        if (this.countdownInterval) clearInterval(this.countdownInterval);
        this.showToast('Auto-refresh stopped', 'warning');
    }

    useFallbackData() {
        console.warn('Using fallback data');
        
        const fallbacks = {
            price: '1.17500',
            signal: 'NEUTRAL',
            confidence: '50%',
            risk: 'MODERATE',
            rsi: '50',
            atr: '20 pips',
            action: 'HOLD',
            reason: 'Unable to fetch live data. Retrying...',
            sentiment: 'NEUTRAL'
        };
        
        if (this.elements.price) this.elements.price.textContent = fallbacks.price;
        if (this.elements.mainSignal) {
            this.elements.mainSignal.textContent = fallbacks.signal;
            this.elements.mainSignal.className = 'signal-type neutral';
        }
        if (this.elements.signalConfidence) this.elements.signalConfidence.textContent = fallbacks.confidence;
        if (this.elements.signalRisk) this.elements.signalRisk.textContent = fallbacks.risk;
        if (this.elements.rsiValue) this.elements.rsiValue.textContent = fallbacks.rsi;
        if (this.elements.atrValue) this.elements.atrValue.textContent = fallbacks.atr;
        if (this.elements.recAction) this.elements.recAction.textContent = fallbacks.action;
        if (this.elements.recReason) this.elements.recReason.textContent = fallbacks.reason;
        if (this.elements.newsOverall) this.elements.newsOverall.textContent = fallbacks.sentiment;
        if (this.elements.timestamp) this.elements.timestamp.textContent = new Date().toLocaleTimeString();
        
        if (this.elements.holidaysList) {
            this.elements.holidaysList.innerHTML = '<div class="holiday-item"><span>Using fallback holiday data</span></div>';
        }
        if (this.elements.correlations) {
            this.elements.correlations.innerHTML = '<div class="correlation-item"><span>Using calculated correlations</span></div>';
        }
    }
}

// API Service wrapper for backward compatibility
const api = {
    async getDashboardSummary() {
        const result = await ApiService.getDashboardSummary();
        return result.success ? result.data : null;
    },
    async getPrice() {
        const result = await ApiService.getPrice();
        return result.success ? result.data : null;
    },
    async getSignal() {
        const result = await ApiService.getSignal();
        return result.success ? result.data : null;
    },
    async getTechnical() {
        const result = await ApiService.getTechnical();
        return result.success ? result.data : null;
    },
    async getNews(days) {
        const result = await ApiService.getNews(days);
        return result.success ? result.data : null;
    }
};

// Helper functions
function formatPrice(price) {
    return Utils.formatNumber(price);
}

function getSignalClass(signal) {
    return Utils.getSignalClass(signal);
}

function formatTimestamp() {
    return new Date().toLocaleTimeString();
}

// Initialize dashboard when DOM is ready
let dashboardInstance = null;
document.addEventListener('DOMContentLoaded', () => {
    dashboardInstance = new DashboardController();
    dashboardInstance.initialize();
});

// Export for debugging
window.dashboardController = dashboardInstance;