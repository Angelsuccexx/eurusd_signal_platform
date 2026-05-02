"""
setup_frontend_complete.py - Complete frontend setup
Deletes old structure and creates new professional frontend
Run: python setup_frontend_complete.py
"""

import os
import shutil
from pathlib import Path

def delete_old_frontend():
    """Delete old frontend structure"""
    frontend_path = Path("frontend")
    if frontend_path.exists():
        shutil.rmtree(frontend_path)
        print("✅ Deleted old frontend structure")
    else:
        print("⚠️ No old frontend found")

def create_directory_structure():
    """Create new directory structure"""
    directories = [
        'frontend',
        'frontend/css',
        'frontend/js',
        'frontend/pages',
        'frontend/assets',
        'frontend/assets/images',
        'frontend/assets/fonts'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")

def create_main_css():
    """Create professional main CSS file"""
    css_content = '''/* ========================================
   EUR/USD SIGNAL PLATFORM - PROFESSIONAL CSS
   Version: 5.0.0
   ======================================== */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --primary-light: #818cf8;
    --secondary: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    --info: #3b82f6;
    --dark-bg: #0a0a0f;
    --card-bg: #13131a;
    --sidebar-bg: #0a0a0f;
    --header-bg: #0f0f1a;
    --border: #1e1e2e;
    --border-light: #2a2a3a;
    --text-primary: #f3f4f6;
    --text-secondary: #9ca3af;
    --text-muted: #6b7280;
    --success: #10b981;
    --success-bg: rgba(16, 185, 129, 0.1);
    --danger-bg: rgba(239, 68, 68, 0.1);
    --warning-bg: rgba(245, 158, 11, 0.1);
    --info-bg: rgba(59, 130, 246, 0.1);
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--dark-bg);
    color: var(--text-primary);
    line-height: 1.5;
    overflow-x: hidden;
}

/* ========================================
   LAYOUT
   ======================================== */
.app {
    display: flex;
    min-height: 100vh;
}

/* Sidebar */
.sidebar {
    width: 280px;
    background: var(--sidebar-bg);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    position: fixed;
    height: 100vh;
    overflow-y: auto;
    z-index: 100;
}

.sidebar-header {
    padding: 24px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 12px;
}

.logo-icon {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 20px;
    color: white;
}

.logo-text h2 {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 4px;
}

.logo-text span {
    font-size: 11px;
    color: var(--text-muted);
}

/* Navigation */
.sidebar-nav {
    flex: 1;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.nav-link {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 12px;
    color: var(--text-secondary);
    text-decoration: none;
    transition: all 0.2s ease;
    position: relative;
}

.nav-link i {
    width: 20px;
    font-size: 18px;
}

.nav-link:hover {
    background: rgba(99, 102, 241, 0.1);
    color: var(--text-primary);
}

.nav-link.active {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(79, 70, 229, 0.1));
    color: var(--primary);
    border: 1px solid rgba(99, 102, 241, 0.3);
}

.nav-link .badge {
    margin-left: auto;
    background: var(--border-light);
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 600;
}

.nav-link .badge.live {
    background: var(--danger);
    color: white;
}

.nav-link.active .badge {
    background: var(--primary);
    color: white;
}

/* Main Content */
.main-content {
    flex: 1;
    margin-left: 280px;
    min-height: 100vh;
}

/* Header */
.main-header {
    background: var(--header-bg);
    border-bottom: 1px solid var(--border);
    padding: 16px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 99;
}

.page-title h1 {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 4px;
}

.page-title .breadcrumb {
    font-size: 12px;
    color: var(--text-muted);
}

.header-controls {
    display: flex;
    align-items: center;
    gap: 16px;
}

.live-status {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background: var(--card-bg);
    border-radius: 20px;
    font-size: 12px;
}

.pulse {
    width: 8px;
    height: 8px;
    background: var(--secondary);
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.2); }
}

.auto-refresh {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
}

.auto-refresh label {
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
}

#refreshInterval {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px 10px;
    color: var(--text-primary);
    font-size: 12px;
    cursor: pointer;
}

.btn-icon {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 12px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s;
    font-size: 14px;
}

.btn-icon:hover {
    background: var(--border-light);
    color: var(--text-primary);
}

/* Price Bar */
.price-bar {
    background: linear-gradient(135deg, var(--card-bg), var(--dark-bg));
    padding: 16px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
    gap: 16px;
}

.price-main {
    display: flex;
    align-items: baseline;
    gap: 12px;
}

.symbol {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-muted);
}

.price {
    font-size: 32px;
    font-weight: 800;
}

.change {
    font-size: 14px;
    font-weight: 500;
    padding: 4px 8px;
    border-radius: 20px;
}

.change.positive {
    color: var(--secondary);
    background: var(--success-bg);
}

.change.negative {
    color: var(--danger);
    background: var(--danger-bg);
}

.price-details {
    display: flex;
    gap: 24px;
    font-size: 13px;
}

.price-details span {
    color: var(--text-muted);
}

.price-details span strong {
    color: var(--text-primary);
}

/* Page Content */
.page-container {
    padding: 24px;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Cards Grid */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 24px;
}

.main-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 20px;
    overflow: hidden;
    transition: all 0.3s ease;
}

.main-card:hover {
    transform: translateY(-2px);
    border-color: var(--primary-light);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.card-header {
    padding: 20px 24px;
    background: rgba(255, 255, 255, 0.02);
    display: flex;
    align-items: center;
    gap: 16px;
    cursor: pointer;
    transition: background 0.2s;
}

.card-header:hover {
    background: rgba(255, 255, 255, 0.05);
}

.card-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}

.card-title h3 {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 4px;
}

.card-title p {
    font-size: 12px;
    color: var(--text-muted);
}

.module-count {
    margin-left: auto;
    font-size: 12px;
    padding: 4px 10px;
    background: var(--border-light);
    border-radius: 20px;
}

.card-toggle {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    font-size: 14px;
    transition: transform 0.3s;
}

.card-toggle.open {
    transform: rotate(180deg);
}

.card-content {
    display: none;
    padding: 20px 24px;
    border-top: 1px solid var(--border);
    background: rgba(0, 0, 0, 0.2);
}

.card-content.open {
    display: block;
}

/* Modules Grid */
.modules-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
}

.module-link {
    background: var(--dark-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px;
    display: flex;
    align-items: center;
    gap: 14px;
    text-decoration: none;
    transition: all 0.2s;
    cursor: pointer;
}

.module-link:hover {
    border-color: var(--primary);
    transform: translateX(5px);
    background: rgba(99, 102, 241, 0.05);
}

.module-icon {
    width: 44px;
    height: 44px;
    background: var(--card-bg);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
}

.module-info {
    flex: 1;
}

.module-name {
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 4px;
}

.module-desc {
    font-size: 11px;
    color: var(--text-muted);
}

.module-arrow {
    color: var(--text-muted);
    font-size: 14px;
}

/* Module Detail Page */
.module-detail {
    max-width: 1200px;
    margin: 0 auto;
}

.detail-header {
    margin-bottom: 24px;
}

.detail-header h2 {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 8px;
}

.detail-header p {
    color: var(--text-muted);
}

.detail-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 24px;
}

.detail-card h3 {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Metrics Grid */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
}

.metric-card {
    background: var(--dark-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px;
    transition: all 0.2s;
}

.metric-card:hover {
    border-color: var(--primary);
}

.metric-label {
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 8px;
    display: block;
}

.metric-value {
    font-size: 24px;
    font-weight: 700;
}

.metric-value.small {
    font-size: 16px;
}

.metric-change {
    font-size: 11px;
    margin-top: 6px;
}

.metric-change.positive {
    color: var(--secondary);
}

.metric-change.negative {
    color: var(--danger);
}

/* Chart Container */
.chart-container {
    background: var(--dark-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    margin-top: 20px;
}

.chart-container canvas {
    width: 100%;
    height: 300px;
}

/* Signal Display */
.signal-display {
    text-align: center;
    padding: 20px;
}

.signal-type {
    font-size: 48px;
    font-weight: 800;
    margin-bottom: 16px;
}

.signal-type.BUY {
    color: var(--secondary);
}

.signal-type.SELL {
    color: var(--danger);
}

.signal-type.NEUTRAL {
    color: var(--warning);
}

.confidence-bar {
    height: 8px;
    background: var(--border);
    border-radius: 4px;
    overflow: hidden;
    margin: 16px 0;
}

.confidence-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--primary), var(--primary-light));
    border-radius: 4px;
    transition: width 0.5s ease;
}

/* Levels Grid */
.levels-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 16px;
}

.level-card {
    background: var(--dark-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px;
    text-align: center;
}

.level-label {
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 8px;
}

.level-price {
    font-size: 18px;
    font-weight: 700;
}

/* Timeframe Grid */
.timeframes-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 12px;
    margin-bottom: 20px;
}

.timeframe-card {
    background: var(--dark-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 12px;
    text-align: center;
}

.timeframe-name {
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 6px;
}

.timeframe-value {
    font-size: 14px;
    font-weight: 600;
}

.timeframe-value.bullish {
    color: var(--secondary);
}

.timeframe-value.bearish {
    color: var(--danger);
}

/* Events List */
.events-list {
    max-height: 400px;
    overflow-y: auto;
}

.event-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    border-bottom: 1px solid var(--border);
}

.event-date {
    font-size: 11px;
    color: var(--text-muted);
    min-width: 100px;
}

.event-name {
    flex: 1;
    margin: 0 12px;
    font-size: 13px;
}

.event-impact {
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 12px;
}

.event-impact.high {
    background: var(--danger-bg);
    color: var(--danger);
}

.event-impact.medium {
    background: var(--warning-bg);
    color: var(--warning);
}

.event-impact.low {
    background: var(--success-bg);
    color: var(--success);
}

/* Back Button */
.back-button {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 8px 16px;
    color: var(--text-primary);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    margin-bottom: 16px;
    transition: all 0.2s;
}

.back-button:hover {
    background: var(--border-light);
    border-color: var(--primary);
}

/* Loading State */
.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: var(--dark-bg);
}

::-webkit-scrollbar-thumb {
    background: var(--border-light);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--primary);
}

/* Responsive */
@media (max-width: 1024px) {
    .sidebar {
        width: 80px;
    }
    
    .sidebar-header .logo-text,
    .nav-link span:not(.badge) {
        display: none;
    }
    
    .nav-link {
        justify-content: center;
    }
    
    .main-content {
        margin-left: 80px;
    }
    
    .cards-grid {
        grid-template-columns: 1fr;
    }
    
    .timeframes-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}

@media (max-width: 768px) {
    .price-bar {
        flex-direction: column;
        text-align: center;
    }
    
    .price-details {
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .header-controls {
        flex-wrap: wrap;
    }
    
    .timeframes-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .metrics-grid {
        grid-template-columns: 1fr;
    }
}'''
    
    css_path = Path("frontend/css/main.css")
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("✅ Created: frontend/css/main.css")

def create_main_js():
    """Create main JavaScript file"""
    js_content = '''/**
 * EUR/USD SIGNAL PLATFORM - MAIN APPLICATION
 * Version: 5.0.0
 */

// API Configuration
const API_BASE = '';

// Global state
let currentData = null;
let autoRefresh = true;
let refreshInterval = null;
let refreshSeconds = 30;

// Page definitions with modules
const PAGES = {
    analysis: {
        title: 'Analysis Dashboard',
        modules: [
            { id: 'technical', name: 'Technical Analysis', icon: '📈', desc: 'RSI, MACD, Bollinger Bands, ATR', page: 'technical.html' },
            { id: 'fundamental', name: 'Fundamental Analysis', icon: '🏦', desc: 'Economic indicators, central bank rates', page: 'fundamental.html' },
            { id: 'sentiment', name: 'Sentiment Analysis', icon: '😊', desc: 'News sentiment, market mood', page: 'sentiment.html' },
            { id: 'regime', name: 'Market Regime', icon: '🌊', desc: 'Trending, ranging, volatile detection', page: 'regime.html' },
            { id: 'trend', name: 'Trend Analysis', icon: '📉', desc: 'Direction and strength', page: 'trend.html' },
            { id: 'mtf', name: 'Multi-Timeframe', icon: '⏰', desc: 'M5, M15, H1, H4, D1, W1', page: 'mtf.html' },
            { id: 'ai', name: 'AI Prediction', icon: '🤖', desc: 'Machine learning forecasts', page: 'ai.html' }
        ]
    },
    data: {
        title: 'Data Management',
        modules: [
            { id: 'market-data', name: 'Market Data', icon: '📊', desc: 'Live prices, volume, spreads', page: 'market-data.html' },
            { id: 'calendar', name: 'Economic Calendar', icon: '📅', desc: 'Upcoming economic events', page: 'calendar.html' }
        ]
    },
    signals: {
        title: 'Trading Signals',
        modules: [
            { id: 'current-signal', name: 'Current Signal', icon: '🎯', desc: 'Real-time trading signal', page: 'current-signal.html' },
            { id: 'trading-levels', name: 'Trading Levels', icon: '📐', desc: 'Entry, stop loss, take profit', page: 'trading-levels.html' },
            { id: 'risk', name: 'Risk Management', icon: '🛡️', desc: 'Position sizing, risk assessment', page: 'risk.html' }
        ]
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Platform initializing...');
    loadPage('analysis');
    setupEventListeners();
    startAutoRefresh();
    loadPriceData();
});

function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            if (page) {
                document.querySelectorAll('.nav-link').forEach(nav => nav.classList.remove('active'));
                link.classList.add('active');
                loadPage(page);
            }
        });
    });
    
    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) refreshBtn.addEventListener('click', () => refreshData());
    
    // Export button
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) exportBtn.addEventListener('click', exportReport);
    
    // Auto-refresh toggle
    const autoRefreshToggle = document.getElementById('autoRefreshToggle');
    if (autoRefreshToggle) {
        autoRefreshToggle.addEventListener('change', (e) => {
            autoRefresh = e.target.checked;
            autoRefresh ? startAutoRefresh() : stopAutoRefresh();
        });
    }
    
    // Refresh interval
    const refreshIntervalSelect = document.getElementById('refreshInterval');
    if (refreshIntervalSelect) {
        refreshIntervalSelect.addEventListener('change', (e) => {
            refreshSeconds = parseInt(e.target.value);
            if (autoRefresh) {
                stopAutoRefresh();
                startAutoRefresh();
            }
        });
    }
    
    // Back button
    const backButton = document.getElementById('backButton');
    if (backButton) {
        backButton.addEventListener('click', () => {
            loadPage(currentPage || 'analysis');
        });
    }
}

async function loadPage(page) {
    currentPage = page;
    const container = document.getElementById('pageContainer');
    const backButton = document.getElementById('backButton');
    
    if (!container) return;
    
    // Update back button visibility
    if (backButton) {
        backButton.style.display = page.includes('.html') ? 'flex' : 'none';
    }
    
    if (page.includes('.html')) {
        // Load module detail page
        await loadModulePage(page);
        return;
    }
    
    // Load main dashboard page
    const pageConfig = PAGES[page];
    if (!pageConfig) return;
    
    // Update page title
    document.getElementById('pageTitle').textContent = pageConfig.title;
    
    // Generate HTML
    container.innerHTML = `
        <div class="page-container">
            <div class="cards-grid">
                ${pageConfig.modules.map(module => `
                    <div class="main-card" data-module="${module.id}">
                        <div class="card-header" onclick="navigateToModule('${module.page}')">
                            <div class="card-icon">${module.icon}</div>
                            <div class="card-title">
                                <h3>${module.name}</h3>
                                <p>${module.desc}</p>
                            </div>
                            <i class="fas fa-chevron-right" style="color: var(--text-muted);"></i>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

async function loadModulePage(pageName) {
    const container = document.getElementById('pageContainer');
    if (!container) return;
    
    container.innerHTML = '<div class="loading-container"><div class="spinner"></div><p>Loading module...</p></div>';
    
    try {
        const response = await fetch(`/static/pages/${pageName}`);
        const html = await response.text();
        container.innerHTML = html;
        
        // Initialize charts and load data based on page
        const pageId = pageName.replace('.html', '');
        initializeModulePage(pageId);
        
    } catch (error) {
        console.error('Failed to load page:', error);
        container.innerHTML = `
            <div class="page-container">
                <div class="detail-card" style="text-align: center; padding: 60px;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: var(--warning); margin-bottom: 16px;"></i>
                    <h3>Failed to Load Module</h3>
                    <p style="color: var(--text-muted); margin-top: 8px;">Please try again later.</p>
                    <button onclick="loadPage('${currentPage}')" class="btn-icon" style="margin-top: 20px;">← Go Back</button>
                </div>
            </div>
        `;
    }
}

async function initializeModulePage(pageId) {
    await loadPriceData();
    
    switch(pageId) {
        case 'technical':
            await loadTechnicalData();
            break;
        case 'fundamental':
            await loadFundamentalData();
            break;
        case 'sentiment':
            await loadSentimentData();
            break;
        case 'regime':
            await loadRegimeData();
            break;
        case 'trend':
            await loadTrendData();
            break;
        case 'mtf':
            await loadMTFData();
            break;
        case 'ai':
            await loadAIData();
            break;
        case 'market-data':
            await loadMarketData();
            break;
        case 'calendar':
            await loadCalendarData();
            break;
        case 'current-signal':
            await loadSignalData();
            break;
        case 'trading-levels':
            await loadLevelsData();
            break;
        case 'risk':
            await loadRiskData();
            break;
    }
}

async function loadPriceData() {
    try {
        const response = await fetch(`${API_BASE}/api/price`);
        const data = await response.json();
        
        document.getElementById('currentPrice').textContent = data.price?.toFixed(5) || '1.17675';
        const change = data.change_24h || -0.18;
        const changeEl = document.getElementById('priceChange');
        if (changeEl) {
            changeEl.textContent = `${change}%`;
            changeEl.className = `change ${change >= 0 ? 'positive' : 'negative'}`;
        }
        
        document.getElementById('bidPrice').textContent = (data.price - 0.00006)?.toFixed(5) || '1.17669';
        document.getElementById('askPrice').textContent = (data.price + 0.00006)?.toFixed(5) || '1.17681';
        
    } catch (error) {
        console.error('Failed to load price:', error);
    }
}

async function loadTechnicalData() {
    try {
        const response = await fetch(`${API_BASE}/api/technical`);
        const data = await response.json();
        
        updateMetric('rsiValue', data.rsi?.toFixed(1) || '50.0');
        updateMetric('macdValue', data.macd?.toFixed(6) || '0.000000');
        updateMetric('atrValue', (data.atr_pips || 20) + ' pips');
        updateMetric('adxValue', data.adx?.toFixed(1) || '25.0');
        
        const trendEl = document.getElementById('trendValue');
        if (trendEl) {
            trendEl.textContent = data.trend || 'SIDEWAYS';
            trendEl.className = `metric-value ${data.trend === 'BULLISH' ? 'positive' : data.trend === 'BEARISH' ? 'negative' : ''}`;
        }
        
        // Create chart
        createChart('technicalChart', 'Technical Indicators', ['RSI', 'MACD', 'ADX'], [data.rsi || 50, data.macd || 0, data.adx || 25]);
        
    } catch (error) {
        console.error('Failed to load technical data:', error);
    }
}

async function loadFundamentalData() {
    try {
        const response = await fetch(`${API_BASE}/api/fundamental`);
        const data = await response.json();
        const indicators = data.indicators || {};
        
        updateMetric('fedRate', (indicators.fed_funds_rate || 3.64) + '%');
        updateMetric('gdpValue', (indicators.gdp || 2.1) + '%');
        updateMetric('unemploymentValue', (indicators.unemployment || 4.3) + '%');
        updateMetric('cpiValue', (indicators.cpi || 3.29) + '%');
        updateMetric('biasValue', data.bias || 'NEUTRAL');
        
        createChart('fundamentalChart', 'Economic Indicators', ['Fed Rate', 'GDP', 'Unemployment', 'CPI'], 
                   [indicators.fed_funds_rate || 3.64, indicators.gdp || 2.1, indicators.unemployment || 4.3, indicators.cpi || 3.29]);
        
    } catch (error) {
        console.error('Failed to load fundamental data:', error);
    }
}

async function loadSentimentData() {
    try {
        const response = await fetch(`${API_BASE}/api/sentiment`);
        const data = await response.json();
        
        updateMetric('sentimentScore', data.score?.toFixed(2) || '0.00');
        updateMetric('overallSentiment', data.overall_sentiment || 'NEUTRAL');
        updateMetric('bullishPercent', (data.bullish_percent || 33) + '%');
        updateMetric('bearishPercent', (data.bearish_percent || 33) + '%');
        updateMetric('neutralPercent', (data.neutral_percent || 34) + '%');
        
        createChart('sentimentChart', 'Sentiment Distribution', ['Bullish', 'Bearish', 'Neutral'], 
                   [data.bullish_percent || 33, data.bearish_percent || 33, data.neutral_percent || 34], 'doughnut');
        
    } catch (error) {
        console.error('Failed to load sentiment data:', error);
    }
}

async function loadRegimeData() {
    try {
        const response = await fetch(`${API_BASE}/api/regime`);
        const data = await response.json();
        
        updateMetric('currentRegime', data.regime || 'ranging');
        updateMetric('regimeConfidence', (data.confidence || 34.1) + '%');
        updateMetric('trendDirection', data.trend_direction || 'SIDEWAYS');
        updateMetric('volRegime', data.volatility_regime || 'low');
        
    } catch (error) {
        console.error('Failed to load regime data:', error);
    }
}

async function loadTrendData() {
    try {
        const response = await fetch(`${API_BASE}/api/trend`);
        const data = await response.json();
        
        updateMetric('trendDirection', data.direction || 'SIDEWAYS');
        updateMetric('trendStrength', (data.strength || 50) + '%');
        updateMetric('adxTrend', data.adx?.toFixed(1) || '25.0');
        updateMetric('diPlus', data.plus_di?.toFixed(1) || '25.0');
        updateMetric('diMinus', data.minus_di?.toFixed(1) || '25.0');
        
    } catch (error) {
        console.error('Failed to load trend data:', error);
    }
}

async function loadMTFData() {
    try {
        const response = await fetch(`${API_BASE}/api/mtf`);
        const data = await response.json();
        
        const timeframes = ['M5', 'M15', 'H1', 'H4', 'D1', 'W1'];
        timeframes.forEach(tf => {
            const value = data[tf] || '--';
            const el = document.getElementById(`tf${tf}`);
            if (el) {
                el.textContent = value;
                el.className = `timeframe-value ${value === 'Bullish' ? 'bullish' : value === 'Bearish' ? 'bearish' : ''}`;
            }
        });
        
        updateMetric('mtfAlignment', data.alignment || 'Mixed');
        
    } catch (error) {
        console.error('Failed to load MTF data:', error);
    }
}

async function loadAIData() {
    try {
        const response = await fetch(`${API_BASE}/api/ai`);
        const data = await response.json();
        
        updateMetric('aiPrediction', data.prediction || 'NEUTRAL');
        updateMetric('aiConfidence', ((data.confidence || 0.5) * 100).toFixed(0) + '%');
        updateMetric('expectedMove', (data.expected_move_pips || 20) + ' pips');
        updateMetric('nextHour', data.next_hour?.toFixed(5) || '--');
        updateMetric('nextDay', data.next_day?.toFixed(5) || '--');
        
    } catch (error) {
        console.error('Failed to load AI data:', error);
    }
}

async function loadMarketData() {
    try {
        const response = await fetch(`${API_BASE}/api/price`);
        const data = await response.json();
        
        updateMetric('currentPrice', data.price?.toFixed(5) || '1.17675');
        updateMetric('bidValue', (data.price - 0.00006)?.toFixed(5) || '1.17669');
        updateMetric('askValue', (data.price + 0.00006)?.toFixed(5) || '1.17681');
        updateMetric('spreadValue', '0.6 pips');
        updateMetric('dailyHigh', '1.18526');
        updateMetric('dailyLow', '1.17661');
        
        // Create price chart
        await createPriceChart();
        
    } catch (error) {
        console.error('Failed to load market data:', error);
    }
}

async function loadCalendarData() {
    try {
        const response = await fetch(`${API_BASE}/api/events`);
        const data = await response.json();
        
        const eventsList = document.getElementById('eventsList');
        if (eventsList && data.events) {
            eventsList.innerHTML = data.events.map(event => `
                <div class="event-item">
                    <div class="event-date">${event.date || 'TBD'}</div>
                    <div class="event-name">${event.name || 'Event'}</div>
                    <div class="event-impact ${event.impact || 'medium'}">${(event.impact || 'MEDIUM').toUpperCase()}</div>
                </div>
            `).join('');
        }
        
    } catch (error) {
        console.error('Failed to load calendar data:', error);
    }
}

async function loadSignalData() {
    try {
        const response = await fetch(`${API_BASE}/api/signal`);
        const data = await response.json();
        const signal = data.signal || {};
        
        const signalType = signal.type || 'NEUTRAL';
        const signalEl = document.getElementById('signalType');
        if (signalEl) {
            signalEl.textContent = signalType;
            signalEl.className = `signal-type ${signalType}`;
        }
        
        updateMetric('signalConfidence', (signal.confidence || 50) + '%');
        
        const fillEl = document.getElementById('confidenceFill');
        if (fillEl) fillEl.style.width = (signal.confidence || 50) + '%';
        
    } catch (error) {
        console.error('Failed to load signal data:', error);
    }
}

async function loadLevelsData() {
    try {
        const response = await fetch(`${API_BASE}/api/signal`);
        const data = await response.json();
        const levels = data.levels || {};
        
        updateMetric('entryPrice', levels.entry?.toFixed(5) || '1.17675');
        updateMetric('stopPrice', levels.stop_loss?.toFixed(5) || '1.17875');
        updateMetric('tp1Price', levels.take_profit_1?.toFixed(5) || '1.17375');
        updateMetric('tp2Price', levels.take_profit_2?.toFixed(5) || '1.17175');
        updateMetric('tp3Price', levels.take_profit_3?.toFixed(5) || '1.16975');
        
    } catch (error) {
        console.error('Failed to load levels data:', error);
    }
}

async function loadRiskData() {
    try {
        const response = await fetch(`${API_BASE}/api/risk`);
        const data = await response.json();
        
        updateMetric('accountBalance', '$' + (data.account_balance || 10000).toLocaleString());
        updateMetric('riskPercent', ((data.max_risk_per_trade || 0.02) * 100) + '%');
        updateMetric('riskAmount', '$' + (data.risk_amount || 200));
        updateMetric('positionSize', (data.position_size_lots || 0.10) + ' lots');
        updateMetric('rrRatio', (data.risk_reward_ratio || 2.0) + ':1');
        
    } catch (error) {
        console.error('Failed to load risk data:', error);
    }
}

async function createPriceChart() {
    try {
        const response = await fetch(`${API_BASE}/api/historical/chart?days=30`);
        const data = await response.json();
        
        const ctx = document.getElementById('priceChart')?.getContext('2d');
        if (!ctx) return;
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.data?.labels || [],
                datasets: [{
                    label: 'EUR/USD Price',
                    data: data.data?.prices || [],
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#9ca3af' } }
                },
                scales: {
                    y: { grid: { color: '#1e1e2e' }, ticks: { color: '#9ca3af' } },
                    x: { grid: { display: false }, ticks: { color: '#9ca3af' } }
                }
            }
        });
        
    } catch (error) {
        console.error('Failed to create price chart:', error);
    }
}

function createChart(chartId, title, labels, data, type = 'bar') {
    const ctx = document.getElementById(chartId)?.getContext('2d');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: type === 'doughnut' 
                    ? ['#10b981', '#ef4444', '#f59e0b']
                    : 'rgba(99, 102, 241, 0.7)',
                borderColor: '#6366f1',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#9ca3af' } }
            },
            scales: type !== 'doughnut' ? {
                y: { grid: { color: '#1e1e2e' }, ticks: { color: '#9ca3af' } },
                x: { grid: { display: false }, ticks: { color: '#9ca3af' } }
            } : undefined
        }
    });
}

function updateMetric(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

async function refreshData() {
    await loadPriceData();
    
    if (currentPage === 'analysis') {
        // Already handled by page load
    } else if (currentPage) {
        await initializeModulePage(currentPage);
    }
}

function exportReport() {
    if (!currentData) {
        alert('No data available to export');
        return;
    }
    
    const exportData = {
        timestamp: new Date().toISOString(),
        platform: 'EUR/USD Signal Platform',
        version: '5.0',
        data: currentData
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `eurusd_report_${new Date().toISOString().slice(0, 19)}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

function startAutoRefresh() {
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = setInterval(() => {
        if (autoRefresh) refreshData();
    }, refreshSeconds * 1000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connectionStatus');
    const pulseEl = document.querySelector('.pulse');
    if (statusEl) {
        statusEl.textContent = connected ? 'Live' : 'Reconnecting...';
        statusEl.style.color = connected ? 'var(--secondary)' : 'var(--danger)';
    }
    if (pulseEl) {
        pulseEl.style.background = connected ? 'var(--secondary)' : 'var(--danger)';
    }
}

function navigateToModule(page) {
    loadPage(page);
}

// Make functions global
window.navigateToModule = navigateToModule;
window.loadPage = loadPage;
window.refreshData = refreshData;

console.log('✅ Platform initialized');'''
    
    js_path = Path("frontend/js/main.js")
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("✅ Created: frontend/js/main.js")

def create_index_html():
    """Create main index.html"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EUR/USD Signal Platform | Professional Trading Intelligence</title>
    <link rel="stylesheet" href="/static/css/main.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="app">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="logo-icon">€$</div>
                <div class="logo-text">
                    <h2>FX Signal</h2>
                    <span>Professional Edition</span>
                </div>
            </div>
            
            <nav class="sidebar-nav">
                <a href="#" class="nav-link active" data-page="analysis">
                    <i class="fas fa-chart-line"></i>
                    <span>Analysis</span>
                    <span class="badge">7</span>
                </a>
                <a href="#" class="nav-link" data-page="data">
                    <i class="fas fa-database"></i>
                    <span>Data</span>
                    <span class="badge">2</span>
                </a>
                <a href="#" class="nav-link" data-page="signals">
                    <i class="fas fa-bullhorn"></i>
                    <span>Signals</span>
                    <span class="badge live">LIVE</span>
                </a>
            </nav>
            
            <div class="sidebar-footer">
                <div class="version-info">
                    <i class="fas fa-shield-alt"></i>
                    <span>v5.0 | 24 Modules</span>
                </div>
            </div>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            <header class="main-header">
                <div class="page-title">
                    <h1 id="pageTitle">Analysis Dashboard</h1>
                    <div class="breadcrumb" id="breadcrumb">Dashboard / Analysis</div>
                </div>
                <div class="header-controls">
                    <div class="live-status">
                        <span class="pulse"></span>
                        <span id="connectionStatus">Live</span>
                    </div>
                    <div class="auto-refresh">
                        <label>
                            <input type="checkbox" id="autoRefreshToggle" checked> Auto Refresh
                        </label>
                        <select id="refreshInterval">
                            <option value="30">30 seconds</option>
                            <option value="60">60 seconds</option>
                            <option value="120">2 minutes</option>
                        </select>
                    </div>
                    <button id="exportBtn" class="btn-icon">
                        <i class="fas fa-download"></i>
                    </button>
                    <button id="refreshBtn" class="btn-icon">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                </div>
            </header>

            <!-- Price Bar -->
            <div class="price-bar">
                <div class="price-main">
                    <span class="symbol">EUR/USD</span>
                    <span class="price" id="currentPrice">1.17675</span>
                    <span class="change negative" id="priceChange">-0.18%</span>
                </div>
                <div class="price-details">
                    <span>Bid: <strong id="bidPrice">1.17669</strong></span>
                    <span>Ask: <strong id="askPrice">1.17681</strong></span>
                    <span>Spread: <strong id="spread">0.6</strong> pips</span>
                    <span>Session: <strong id="session">London</strong></span>
                </div>
            </div>

            <!-- Dynamic Page Container -->
            <div id="pageContainer" class="page-container">
                <div class="loading-container">
                    <div class="spinner"></div>
                    <p>Loading dashboard...</p>
                </div>
            </div>
        </main>
    </div>

    <button id="backButton" class="back-button" style="display: none; position: fixed; bottom: 20px; left: 300px; z-index: 1000;">
        <i class="fas fa-arrow-left"></i> Back to Dashboard
    </button>

    <script src="/static/js/main.js"></script>
</body>
</html>'''
    
    html_path = Path("frontend/index.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("✅ Created: frontend/index.html")

def create_module_pages():
    """Create all module detail pages"""
    
    # Template for module pages
    module_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | EUR/USD Signal Platform</title>
    <link rel="stylesheet" href="/static/css/main.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="app">
        <main class="main-content" style="margin-left: 0;">
            <div class="page-container">
                <button class="back-button" onclick="window.location.href='/'">
                    <i class="fas fa-arrow-left"></i> Back to Dashboard
                </button>
                
                <div class="detail-header">
                    <h2>{title}</h2>
                    <p>{description}</p>
                </div>
                
                <div class="detail-card">
                    <h3><i class="{icon}"></i> {title} Overview</h3>
                    <div class="metrics-grid" id="metricsGrid">
                        <!-- Metrics will be populated by JavaScript -->
                    </div>
                </div>
                
                <div class="detail-card">
                    <h3><i class="fas fa-chart-line"></i> Analysis Chart</h3>
                    <div class="chart-container">
                        <canvas id="moduleChart" height="300"></canvas>
                    </div>
                </div>
            </div>
        </main>
    </div>
    <script src="/static/js/main.js"></script>
</body>
</html>'''
    
    modules = [
        ('technical.html', 'Technical Analysis', 'Real-time technical indicators and chart patterns', 'fas fa-chart-line'),
        ('fundamental.html', 'Fundamental Analysis', 'Economic indicators and central bank policies', 'fas fa-building'),
        ('sentiment.html', 'Sentiment Analysis', 'Market sentiment and news analysis', 'fas fa-smile'),
        ('regime.html', 'Market Regime', 'Current market condition identification', 'fas fa-waveform'),
        ('trend.html', 'Trend Analysis', 'Price trend direction and strength', 'fas fa-chart-simple'),
        ('mtf.html', 'Multi-Timeframe Analysis', 'Analysis across multiple timeframes', 'fas fa-clock'),
        ('ai.html', 'AI Price Prediction', 'Machine learning based price forecasts', 'fas fa-robot'),
        ('market-data.html', 'Market Data', 'Live price quotes and market statistics', 'fas fa-chart-line'),
        ('calendar.html', 'Economic Calendar', 'Upcoming economic events and releases', 'fas fa-calendar-alt'),
        ('current-signal.html', 'Current Trading Signal', 'Real-time trading signals', 'fas fa-bullhorn'),
        ('trading-levels.html', 'Trading Levels', 'Entry, stop loss and take profit levels', 'fas fa-chart-simple'),
        ('risk.html', 'Risk Management', 'Position sizing and risk assessment', 'fas fa-shield-alt')
    ]
    
    for filename, title, description, icon in modules:
        content = module_template.format(title=title, description=description, icon=icon)
        file_path = Path(f"frontend/pages/{filename}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created: frontend/pages/{filename}")

def main():
    print("\n" + "="*60)
    print("🚀 SETTING UP PROFESSIONAL FRONTEND")
    print("="*60 + "\n")
    
    # Delete old structure
    delete_old_frontend()
    
    # Create new structure
    create_directory_structure()
    
    # Create all files
    create_main_css()
    create_main_js()
    create_index_html()
    create_module_pages()
    
    print("\n" + "="*60)
    print("✅ FRONTEND SETUP COMPLETE!")
    print("="*60)
    print("\n📁 New structure created:")
    print("   frontend/")
    print("   ├── index.html")
    print("   ├── css/main.css")
    print("   ├── js/main.js")
    print("   └── pages/ (15 module pages)")
    print("\n🚀 Run your backend and visit: http://localhost:5000")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()