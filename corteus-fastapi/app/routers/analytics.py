from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import os
import json

from app.models.analytics import AnalyticsEvent, analytics_storage, active_users_tracker

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

class TrackRequest(BaseModel):
    event: str
    page: str
    session_id: str = ""
    user_id: str = ""
    referrer: str = ""
    screen_resolution: str = ""
    data: dict = {}

class HeartbeatRequest(BaseModel):
    user_id: str
    session_id: str = ""
    page: str = "/"

@router.post("/track")
async def track_event(track_data: TrackRequest, request: Request):
    """Endpoint para receber eventos de analytics"""
    try:
        # Criar evento de analytics
        event = AnalyticsEvent(
            event=track_data.event,
            page=track_data.page,
            user_agent=request.headers.get("user-agent", ""),
            ip=request.client.host if request.client else "",
            session_id=track_data.session_id,
            user_id=track_data.user_id,
            referrer=track_data.referrer,
            screen_resolution=track_data.screen_resolution,
            data=track_data.data
        )
        
        # Salvar evento
        analytics_storage.save_event(event)
        
        return {"success": True}
        
    except Exception as e:
        print(f"Erro ao processar evento de analytics: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/track-batch")
async def track_batch_events(request: Request):
    """Endpoint para receber múltiplos eventos de analytics em lote"""
    try:
        body = await request.json()
        events = body.get('events', [])
        
        if not events:
            return {"success": True, "processed": 0}
        
        processed = 0
        for event_data in events:
            try:
                # Criar evento de analytics
                event = AnalyticsEvent(
                    event=event_data.get('event', ''),
                    page=event_data.get('page', ''),
                    user_agent=request.headers.get("user-agent", ""),
                    ip=request.client.host if request.client else "",
                    session_id=event_data.get('session_id', ''),
                    user_id=event_data.get('user_id', ''),
                    referrer=event_data.get('referrer', ''),
                    screen_resolution=event_data.get('screen_resolution', ''),
                    data=event_data.get('data', {})
                )
                
                # Salvar evento
                analytics_storage.save_event(event)
                processed += 1
                
            except Exception as e:
                print(f"Erro ao processar evento individual: {e}")
                continue
        
        return {"success": True, "processed": processed}
        
    except Exception as e:
        print(f"Erro ao processar lote de eventos de analytics: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/analytics-data")
async def get_analytics_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Endpoint para obter dados do dashboard"""
    try:
        # Converter strings de data para datetime
        start_dt = None
        end_dt = None
        
        if start_date:
            # Interpretar a data como início do dia no fuso horário local
            start_dt = datetime.fromisoformat(start_date + "T00:00:00")
        if end_date:
            # Interpretar a data como final do dia no fuso horário local
            end_dt = datetime.fromisoformat(end_date + "T23:59:59")
        
        # Obter estatísticas
        stats = analytics_storage.get_stats(start_dt, end_dt)
        
        return stats
        
    except Exception as e:
        print(f"Erro ao obter dados de analytics: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter dados")

@router.get("/dashboard", response_class=HTMLResponse)
async def analytics_dashboard(request: Request):
    """Página do dashboard de analytics"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Analytics Dashboard - Corteus"
    })

@router.get("/analytics-stats")
async def get_analytics_stats():
    """Endpoint para monitorar performance do sistema de analytics"""
    try:
        # Estatísticas do arquivo
        file_size = 0
        event_count = 0
        
        if os.path.exists("analytics_data.json"):
            file_size = os.path.getsize("analytics_data.json")
            with open("analytics_data.json", 'r') as f:
                data = json.load(f)
                event_count = len(data)
        
        # Estatísticas do rate limiting
        session_stats = {
            "active_sessions": len(analytics_storage.session_event_count),
            "events_per_session": dict(analytics_storage.session_event_count)
        }
        
        return {
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "total_events": event_count,
            "rate_limiting": session_stats,
            "last_cleanup": analytics_storage.last_cleanup.isoformat()
        }
        
    except Exception as e:
        print(f"Erro ao obter estatísticas de analytics: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter estatísticas")

@router.post("/clear-data")
async def clear_analytics_data():
    """Endpoint para limpar todos os dados de analytics (cuidado!)"""
    try:
        analytics_storage.clear_all_data()
        return {"success": True, "message": "Dados de analytics limpos com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar dados: {str(e)}")

@router.post("/heartbeat")
async def heartbeat(heartbeat_data: HeartbeatRequest):
    """Endpoint para heartbeat de usuários ativos (não salva em arquivo)"""
    try:
        # Atualizar atividade do usuário apenas na memória
        success = active_users_tracker.update_user_activity(
            user_id=heartbeat_data.user_id,
            session_id=heartbeat_data.session_id,
            page=heartbeat_data.page
        )
        
        if success:
            return {
                "success": True,
                "active_users_count": active_users_tracker.get_active_users_count()
            }
        else:
            return {"success": False, "error": "Invalid user_id"}
        
    except Exception as e:
        print(f"Erro no heartbeat: {e}")
        return {"success": False, "error": "Internal error"}

@router.get("/active-users")
async def get_active_users():
    """Endpoint para obter usuários ativos agora"""
    try:
        return active_users_tracker.get_stats_summary()
    except Exception as e:
        print(f"Erro ao obter usuários ativos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter usuários ativos")

@router.get("/active-users/details")
async def get_active_users_details():
    """Endpoint para obter detalhes dos usuários ativos (admin)"""
    try:
        return active_users_tracker.get_active_users_details()
    except Exception as e:
        print(f"Erro ao obter detalhes dos usuários ativos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter detalhes")

@router.post("/compact")
async def compact_analytics_log():
    """Endpoint para compactar o log de analytics"""
    try:
        result = analytics_storage.compact_log()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro durante compactação: {str(e)}")

@router.get("/log-info")
async def get_log_info():
    """Endpoint para obter informações sobre o log de analytics"""
    try:
        info = analytics_storage.get_log_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter informações do log: {str(e)}")
