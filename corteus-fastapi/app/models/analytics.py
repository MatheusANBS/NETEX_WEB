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
        """Gera estatísticas dos eventos"""
        events = self.get_events(start_date, end_date)
        
        if not events:
            return {
                "total_views": 0,
                "unique_users": 0,
                "top_pages": [],
                "daily_views": []
            }
        
        # Contar visualizações de página
        page_views = [e for e in events if e.get('event') == 'page_view']
        
        # Usuários únicos (baseado em session_id)
        unique_sessions = set(e.get('session_id', '') for e in events if e.get('session_id'))
        
        # Páginas mais visitadas
        page_counts = {}
        for event in page_views:
            page = event.get('page', '/')
            page_counts[page] = page_counts.get(page, 0) + 1
        
        top_pages = [{"page": page, "count": count} for page, count in 
                    sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
        
        # Visualizações por dia
        daily_counts = {}
        for event in page_views:
            date = event.get('timestamp', '').split('T')[0]
            daily_counts[date] = daily_counts.get(date, 0) + 1
        
        daily_views = [{"date": date, "count": count} for date, count in 
                      sorted(daily_counts.items())]
        
        return {
            "total_views": len(page_views),
            "unique_users": len(unique_sessions),
            "top_pages": top_pages,
            "daily_views": daily_views
        }

# Instância global do storage
analytics_storage = AnalyticsStorage()
