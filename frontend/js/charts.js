/**
 * Chart Utilities for EUR/USD Platform
 * Version: 3.1 - Added Market Holidays Calendar, Correlation Matrix & API Status Charts
 */

class ChartManager {
    constructor() {
        this.charts = {};
        this.chartOptions = {};
        this.defaultColors = {
            primary: '#00d4ff',
            success: '#00ff88',
            danger: '#ff4444',
            warning: '#ffaa00',
            info: '#3498db',
            purple: '#9b59b6',
            orange: '#e67e22',
            pink: '#ff6b6b',
            teal: '#00cec9',
            background: 'rgba(0, 212, 255, 0.1)'
        };
        
        // Chart themes
        this.themes = {
            dark: {
                backgroundColor: 'rgba(0, 0, 0, 0)',
                gridColor: 'rgba(255, 255, 255, 0.05)',
                textColor: '#8a8fa8',
                titleColor: '#ffffff'
            },
            light: {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                gridColor: 'rgba(0, 0, 0, 0.1)',
                textColor: '#666666',
                titleColor: '#333333'
            }
        };
        
        this.currentTheme = 'dark';
    }

    // ============================================================
    // REAL CANDLESTICK CHART (Using Chart.js Financial)
    // ============================================================
    
    createRealCandlestickChart(canvasId, data, options = {}) {
        this.destroyChart(canvasId);
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;
        
        const ctx = canvas.getContext('2d');
        
        // Check if candlestick plugin is available
        if (typeof Chart === 'undefined' || !Chart.controllers?.candlestick) {
            console.warn('Candlestick chart not available, falling back to OHLC bars');
            return this.createOHLCBarChart(canvasId, data, options);
        }
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { 
                    labels: { 
                        color: this.themes[this.currentTheme].textColor,
                        font: { size: 11 }
                    } 
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: (context) => {
                            const item = context.raw;
                            if (item && item.o !== undefined) {
                                return [
                                    `Open: ${item.o.toFixed(5)}`,
                                    `High: ${item.h.toFixed(5)}`,
                                    `Low: ${item.l.toFixed(5)}`,
                                    `Close: ${item.c.toFixed(5)}`
                                ];
                            }
                            return `Price: ${context.raw.toFixed(5)}`;
                        }
                    }
                }
            },
            scales: {
                x: { 
                    ticks: { color: this.themes[this.currentTheme].textColor },
                    grid: { color: this.themes[this.currentTheme].gridColor }
                },
                y: { 
                    ticks: { color: this.themes[this.currentTheme].textColor },
                    grid: { color: this.themes[this.currentTheme].gridColor }
                }
            }
        };
        
        const chartOptions = { ...defaultOptions, ...options };
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'candlestick',
            data: {
                datasets: [{
                    label: 'EUR/USD',
                    data: data.candles || data,
                    borderColor: this.defaultColors.primary,
                    borderWidth: 1,
                    upColor: this.defaultColors.success,
                    downColor: this.defaultColors.danger,
                    wickColor: this.defaultColors.primary
                }]
            },
            options: chartOptions
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // OHLC BAR CHART (Fallback for candlestick)
    // ============================================================
    
    createOHLCBarChart(canvasId, data, options = {}) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        const candles = data.candles || data;
        const labels = candles.map((_, i) => i);
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Bullish',
                        data: candles.map(c => c.c >= c.o ? c.c : null),
                        backgroundColor: this.defaultColors.success,
                        borderColor: this.defaultColors.success,
                        borderWidth: 1,
                        borderRadius: 2,
                        barPercentage: 0.7,
                        categoryPercentage: 0.8
                    },
                    {
                        label: 'Bearish',
                        data: candles.map(c => c.c < c.o ? c.c : null),
                        backgroundColor: this.defaultColors.danger,
                        borderColor: this.defaultColors.danger,
                        borderWidth: 1,
                        borderRadius: 2,
                        barPercentage: 0.7,
                        categoryPercentage: 0.8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const index = context.dataIndex;
                                const candle = candles[index];
                                if (candle) {
                                    return [
                                        `Open: ${candle.o.toFixed(5)}`,
                                        `High: ${candle.h.toFixed(5)}`,
                                        `Low: ${candle.l.toFixed(5)}`,
                                        `Close: ${candle.c.toFixed(5)}`
                                    ];
                                }
                                return '';
                            }
                        }
                    },
                    legend: { labels: { color: this.themes[this.currentTheme].textColor } }
                },
                scales: {
                    x: { ticks: { color: this.themes[this.currentTheme].textColor }, grid: { color: this.themes[this.currentTheme].gridColor } },
                    y: { ticks: { color: this.themes[this.currentTheme].textColor }, grid: { color: this.themes[this.currentTheme].gridColor } }
                }
            }
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // NEW: CORRELATION MATRIX CHART (Heatmap style)
    // ============================================================
    
    createCorrelationMatrixChart(canvasId, correlations) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        const pairs = correlations.map(c => c.pair);
        const values = correlations.map(c => c.correlation);
        
        // Create horizontal bar chart for correlations
        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: pairs,
                datasets: [{
                    label: 'Correlation with EUR/USD',
                    data: values,
                    backgroundColor: values.map(v => {
                        if (v > 0.5) return this.defaultColors.success;
                        if (v > 0) return this.defaultColors.info;
                        if (v > -0.3) return this.defaultColors.warning;
                        return this.defaultColors.danger;
                    }),
                    borderRadius: 4,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const value = context.raw;
                                const strength = Math.abs(value) > 0.7 ? 'Strong' : Math.abs(value) > 0.4 ? 'Moderate' : 'Weak';
                                const direction = value > 0 ? 'Positive' : value < 0 ? 'Negative' : 'Neutral';
                                return `${direction} correlation (${value.toFixed(3)}) - ${strength}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Correlation Coefficient', color: this.themes[this.currentTheme].textColor },
                        ticks: { color: this.themes[this.currentTheme].textColor, callback: (v) => v.toFixed(2) },
                        grid: { color: this.themes[this.currentTheme].gridColor },
                        min: -1,
                        max: 1
                    },
                    y: {
                        ticks: { color: this.themes[this.currentTheme].textColor },
                        grid: { color: this.themes[this.currentTheme].gridColor }
                    }
                }
            }
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // NEW: MARKET HOLIDAYS CALENDAR CHART
    // ============================================================
    
    createHolidaysCalendarChart(canvasId, holidays) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        // Group holidays by month
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const holidayCountByMonth = new Array(12).fill(0);
        
        holidays.forEach(holiday => {
            const date = new Date(holiday.date);
            const month = date.getMonth();
            holidayCountByMonth[month]++;
        });
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Number of Market Holidays',
                    data: holidayCountByMonth,
                    borderColor: this.defaultColors.primary,
                    backgroundColor: `${this.defaultColors.primary}33`,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: this.defaultColors.primary,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: this.themes[this.currentTheme].textColor } },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const count = context.raw;
                                const month = months[context.dataIndex];
                                return `${month}: ${count} holiday${count !== 1 ? 's' : ''}`;
                            }
                        }
                    }
                },
                scales: {
                    x: { 
                        ticks: { color: this.themes[this.currentTheme].textColor },
                        grid: { color: this.themes[this.currentTheme].gridColor }
                    },
                    y: {
                        ticks: { color: this.themes[this.currentTheme].textColor, stepSize: 1 },
                        grid: { color: this.themes[this.currentTheme].gridColor },
                        title: { display: true, text: 'Number of Holidays', color: this.themes[this.currentTheme].textColor }
                    }
                }
            }
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // NEW: API STATUS DASHBOARD CHART
    // ============================================================
    
    createAPIStatusChart(canvasId, statusData) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        const apis = statusData.map(s => s.name);
        const responseTimes = statusData.map(s => s.responseTime || 0);
        const colors = statusData.map(s => {
            if (s.status === 'online') return this.defaultColors.success;
            if (s.status === 'degraded') return this.defaultColors.warning;
            return this.defaultColors.danger;
        });
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: apis,
                datasets: [{
                    label: 'Response Time (ms)',
                    data: responseTimes,
                    backgroundColor: colors,
                    borderRadius: 4,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const index = context.dataIndex;
                                const api = statusData[index];
                                return [
                                    `Status: ${api.status.toUpperCase()}`,
                                    `Response: ${api.responseTime || 0}ms`,
                                    `Last Update: ${api.lastUpdate || 'N/A'}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        title: { display: true, text: 'Response Time (ms)', color: this.themes[this.currentTheme].textColor },
                        ticks: { color: this.themes[this.currentTheme].textColor },
                        grid: { color: this.themes[this.currentTheme].gridColor }
                    },
                    x: {
                        ticks: { color: this.themes[this.currentTheme].textColor },
                        grid: { color: this.themes[this.currentTheme].gridColor }
                    }
                }
            }
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // NEW: API STATUS DONUT CHART (Uptime/Downtime)
    // ============================================================
    
    createAPIUptimeChart(canvasId, uptimePercent, apiName) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        const color = uptimePercent >= 99 ? this.defaultColors.success : 
                      uptimePercent >= 95 ? this.defaultColors.warning : 
                      this.defaultColors.danger;
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Uptime', 'Downtime'],
                datasets: [{
                    data: [uptimePercent, 100 - uptimePercent],
                    backgroundColor: [color, '#2c3e50'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: '60%',
                plugins: {
                    legend: { 
                        position: 'bottom',
                        labels: { color: this.themes[this.currentTheme].textColor, font: { size: 10 } }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label;
                                const value = context.raw;
                                return `${label}: ${value.toFixed(1)}%`;
                            }
                        }
                    }
                }
            }
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // PRICE LINE CHART
    // ============================================================
    
    createPriceChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;
        
        this.destroyChart(canvasId);
        const ctx = canvas.getContext('2d');
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: true,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { 
                    labels: { 
                        color: this.themes[this.currentTheme].textColor,
                        font: { size: 11 }
                    } 
                },
                tooltip: { 
                    mode: 'index', 
                    intersect: false,
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    titleColor: this.defaultColors.primary,
                    bodyColor: '#ffffff',
                    borderColor: this.defaultColors.primary,
                    borderWidth: 1
                }
            },
            scales: {
                x: { 
                    grid: { color: this.themes[this.currentTheme].gridColor }, 
                    ticks: { color: this.themes[this.currentTheme].textColor } 
                },
                y: { 
                    grid: { color: this.themes[this.currentTheme].gridColor }, 
                    ticks: { color: this.themes[this.currentTheme].textColor } 
                }
            }
        };
        
        const chartOptions = { ...defaultOptions, ...options };
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'EUR/USD',
                    data: data.prices || [],
                    borderColor: this.defaultColors.primary,
                    backgroundColor: this.defaultColors.background,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: this.defaultColors.primary,
                    pointHoverBorderColor: '#ffffff',
                    pointHoverBorderWidth: 2
                }]
            },
            options: chartOptions
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // AREA CHART
    // ============================================================
    
    createAreaChart(canvasId, data, color = null) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        const chartColor = color || this.defaultColors.primary;
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: data.label || 'Value',
                    data: data.values || [],
                    borderColor: chartColor,
                    backgroundColor: `${chartColor}33`,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: this.themes[this.currentTheme].textColor } },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    x: { ticks: { color: this.themes[this.currentTheme].textColor }, grid: { color: this.themes[this.currentTheme].gridColor } },
                    y: { ticks: { color: this.themes[this.currentTheme].textColor }, grid: { color: this.themes[this.currentTheme].gridColor } }
                }
            }
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // RSI GAUGE
    // ============================================================
    
    createRSIGauge(canvasId, rsiValue) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        let color;
        if (rsiValue < 30) color = this.defaultColors.success;
        else if (rsiValue > 70) color = this.defaultColors.danger;
        else color = this.defaultColors.warning;
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [rsiValue, 100 - rsiValue],
                    backgroundColor: [color, '#2c3e50'],
                    borderWidth: 0,
                    circumference: 180,
                    rotation: 270
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: '70%',
                plugins: {
                    legend: { display: false },
                    tooltip: { 
                        enabled: true,
                        callbacks: {
                            label: () => `RSI: ${rsiValue.toFixed(1)}`
                        }
                    }
                }
            }
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // FEAR & GREED GAUGE
    // ============================================================
    
    createFearGreedGauge(canvasId, value) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        let color;
        let label = '';
        if (value >= 80) { color = this.defaultColors.success; label = 'Extreme Greed'; }
        else if (value >= 60) { color = this.defaultColors.success; label = 'Greed'; }
        else if (value >= 40) { color = this.defaultColors.warning; label = 'Neutral'; }
        else if (value >= 20) { color = this.defaultColors.danger; label = 'Fear'; }
        else { color = this.defaultColors.danger; label = 'Extreme Fear'; }
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [value, 100 - value],
                    backgroundColor: [color, '#2c3e50'],
                    borderWidth: 0,
                    circumference: 180,
                    rotation: 270
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: '70%',
                plugins: {
                    legend: { display: false },
                    tooltip: { 
                        enabled: true,
                        callbacks: {
                            label: () => `${label}: ${value.toFixed(0)}`
                        }
                    }
                }
            }
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // GAUGE CHART (General purpose)
    // ============================================================
    
    createGauge(canvasId, value, min, max, title, colorMap = null) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        const percent = ((value - min) / (max - min)) * 100;
        const clampedPercent = Math.min(100, Math.max(0, percent));
        
        let color = this.defaultColors.primary;
        if (colorMap) {
            for (const [range, col] of Object.entries(colorMap)) {
                const [low, high] = range.split('-').map(Number);
                if (value >= low && value <= high) color = col;
            }
        }
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [title, ''],
                datasets: [{
                    data: [clampedPercent, 100 - clampedPercent],
                    backgroundColor: [color, '#2c3e50'],
                    borderWidth: 0
                }]
            },
            options: {
                cutout: '70%',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: () => `${title}: ${value.toFixed(1)}`
                        }
                    }
                }
            }
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // ADX CHART
    // ============================================================
    
    createADXChart(canvasId, data) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [
                    {
                        label: 'ADX',
                        data: data.adx || [],
                        borderColor: this.defaultColors.primary,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3
                    },
                    {
                        label: '+DI',
                        data: data.plusDi || [],
                        borderColor: this.defaultColors.success,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3
                    },
                    {
                        label: '-DI',
                        data: data.minusDi || [],
                        borderColor: this.defaultColors.danger,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: this.themes[this.currentTheme].textColor, font: { size: 10 } } }
                },
                scales: {
                    x: { ticks: { color: this.themes[this.currentTheme].textColor }, grid: { color: this.themes[this.currentTheme].gridColor } },
                    y: { ticks: { color: this.themes[this.currentTheme].textColor }, grid: { color: this.themes[this.currentTheme].gridColor } }
                }
            }
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // MACD CHART
    // ============================================================
    
    createMACDChart(canvasId, data) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        const histogramColors = data.histogram.map(v => v >= 0 ? this.defaultColors.success : this.defaultColors.danger);
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [
                    {
                        label: 'MACD Histogram',
                        data: data.histogram || [],
                        backgroundColor: histogramColors,
                        borderWidth: 0,
                        barPercentage: 0.8,
                        yAxisID: 'y'
                    },
                    {
                        label: 'MACD Line',
                        data: data.macd || [],
                        borderColor: this.defaultColors.primary,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        fill: false,
                        type: 'line',
                        tension: 0.3,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Signal Line',
                        data: data.signal || [],
                        borderColor: this.defaultColors.warning,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        fill: false,
                        type: 'line',
                        tension: 0.3,
                        yAxisID: 'y'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: this.themes[this.currentTheme].textColor, font: { size: 10 } } }
                },
                scales: {
                    x: { ticks: { color: this.themes[this.currentTheme].textColor }, grid: { color: this.themes[this.currentTheme].gridColor } },
                    y: { ticks: { color: this.themes[this.currentTheme].textColor }, grid: { color: this.themes[this.currentTheme].gridColor } }
                }
            }
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // BOLLINGER BANDS CHART
    // ============================================================
    
    createBollingerBandsChart(canvasId, data) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [
                    {
                        label: 'Price',
                        data: data.prices || [],
                        borderColor: this.defaultColors.primary,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.2,
                        pointRadius: 0
                    },
                    {
                        label: 'Upper Band',
                        data: data.upper || [],
                        borderColor: this.defaultColors.danger,
                        backgroundColor: 'transparent',
                        borderWidth: 1,
                        fill: false,
                        borderDash: [5, 5],
                        pointRadius: 0
                    },
                    {
                        label: 'Middle Band (SMA)',
                        data: data.middle || [],
                        borderColor: this.defaultColors.warning,
                        backgroundColor: 'transparent',
                        borderWidth: 1,
                        fill: false,
                        pointRadius: 0
                    },
                    {
                        label: 'Lower Band',
                        data: data.lower || [],
                        borderColor: this.defaultColors.success,
                        backgroundColor: 'transparent',
                        borderWidth: 1,
                        fill: false,
                        borderDash: [5, 5],
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: this.themes[this.currentTheme].textColor, font: { size: 10 } } }
                },
                scales: {
                    x: { ticks: { color: this.themes[this.currentTheme].textColor }, grid: { color: this.themes[this.currentTheme].gridColor } },
                    y: { ticks: { color: this.themes[this.currentTheme].textColor }, grid: { color: this.themes[this.currentTheme].gridColor } }
                }
            }
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // VOLUME CHART
    // ============================================================
    
    createVolumeChart(canvasId, data) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        const avgVolume = data.volumes.reduce((a, b) => a + b, 0) / data.volumes.length;
        const colors = data.volumes.map(v => v > avgVolume ? this.defaultColors.success : this.defaultColors.warning);
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Volume',
                    data: data.volumes || [],
                    backgroundColor: colors,
                    borderWidth: 0,
                    barPercentage: 0.8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: this.themes[this.currentTheme].textColor } },
                    tooltip: {
                        callbacks: {
                            label: (context) => `Volume: ${context.raw.toLocaleString()}`
                        }
                    }
                },
                scales: {
                    x: { ticks: { color: this.themes[this.currentTheme].textColor }, grid: { display: false } },
                    y: { ticks: { color: this.themes[this.currentTheme].textColor }, grid: { color: this.themes[this.currentTheme].gridColor } }
                }
            }
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // OBV (On-Balance Volume) CHART
    // ============================================================
    
    createOBVChart(canvasId, data) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'OBV',
                    data: data.obv || [],
                    borderColor: this.defaultColors.info,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.3,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: this.themes[this.currentTheme].textColor } }
                },
                scales: {
                    x: { ticks: { color: this.themes[this.currentTheme].textColor }, grid: { color: this.themes[this.currentTheme].gridColor } },
                    y: { ticks: { color: this.themes[this.currentTheme].textColor }, grid: { color: this.themes[this.currentTheme].gridColor } }
                }
            }
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // CONFIDENCE GAUGE
    // ============================================================
    
    createConfidenceGauge(canvasId, confidence) {
        return this.createGauge(canvasId, confidence, 0, 100, 'Confidence', {
            '0-30': this.defaultColors.danger,
            '30-60': this.defaultColors.warning,
            '60-100': this.defaultColors.success
        });
    }
    
    // ============================================================
    // RISK GAUGE
    // ============================================================
    
    createRiskGauge(canvasId, riskScore) {
        return this.createGauge(canvasId, riskScore, 0, 100, 'Risk', {
            '0-30': this.defaultColors.success,
            '30-60': this.defaultColors.warning,
            '60-100': this.defaultColors.danger
        });
    }
    
    // ============================================================
    // SENTIMENT GAUGE
    // ============================================================
    
    createSentimentGauge(canvasId, sentimentScore) {
        const value = ((sentimentScore + 1) / 2) * 100;
        return this.createGauge(canvasId, value, 0, 100, 'Sentiment', {
            '0-33': this.defaultColors.danger,
            '33-66': this.defaultColors.warning,
            '66-100': this.defaultColors.success
        });
    }
    
    // ============================================================
    // NEW: API RESPONSE TIME CHART (for monitoring)
    // ============================================================
    
    createAPIResponseChart(canvasId, timestamps, responseTimes) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: 'API Response Time (ms)',
                    data: responseTimes,
                    borderColor: this.defaultColors.primary,
                    backgroundColor: `${this.defaultColors.primary}33`,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: this.themes[this.currentTheme].textColor } },
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.raw.toFixed(0)}ms`
                        }
                    }
                },
                scales: {
                    y: {
                        title: { display: true, text: 'Response Time (ms)', color: this.themes[this.currentTheme].textColor },
                        ticks: { color: this.themes[this.currentTheme].textColor },
                        grid: { color: this.themes[this.currentTheme].gridColor }
                    },
                    x: {
                        ticks: { color: this.themes[this.currentTheme].textColor },
                        grid: { color: this.themes[this.currentTheme].gridColor }
                    }
                }
            }
        });
        
        return this.charts[canvasId];
    }
    
    // ============================================================
    // SET THEME
    // ============================================================
    
    setTheme(theme) {
        if (this.themes[theme]) {
            this.currentTheme = theme;
            // Refresh all charts with new theme
            Object.keys(this.charts).forEach(chartId => {
                const chart = this.charts[chartId];
                if (chart) {
                    if (chart.options.scales) {
                        if (chart.options.scales.x) {
                            chart.options.scales.x.ticks.color = this.themes[theme].textColor;
                            chart.options.scales.x.grid.color = this.themes[theme].gridColor;
                        }
                        if (chart.options.scales.y) {
                            chart.options.scales.y.ticks.color = this.themes[theme].textColor;
                            chart.options.scales.y.grid.color = this.themes[theme].gridColor;
                        }
                    }
                    chart.update();
                }
            });
        }
    }
    
    // ============================================================
    // UTILITY METHODS
    // ============================================================
    
    updateChart(chartId, newData, datasetIndex = 0) {
        if (this.charts[chartId]) {
            this.charts[chartId].data.datasets[datasetIndex].data = newData;
            this.charts[chartId].update('none');
        }
    }
    
    updateChartDataset(chartId, datasetIndex, newData, newLabel = null) {
        if (this.charts[chartId]) {
            this.charts[chartId].data.datasets[datasetIndex].data = newData;
            if (newLabel) {
                this.charts[chartId].data.datasets[datasetIndex].label = newLabel;
            }
            this.charts[chartId].update('none');
        }
    }
    
    addDataToChart(chartId, newDataPoint, datasetIndex = 0) {
        if (this.charts[chartId]) {
            this.charts[chartId].data.datasets[datasetIndex].data.push(newDataPoint);
            this.charts[chartId].update('none');
        }
    }
    
    removeFirstDataPoint(chartId, datasetIndex = 0) {
        if (this.charts[chartId]) {
            this.charts[chartId].data.datasets[datasetIndex].data.shift();
            this.charts[chartId].update('none');
        }
    }
    
    destroyChart(chartId) {
        if (this.charts[chartId]) {
            this.charts[chartId].destroy();
            delete this.charts[chartId];
        }
    }
    
    destroyAll() {
        Object.keys(this.charts).forEach(id => this.destroyChart(id));
    }
    
    getChart(chartId) {
        return this.charts[chartId] || null;
    }
    
    chartExists(chartId) {
        return !!this.charts[chartId];
    }
    
    // ============================================================
    // EXPORT CHART AS IMAGE
    // ============================================================
    
    exportAsImage(chartId, format = 'png') {
        const chart = this.charts[chartId];
        if (!chart) return null;
        
        const canvas = chart.canvas;
        const link = document.createElement('a');
        link.download = `chart_${chartId}_${Date.now()}.${format}`;
        link.href = canvas.toDataURL(`image/${format}`);
        link.click();
    }
    
    // ============================================================
    // TOGGLE DATASET VISIBILITY
    // ============================================================
    
    toggleDataset(chartId, datasetIndex) {
        if (this.charts[chartId]) {
            const meta = this.charts[chartId].getDatasetMeta(datasetIndex);
            meta.hidden = !meta.hidden;
            this.charts[chartId].update();
        }
    }
    
    // ============================================================
    // RESIZE ALL CHARTS
    // ============================================================
    
    resizeAll() {
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.resize) {
                chart.resize();
            }
        });
    }
    
    // ============================================================
    // NEW: HOLIDAY IMPACT HEATMAP (which months have most holidays)
    // ============================================================
    
    createHolidayImpactHeatmap(canvasId, holidays) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        // Count holidays by month
        const monthCounts = new Array(12).fill(0);
        holidays.forEach(holiday => {
            const month = new Date(holiday.date).getMonth();
            monthCounts[month]++;
        });
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Market Holidays',
                    data: monthCounts,
                    backgroundColor: `${this.defaultColors.primary}33`,
                    borderColor: this.defaultColors.primary,
                    borderWidth: 2,
                    pointBackgroundColor: this.defaultColors.primary,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: this.themes[this.currentTheme].textColor } },
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.label}: ${context.raw} holiday${context.raw !== 1 ? 's' : ''}`
                        }
                    }
                },
                scales: {
                    r: {
                        ticks: { color: this.themes[this.currentTheme].textColor, stepSize: 1 },
                        grid: { color: this.themes[this.currentTheme].gridColor },
                        angleLines: { color: this.themes[this.currentTheme].gridColor }
                    }
                }
            }
        });
        
        return this.charts[canvasId];
    }
}

// Create global instance
window.ChartManager = ChartManager;
window.chartManager = new ChartManager();

// Handle window resize
window.addEventListener('resize', () => {
    if (window.chartManager) {
        window.chartManager.resizeAll();
    }
});

console.log('✅ Chart Manager v3.1 loaded with Correlations, Holidays & API Status charts');