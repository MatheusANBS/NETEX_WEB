from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
import json
import os

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
            data['timestamp'] = datetime.now()
        super().__init__(**data)

class AnalyticsStorage:
    """Sistema simples de armazenamento em arquivo JSON"""
    
    def __init__(self, file_path: str = "analytics_data.json"):
        self.file_path = file_path
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        """Garante que o arquivo existe"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)
    
    def save_event(self, event: AnalyticsEvent):
        """Salva um evento no arquivo"""
        try:
            # Ler dados existentes
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            # Adicionar novo evento
            event_dict = event.dict()
            event_dict['timestamp'] = event.timestamp.isoformat()
            data.append(event_dict)
            
            # Manter apenas os últimos 10000 eventos para evitar arquivo muito grande
            if len(data) > 10000:
                data = data[-10000:]
            
            # Salvar de volta
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
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
                    event_time = datetime.fromisoformat(event['timestamp'])
                    if start_date and event_time < start_date:
                        continue
                    if end_date and event_time > end_date:
                        continue
                    filtered_data.append(event)
                return filtered_data
            
            return data
            
        except Exception as e:
            print(f"Erro ao ler eventos de analytics: {e}")
            return []
    
    def get_stats(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> dict:
        """Gera estatísticas avançadas dos eventos"""
        events = self.get_events(start_date, end_date)
        
        if not events:
            return {
                "total_views": 0,
                "unique_users": 0,
                "top_pages": [],
                "daily_views": [],
                "user_engagement": {},
                "performance_metrics": {},
                "conversion_funnel": {},
                "device_analytics": {},
                "time_analytics": {}
            }
        
        # Separar tipos de eventos
        page_views = [e for e in events if e.get('event') == 'page_view']
        button_clicks = [e for e in events if e.get('event') == 'button_click']
        form_submissions = [e for e in events if e.get('event') == 'form_submit']
        time_events = [e for e in events if e.get('event') == 'time_on_page']
        scroll_events = [e for e in events if e.get('event') == 'scroll_depth']
        
        # ✅ CORRIGIDO: Usuários únicos baseados em user_id (persistente)
        unique_users = set(e.get('user_id', '') for e in events if e.get('user_id'))
        # Sessões únicas para análise de bounce rate
        unique_sessions = set(e.get('session_id', '') for e in events if e.get('session_id'))
        
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
        if time_events:
            total_time = sum(e.get('data', {}).get('duration', 0) for e in time_events)
            avg_time_on_page = total_time / len(time_events) / 1000  # converter para segundos
        
        bounce_rate = 0
        if unique_sessions:
            single_page_sessions = 0
            for session in unique_sessions:
                session_events = [e for e in page_views if e.get('session_id') == session]
                if len(session_events) <= 1:
                    single_page_sessions += 1
            bounce_rate = (single_page_sessions / len(unique_sessions)) * 100
        
        # 4. Análise de Conversão (Funil)
        total_visitors = len(unique_users)  # ✅ Usuários únicos reais
        form_interactions = len(set(e.get('user_id') for e in events if e.get('event') == 'form_field_change' and e.get('user_id')))  # ✅ Usuários únicos que interagiram
        report_generations = len(set(e.get('user_id') for e in events if e.get('event') == 'report_generation' and e.get('user_id')))  # ✅ Usuários únicos que geraram relatórios
        
        conversion_funnel = {
            "visitors": total_visitors,
            "form_interactions": form_interactions,
            "report_generations": report_generations,
            "conversion_rate": (report_generations / total_visitors * 100) if total_visitors > 0 else 0
        }
        
        # 5. Análise de Dispositivos
        device_data = {}
        browser_data = {}
        for event in events:
            user_agent = event.get('user_agent', '')
            resolution = event.get('screen_resolution', '')
            
            # Detectar dispositivo móvel
            is_mobile = any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone'])
            device_type = 'Mobile' if is_mobile else 'Desktop'
            device_data[device_type] = device_data.get(device_type, 0) + 1
            
            # Detectar navegador
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
            
            browser_data[browser] = browser_data.get(browser, 0) + 1
        
        # 6. Análise Temporal (horários de pico)
        hourly_activity = {}
        for event in page_views:
            try:
                timestamp = datetime.fromisoformat(event.get('timestamp', ''))
                hour = timestamp.hour
                hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
            except:
                continue
        
        # 7. Botões mais clicados
        button_clicks_count = {}
        for event in button_clicks:
            button_text = event.get('data', {}).get('button_text', 'Unknown')
            button_clicks_count[button_text] = button_clicks_count.get(button_text, 0) + 1
        
        top_buttons = [{"button": btn, "clicks": count} for btn, count in 
                      sorted(button_clicks_count.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        # 8. Scroll depth médio
        avg_scroll_depth = 0
        if scroll_events:
            total_scroll = sum(e.get('data', {}).get('depth', 0) for e in scroll_events)
            avg_scroll_depth = total_scroll / len(scroll_events)
        
        return {
            "total_views": len(page_views),
            "unique_users": len(unique_users),  # ✅ Usuários únicos reais
            "total_sessions": len(unique_sessions),  # ✅ Adicionado: sessões totais
            "top_pages": top_pages,
            "daily_views": daily_views,
            "user_engagement": {
                "avg_time_on_page": round(avg_time_on_page, 2),
                "bounce_rate": round(bounce_rate, 2),
                "avg_scroll_depth": round(avg_scroll_depth, 2),
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
                "devices": [{"type": device, "count": count} for device, count in device_data.items()],
                "browsers": [{"browser": browser, "count": count} for browser, count in browser_data.items()],
                "top_resolutions": self._get_top_resolutions(events)
            },
            "time_analytics": {
                "hourly_activity": [{"hour": hour, "activity": count} for hour, count in sorted(hourly_activity.items())],
                "peak_hour": max(hourly_activity, key=hourly_activity.get) if hourly_activity else 0
            },
            "interaction_analytics": {
                "top_buttons": top_buttons,
                "form_completions": len(form_submissions),
                "help_clicks": len([e for e in events if e.get('event') == 'help_clicked'])
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

# Instância global do storage
analytics_storage = AnalyticsStorage()
