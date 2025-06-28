from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

from app.models.analytics import AnalyticsEvent, analytics_storage

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
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
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
