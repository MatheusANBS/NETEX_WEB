// Sistema de Analytics Customizado para Corteus
class CorteuAnalytics {
    constructor() {
        this.serverUrl = window.location.origin;
        this.sessionId = this.generateSessionId();
        this.userId = this.getUserId();
        this.startTime = Date.now();
        this.maxScroll = 0;
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
            data: data
        };

        try {
            await fetch(`${this.serverUrl}/api/track`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });
        } catch (error) {
            console.error('Erro ao enviar analytics:', error);
        }
    }

    init() {
        // Track page view automaticamente
        this.track('page_view');

        // Track clicks em links
        document.addEventListener('click', (e) => {
            if (e.target.tagName === 'A') {
                this.track('link_click', {
                    link_text: e.target.textContent.trim(),
                    link_url: e.target.href,
                    link_target: e.target.getAttribute('target')
                });
            }
            
            // Track clicks em botões
            if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
                const button = e.target.tagName === 'BUTTON' ? e.target : e.target.closest('button');
                this.track('button_click', {
                    button_text: button.textContent.trim(),
                    button_id: button.id,
                    button_class: button.className
                });
            }
        });

        // Track scroll depth
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                const scrollPercent = Math.round(
                    (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
                );
                
                if (scrollPercent > this.maxScroll) {
                    this.maxScroll = scrollPercent;
                    
                    // Track marcos de scroll
                    if ([25, 50, 75, 100].includes(scrollPercent)) {
                        this.track('scroll_depth', { 
                            depth: scrollPercent,
                            page_height: document.body.scrollHeight,
                            viewport_height: window.innerHeight
                        });
                    }
                }
            }, 100);
        });

        // Track form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.tagName === 'FORM') {
                this.track('form_submit', {
                    form_id: e.target.id,
                    form_action: e.target.action,
                    form_method: e.target.method
                });
            }
        });

        // Track downloads/reports (específico para Corteus)
        this.trackCorteuEvents();

        // Track time on page quando sair
        window.addEventListener('beforeunload', () => {
            const timeOnPage = Date.now() - this.startTime;
            
            // Use sendBeacon para garantir que o evento seja enviado
            const payload = {
                event: 'time_on_page',
                page: window.location.pathname,
                session_id: this.sessionId,
                user_id: this.userId,
                referrer: document.referrer,
                screen_resolution: `${screen.width}x${screen.height}`,
                data: { 
                    duration: timeOnPage,
                    max_scroll: this.maxScroll
                }
            };

            if (navigator.sendBeacon) {
                navigator.sendBeacon(
                    `${this.serverUrl}/api/track`, 
                    JSON.stringify(payload)
                );
            }
        });

        // Track visibility change (tab focus/blur)
        document.addEventListener('visibilitychange', () => {
            this.track('visibility_change', {
                visible: !document.hidden,
                timestamp: new Date().toISOString()
            });
        });
    }

    trackCorteuEvents() {
        // Track quando formulários do Corteus são preenchidos
        const corteuForm = document.getElementById('corteus-form');
        if (corteuForm) {
            // Track mudanças nos selects/inputs importantes
            const importantFields = ['projeto', 'ss', 'lote', 'comprimento-barra'];
            
            importantFields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    field.addEventListener('change', () => {
                        this.track('form_field_change', {
                            field_id: fieldId,
                            field_value: field.value,
                            field_type: field.tagName.toLowerCase()
                        });
                    });
                }
            });
        }

        // Track uso do help button
        const helpButton = document.getElementById('help-button');
        if (helpButton) {
            helpButton.addEventListener('click', () => {
                this.track('help_clicked');
            });
        }

        // Track geração de relatórios (se os botões existirem)
        const reportButtons = document.querySelectorAll('[id*="relatorio"], [onclick*="relatorio"]');
        reportButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.track('report_generation', {
                    report_type: button.textContent.trim()
                });
            });
        });
    }

    // Método público para tracking customizado
    trackCustomEvent(eventName, data = {}) {
        this.track(eventName, data);
    }
}

// Inicializar analytics quando a página carregar
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', () => {
        window.corteuAnalytics = new CorteuAnalytics();
    });
}

// Exportar para uso em outros scripts se necessário
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CorteuAnalytics;
}
