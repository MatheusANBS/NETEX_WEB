from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import json
import os

# Definir fuso horário do Brasil (UTC-3)
BRAZIL_TZ = timezone(timedelta(hours=-3))

class AnalyticsEvent(BaseModel):
    event: str
    page: str
    timestamp: datetime = None
    user_agent: str = ""
    ip: str = ""
    session_id: str = ""
    user_id: str = ""
    referrer: str = ""
    screen_resolution: str = ""
    data: Optional[Dict[str, Any]] = {}
    
    def __init__(self, **data):
        if 'timestamp' not in data or data['timestamp'] is None:
            # Usar horário do Brasil (UTC-3) em vez de UTC
            data['timestamp'] = datetime.now(BRAZIL_TZ).replace(tzinfo=None)
        super().__init__(**data)

class AnalyticsStorage:
    """Sistema otimizado de armazenamento com rate limiting"""
    
    def __init__(self, file_path: str = "analytics_data.json"):
        self.file_path = file_path
        self.ensure_file_exists()
        # Cache para rate limiting
        self.session_event_count = {}
        self.last_cleanup = datetime.now()
    
    def ensure_file_exists(self):
        """Garante que o arquivo existe"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)
    
    def should_accept_event(self, event: AnalyticsEvent) -> bool:
        """Rate limiting - limitar eventos por sessão"""
        session_id = event.session_id
        
        # Limpeza periódica do cache (a cada hora)
        if (datetime.now() - self.last_cleanup).seconds > 3600:
            self.session_event_count.clear()
            self.last_cleanup = datetime.now()
        
        # Contar eventos da sessão
        current_count = self.session_event_count.get(session_id, 0)
        
        # Limite de 50 eventos por sessão (muito mais razoável)
        if current_count >= 50:
            print(f"Rate limit atingido para sessão {session_id}: {current_count} eventos")
            return False
        
        return True
    
    def save_event(self, event: AnalyticsEvent):
        """Salva um evento com rate limiting"""
        try:
            # Verificar rate limiting
            if not self.should_accept_event(event):
                return False
            
            # Ler dados existentes
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            # Adicionar novo evento
            event_dict = event.dict()
            event_dict['timestamp'] = event.timestamp.isoformat()
            data.append(event_dict)
            
            # Manter apenas os últimos 1000 eventos para evitar arquivo muito grande
            if len(data) > 1000:
                data = data[-1000:]
            
            # Salvar dados
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Atualizar contador da sessão
            session_id = event.session_id
            self.session_event_count[session_id] = self.session_event_count.get(session_id, 0) + 1
            
            return True
            
        except Exception as e:
            print(f"Erro ao salvar evento de analytics: {e}")
            return False
                
        except Exception as e:
            print(f"Erro ao salvar evento de analytics: {e}")
    
    def get_events(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> list:
        """Recupera eventos filtrados por data"""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            if start_date or end_date:
                filtered_data = []
                for event in data:
                    try:
                        timestamp_str = event['timestamp']
                        # Remover timezone se presente para normalizar
                        if 'Z' in timestamp_str:
                            timestamp_str = timestamp_str.replace('Z', '+00:00')
                        
                        event_time = datetime.fromisoformat(timestamp_str)
                        
                        # Converter para naive datetime se necessário
                        if event_time.tzinfo is not None:
                            event_time = event_time.replace(tzinfo=None)
                        
                        # Normalizar start_date e end_date também
                        if start_date:
                            start_naive = start_date.replace(tzinfo=None) if start_date.tzinfo else start_date
                            if event_time < start_naive:
                                continue
                        
                        if end_date:
                            end_naive = end_date.replace(tzinfo=None) if end_date.tzinfo else end_date
                            if event_time > end_naive:
                                continue
                        
                        filtered_data.append(event)
                    except Exception as e:
                        print(f"Erro ao processar timestamp {event.get('timestamp', 'N/A')}: {e}")
                        continue
                
                return filtered_data
            
            return data
            
        except Exception as e:
            print(f"Erro ao ler eventos de analytics: {e}")
            return []
    
    def get_stats(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> dict:
        """Gera estatísticas avançadas dos eventos"""
        events = self.get_events(start_date, end_date)
        
        if not events:
            # Retornar estrutura completa com valores padrão quando não há dados
            return {
                "total_views": 0,
                "unique_users": 0,
                "top_pages": [],
                "daily_views": [],
                "user_engagement": {
                    "avg_time_on_page": 0,
                    "total_interactions": 0
                },
                "performance_metrics": {
                    "total_events": 0,
                    "events_per_user": 0,
                    "active_sessions": 0,
                    "avg_sessions_per_user": 0
                },
                "conversion_funnel": {
                    "visitors": 0,
                    "form_interactions": 0,
                    "report_generations": 0,
                    "conversion_rate": 0
                },
                "device_analytics": {
                    "devices": [],
                    "browsers": [],
                    "top_resolutions": []
                },
                "time_analytics": {
                    "hourly_activity": [],
                    "peak_hour": 0
                },
                "interaction_analytics": {
                    "top_buttons": [],
                    "form_completions": 0,
                    "help_clicks": 0
                }
            }
        
        # Separar tipos de eventos
        page_views = [e for e in events if e.get('event') == 'page_view']
        button_clicks = [e for e in events if e.get('event') == 'button_click']
        form_submissions = [e for e in events if e.get('event') == 'form_submit']
        scroll_events = [e for e in events if e.get('event') == 'scroll_milestone']
        visibility_changes = [e for e in events if e.get('event') == 'visibility_change']
        help_clicks = [e for e in events if e.get('event') == 'help_clicked']
        
        # ✅ CORRIGIDO: Usuários únicos baseados em user_id (persistente) - APENAS com user_id válido
        unique_users = set(e.get('user_id', '') for e in events if e.get('user_id') and e.get('user_id').strip())
        # Sessões únicas - APENAS com session_id válido
        unique_sessions = set(e.get('session_id', '') for e in events if e.get('session_id') and e.get('session_id').strip())
        
        # 1. Páginas mais visitadas
        page_counts = {}
        for event in page_views:
            page = event.get('page', '/')
            page_counts[page] = page_counts.get(page, 0) + 1
        
        top_pages = [{"page": page, "count": count} for page, count in 
                    sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
        
        # 2. Visualizações por dia
        daily_counts = {}
        for event in page_views:
            date = event.get('timestamp', '').split('T')[0]
            daily_counts[date] = daily_counts.get(date, 0) + 1
        
        daily_views = [{"date": date, "count": count} for date, count in 
                      sorted(daily_counts.items())]
        
        # 3. Análise de Engajamento
        avg_time_on_page = 0
        # Calcular tempo médio usando visibility_change events (quando o usuário sai da página)
        if visibility_changes:
            valid_times = []
            for event in visibility_changes:
                if not event.get('data', {}).get('visible', True):  # Quando fica invisível (usuário saiu)
                    time_on_page = event.get('data', {}).get('time_since_load', 0)
                    if time_on_page > 0:
                        valid_times.append(time_on_page)
            
            if valid_times:
                avg_time_on_page = sum(valid_times) / len(valid_times) / 1000  # converter para segundos
        
        # Se não há visibility_change, usar uma estimativa baseada no último evento de cada sessão
        if avg_time_on_page == 0:
            session_times = {}
            for event in events:
                session_id = event.get('session_id')
                if session_id:
                    time_since_load = event.get('data', {}).get('time_since_load', 0)
                    if time_since_load > 0:
                        if session_id not in session_times or time_since_load > session_times[session_id]:
                            session_times[session_id] = time_since_load
            
            if session_times:
                avg_time_on_page = sum(session_times.values()) / len(session_times) / 1000
        
        # 4. Análise de Conversão (Funil) - Adaptado para eventos disponíveis
        total_visitors = len(unique_users)  # ✅ Usuários únicos reais
        
        # Interações com formulários: contar cliques em "Gerar Relatório" (preenchimento de formulário)
        form_interactions = sum(1 for event in button_clicks 
                               if 'Gerar Relatório' in event.get('data', {}).get('button_text', ''))
        
        # "Relatórios": contar apenas downloads de PDF (relatórios consolidados)
        pdf_downloads = sum(1 for event in button_clicks 
                           if 'Baixar PDF' in event.get('data', {}).get('button_text', ''))
        
        conversion_funnel = {
            "visitors": total_visitors,
            "form_interactions": form_interactions,
            "report_generations": pdf_downloads,
            "conversion_rate": (pdf_downloads / total_visitors * 100) if total_visitors > 0 else 0
        }
        
        # 5. Análise de Dispositivos e Navegadores (por usuários únicos)
        device_users = {}
        browser_users = {}
        
        # Agrupar por usuário para evitar contagem dupla
        user_devices = {}
        user_browsers = {}
        
        for event in events:
            user_id = event.get('user_id', '')
            if not user_id:
                continue
                
            user_agent = event.get('user_agent', '')
            
            # Detectar dispositivo móvel para este usuário (só conta uma vez por usuário)
            if user_id not in user_devices:
                is_mobile = any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone'])
                device_type = 'Mobile' if is_mobile else 'Desktop'
                user_devices[user_id] = device_type
            
            # Detectar navegador para este usuário (só conta uma vez por usuário)
            if user_id not in user_browsers:
                if 'Chrome' in user_agent:
                    browser = 'Chrome'
                elif 'Firefox' in user_agent:
                    browser = 'Firefox'
                elif 'Safari' in user_agent and 'Chrome' not in user_agent:
                    browser = 'Safari'
                elif 'Edge' in user_agent:
                    browser = 'Edge'
                else:
                    browser = 'Outros'
                user_browsers[user_id] = browser
        
        # Contar usuários únicos por dispositivo
        for device in user_devices.values():
            device_users[device] = device_users.get(device, 0) + 1
            
        # Contar usuários únicos por navegador
        for browser in user_browsers.values():
            browser_users[browser] = browser_users.get(browser, 0) + 1
        
        # 6. Análise Temporal (horários de pico)
        hourly_activity = {}
        for event in page_views:
            try:
                timestamp = datetime.fromisoformat(event.get('timestamp', ''))
                hour = timestamp.hour
                hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
            except:
                continue
        
        # 7. Botões mais clicados (excluindo botão de ajuda)
        button_clicks_count = {}
        for event in button_clicks:
            button_text = event.get('data', {}).get('button_text', 'Unknown')
            # Excluir cliques de ajuda da contagem geral de botões
            if button_text.lower() not in ['ajuda', 'help']:
                button_clicks_count[button_text] = button_clicks_count.get(button_text, 0) + 1
        
        top_buttons = [{"button": btn, "clicks": count} for btn, count in 
                      sorted(button_clicks_count.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        return {
            "total_views": len(page_views),
            "unique_users": len(unique_users),  # ✅ Usuários únicos reais
            "total_sessions": len(unique_sessions),  # ✅ Adicionado: sessões totais
            "top_pages": top_pages,
            "daily_views": daily_views,
            "user_engagement": {
                "avg_time_on_page": round(avg_time_on_page, 2),
                "total_interactions": len(button_clicks) + len(form_submissions)
            },
            "performance_metrics": {
                "total_events": len(events),
                "events_per_user": round(len(events) / len(unique_users), 2) if unique_users else 0,  # ✅ Por usuário único
                "events_per_session": round(len(events) / len(unique_sessions), 2) if unique_sessions else 0,  # ✅ Por sessão
                "active_sessions": len(unique_sessions),
                "avg_sessions_per_user": round(len(unique_sessions) / len(unique_users), 2) if unique_users else 0  # ✅ Sessões por usuário
            },
            "conversion_funnel": conversion_funnel,
            "device_analytics": {
                "devices": [{"type": device, "count": count} for device, count in device_users.items()],
                "browsers": [{"browser": browser, "count": count} for browser, count in browser_users.items()],
                "top_resolutions": self._get_top_resolutions(events)
            },
            "time_analytics": {
                "hourly_activity": [{"hour": hour, "activity": count} for hour, count in sorted(hourly_activity.items())],
                "peak_hour": max(hourly_activity, key=hourly_activity.get) if hourly_activity else 0
            },
            "interaction_analytics": {
                "top_buttons": top_buttons,
                "form_completions": len(form_submissions),
                "help_clicks": len(help_clicks)
            }
        }
    
    def _get_top_resolutions(self, events) -> list:
        """Obter resoluções de tela mais comuns"""
        resolutions = {}
        for event in events:
            resolution = event.get('screen_resolution', '')
            if resolution:
                resolutions[resolution] = resolutions.get(resolution, 0) + 1
        
        return [{"resolution": res, "count": count} for res, count in 
               sorted(resolutions.items(), key=lambda x: x[1], reverse=True)[:5]]
    
    def clear_all_data(self):
        """Limpa todos os dados de analytics"""
        try:
            with open(self.file_path, 'w') as f:
                json.dump([], f)
            print("Dados de analytics limpos com sucesso")
        except Exception as e:
            print(f"Erro ao limpar dados de analytics: {e}")
            raise e

# Instância global do storage
analytics_storage = AnalyticsStorage()

# Sistema de usuários ativos em tempo real (apenas em memória)
class ActiveUsersTracker:
    """Sistema para rastrear usuários ativos em tempo real usando apenas memória RAM"""
    
    def __init__(self):
        # Dicionário para armazenar último heartbeat de cada usuário
        # Estrutura: {user_id: {'last_seen': datetime, 'session_id': str, 'page': str}}
        self.active_users = {}
        
        # Timeout em segundos - usuário é considerado inativo após 2 minutos
        self.timeout_seconds = 120
        
        # Cache para otimizar consultas frequentes
        self._last_cleanup = datetime.now()
        self._cached_count = 0
        self._cache_valid_until = datetime.now()
    
    def update_user_activity(self, user_id: str, session_id: str = "", page: str = "/"):
        """Atualiza a atividade de um usuário (heartbeat)"""
        if not user_id or not user_id.strip():
            return False
            
        now = datetime.now()
        
        # Atualizar informações do usuário
        self.active_users[user_id] = {
            'last_seen': now,
            'session_id': session_id,
            'page': page
        }
        
        # Invalidar cache
        self._cache_valid_until = now
        
        # Fazer limpeza automática a cada 30 segundos
        if (now - self._last_cleanup).seconds >= 30:
            self._cleanup_inactive_users()
            
        return True
    
    def _cleanup_inactive_users(self):
        """Remove usuários inativos da memória"""
        now = datetime.now()
        timeout_threshold = now - timedelta(seconds=self.timeout_seconds)
        
        # Remover usuários inativos
        inactive_users = [
            user_id for user_id, data in self.active_users.items()
            if data['last_seen'] < timeout_threshold
        ]
        
        for user_id in inactive_users:
            del self.active_users[user_id]
        
        self._last_cleanup = now
        
        # Log apenas se houve limpeza significativa
        if len(inactive_users) > 0:
            print(f"ActiveUsers: Removidos {len(inactive_users)} usuários inativos")
    
    def get_active_users_count(self) -> int:
        """Retorna o número de usuários ativos agora"""
        now = datetime.now()
        
        # Usar cache se ainda for válido (válido por 10 segundos)
        if now < self._cache_valid_until + timedelta(seconds=10):
            return self._cached_count
        
        # Fazer limpeza antes de contar
        self._cleanup_inactive_users()
        
        # Contar usuários ativos
        timeout_threshold = now - timedelta(seconds=self.timeout_seconds)
        active_count = sum(
            1 for data in self.active_users.values()
            if data['last_seen'] >= timeout_threshold
        )
        
        # Atualizar cache
        self._cached_count = active_count
        self._cache_valid_until = now
        
        return active_count
    
    def get_active_users_details(self) -> dict:
        """Retorna detalhes dos usuários ativos (para debugging/admin)"""
        self._cleanup_inactive_users()
        
        now = datetime.now()
        timeout_threshold = now - timedelta(seconds=self.timeout_seconds)
        
        active_users_info = []
        pages_count = {}
        
        for user_id, data in self.active_users.items():
            if data['last_seen'] >= timeout_threshold:
                seconds_ago = int((now - data['last_seen']).total_seconds())
                
                active_users_info.append({
                    'user_id': user_id[:8] + "...",  # Truncar por privacidade
                    'session_id': data['session_id'][:8] + "..." if data['session_id'] else "",
                    'page': data['page'],
                    'last_seen_seconds_ago': seconds_ago
                })
                
                # Contar páginas
                page = data['page']
                pages_count[page] = pages_count.get(page, 0) + 1
        
        return {
            'active_count': len(active_users_info),
            'users': active_users_info,
            'pages_distribution': [
                {'page': page, 'users': count} 
                for page, count in sorted(pages_count.items(), key=lambda x: x[1], reverse=True)
            ],
            'last_cleanup': self._last_cleanup.isoformat(),
            'timeout_seconds': self.timeout_seconds
        }
    
    def get_stats_summary(self) -> dict:
        """Retorna estatísticas resumidas para o dashboard"""
        return {
            'active_users_now': self.get_active_users_count(),
            'last_updated': datetime.now().isoformat(),
            'timeout_minutes': self.timeout_seconds // 60
        }

# Instância global do tracker de usuários ativos
active_users_tracker = ActiveUsersTracker()
