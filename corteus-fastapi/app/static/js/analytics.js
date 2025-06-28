// Sistema de Analytics Customizado Avançado para Corteus
class CorteuAnalytics {
    constructor() {
        this.serverUrl = window.location.origin;
        this.sessionId = this.generateSessionId();
        this.userId = this.getUserId();
        this.startTime = Date.now();
        this.maxScroll = 0;
        this.scrollMilestones = new Set();
        this.interactions = 0;
        this.mouseMoves = 0;
        this.keystrokes = 0;
        this.lastActivity = Date.now();
        this.pageLoadTime = null;
        this.performanceData = {};
        this.heatmapData = [];
        this.errors = [];
        this.init();
    }

    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }

    getUserId() {
        let userId = localStorage.getItem('corteus_analytics_user_id');
        if (!userId) {
            userId = 'user_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('corteus_analytics_user_id', userId);
        }
        return userId;
    }

    async track(event, data = {}) {
        const payload = {
            event,
            page: window.location.pathname,
            session_id: this.sessionId,
            user_id: this.userId,
            referrer: document.referrer,
            screen_resolution: `${screen.width}x${screen.height}`,
            viewport: `${window.innerWidth}x${window.innerHeight}`,
            user_agent: navigator.userAgent,
            timestamp: new Date().toISOString(),
            data: {
                ...data,
                interactions_count: this.interactions,
                time_since_load: Date.now() - this.startTime
            }
        };

        try {
            await fetch(`${this.serverUrl}/track`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });
        } catch (error) {
            console.error('Erro ao enviar analytics:', error);
            this.errors.push({
                error: error.message,
                timestamp: new Date().toISOString(),
                event: event
            });
        }
    }

    init() {
        this.setupPerformanceTracking();
        this.trackPageView();
        this.setupEventListeners();
        this.setupHeatmapTracking();
        this.setupErrorTracking();
        this.setupEngagementTracking();
        this.trackCorteuEvents();
    }

    setupPerformanceTracking() {
        // Track page load performance
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                this.pageLoadTime = perfData.loadEventEnd - perfData.fetchStart;
                
                this.performanceData = {
                    dns_lookup: perfData.domainLookupEnd - perfData.domainLookupStart,
                    tcp_connect: perfData.connectEnd - perfData.connectStart,
                    server_response: perfData.responseEnd - perfData.requestStart,
                    dom_processing: perfData.domContentLoadedEventEnd - perfData.responseEnd,
                    page_load: this.pageLoadTime,
                    first_paint: this.getFirstPaint(),
                    largest_contentful_paint: this.getLCP()
                };

                this.track('performance_metrics', this.performanceData);
            }, 1000);
        });
    }

    getFirstPaint() {
        const paintEntries = performance.getEntriesByType('paint');
        const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
        return firstPaint ? firstPaint.startTime : null;
    }

    getLCP() {
        return new Promise((resolve) => {
            if ('PerformanceObserver' in window) {
                const observer = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    resolve(lastEntry.startTime);
                });
                observer.observe({ entryTypes: ['largest-contentful-paint'] });
                
                setTimeout(() => resolve(null), 5000); // timeout after 5s
            } else {
                resolve(null);
            }
        });
    }

    trackPageView() {
        // Track page view with additional context
        const pageData = {
            url: window.location.href,
            title: document.title,
            loading_time: this.pageLoadTime,
            device_type: this.getDeviceType(),
            browser_info: this.getBrowserInfo(),
            connection_type: this.getConnectionType(),
            language: navigator.language,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        };

        this.track('page_view', pageData);
    }

    setupEventListeners() {
        // Enhanced click tracking
        document.addEventListener('click', (e) => {
            this.interactions++;
            this.lastActivity = Date.now();
            
            const clickData = {
                element_tag: e.target.tagName.toLowerCase(),
                element_text: e.target.textContent.trim().substring(0, 100),
                element_id: e.target.id,
                element_classes: e.target.className,
                click_x: e.clientX,
                click_y: e.clientY,
                page_x: e.pageX,
                page_y: e.pageY,
                timestamp: Date.now() - this.startTime
            };

            // Specific tracking for different elements
            if (e.target.tagName === 'A') {
                this.track('link_click', {
                    ...clickData,
                    link_url: e.target.href,
                    link_target: e.target.getAttribute('target'),
                    external: !e.target.href.includes(window.location.origin)
                });
            } else if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
                const button = e.target.tagName === 'BUTTON' ? e.target : e.target.closest('button');
                
                // Melhor detecção de texto do botão
                let buttonText = button.textContent?.trim() || button.innerText?.trim() || '';
                if (!buttonText && button.title) buttonText = button.title;
                if (!buttonText && button.alt) buttonText = button.alt;
                if (!buttonText && button.value) buttonText = button.value;
                if (!buttonText && button.getAttribute('aria-label')) buttonText = button.getAttribute('aria-label');
                if (!buttonText && button.id) buttonText = button.id.replace(/[-_]/g, ' ');
                if (!buttonText && button.className) {
                    const classList = button.className.split(' ');
                    buttonText = classList.find(cls => cls.includes('btn') || cls.includes('button'))?.replace(/btn-?|button-?/g, '') || '';
                }
                if (!buttonText) buttonText = 'Button';

                // Não rastrear cliques do botão de ajuda aqui (será rastreado especificamente)
                if (button.id === 'help-button' || buttonText.toLowerCase().includes('ajuda')) {
                    return; // Parar aqui para evitar tracking duplo
                }
                
                this.track('button_click', {
                    ...clickData,
                    button_text: buttonText,
                    button_type: button.type,
                    button_form: button.form?.id || null,
                    button_id: button.id
                });
            } else if (e.target.closest('label') || e.target.tagName === 'LABEL') {
                // Rastrear cliques em labels (podem ser botões estilizados)
                const label = e.target.closest('label') || e.target;
                let labelText = label.textContent?.trim() || label.innerText?.trim() || '';
                if (!labelText && label.getAttribute('for')) {
                    const targetElement = document.getElementById(label.getAttribute('for'));
                    if (targetElement) labelText = targetElement.getAttribute('placeholder') || targetElement.name || 'Form Label';
                }
                if (!labelText) labelText = 'Label';
                
                this.track('button_click', {
                    ...clickData,
                    button_text: labelText,
                    button_type: 'label',
                    element_for: label.getAttribute('for')
                });
            } else if (e.target.onclick || e.target.getAttribute('onclick') || 
                       e.target.style.cursor === 'pointer' || 
                       e.target.closest('[onclick]') ||
                       e.target.getAttribute('role') === 'button' ||
                       e.target.classList.contains('btn') ||
                       e.target.classList.contains('button') ||
                       e.target.classList.contains('clickable')) {
                // Rastrear elementos que funcionam como botões mas não são <button>
                const clickableElement = e.target.closest('[onclick]') || e.target;
                let elementText = clickableElement.textContent?.trim() || clickableElement.innerText?.trim() || '';
                if (!elementText && clickableElement.title) elementText = clickableElement.title;
                if (!elementText && clickableElement.alt) elementText = clickableElement.alt;
                if (!elementText && clickableElement.getAttribute('aria-label')) elementText = clickableElement.getAttribute('aria-label');
                if (!elementText && clickableElement.id) elementText = clickableElement.id.replace(/[-_]/g, ' ');
                
                // Melhor descrição para elementos específicos
                if (!elementText) {
                    if (clickableElement.tagName === 'IMG') elementText = 'Image';
                    else if (clickableElement.tagName === 'SPAN') elementText = 'Text Element';
                    else if (clickableElement.tagName === 'DIV') elementText = 'Container';
                    else elementText = `${clickableElement.tagName.toLowerCase()} clickable`;
                }
                
                this.track('button_click', {
                    ...clickData,
                    button_text: elementText,
                    button_type: 'clickable_element',
                    element_onclick: clickableElement.getAttribute('onclick')?.substring(0, 50) || null
                });
            } else {
                this.track('element_click', clickData);
            }

            // Add to heatmap data
            this.heatmapData.push({
                x: e.clientX,
                y: e.clientY,
                timestamp: Date.now(),
                element: e.target.tagName.toLowerCase()
            });
        });

        // Enhanced scroll tracking
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                const scrollPercent = Math.round(
                    (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
                );
                
                if (scrollPercent > this.maxScroll) {
                    this.maxScroll = scrollPercent;
                }

                // Track scroll milestones
                const milestones = [10, 25, 50, 75, 90, 100];
                milestones.forEach(milestone => {
                    if (scrollPercent >= milestone && !this.scrollMilestones.has(milestone)) {
                        this.scrollMilestones.add(milestone);
                        this.track('scroll_milestone', { 
                            depth: milestone,
                            time_to_reach: Date.now() - this.startTime,
                            scroll_speed: this.calculateScrollSpeed()
                        });
                    }
                });
            }, 100);
        });

        // Form interaction tracking
        document.addEventListener('input', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
                this.interactions++;
                this.track('form_interaction', {
                    field_id: e.target.id,
                    field_name: e.target.name,
                    field_type: e.target.type,
                    field_value_length: e.target.value.length,
                    time_since_load: Date.now() - this.startTime
                });
            }
        });

        // Keystroke tracking (general activity)
        document.addEventListener('keydown', () => {
            this.keystrokes++;
            this.lastActivity = Date.now();
        });

        // Mouse movement tracking (activity indicator)
        let mouseMoveTimeout;
        document.addEventListener('mousemove', () => {
            clearTimeout(mouseMoveTimeout);
            mouseMoveTimeout = setTimeout(() => {
                this.mouseMoves++;
                this.lastActivity = Date.now();
            }, 100);
        });

        // Right-click tracking
        document.addEventListener('contextmenu', (e) => {
            this.track('right_click', {
                element_tag: e.target.tagName.toLowerCase(),
                element_text: e.target.textContent.trim().substring(0, 50),
                x: e.clientX,
                y: e.clientY
            });
        });

        // Copy/paste tracking
        document.addEventListener('copy', () => {
            this.track('copy_action', { timestamp: Date.now() - this.startTime });
        });

        document.addEventListener('paste', () => {
            this.track('paste_action', { timestamp: Date.now() - this.startTime });
        });
    }

    setupHeatmapTracking() {
        // Send heatmap data periodically
        setInterval(() => {
            if (this.heatmapData.length > 0) {
                this.track('heatmap_data', {
                    clicks: this.heatmapData.splice(0, 50), // Send max 50 points at a time
                    viewport: `${window.innerWidth}x${window.innerHeight}`
                });
            }
        }, 30000); // Every 30 seconds
    }

    setupErrorTracking() {
        // JavaScript error tracking
        window.addEventListener('error', (e) => {
            this.track('javascript_error', {
                message: e.message,
                filename: e.filename,
                line: e.lineno,
                column: e.colno,
                stack: e.error?.stack?.substring(0, 500)
            });
        });

        // Promise rejection tracking
        window.addEventListener('unhandledrejection', (e) => {
            this.track('promise_rejection', {
                reason: e.reason?.toString()?.substring(0, 200)
            });
        });
    }

    setupEngagementTracking() {
        // Track user engagement score
        setInterval(() => {
            const engagementScore = this.calculateEngagementScore();
            this.track('engagement_pulse', {
                score: engagementScore,
                interactions: this.interactions,
                mouse_moves: this.mouseMoves,
                keystrokes: this.keystrokes,
                max_scroll: this.maxScroll,
                time_active: Date.now() - this.startTime,
                last_activity: Date.now() - this.lastActivity
            });
        }, 60000); // Every minute

        // Track idle detection
        let idleTimer;
        const resetIdleTimer = () => {
            clearTimeout(idleTimer);
            idleTimer = setTimeout(() => {
                this.track('user_idle', {
                    idle_time: 5 * 60 * 1000, // 5 minutes
                    last_activity: Date.now() - this.lastActivity
                });
            }, 5 * 60 * 1000);
        };

        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
            document.addEventListener(event, resetIdleTimer);
        });
        resetIdleTimer();
    }

    calculateEngagementScore() {
        const timeOnPage = (Date.now() - this.startTime) / 1000;
        const interactionRate = this.interactions / Math.max(timeOnPage / 60, 1); // per minute
        const scrollEngagement = this.maxScroll / 100;
        const activityRecency = Math.max(0, 1 - (Date.now() - this.lastActivity) / 60000); // decay over 1 minute
        
        return Math.round((interactionRate * 30 + scrollEngagement * 40 + activityRecency * 30));
    }

    calculateScrollSpeed() {
        // Simple scroll speed calculation (can be improved)
        return 'medium'; // placeholder
    }

    getDeviceType() {
        const width = window.innerWidth;
        if (width <= 768) return 'mobile';
        if (width <= 1024) return 'tablet';
        return 'desktop';
    }

    getBrowserInfo() {
        const ua = navigator.userAgent;
        let browser = 'unknown';
        
        if (ua.includes('Chrome')) browser = 'chrome';
        else if (ua.includes('Firefox')) browser = 'firefox';
        else if (ua.includes('Safari') && !ua.includes('Chrome')) browser = 'safari';
        else if (ua.includes('Edge')) browser = 'edge';
        
        return {
            name: browser,
            version: this.getBrowserVersion(ua),
            mobile: /Mobi|Android/i.test(ua)
        };
    }

    getBrowserVersion(ua) {
        const version = ua.match(/(chrome|firefox|safari|edge)\/(\d+)/i);
        return version ? version[2] : 'unknown';
    }

    getConnectionType() {
        if ('connection' in navigator) {
            return navigator.connection.effectiveType || 'unknown';
        }
        return 'unknown';
    }

    trackCorteuEvents() {
        // Enhanced Corteus-specific tracking
        const corteuForm = document.getElementById('corteus-form');
        if (corteuForm) {
            // Track form completion funnel
            const formFields = corteuForm.querySelectorAll('input, select, textarea');
            const totalFields = formFields.length;
            let completedFields = 0;

            formFields.forEach((field, index) => {
                field.addEventListener('change', () => {
                    if (field.value.trim() !== '') {
                        completedFields++;
                    }

                    const completionRate = (completedFields / totalFields) * 100;
                    
                    this.track('form_field_change', {
                        field_id: field.id,
                        field_index: index,
                        field_value_length: field.value.length,
                        completion_rate: completionRate,
                        field_type: field.type || field.tagName.toLowerCase()
                    });

                    // Track completion milestones
                    if ([25, 50, 75, 100].includes(Math.round(completionRate))) {
                        this.track('form_completion_milestone', {
                            milestone: Math.round(completionRate),
                            time_to_reach: Date.now() - this.startTime
                        });
                    }
                });

                // Track field focus time
                let focusTime;
                field.addEventListener('focus', () => {
                    focusTime = Date.now();
                });

                field.addEventListener('blur', () => {
                    if (focusTime) {
                        this.track('field_focus_time', {
                            field_id: field.id,
                            focus_duration: Date.now() - focusTime
                        });
                    }
                });
            });
        }

        // Track help usage patterns
        const helpButton = document.getElementById('help-button');
        if (helpButton) {
            helpButton.addEventListener('click', (e) => {
                // Evitar tracking duplo - parar propagação do evento geral
                e.stopPropagation();
                
                this.track('help_clicked', {
                    time_since_load: Date.now() - this.startTime,
                    form_completion: this.getFormCompletionRate(),
                    button_text: 'Ajuda' // Texto específico para o botão de ajuda
                });
            });
        }

        // Enhanced report generation tracking
        const reportButtons = document.querySelectorAll('[id*="relatorio"], [onclick*="relatorio"]');
        reportButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.track('report_generation', {
                    report_type: button.textContent.trim(),
                    form_data_present: this.checkFormDataPresent(),
                    time_to_generate: Date.now() - this.startTime,
                    user_engagement_score: this.calculateEngagementScore()
                });
            });
        });

        // Track logo triple-click for admin mode
        let logoClickCount = 0;
        let logoClickTimer;
        const logo = document.querySelector('.logo, [onclick*="logo"], img[src*="logo"]');
        if (logo) {
            logo.addEventListener('click', () => {
                logoClickCount++;
                clearTimeout(logoClickTimer);
                
                if (logoClickCount === 3) {
                    this.track('admin_mode_attempt', {
                        time_since_load: Date.now() - this.startTime
                    });
                    logoClickCount = 0;
                } else {
                    logoClickTimer = setTimeout(() => {
                        logoClickCount = 0;
                    }, 1000);
                }
            });
        }
    }

    getFormCompletionRate() {
        const form = document.getElementById('corteus-form');
        if (!form) return 0;
        
        const fields = form.querySelectorAll('input, select, textarea');
        const completedFields = Array.from(fields).filter(field => field.value.trim() !== '').length;
        return fields.length > 0 ? (completedFields / fields.length) * 100 : 0;
    }

    checkFormDataPresent() {
        const form = document.getElementById('corteus-form');
        if (!form) return false;
        
        const fields = form.querySelectorAll('input, select, textarea');
        return Array.from(fields).some(field => field.value.trim() !== '');
    }

    // Enhanced beforeunload tracking
    trackPageExit() {
        const exitData = {
            time_on_page: Date.now() - this.startTime,
            max_scroll: this.maxScroll,
            interactions: this.interactions,
            mouse_moves: this.mouseMoves,
            keystrokes: this.keystrokes,
            engagement_score: this.calculateEngagementScore(),
            form_completion: this.getFormCompletionRate(),
            errors_count: this.errors.length,
            scroll_milestones: Array.from(this.scrollMilestones),
            exit_type: 'beforeunload'
        };

        // Use sendBeacon for reliable exit tracking
        if (navigator.sendBeacon) {
            const payload = {
                event: 'page_exit',
                page: window.location.pathname,
                session_id: this.sessionId,
                user_id: this.userId,
                referrer: document.referrer,
                screen_resolution: `${screen.width}x${screen.height}`,
                data: exitData
            };

            navigator.sendBeacon(
                `${this.serverUrl}/track`, 
                JSON.stringify(payload)
            );
        }
    }

    // Public method for custom tracking
    trackCustomEvent(eventName, data = {}) {
        this.track(eventName, data);
    }

    // Method to get current analytics state
    getAnalyticsState() {
        return {
            sessionId: this.sessionId,
            userId: this.userId,
            interactions: this.interactions,
            timeOnPage: Date.now() - this.startTime,
            maxScroll: this.maxScroll,
            engagementScore: this.calculateEngagementScore()
        };
    }
}

// Initialize analytics when page loads
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', () => {
        window.corteuAnalytics = new CorteuAnalytics();
        
        // Setup page exit tracking
        window.addEventListener('beforeunload', () => {
            window.corteuAnalytics.trackPageExit();
        });

        // Track visibility changes (tab switching)
        document.addEventListener('visibilitychange', () => {
            window.corteuAnalytics.track('visibility_change', {
                visible: !document.hidden,
                time_since_load: Date.now() - window.corteuAnalytics.startTime
            });
        });
    });
}

// Export for use in other scripts if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CorteuAnalytics;
}
