// Sistema de Analytics Lite - Coleta apenas dados essenciais
class CorteuAnalyticsLite {
    constructor() {
        this.serverUrl = window.location.origin;
        this.sessionId = this.generateSessionId();
        this.userId = this.getUserId();
        this.startTime = Date.now();
        this.interactions = 0;
        this.lastActivity = Date.now();
        
        // Throttles para evitar spam de eventos
        this.lastInteractionEvent = 0;
        
        // Buffer para agrupar eventos
        this.eventBuffer = [];
        this.bufferTimeout = null;
        
        this.init();
    }

    generateSessionId() {
        // Usar sessionStorage para manter a sessão durante a aba do navegador
        let sessionId = sessionStorage.getItem('corteus_analytics_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
            sessionStorage.setItem('corteus_analytics_session_id', sessionId);
        }
        return sessionId;
    }

    getUserId() {
        let userId = localStorage.getItem('corteus_analytics_user_id');
        if (!userId) {
            userId = 'user_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('corteus_analytics_user_id', userId);
        }
        return userId;
    }

    // Método otimizado para track com buffer
    async track(event, data = {}) {
        const payload = {
            event,
            page: window.location.pathname,
            session_id: this.sessionId,
            user_id: this.userId,
            referrer: document.referrer,
            screen_resolution: `${screen.width}x${screen.height}`,
            data: {
                ...data,
                interactions_count: this.interactions,
                time_since_load: Date.now() - this.startTime
            }
        };

        // Adicionar ao buffer em vez de enviar imediatamente
        this.eventBuffer.push(payload);
        
        // Agendar envio do buffer (debounce)
        if (this.bufferTimeout) {
            clearTimeout(this.bufferTimeout);
        }
        
        this.bufferTimeout = setTimeout(() => {
            this.flushBuffer();
        }, 2000); // Agrupar eventos por 2 segundos
    }

    // Enviar buffer de eventos
    async flushBuffer() {
        if (this.eventBuffer.length === 0) return;
        
        const events = [...this.eventBuffer];
        this.eventBuffer = [];
        
        try {
            await fetch(`${this.serverUrl}/track-batch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ events })
            });
        } catch (error) {
            console.warn('Analytics batch failed:', error);
        }
    }

    init() {
        // Page view - essencial
        this.track('page_view', {
            url: window.location.href,
            title: document.title,
            device_type: this.getDeviceType(),
            browser_info: this.getBrowserInfo(),
            language: navigator.language,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        });

        // Click tracking - apenas cliques importantes
        document.addEventListener('click', (e) => {
            // Só trackear cliques em botões, links ou elementos com id/class importantes
            if (e.target.tagName === 'BUTTON' || 
                e.target.tagName === 'A' || 
                e.target.id.includes('help') || 
                e.target.className.includes('btn')) {
                this.handleClick(e);
            }
        });

        // Visibility change - quando usuário sai da página
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.track('page_exit', {
                    time_on_page: Date.now() - this.startTime,
                    total_interactions: this.interactions
                });
                this.flushBuffer(); // Enviar imediatamente ao sair
            }
        });

        // Unload - última chance de enviar dados
        window.addEventListener('beforeunload', () => {
            this.flushBuffer();
        });

        // Performance metrics - apenas uma vez após load
        window.addEventListener('load', () => {
            setTimeout(() => {
                this.trackPerformance();
            }, 1000);
        });
    }

    handleClick(event) {
        this.interactions++;
        
        // Rate limiting - max 1 click event por segundo
        const now = Date.now();
        if (now - this.lastInteractionEvent < 1000) return;
        this.lastInteractionEvent = now;

        const target = event.target;
        
        // Trackear apenas cliques importantes
        if (target.id === 'help-button' || target.textContent.includes('Ajuda')) {
            this.track('help_clicked', {
                button_text: target.textContent.trim(),
                time_since_load: now - this.startTime
            });
        } else if (target.tagName === 'BUTTON') {
            this.track('button_click', {
                button_text: target.textContent.trim(),
                button_id: target.id,
                button_type: target.type
            });
        }
    }

    trackPerformance() {
        if ('performance' in window && 'getEntriesByType' in performance) {
            const navigation = performance.getEntriesByType('navigation')[0];
            if (navigation) {
                this.track('performance_metrics', {
                    page_load: Math.round(navigation.loadEventEnd - navigation.fetchStart),
                    dns_lookup: Math.round(navigation.domainLookupEnd - navigation.domainLookupStart),
                    server_response: Math.round(navigation.responseEnd - navigation.requestStart),
                    dom_processing: Math.round(navigation.domContentLoadedEventEnd - navigation.responseEnd)
                });
            }
        }
    }

    getDeviceType() {
        return /Mobi|Android/i.test(navigator.userAgent) ? 'mobile' : 'desktop';
    }

    getBrowserInfo() {
        const ua = navigator.userAgent;
        let browser = 'unknown';
        
        if (ua.includes('Chrome')) browser = 'chrome';
        else if (ua.includes('Firefox')) browser = 'firefox';
        else if (ua.includes('Safari')) browser = 'safari';
        else if (ua.includes('Edge')) browser = 'edge';
        
        return {
            name: browser,
            mobile: this.getDeviceType() === 'mobile'
        };
    }
}

// Inicializar analytics lite se não existir o analytics completo
if (typeof window.analytics === 'undefined') {
    window.analytics = new CorteuAnalyticsLite();
}
