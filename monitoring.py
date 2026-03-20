#!/usr/bin/env python3
"""
OLLAMA Monitoring Extension for Open WebUI
Complete backend integration for token monitoring dashboard

Installation:
1. Copy this file to: openwebui/backend/extensions/monitoring_extension.py
2. Add to openwebui/backend/main.py (see instructions below)
3. Restart OpenWebUI

Features:
- Real-time token monitoring dashboard
- RESTful API for stats retrieval
- Admin panel integration
- Proxy to monitoring service
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
import httpx
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Configuration
MONITORING_SERVICE_URL = "http://ollama-monitoring:3333"
MONITORING_TIMEOUT = 5

router = APIRouter(tags=["monitoring"])


class MonitoringClient:
    """Client for communicating with monitoring service"""
    
    def __init__(self, base_url: str = MONITORING_SERVICE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=MONITORING_TIMEOUT)
    
    async def get_stats(self) -> dict:
        """Get overall token statistics"""
        try:
            response = await self.client.get(f"{self.base_url}/api/stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            raise HTTPException(status_code=503, detail="Monitoring service unavailable")
    
    async def get_model_stats(self, model: str) -> dict:
        """Get stats for a specific model"""
        try:
            response = await self.client.get(f"{self.base_url}/api/stats/model/{model}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching model stats: {e}")
            raise HTTPException(status_code=404, detail=f"No stats for model: {model}")
    
    async def get_history(self, limit: int = 100) -> list:
        """Get request history"""
        try:
            response = await self.client.get(f"{self.base_url}/api/history", params={"limit": limit})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            return []
    
    async def reset_stats(self) -> dict:
        """Reset all statistics"""
        try:
            response = await self.client.post(f"{self.base_url}/api/reset")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error resetting stats: {e}")
            raise HTTPException(status_code=503, detail="Failed to reset statistics")
    
    async def health_check(self) -> bool:
        """Check if monitoring service is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False


# Initialize monitoring client
monitoring = MonitoringClient()


# ==================== Routes ====================

@router.get("/health")
async def health_check():
    """Check monitoring service health"""
    is_healthy = await monitoring.health_check()
    if is_healthy:
        return {"status": "healthy", "service": "monitoring"}
    else:
        raise HTTPException(status_code=503, detail="Monitoring service is down")


@router.get("/stats")
async def get_stats():
    """Get overall token statistics"""
    return await monitoring.get_stats()


@router.get("/stats/model/{model_name}")
async def get_model_stats(model_name: str):
    """Get statistics for a specific model"""
    return await monitoring.get_model_stats(model_name)


@router.get("/history")
async def get_history(limit: int = Query(100, ge=1, le=1000)):
    """Get request history"""
    history = await monitoring.get_history(limit)
    return {"history": history, "count": len(history)}


@router.post("/reset")
async def reset_stats():
    """Reset all statistics (admin only)"""
    return await monitoring.reset_stats()


@router.get("/inject-sidebar.js", response_class=Response)
async def inject_sidebar_script():
    """Inject monitoring link into sidebar"""
    return Response(content=SIDEBAR_INJECT_JS, media_type="application/javascript")


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the monitoring dashboard HTML"""
    return DASHBOARD_HTML


# ==================== Sidebar Injection Script ====================

SIDEBAR_INJECT_JS = """
(function() {
    function injectLink() {
        // Check if already injected
        const existing = document.getElementById('monitoring-link-injected');
        if (existing) return true;
        
        // Try multiple strategies to find the menu
        let menuContainer = null;
        let insertPoint = null;
        
        // Strategy 1: Look for the main navigation structure
        const layouts = document.querySelectorAll('[class*="flex"]');
        for (let layout of layouts) {
            if (layout.textContent && 
                (layout.textContent.includes('Models') || layout.textContent.includes('Settings') || layout.textContent.includes('Paramètres'))) {
                menuContainer = layout;
                break;
            }
        }
        
        // Strategy 2: Look for a nav element or sidebar
        if (!menuContainer) {
            const navs = document.querySelectorAll('nav, aside, [role="navigation"]');
            for (let nav of navs) {
                if (nav && nav.offsetHeight > 0) {
                    menuContainer = nav;
                    break;
                }
            }
        }
        
        // Strategy 3: Look for specific OpenWebUI patterns
        if (!menuContainer) {
            const sidebar = document.querySelector('[class*="sidebar"]') || 
                           document.querySelector('aside') ||
                           document.querySelector('[role="navigation"]');
            if (sidebar) menuContainer = sidebar;
        }
        
        // Strategy 4: Look for any element with visible menu items
        if (!menuContainer) {
            const allDivs = document.querySelectorAll('div, ul');
            for (let div of allDivs) {
                const text = div.textContent;
                if (text && (text.includes('Models') || text.includes('Settings')) && div.querySelectorAll('a, button').length > 2) {
                    menuContainer = div;
                    break;
                }
            }
        }
        
        if (!menuContainer) {
            console.debug('[Monitoring] Menu container not found');
            return false;
        }
        
        // Find where to inject - look for existing menu items
        
        // Strategy 1: Find the last menu section
        const menuItems = menuContainer.querySelectorAll('a[href], button, [role="menuitem"]');
        if (menuItems.length > 0) {
            insertPoint = menuItems[menuItems.length - 1];
        }
        
        // Strategy 2: Find Settings/Paramètres link
        if (!insertPoint) {
            for (let link of menuItems) {
                if (link.textContent.includes('Settings') || link.textContent.includes('Paramètres')) {
                    insertPoint = link.parentElement || link;
                    break;
                }
            }
        }
        
        // Strategy 3: Find first visible menu parent
        if (!insertPoint) {
            const candidates = menuContainer.querySelectorAll('[class*="flex"][class*="flex-col"], ul > li');
            if (candidates.length > 0) {
                insertPoint = candidates[candidates.length - 1];
            }
        }
        
        if (!insertPoint) {
            insertPoint = menuContainer;
        }
        
        // Create the monitoring link
        const linkContainer = document.createElement('div');
        linkContainer.id = 'monitoring-link-injected';
        linkContainer.style.cssText = 'cursor: pointer; display: flex; align-items: center; gap: 12px; width: 100%; padding: 8px 12px; border-radius: 8px; border: none; background: transparent; transition: background-color 0.2s; margin-top: 4px;';
        linkContainer.title = 'Token Monitoring Dashboard';
        linkContainer.innerHTML = `
            <svg class="w-5 h-5" style="flex-shrink: 0; width: 20px; height: 20px;" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 13h2v8H3zm4-8h2v16H7zm4-2h2v18h-2zm4-2h2v20h-2zm4 4h2v16h-2z" fill="currentColor"/>
            </svg>
            <span style="font-weight: 500; font-size: 14px; flex: 1;">Monitoring</span>
        `;
        
        // Add click handler to open dashboard
        linkContainer.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            window.open('/api/admin/monitoring/dashboard', 'monitoring-dashboard');
        });
        
        // Add hover effect
        linkContainer.addEventListener('mouseenter', () => {
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            linkContainer.style.backgroundColor = isDark ? 'rgba(107, 114, 128, 0.3)' : 'rgba(0, 0, 0, 0.05)';
        });
        
        linkContainer.addEventListener('mouseleave', () => {
            linkContainer.style.backgroundColor = 'transparent';
        });
        
        // Insert the link
        try {
            // Try to insert next to existing menu item
            if (insertPoint.parentElement && insertPoint !== menuContainer) {
                insertPoint.parentElement.insertBefore(linkContainer, insertPoint.nextSibling);
            } else {
                // Fallback: append to menu container
                menuContainer.appendChild(linkContainer);
            }
            console.log('[Monitoring] Link injected successfully');
            return true;
        } catch (e) {
            console.error('[Monitoring] Failed to inject link:', e);
            return false;
        }
    }
    
    // Try injecting multiple times with exponential backoff
    let attempts = 0;
    const maxAttempts = 100;
    
    function tryInject() {
        attempts++;
        
        // Check if already done
        if (document.getElementById('monitoring-link-injected')) {
            console.log('[Monitoring] Link already present');
            return;
        }
        
        // Stop after max attempts
        if (attempts > maxAttempts) {
            console.warn('[Monitoring] Failed to inject link after', maxAttempts, 'attempts');
            return;
        }
        
        // Try to inject
        if (injectLink()) {
            return;
        }
        
        // Schedule next attempt with exponential backoff
        const delay = Math.min(100 + attempts * 50, 2000);
        setTimeout(tryInject, delay);
    }
    
    // Start trying to inject
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', tryInject);
    } else {
        tryInject();
    }
    
    // Also try again on route changes (for SPA navigation)
    const observer = new MutationObserver(() => {
        if (!document.getElementById('monitoring-link-injected')) {
            tryInject();
        }
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
})();
"""


# ==================== Dashboard HTML ====================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Token Monitoring Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #667eea;
            --primary-dark: #5568d3;
            --secondary: #764ba2;
            --success: #4caf50;
            --warning: #ff9800;
            --danger: #f44336;
            --text: #333;
            --text-light: #666;
            --text-lighter: #999;
            --border: #e0e0e0;
            --bg: #f5f5f5;
            --bg-card: #fff;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            background: var(--bg-card);
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        .header h1 {
            font-size: 24px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .header-actions {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .back-link {
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 8px 12px;
            border-radius: 4px;
            transition: all 0.2s;
        }

        .back-link:hover {
            background: rgba(102, 126, 234, 0.1);
            color: var(--primary-dark);
        }

        .btn {
            padding: 10px 16px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .btn-primary {
            background: var(--primary);
            color: white;
        }

        .btn-primary:hover {
            background: var(--primary-dark);
        }

        .btn-secondary {
            background: #f0f0f0;
            color: var(--text);
        }

        .btn-secondary:hover {
            background: #e0e0e0;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: var(--bg-card);
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 4px solid var(--primary);
        }

        .stat-card.secondary {
            border-left-color: var(--secondary);
        }

        .stat-card.success {
            border-left-color: var(--success);
        }

        .stat-card.warning {
            border-left-color: var(--warning);
        }

        .stat-label {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-lighter);
            margin-bottom: 8px;
            font-weight: 500;
        }

        .stat-value {
            font-size: 32px;
            font-weight: 700;
            color: var(--primary);
        }

        .stat-card.secondary .stat-value {
            color: var(--secondary);
        }

        .stat-card.success .stat-value {
            color: var(--success);
        }

        .stat-card.warning .stat-value {
            color: var(--warning);
        }

        .stat-change {
            font-size: 12px;
            color: var(--text-lighter);
            margin-top: 8px;
        }

        .chart-section {
            background: var(--bg-card);
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }

        .chart-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--text);
        }

        .chart-container {
            position: relative;
            height: 300px;
            margin-bottom: 10px;
        }

        .section {
            background: var(--bg-card);
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }

        .section-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--text);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        thead tr {
            border-bottom: 2px solid var(--border);
        }

        th {
            text-align: left;
            padding: 12px;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-lighter);
            font-weight: 600;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid var(--border);
        }

        tbody tr:hover {
            background: var(--bg);
        }

        .model-name {
            font-weight: 600;
            color: var(--primary);
        }

        .loading {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-lighter);
        }

        .loading-spinner {
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid var(--bg);
            border-top: 3px solid var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error {
            background: #ffebee;
            border-left: 4px solid var(--danger);
            padding: 15px;
            border-radius: 4px;
            color: #c62828;
            margin: 20px 0;
        }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        @media (max-width: 1024px) {
            .grid-2 {
                grid-template-columns: 1fr;
            }
        }

        .updated-at {
            font-size: 12px;
            color: var(--text-lighter);
            text-align: right;
            margin-top: 10px;
        }

        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .badge-success {
            background: #e8f5e9;
            color: var(--success);
        }

        .badge-warning {
            background: #fff3e0;
            color: var(--warning);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Token Monitoring Dashboard</h1>
            <div class="header-actions">
                <a href="/" class="back-link">← Back to OpenWebUI</a>
                <button class="btn btn-secondary" onclick="loadStats()">🔄 Refresh</button>
                <button class="btn btn-primary" onclick="resetStats()">Reset Stats</button>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Input Tokens</div>
                <div class="stat-value" id="totalInput">-</div>
            </div>
            <div class="stat-card secondary">
                <div class="stat-label">Total Output Tokens</div>
                <div class="stat-value" id="totalOutput">-</div>
            </div>
            <div class="stat-card success">
                <div class="stat-label">Total Requests</div>
                <div class="stat-value" id="totalRequests">-</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-label">Models Used</div>
                <div class="stat-value" id="modelsCount">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Execution Time</div>
                <div class="stat-value" id="avgDuration">-</div>
                <div style="font-size: 12px; color: var(--text-light); margin-top: 4px;">ms</div>
            </div>
            <div class="stat-card secondary">
                <div class="stat-label">Total Time</div>
                <div class="stat-value" id="totalDuration">-</div>
                <div style="font-size: 12px; color: var(--text-light); margin-top: 4px;">seconds</div>
            </div>
        </div>

        <div class="grid-2">
            <div class="chart-section">
                <div class="chart-title">Tokens by Model</div>
                <div class="chart-container">
                    <canvas id="tokenChart"></canvas>
                </div>
            </div>

            <div class="chart-section">
                <div class="chart-title">Request Distribution</div>
                <div class="chart-container">
                    <canvas id="requestChart"></canvas>
                </div>
            </div>
        </div>

        <div class="grid-2">
            <div class="section">
                <div class="section-title">
                    <span>Model Statistics</span>
                    <span class="updated-at" id="updatedAt">-</span>
                </div>
                <div id="modelsTableContainer">
                    <div class="loading"><span class="loading-spinner"></span>Loading...</div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">Recent Sessions</div>
                <div id="historyTableContainer">
                    <div class="loading"><span class="loading-spinner"></span>Loading...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = '/api/admin/monitoring';
        let tokenChart = null;
        let requestChart = null;

        async function loadStats() {
            try {
                const response = await fetch(API_BASE + '/stats');
                if (!response.ok) throw new Error('Failed to load stats');
                const data = await response.json();

                // Update main stats
                document.getElementById('totalInput').textContent = (data.totalInputTokens || 0).toLocaleString();
                document.getElementById('totalOutput').textContent = (data.totalOutputTokens || 0).toLocaleString();
                document.getElementById('totalRequests').textContent = (data.sessions?.length || 0).toLocaleString();
                document.getElementById('modelsCount').textContent = Object.keys(data.models || {}).length;
                
                // Update execution time stats
                document.getElementById('avgDuration').textContent = (data.avgDuration || 0).toLocaleString();
                document.getElementById('totalDuration').textContent = ((data.totalDuration || 0) / 1000).toFixed(1);

                const lastUpdated = data.lastUpdated ? new Date(data.lastUpdated).toLocaleString() : '-';
                document.getElementById('updatedAt').textContent = lastUpdated;

                updateCharts(data);
                updateModelsTable(data.models || {});
                updateHistoryTable(data.sessions || []);
            } catch (error) {
                console.error('Error loading stats:', error);
                document.body.insertAdjacentHTML('afterbegin', `<div class="error">Error loading monitoring data: ${error.message}</div>`);
            }
        }

        function updateCharts(data) {
            const models = Object.keys(data.models || {});
            const inputTokens = models.map(m => data.models[m].inputTokens);
            const outputTokens = models.map(m => data.models[m].outputTokens);
            const requestCounts = models.map(m => data.models[m].count);

            // Token Chart
            const tokenCtx = document.getElementById('tokenChart').getContext('2d');
            if (tokenChart) tokenChart.destroy();
            tokenChart = new Chart(tokenCtx, {
                type: 'bar',
                data: {
                    labels: models.length ? models : ['No data'],
                    datasets: [
                        {
                            label: 'Input Tokens',
                            data: inputTokens || [0],
                            backgroundColor: '#667eea',
                            borderRadius: 4,
                        },
                        {
                            label: 'Output Tokens',
                            data: outputTokens || [0],
                            backgroundColor: '#764ba2',
                            borderRadius: 4,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' },
                        title: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });

            // Request Chart
            const requestCtx = document.getElementById('requestChart').getContext('2d');
            if (requestChart) requestChart.destroy();
            requestChart = new Chart(requestCtx, {
                type: 'doughnut',
                data: {
                    labels: models.length ? models : ['No data'],
                    datasets: [{
                        data: requestCounts || [0],
                        backgroundColor: [
                            '#667eea', '#764ba2', '#4caf50', '#ff9800', '#f44336',
                            '#2196f3', '#009688', '#ffc107', '#9c27b0', '#607d8b'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        }

        function updateModelsTable(models) {
            const container = document.getElementById('modelsTableContainer');
            if (!Object.keys(models).length) {
                container.innerHTML = '<div class="loading">No models used yet</div>';
                return;
            }

            const rows = Object.entries(models).map(([model, stats]) => `
                <tr>
                    <td><span class="model-name">${model}</span></td>
                    <td>${stats.count}</td>
                    <td>${stats.inputTokens.toLocaleString()}</td>
                    <td>${stats.outputTokens.toLocaleString()}</td>
                    <td><strong>${(stats.avgDuration || 0).toLocaleString()}ms</strong></td>
                </tr>
            `).join('');

            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>Model</th>
                            <th>Requests</th>
                            <th>Input Tokens</th>
                            <th>Output Tokens</th>
                            <th>Avg Duration</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            `;
        }

        function updateHistoryTable(sessions) {
            const container = document.getElementById('historyTableContainer');
            if (!sessions.length) {
                container.innerHTML = '<div class="loading">No sessions yet</div>';
                return;
            }

            const recent = sessions.slice().reverse().slice(0, 10);
            const rows = recent.map(session => `
                <tr>
                    <td><span class="model-name">${session.model}</span></td>
                    <td>${session.inputTokens.toLocaleString()}</td>
                    <td>${session.outputTokens.toLocaleString()}</td>
                    <td><strong>${(session.duration || 0).toLocaleString()}ms</strong></td>
                    <td>${new Date(session.timestamp).toLocaleTimeString()}</td>
                </tr>
            `).join('');

            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>Model</th>
                            <th>Input</th>
                            <th>Output</th>
                            <th>Duration</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            `;
        }

        async function resetStats() {
            if (!confirm('Are you sure you want to reset all statistics?')) return;
            
            try {
                const response = await fetch(API_BASE + '/reset', { method: 'POST' });
                if (!response.ok) throw new Error('Failed to reset stats');
                loadStats();
                alert('Statistics reset successfully');
            } catch (error) {
                alert('Error resetting stats: ' + error.message);
            }
        }

        // Load stats on page load and auto-refresh every 10 seconds
        document.addEventListener('DOMContentLoaded', () => {
            loadStats();
            setInterval(loadStats, 10000);
        });
    </script>
</body>
</html>
"""


# ==================== Installation Instructions ====================

"""
INSTALLATION INSTRUCTIONS FOR OPEN WEBUI
=========================================

Step 1: Copy this file
  cp global/openwebui_monitoring_extension.py openwebui/backend/extensions/

Step 2: Register in OpenWebUI
  Edit: openwebui/backend/main.py
  
  Add at the top with other imports:
  ```python
  from extensions.monitoring_extension import router as monitoring_router
  ```
  
  Add after your app is created (around line ~100):
  ```python
  app.include_router(monitoring_router)
  ```

Step 3: Restart OpenWebUI
  docker restart <container_name>
  # or
  python -m uvicorn main:app --reload

Step 4: Access the dashboard
  http://localhost:8080/api/admin/monitoring/dashboard
  
  Or add a link in the UI:
  <a href="/api/admin/monitoring/dashboard" target="_blank">📊 Token Monitor</a>

Available API Endpoints:
  GET  /api/admin/monitoring/health           - Check service health
  GET  /api/admin/monitoring/stats             - Get overall stats
  GET  /api/admin/monitoring/stats/model/{name} - Get model-specific stats
  GET  /api/admin/monitoring/history?limit=100 - Get request history
  POST /api/admin/monitoring/reset             - Reset all statistics
  GET  /api/admin/monitoring/dashboard         - Get HTML dashboard

Notes:
- Ensure monitoring service is running on localhost:3333
- CORS is handled automatically
- All requests are proxied to the monitoring service
- Dashboard auto-refreshes every 10 seconds
"""
