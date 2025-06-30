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
    """Sistema otimizado de armazenamento com rate limiting e compactação"""
    
    def __init__(self, file_path: str = "analytics_data.json"):
        self.file_path = file_path
        self.ensure_file_exists()
        # Cache para rate limiting
        self.session_event_count = {}
        self.last_cleanup = datetime.now()
        # Cache para deduplicação
        self.recent_events_cache = {}
        self.cache_cleanup_interval = 300  # 5 minutos
    
    def ensure_file_exists(self):
        """Garante que o arquivo existe"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)
    
    def should_accept_event(self, event: AnalyticsEvent) -> bool:
        """Rate limiting e deduplicação - limitar eventos por sessão"""
        session_id = event.session_id
        
        # Limpeza periódica do cache (a cada hora)
        if (datetime.now() - self.last_cleanup).seconds > 3600:
            self.session_event_count.clear()
            self.recent_events_cache.clear()
            self.last_cleanup = datetime.now()
        
        # Deduplicação - evitar eventos idênticos recentes
        event_key = f"{session_id}_{event.event}_{event.page}"
        current_time = datetime.now()
        
        if event_key in self.recent_events_cache:
            last_time = self.recent_events_cache[event_key]
            # Se o mesmo evento aconteceu há menos de 30 segundos, ignora
            if (current_time - last_time).seconds < 30:
                print(f"Evento duplicado ignorado: {event.event} na página {event.page}")
                return False
        
        # Atualizar cache de deduplicação
        self.recent_events_cache[event_key] = current_time
        
        # Contar eventos da sessão
        current_count = self.session_event_count.get(session_id, 0)
        
        # Limite de 30 eventos por sessão (reduzido ainda mais)
        if current_count >= 30:
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
            
            # Manter apenas os últimos 500 eventos para evitar arquivo muito grande
            if len(data) > 500:
                data = data[-500:]
            
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
        
        # Processar eventos - garantir que events é uma lista
        if not isinstance(events, list):
            print(f"Erro: events não é uma lista, é {type(events)}")
            events = []
        
        # RESTAURADO: filtrar eventos específicos do sistema
        page_views = [e for e in events if e.get('event') == 'page_view']
        button_clicks = [e for e in events if e.get('event') == 'button_click']
        form_submissions = [e for e in events if e.get('event') == 'form_submission']
        help_clicks = [e for e in events if e.get('event') == 'help_clicked']
        report_generated_events = [e for e in events if e.get('event') == 'report_generated']
        pdf_download_events = [e for e in events if e.get('event') == 'pdf_download']
        corte_events = [e for e in events if e.get('event') == 'corte_generated']
        
        # Obter usuários únicos de forma segura
        unique_user_ids = set()
        unique_session_ids = set()
        
        for event in events:
            if isinstance(event, dict):
                user_id = event.get('user_id', '')
                session_id = event.get('session_id', '')
                
                if user_id and user_id.strip():
                    unique_user_ids.add(user_id)
                if session_id and session_id.strip():
                    unique_session_ids.add(session_id)
        
        unique_users = len(unique_user_ids)
        unique_sessions = len(unique_session_ids)
        
        # Top páginas
        page_counts = {}
        for event in page_views:
            page = event.get('page', '/')
            page_counts[page] = page_counts.get(page, 0) + 1
        
        top_pages = [{"page": page, "views": count} for page, count in 
                    sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        # Views diárias - CORRIGIDO: contar apenas page_views como estava antes
        daily_counts = {}
        for event in page_views:  # Voltar a usar apenas page_views
            try:
                timestamp_str = event['timestamp']
                if 'Z' in timestamp_str:
                    timestamp_str = timestamp_str.replace('Z', '+00:00')
                
                event_date = datetime.fromisoformat(timestamp_str).date()
                daily_counts[event_date] = daily_counts.get(event_date, 0) + 1
            except:
                continue
        
        daily_views = [{"date": str(date), "views": count} for date, count in 
                      sorted(daily_counts.items())]
        
        # Tempo médio na página (calculado a partir dos eventos page_exit)
        page_exit_events = [e for e in events if e.get('event') == 'page_exit']
        total_time = 0
        valid_sessions = 0
        
        for exit_event in page_exit_events:
            data = exit_event.get('data', {})
            time_on_page = data.get('time_on_page')
            
            if time_on_page and isinstance(time_on_page, (int, float)) and time_on_page > 0:
                # Converter de milissegundos para segundos
                time_in_seconds = time_on_page / 1000
                # Filtrar valores muito altos (mais de 1 hora) que podem ser outliers
                if time_in_seconds <= 3600:
                    total_time += time_in_seconds
                    valid_sessions += 1
        
        # Calcular média ou usar fallback baseado em page views
        if valid_sessions > 0:
            avg_time_on_page = total_time / valid_sessions
        elif page_views:
            # Fallback: estimar baseado no número de page views (usuários que ficaram pouco tempo)
            avg_time_on_page = min(30, len(page_views) * 2)  # Máximo 30s, mínimo baseado em atividade
        else:
            avg_time_on_page = 0
        
        # Análise de dispositivos
        device_users = {}
        browser_users = {}
        for event in events:
            user_agent = event.get('user_agent', '').lower()
            user_id = event.get('user_id', '')
            
            if user_id and user_agent:
                if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
                    device_users['Mobile'] = device_users.get('Mobile', set())
                    device_users['Mobile'].add(user_id)
                elif 'tablet' in user_agent or 'ipad' in user_agent:
                    device_users['Tablet'] = device_users.get('Tablet', set())
                    device_users['Tablet'].add(user_id)
                else:
                    device_users['Desktop'] = device_users.get('Desktop', set())
                    device_users['Desktop'].add(user_id)
                
                if 'chrome' in user_agent:
                    browser_users['Chrome'] = browser_users.get('Chrome', set())
                    browser_users['Chrome'].add(user_id)
                elif 'firefox' in user_agent:
                    browser_users['Firefox'] = browser_users.get('Firefox', set())
                    browser_users['Firefox'].add(user_id)
                elif 'safari' in user_agent:
                    browser_users['Safari'] = browser_users.get('Safari', set())
                    browser_users['Safari'].add(user_id)
                else:
                    browser_users['Other'] = browser_users.get('Other', set())
                    browser_users['Other'].add(user_id)
        
        # Converter sets para contadores
        for device in device_users:
            device_users[device] = len(device_users[device])
        for browser in browser_users:
            browser_users[browser] = len(browser_users[browser])
        
        # Atividade por hora
        hourly_activity = {}
        for event in events:
            try:
                timestamp_str = event['timestamp']
                if 'Z' in timestamp_str:
                    timestamp_str = timestamp_str.replace('Z', '+00:00')
                
                event_time = datetime.fromisoformat(timestamp_str)
                hour = event_time.hour
                hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
            except:
                continue
        
        # Top botões clicados - RESTAURADO: detecção correta de botões
        button_counts = {}
        pdf_downloads = len(pdf_download_events)  # Contar eventos diretos de PDF
        report_generations = len(report_generated_events)  # Contar eventos diretos de relatório
        
        for click in button_clicks:
            # Extrair informações do botão de forma mais robusta
            data = click.get('data', {})
            button_text = data.get('buttonText', data.get('button_text', 'Unknown'))
            button_id = data.get('buttonId', data.get('button_id', ''))
            
            # Detectar downloads de PDF e relatórios gerados via cliques de botão
            if 'download' in button_text.lower() or 'baixar' in button_text.lower() or 'pdf' in button_text.lower():
                pdf_downloads += 1
            if 'gerar' in button_text.lower() or 'relatório' in button_text.lower() or 'relatorio' in button_text.lower():
                report_generations += 1
            
            # Contar cliques por botão
            button_key = f"{button_text} ({button_id})" if button_id else button_text
            button_counts[button_key] = button_counts.get(button_key, 0) + 1
        
        # Adicionar eventos de corte ao contador de relatórios
        report_generations += len(corte_events)
        
        top_buttons = [{"button": button, "clicks": count} for button, count in 
                      sorted(button_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        return {
            "total_views": len(page_views),
            "unique_users": unique_users,
            "total_sessions": unique_sessions,  # unique_sessions já é um inteiro
            "top_pages": top_pages,
            "daily_views": daily_views,
            "user_engagement": {
                "avg_time_on_page": round(avg_time_on_page, 2),
                "total_interactions": len(button_clicks) + len(form_submissions) + len(help_clicks)  # CORRIGIDO: incluir help_clicks
            },
            "performance_metrics": {
                "total_events": len(events),
                "events_per_user": round(len(events) / unique_users, 2) if unique_users else 0,
                "events_per_session": round(len(events) / unique_sessions, 2) if unique_sessions else 0,
                "active_sessions": unique_sessions,  # unique_sessions já é um inteiro
                "avg_sessions_per_user": round(unique_sessions / unique_users, 2) if unique_users else 0
            },
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
                "help_clicks": len(help_clicks),
                "pdf_downloads": pdf_downloads,  # RESTAURADO: downloads de PDF
                "report_generations": report_generations,  # RESTAURADO: relatórios gerados
                "corte_generations": len(corte_events),  # RESTAURADO: cortes gerados
                "total_button_clicks": len(button_clicks)  # RESTAURADO: total de cliques
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
    
    def compact_log(self) -> dict:
        """Compacta o log removendo duplicatas e eventos antigos"""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            original_count = len(data)
            print(f"Iniciando compactação: {original_count} eventos")
            
            # 1. Remover eventos mais antigos que 30 dias
            cutoff_date = datetime.now() - timedelta(days=30)
            recent_events = []
            
            for event in data:
                try:
                    timestamp_str = event['timestamp']
                    if 'Z' in timestamp_str:
                        timestamp_str = timestamp_str.replace('Z', '+00:00')
                    
                    event_time = datetime.fromisoformat(timestamp_str)
                    if event_time.tzinfo is not None:
                        event_time = event_time.replace(tzinfo=None)
                    
                    if event_time >= cutoff_date:
                        recent_events.append(event)
                except Exception as e:
                    print(f"Erro ao processar timestamp: {e}")
                    continue
            
            # 2. Remover duplicatas exatas (mantendo apenas a mais recente)
            unique_events = {}
            for event in recent_events:
                # Criar chave única baseada em evento, página, sessão e tempo aproximado
                try:
                    timestamp_str = event['timestamp']
                    if 'Z' in timestamp_str:
                        timestamp_str = timestamp_str.replace('Z', '+00:00')
                    event_time = datetime.fromisoformat(timestamp_str)
                    minute_key = event_time.replace(second=0, microsecond=0)
                    
                    key = f"{event.get('event', '')}_{event.get('page', '')}_{event.get('session_id', '')}_{minute_key}"
                    
                    # Manter apenas o evento mais recente para cada chave
                    if key not in unique_events or event['timestamp'] > unique_events[key]['timestamp']:
                        unique_events[key] = event
                except:
                    continue
            
            deduplicated_events = list(unique_events.values())
            
            # 3. Filtrar eventos irrelevantes ou muito frequentes - RESTAURADO: manter eventos do sistema
            filtered_events = []
            for event in deduplicated_events:
                event_type = event.get('event', '')
                
                # RESTAURADO: Manter todos os eventos importantes do sistema
                if event_type in ['page_view', 'button_click', 'form_submission', 'report_generated', 
                                'help_clicked', 'pdf_download', 'corte_generated', 'performance_metrics']:
                    filtered_events.append(event)
            
            # 4. Limitar a 300 eventos mais recentes
            filtered_events.sort(key=lambda x: x['timestamp'], reverse=True)
            final_events = filtered_events[:300]
            
            # Salvar dados compactados
            with open(self.file_path, 'w') as f:
                json.dump(final_events, f, indent=2)
            
            final_count = len(final_events)
            removed_count = original_count - final_count
            
            result = {
                "original_count": original_count,
                "final_count": final_count,
                "removed_count": removed_count,
                "compression_ratio": f"{((removed_count / original_count) * 100):.1f}%" if original_count > 0 else "0%",
                "status": "success"
            }
            
            print(f"Compactação concluída: {original_count} → {final_count} eventos ({removed_count} removidos)")
            return result
            
        except Exception as e:
            print(f"Erro durante compactação: {e}")
            return {
                "status": "error",
                "error": str(e),
                "original_count": 0,
                "final_count": 0,
                "removed_count": 0,
                "compression_ratio": "0%"
            }
    
    def get_log_info(self) -> dict:
        """Retorna informações sobre o estado atual do log"""
        try:
            # Informações do arquivo
            file_size = os.path.getsize(self.file_path) if os.path.exists(self.file_path) else 0
            
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            event_count = len(data)
            
            # Analisar tipos de eventos
            event_types = {}
            oldest_event = None
            newest_event = None
            
            for event in data:
                event_type = event.get('event', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1
                
                try:
                    timestamp_str = event['timestamp']
                    if 'Z' in timestamp_str:
                        timestamp_str = timestamp_str.replace('Z', '+00:00')
                    
                    event_time = datetime.fromisoformat(timestamp_str)
                    
                    if oldest_event is None or event_time < oldest_event:
                        oldest_event = event_time
                    if newest_event is None or event_time > newest_event:
                        newest_event = event_time
                except:
                    continue
            
            return {
                "file_size_bytes": file_size,
                "file_size_kb": round(file_size / 1024, 2),
                "event_count": event_count,
                "event_types": event_types,
                "oldest_event": oldest_event.isoformat() if oldest_event else None,
                "newest_event": newest_event.isoformat() if newest_event else None,
                "needs_compaction": event_count > 500 or file_size > 100000  # 100KB
            }
            
        except Exception as e:
            print(f"Erro ao obter informações do log: {e}")
            return {
                "file_size_bytes": 0,
                "file_size_kb": 0,
                "event_count": 0,
                "event_types": {},
                "oldest_event": None,
                "newest_event": None,
                "needs_compaction": False,
                "error": str(e)
            }
    
    def _is_today(self, timestamp_str: str) -> bool:
        """Verifica se um timestamp é de hoje"""
        try:
            if 'Z' in timestamp_str:
                timestamp_str = timestamp_str.replace('Z', '+00:00')
            
            event_time = datetime.fromisoformat(timestamp_str)
            if event_time.tzinfo is not None:
                event_time = event_time.replace(tzinfo=None)
            
            today = datetime.now().date()
            return event_time.date() == today
        except:
            return False

# Instância global do storage
analytics_storage = AnalyticsStorage()

# Sistema de usuários ativos em tempo real (apenas em memória)
class ActiveUsersTracker:
    """Sistema para rastrear usuários ativos em tempo real usando apenas memória RAM"""
    
    def __init__(self):
        # Dicionário para armazenar último heartbeat de cada usuário
        # Estrutura: {user_id: {'last_seen': datetime, 'session_id': str, 'page': str}}
        self.active_users = {}
        
        # Timeout em segundos - usuário é considerado inativo após 1 minuto
        self.timeout_seconds = 60
        
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
        inactive_users = []
        for user_id, info in self.active_users.items():
            if info['last_seen'] < timeout_threshold:
                inactive_users.append(user_id)
        
        for user_id in inactive_users:
            del self.active_users[user_id]
        
        self._last_cleanup = now
        
        if inactive_users:
            print(f"Removidos {len(inactive_users)} usuários inativos da memória")
    
    def get_active_count(self) -> int:
        """Retorna o número de usuários ativos agora"""
        # Cache por 10 segundos para evitar processamento excessivo
        now = datetime.now()
        if now < self._cache_valid_until + timedelta(seconds=10):
            return self._cached_count
        
        # Fazer limpeza antes de contar
        self._cleanup_inactive_users()
        
        # Contar usuários realmente ativos
        self._cached_count = len(self.active_users)
        self._cache_valid_until = now
        
        return self._cached_count
    
    def get_active_users_details(self) -> list:
        """Retorna detalhes dos usuários ativos (para debug/admin)"""
        self._cleanup_inactive_users()
        
        active_list = []
        for user_id, info in self.active_users.items():
            active_list.append({
                'user_id': user_id,
                'session_id': info['session_id'],
                'page': info['page'],
                'last_seen': info['last_seen'].isoformat(),
                'seconds_ago': (datetime.now() - info['last_seen']).seconds
            })
        
        # Ordenar por último acesso
        active_list.sort(key=lambda x: x['seconds_ago'])
        
        return active_list
    
    def get_active_users_count(self) -> int:
        """Alias para get_active_count() - compatibilidade"""
        return self.get_active_count()
    
    def get_stats_summary(self) -> dict:
        """Retorna resumo estatístico dos usuários ativos"""
        self._cleanup_inactive_users()
        
        active_count = len(self.active_users)
        
        # Contar páginas únicas
        pages = set()
        sessions = set()
        
        for info in self.active_users.values():
            if info['page']:
                pages.add(info['page'])
            if info['session_id']:
                sessions.add(info['session_id'])
        
        return {
            "active_users_now": active_count,
            "unique_pages": len(pages),
            "active_sessions": len(sessions),
            "last_cleanup": self._last_cleanup.isoformat() if self._last_cleanup else None,
            "timeout_seconds": self.timeout_seconds
        }

# Instância global do tracker de usuários ativos
active_users_tracker = ActiveUsersTracker()
