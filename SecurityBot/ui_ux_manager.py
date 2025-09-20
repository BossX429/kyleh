"""
Security Bot Enterprise - UI/UX Manager
Responsive user interface management for web dashboard
"""

import json
import logging
from pathlib import Path


class UIUXManager:
    """Enterprise UI/UX management system"""
    
    def __init__(self, static_dir="static", templates_dir="templates"):
        self.static_dir = Path(static_dir)
        self.templates_dir = Path(templates_dir)
        self.static_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        self.setup_logging()
        self.theme_config = self.load_theme_config()
        self.create_static_assets()
    
    def setup_logging(self):
        """Setup UI/UX logging"""
        self.logger = logging.getLogger('UIUXManager')
    
    def load_theme_config(self):
        """Load theme configuration"""
        default_theme = {
            "name": "Security Bot Dark",
            "colors": {
                "primary": "#3498db",
                "secondary": "#2c3e50",
                "success": "#27ae60",
                "warning": "#f39c12",
                "danger": "#e74c3c",
                "info": "#17a2b8",
                "light": "#f8f9fa",
                "dark": "#343a40",
                "background": "#1e3c72",
                "surface": "#ffffff",
                "text": "#2c3e50",
                "text_light": "#7f8c8d"
            },
            "fonts": {
                "primary": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                "monospace": "'Consolas', 'Monaco', 'Courier New', monospace"
            },
            "spacing": {
                "xs": "4px",
                "sm": "8px",
                "md": "16px",
                "lg": "24px",
                "xl": "32px"
            },
            "breakpoints": {
                "mobile": "768px",
                "tablet": "1024px",
                "desktop": "1200px"
            }
        }
        
        config_file = self.static_dir / "theme.json"
        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    theme = json.load(f)
                return {**default_theme, **theme}
        except Exception as e:
            self.logger.error("Failed to load theme config: %s", e)
        
        return default_theme
    
    def create_static_assets(self):
        """Create static CSS and JS assets"""
        self.create_main_css()
        self.create_main_js()
        self.create_dashboard_components()
    
    def create_main_css(self):
        """Create main CSS file"""
        css_content = self.generate_css()
        css_file = self.static_dir / "main.css"
        
        try:
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(css_content)
            self.logger.info("Main CSS file created")
        except Exception as e:
            self.logger.error("Failed to create CSS file: %s", e)
    
    def create_main_js(self):
        """Create main JavaScript file"""
        js_content = self.generate_js()
        js_file = self.static_dir / "main.js"
        
        try:
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(js_content)
            self.logger.info("Main JS file created")
        except Exception as e:
            self.logger.error("Failed to create JS file: %s", e)
    
    def generate_css(self):
        """Generate comprehensive CSS"""
        colors = self.theme_config['colors']
        fonts = self.theme_config['fonts']
        spacing = self.theme_config['spacing']
        breakpoints = self.theme_config['breakpoints']
        
        return f"""
/* Security Bot Enterprise - Main Stylesheet */
:root {{
    --color-primary: {colors['primary']};
    --color-secondary: {colors['secondary']};
    --color-success: {colors['success']};
    --color-warning: {colors['warning']};
    --color-danger: {colors['danger']};
    --color-info: {colors['info']};
    --color-light: {colors['light']};
    --color-dark: {colors['dark']};
    --color-background: {colors['background']};
    --color-surface: {colors['surface']};
    --color-text: {colors['text']};
    --color-text-light: {colors['text_light']};
    
    --font-primary: {fonts['primary']};
    --font-monospace: {fonts['monospace']};
    
    --spacing-xs: {spacing['xs']};
    --spacing-sm: {spacing['sm']};
    --spacing-md: {spacing['md']};
    --spacing-lg: {spacing['lg']};
    --spacing-xl: {spacing['xl']};
    
    --breakpoint-mobile: {breakpoints['mobile']};
    --breakpoint-tablet: {breakpoints['tablet']};
    --breakpoint-desktop: {breakpoints['desktop']};
}}

/* Reset and base styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: var(--font-primary);
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: var(--color-text);
    min-height: 100vh;
    line-height: 1.6;
}}

/* Typography */
h1, h2, h3, h4, h5, h6 {{
    color: var(--color-secondary);
    margin-bottom: var(--spacing-md);
    font-weight: 600;
}}

h1 {{ font-size: 2.5rem; }}
h2 {{ font-size: 2rem; }}
h3 {{ font-size: 1.5rem; }}
h4 {{ font-size: 1.25rem; }}
h5 {{ font-size: 1.1rem; }}
h6 {{ font-size: 1rem; }}

p {{ margin-bottom: var(--spacing-md); }}

/* Layout components */
.container {{
    max-width: var(--breakpoint-desktop);
    margin: 0 auto;
    padding: 0 var(--spacing-md);
}}

.header {{
    background: rgba(0,0,0,0.1);
    color: white;
    padding: var(--spacing-lg);
    text-align: center;
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255,255,255,0.1);
}}

.header h1 {{
    color: white;
    margin-bottom: var(--spacing-sm);
}}

.header p {{
    opacity: 0.9;
    margin-bottom: 0;
}}

/* Grid system */
.grid {{
    display: grid;
    gap: var(--spacing-lg);
}}

.grid-cols-1 {{ grid-template-columns: 1fr; }}
.grid-cols-2 {{ grid-template-columns: repeat(2, 1fr); }}
.grid-cols-3 {{ grid-template-columns: repeat(3, 1fr); }}
.grid-cols-4 {{ grid-template-columns: repeat(4, 1fr); }}

.grid-auto {{ grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }}

/* Card components */
.card {{
    background: var(--color-surface);
    border-radius: 10px;
    padding: var(--spacing-lg);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    border: 1px solid rgba(0,0,0,0.05);
}}

.card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}}

.card-header {{
    border-bottom: 1px solid rgba(0,0,0,0.1);
    padding-bottom: var(--spacing-md);
    margin-bottom: var(--spacing-md);
}}

.card-title {{
    color: var(--color-secondary);
    margin-bottom: var(--spacing-sm);
    font-size: 1.25rem;
    font-weight: 600;
}}

.card-content {{
    flex-grow: 1;
}}

/* Metric cards */
.metric-card {{
    text-align: center;
    padding: var(--spacing-xl);
}}

.metric-value {{
    font-size: 2.5rem;
    font-weight: bold;
    color: var(--color-primary);
    margin-bottom: var(--spacing-sm);
    display: block;
}}

.metric-label {{
    color: var(--color-text-light);
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* Status indicators */
.status-indicator {{
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
}}

.status-online {{
    background: rgba(39, 174, 96, 0.1);
    color: var(--color-success);
    border: 1px solid var(--color-success);
}}

.status-warning {{
    background: rgba(243, 156, 18, 0.1);
    color: var(--color-warning);
    border: 1px solid var(--color-warning);
}}

.status-error {{
    background: rgba(231, 76, 60, 0.1);
    color: var(--color-danger);
    border: 1px solid var(--color-danger);
}}

.status-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: currentColor;
    animation: pulse 2s infinite;
}}

@keyframes pulse {{
    0% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
    100% {{ opacity: 1; }}
}}

/* Tables */
.table-container {{
    overflow-x: auto;
    border-radius: 8px;
    background: var(--color-surface);
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th, td {{
    text-align: left;
    padding: var(--spacing-md);
    border-bottom: 1px solid rgba(0,0,0,0.05);
}}

th {{
    background: var(--color-light);
    font-weight: 600;
    color: var(--color-secondary);
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

tbody tr:hover {{
    background: rgba(52, 152, 219, 0.05);
}}

/* Buttons */
.btn {{
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    border: none;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.2s ease;
    outline: none;
}}

.btn:focus {{
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.3);
}}

.btn-primary {{
    background: var(--color-primary);
    color: white;
}}

.btn-primary:hover {{
    background: #2980b9;
    transform: translateY(-1px);
}}

.btn-secondary {{
    background: var(--color-light);
    color: var(--color-text);
    border: 1px solid rgba(0,0,0,0.1);
}}

.btn-secondary:hover {{
    background: #e9ecef;
}}

.btn-danger {{
    background: var(--color-danger);
    color: white;
}}

.btn-danger:hover {{
    background: #c0392b;
}}

/* Forms */
.form-group {{
    margin-bottom: var(--spacing-md);
}}

.form-label {{
    display: block;
    margin-bottom: var(--spacing-sm);
    font-weight: 500;
    color: var(--color-secondary);
}}

.form-input {{
    width: 100%;
    padding: var(--spacing-sm) var(--spacing-md);
    border: 1px solid rgba(0,0,0,0.2);
    border-radius: 6px;
    font-size: 0.875rem;
    transition: border-color 0.2s ease;
}}

.form-input:focus {{
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}}

/* Alerts */
.alert {{
    padding: var(--spacing-md);
    border-radius: 6px;
    margin-bottom: var(--spacing-md);
    border: 1px solid transparent;
}}

.alert-success {{
    background: rgba(39, 174, 96, 0.1);
    color: var(--color-success);
    border-color: var(--color-success);
}}

.alert-warning {{
    background: rgba(243, 156, 18, 0.1);
    color: var(--color-warning);
    border-color: var(--color-warning);
}}

.alert-danger {{
    background: rgba(231, 76, 60, 0.1);
    color: var(--color-danger);
    border-color: var(--color-danger);
}}

.alert-info {{
    background: rgba(52, 152, 219, 0.1);
    color: var(--color-info);
    border-color: var(--color-info);
}}

/* Charts */
.chart-container {{
    position: relative;
    height: 300px;
    padding: var(--spacing-md);
}}

/* Loading states */
.loading {{
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-xl);
    color: var(--color-text-light);
}}

.spinner {{
    width: 20px;
    height: 20px;
    border: 2px solid rgba(52, 152, 219, 0.3);
    border-top: 2px solid var(--color-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: var(--spacing-sm);
}}

@keyframes spin {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}

/* Responsive design */
@media (max-width: {breakpoints['tablet']}) {{
    .grid-cols-2,
    .grid-cols-3,
    .grid-cols-4 {{
        grid-template-columns: 1fr;
    }}
    
    .container {{
        padding: 0 var(--spacing-sm);
    }}
    
    .card {{
        padding: var(--spacing-md);
    }}
    
    .header {{
        padding: var(--spacing-md);
    }}
    
    h1 {{ font-size: 2rem; }}
    h2 {{ font-size: 1.5rem; }}
    
    .metric-value {{
        font-size: 2rem;
    }}
}}

@media (max-width: {breakpoints['mobile']}) {{
    .grid {{
        gap: var(--spacing-md);
    }}
    
    .card {{
        padding: var(--spacing-sm);
    }}
    
    .table-container {{
        font-size: 0.8rem;
    }}
    
    th, td {{
        padding: var(--spacing-sm);
    }}
    
    .metric-card {{
        padding: var(--spacing-md);
    }}
    
    .metric-value {{
        font-size: 1.5rem;
    }}
}}

/* Utility classes */
.text-center {{ text-align: center; }}
.text-left {{ text-align: left; }}
.text-right {{ text-align: right; }}

.font-bold {{ font-weight: bold; }}
.font-normal {{ font-weight: normal; }}

.text-primary {{ color: var(--color-primary); }}
.text-secondary {{ color: var(--color-secondary); }}
.text-success {{ color: var(--color-success); }}
.text-warning {{ color: var(--color-warning); }}
.text-danger {{ color: var(--color-danger); }}
.text-muted {{ color: var(--color-text-light); }}

.bg-primary {{ background-color: var(--color-primary); }}
.bg-secondary {{ background-color: var(--color-secondary); }}
.bg-success {{ background-color: var(--color-success); }}
.bg-warning {{ background-color: var(--color-warning); }}
.bg-danger {{ background-color: var(--color-danger); }}
.bg-light {{ background-color: var(--color-light); }}

.mt-0 {{ margin-top: 0; }}
.mt-1 {{ margin-top: var(--spacing-xs); }}
.mt-2 {{ margin-top: var(--spacing-sm); }}
.mt-3 {{ margin-top: var(--spacing-md); }}
.mt-4 {{ margin-top: var(--spacing-lg); }}
.mt-5 {{ margin-top: var(--spacing-xl); }}

.mb-0 {{ margin-bottom: 0; }}
.mb-1 {{ margin-bottom: var(--spacing-xs); }}
.mb-2 {{ margin-bottom: var(--spacing-sm); }}
.mb-3 {{ margin-bottom: var(--spacing-md); }}
.mb-4 {{ margin-bottom: var(--spacing-lg); }}
.mb-5 {{ margin-bottom: var(--spacing-xl); }}

.p-0 {{ padding: 0; }}
.p-1 {{ padding: var(--spacing-xs); }}
.p-2 {{ padding: var(--spacing-sm); }}
.p-3 {{ padding: var(--spacing-md); }}
.p-4 {{ padding: var(--spacing-lg); }}
.p-5 {{ padding: var(--spacing-xl); }}

.d-none {{ display: none; }}
.d-block {{ display: block; }}
.d-flex {{ display: flex; }}
.d-grid {{ display: grid; }}

.justify-center {{ justify-content: center; }}
.justify-between {{ justify-content: space-between; }}
.align-center {{ align-items: center; }}

.rounded {{ border-radius: 6px; }}
.rounded-lg {{ border-radius: 10px; }}
.rounded-full {{ border-radius: 50%; }}

.shadow {{ box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
.shadow-lg {{ box-shadow: 0 4px 15px rgba(0,0,0,0.15); }}

/* Animation utilities */
.fade-in {{
    animation: fadeIn 0.3s ease-in-out;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.slide-in {{
    animation: slideIn 0.3s ease-out;
}}

@keyframes slideIn {{
    from {{ transform: translateX(-100%); }}
    to {{ transform: translateX(0); }}
}}
"""
    
    def generate_js(self):
        """Generate comprehensive JavaScript"""
        return """
// Security Bot Enterprise - Main JavaScript

class SecurityBotUI {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.startPeriodicUpdates();
    }
    
    init() {
        console.log('Security Bot Enterprise UI initialized');
        this.loadingElements = document.querySelectorAll('.loading');
        this.charts = {};
        this.updateInterval = 30000; // 30 seconds
    }
    
    setupEventListeners() {
        // Handle responsive navigation
        document.addEventListener('DOMContentLoaded', () => {
            this.handleResponsiveElements();
        });
        
        // Handle window resize
        window.addEventListener('resize', () => {
            this.handleResponsiveElements();
        });
        
        // Handle form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.matches('.ajax-form')) {
                e.preventDefault();
                this.handleFormSubmission(e.target);
            }
        });
        
        // Handle button clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn-async')) {
                e.preventDefault();
                this.handleAsyncAction(e.target);
            }
        });
    }
    
    handleResponsiveElements() {
        const width = window.innerWidth;
        const mobileBreakpoint = 768;
        const tabletBreakpoint = 1024;
        
        // Add responsive classes
        document.body.classList.toggle('mobile', width < mobileBreakpoint);
        document.body.classList.toggle('tablet', width >= mobileBreakpoint && width < tabletBreakpoint);
        document.body.classList.toggle('desktop', width >= tabletBreakpoint);
        
        // Handle responsive charts
        if (this.charts && Object.keys(this.charts).length > 0) {
            Object.values(this.charts).forEach(chart => {
                if (chart && chart.resize) {
                    chart.resize();
                }
            });
        }
    }
    
    showLoading(element) {
        if (element) {
            element.innerHTML = '<div class="loading"><div class="spinner"></div>Loading...</div>';
        }
    }
    
    hideLoading(element) {
        if (element) {
            const loading = element.querySelector('.loading');
            if (loading) {
                loading.remove();
            }
        }
    }
    
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} fade-in`;
        notification.textContent = message;
        
        // Position notification
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.maxWidth = '300px';
        
        document.body.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, duration);
    }
    
    async handleFormSubmission(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn ? submitBtn.textContent : '';
        
        try {
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<div class="spinner"></div> Processing...';
            }
            
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: form.method || 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showNotification(result.message || 'Operation completed successfully', 'success');
                if (result.redirect) {
                    setTimeout(() => {
                        window.location.href = result.redirect;
                    }, 1000);
                }
            } else {
                this.showNotification(result.error || 'Operation failed', 'danger');
            }
            
        } catch (error) {
            console.error('Form submission error:', error);
            this.showNotification('Network error occurred', 'danger');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    }
    
    async handleAsyncAction(button) {
        const action = button.dataset.action;
        const url = button.dataset.url;
        const originalText = button.textContent;
        
        try {
            button.disabled = true;
            button.innerHTML = '<div class="spinner"></div> Processing...';
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showNotification(result.message || 'Action completed', 'success');
            } else {
                this.showNotification(result.error || 'Action failed', 'danger');
            }
            
        } catch (error) {
            console.error('Async action error:', error);
            this.showNotification('Network error occurred', 'danger');
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }
    
    startPeriodicUpdates() {
        // Update dashboard data periodically
        setInterval(() => {
            this.updateDashboardData();
        }, this.updateInterval);
        
        // Initial update
        this.updateDashboardData();
    }
    
    async updateDashboardData() {
        try {
            const response = await fetch('/api/dashboard-data', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateMetrics(data);
                this.updateCharts(data);
                this.updateThreatList(data.recent_threats || []);
            }
        } catch (error) {
            console.error('Dashboard update error:', error);
        }
    }
    
    updateMetrics(data) {
        // Update metric values
        const elements = {
            'totalThreats': data.total_threats_24h || 0,
            'lastUpdate': new Date(data.last_updated).toLocaleTimeString()
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }
    
    updateCharts(data) {
        // Update Chart.js charts if they exist
        if (window.Chart && this.charts.severityChart) {
            const severityData = data.severity_distribution || {};
            this.charts.severityChart.data.datasets[0].data = [
                severityData.critical || 0,
                severityData.high || 0,
                severityData.medium || 0,
                severityData.low || 0
            ];
            this.charts.severityChart.update('none');
        }
        
        if (window.Chart && this.charts.hourlyChart) {
            const hourlyData = new Array(24).fill(0);
            if (data.hourly_distribution) {
                data.hourly_distribution.forEach(([hour, count]) => {
                    hourlyData[parseInt(hour)] = count;
                });
            }
            this.charts.hourlyChart.data.datasets[0].data = hourlyData;
            this.charts.hourlyChart.update('none');
        }
    }
    
    updateThreatList(threats) {
        const threatList = document.getElementById('threatList');
        if (!threatList) return;
        
        if (threats.length === 0) {
            threatList.innerHTML = '<div class="text-center text-muted p-4">No recent threats detected</div>';
            return;
        }
        
        threatList.innerHTML = threats.map(threat => {
            const [type, severity, timestamp, description] = threat;
            const time = new Date(timestamp).toLocaleString();
            
            return `
                <div class="card mb-2 border-left-${severity}">
                    <div class="card-body p-3">
                        <div class="d-flex justify-between align-center mb-2">
                            <span class="font-bold text-${severity}">${type.replace(/_/g, ' ').toUpperCase()}</span>
                            <small class="text-muted">${time}</small>
                        </div>
                        <div class="text-sm">${description || 'No description available'}</div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    // Chart initialization helpers
    initSeverityChart(canvas) {
        if (!window.Chart) return null;
        
        return new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: ['#e74c3c', '#f39c12', '#f1c40f', '#27ae60'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    initHourlyChart(canvas) {
        if (!window.Chart) return null;
        
        return new Chart(canvas, {
            type: 'line',
            data: {
                labels: Array.from({length: 24}, (_, i) => i.toString().padStart(2, '0') + ':00'),
                datasets: [{
                    label: 'Threats Detected',
                    data: new Array(24).fill(0),
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Initialize UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.securityBotUI = new SecurityBotUI();
    
    // Initialize charts if canvases exist
    const severityCanvas = document.getElementById('severityChart');
    const hourlyCanvas = document.getElementById('hourlyChart');
    
    if (severityCanvas) {
        window.securityBotUI.charts.severityChart = window.securityBotUI.initSeverityChart(severityCanvas);
    }
    
    if (hourlyCanvas) {
        window.securityBotUI.charts.hourlyChart = window.securityBotUI.initHourlyChart(hourlyCanvas);
    }
});

// Utility functions
window.SecurityBotUtils = {
    formatBytes: (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    formatDuration: (seconds) => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}h ${minutes}m ${secs}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    },
    
    formatNumber: (num) => {
        return new Intl.NumberFormat().format(num);
    }
};
"""
    
    def create_dashboard_components(self):
        """Create reusable dashboard components"""
        components = {
            'metric_card': self.create_metric_card_template(),
            'threat_card': self.create_threat_card_template(),
            'chart_container': self.create_chart_container_template()
        }
        
        for name, template in components.items():
            template_file = self.templates_dir / f"{name}.html"
            try:
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(template)
                self.logger.info("Component template created: %s", name)
            except Exception as e:
                self.logger.error("Failed to create component %s: %s", name, e)
    
    def create_metric_card_template(self):
        """Create metric card template"""
        return """
<div class="card metric-card">
    <div class="metric-value">{{ value }}</div>
    <div class="metric-label">{{ label }}</div>
</div>
"""
    
    def create_threat_card_template(self):
        """Create threat card template"""
        return """
<div class="card threat-card border-left-{{ severity }}">
    <div class="card-header">
        <div class="d-flex justify-between align-center">
            <span class="font-bold text-{{ severity }}">{{ threat_type }}</span>
            <span class="text-muted text-sm">{{ timestamp }}</span>
        </div>
    </div>
    <div class="card-content">
        <p>{{ description }}</p>
        <div class="d-flex justify-between text-sm text-muted">
            <span>Source: {{ source }}</span>
            <span>Risk: {{ risk_score }}/100</span>
        </div>
    </div>
</div>
"""
    
    def create_chart_container_template(self):
        """Create chart container template"""
        return """
<div class="card">
    <div class="card-header">
        <h3 class="card-title">{{ chart_title }}</h3>
    </div>
    <div class="chart-container">
        <canvas id="{{ chart_id }}"></canvas>
    </div>
</div>
"""
    
    def get_theme_css_vars(self):
        """Get CSS variables for current theme"""
        colors = self.theme_config['colors']
        return {f'--color-{key.replace("_", "-")}': value for key, value in colors.items()}
    
    def customize_theme(self, updates):
        """Customize theme configuration"""
        try:
            # Merge updates with current theme
            for category, values in updates.items():
                if category in self.theme_config:
                    self.theme_config[category].update(values)
            
            # Save updated theme
            config_file = self.static_dir / "theme.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.theme_config, f, indent=2)
            
            # Regenerate CSS
            self.create_main_css()
            
            self.logger.info("Theme updated successfully")
            return True
            
        except Exception as e:
            self.logger.error("Failed to update theme: %s", e)
            return False


if __name__ == '__main__':
    # Test UI/UX manager
    ui_manager = UIUXManager()
    
    # Customize theme
    updates = {
        'colors': {
            'primary': '#2c3e50',
            'secondary': '#34495e'
        }
    }
    
    success = ui_manager.customize_theme(updates)
    print(f"Theme customization: {'Success' if success else 'Failed'}")
    
    print("UI/UX Manager initialized with static assets created")