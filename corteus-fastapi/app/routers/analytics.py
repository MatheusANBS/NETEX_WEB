from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import os
import json

from app.models.analytics import AnalyticsEvent, analytics_storage, active_users_tracker
from app.auth import auth_manager

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def verify_admin_auth(request: Request) -> bool:
    """Verificar se o usuário está autenticado como admin usando JWT"""
    if not auth_manager.is_admin_authenticated(request):
        raise HTTPException(status_code=403, detail="Acesso negado. Autenticação de admin necessária.")
    return True

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
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Endpoint para obter dados do dashboard - Requer autenticação admin"""
    # Verificar autenticação admin
    verify_admin_auth(request)
    
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

@router.get("/analytics-stats")
async def get_analytics_stats(request: Request):
    """Endpoint para monitorar performance do sistema de analytics - Requer autenticação admin"""
    # Verificar autenticação admin
    verify_admin_auth(request)
    
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
async def clear_analytics_data(request: Request):
    """Endpoint para limpar todos os dados de analytics - Requer autenticação admin"""
    # Verificar autenticação admin
    verify_admin_auth(request)
    
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
async def get_active_users_details(request: Request):
    """Endpoint para obter detalhes dos usuários ativos - Requer autenticação admin"""
    # Verificar autenticação admin
    verify_admin_auth(request)
    try:
        return active_users_tracker.get_active_users_details()
    except Exception as e:
        print(f"Erro ao obter detalhes dos usuários ativos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter detalhes")

@router.post("/compact")
async def compact_analytics_log(request: Request):
    """Endpoint para compactar o log de analytics - Requer autenticação admin"""
    # Verificar autenticação admin
    verify_admin_auth(request)
    
    try:
        result = analytics_storage.compact_log()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro durante compactação: {str(e)}")

@router.post("/auto-compact")
async def auto_compact(request: Request):
    """Endpoint para executar compactação automática inteligente - Requer autenticação admin"""
    # Verificar autenticação admin
    verify_admin_auth(request)
    
    try:
        result = analytics_storage.auto_compact_if_needed()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro durante auto-compactação: {str(e)}")

@router.get("/compaction-analysis")
async def get_compaction_analysis(request: Request):
    """Endpoint para obter análise detalhada de compactação - Requer autenticação admin"""
    # Verificar autenticação admin
    verify_admin_auth(request)
    
    try:
        info = analytics_storage.get_log_info()
        
        # Extrair apenas os dados de análise
        analysis = {
            "compaction_score": info.get("compaction_score", 0),
            "needs_compaction": info.get("needs_compaction", False),
            "estimated_reduction": info.get("estimated_reduction", "0%"),
            "compaction_reasons": info.get("compaction_reasons", []),
            "analysis_details": info.get("analysis_details", {}),
            "recommendation": "none"
        }
        
        # Gerar recomendação baseada no score
        score = analysis["compaction_score"]
        if score > 80:
            analysis["recommendation"] = "urgent"
        elif score > 50:
            analysis["recommendation"] = "moderate"
        elif score > 25:
            analysis["recommendation"] = "optional"
        else:
            analysis["recommendation"] = "none"
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter análise de compactação: {str(e)}")

@router.get("/log-info")
async def get_log_info(request: Request):
    """Endpoint para obter informações sobre o log de analytics - Requer autenticação admin"""
    # Verificar autenticação admin
    verify_admin_auth(request)
    
    try:
        info = analytics_storage.get_log_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter informações do log: {str(e)}")

@router.get("/export-full-data")
async def export_full_data(request: Request):
    """Endpoint para exportar TODOS os dados do analytics_data.json - Requer autenticação admin"""
    # Verificar autenticação admin
    verify_admin_auth(request)
    
    try:
        from fastapi.responses import FileResponse
        import os
        from datetime import datetime
        
        # Verificar se arquivo existe
        if not os.path.exists("analytics_data.json"):
            raise HTTPException(status_code=404, detail="Arquivo de dados não encontrado")
        
        # Gerar nome do arquivo com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"corteus_analytics_backup_{timestamp}.json"
        
        # Retornar arquivo para download
        return FileResponse(
            path="analytics_data.json",
            filename=filename,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"Erro ao exportar dados completos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao exportar dados")

@router.post("/import-full-data")
async def import_full_data(request: Request):
    """Endpoint para importar dados completos com validação e análise automática - Requer autenticação admin"""
    # Verificar autenticação admin
    verify_admin_auth(request)
    
    try:
        import json
        import shutil
        from datetime import datetime
        
        # Receber arquivo
        form = await request.form()
        file = form.get("file")
        
        if not file:
            raise HTTPException(status_code=400, detail="Nenhum arquivo enviado")
        
        # Verificar se é JSON válido
        try:
            file_content = await file.read()
            imported_data = json.loads(file_content.decode('utf-8'))
            
            # Verificar se é uma lista (formato esperado)
            if not isinstance(imported_data, list):
                raise HTTPException(status_code=400, detail="Arquivo deve conter uma lista JSON")
                
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Arquivo não é um JSON válido: {str(e)}")
        
        # Validação dos dados importados
        valid_events = []
        invalid_events = 0
        required_fields = ['event', 'page', 'timestamp']
        
        for i, event in enumerate(imported_data):
            if isinstance(event, dict):
                # Verificar campos obrigatórios
                if all(field in event for field in required_fields):
                    # Validar formato de timestamp
                    try:
                        if isinstance(event['timestamp'], str):
                            # Tentar parsear o timestamp para validar
                            datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                            valid_events.append(event)
                        else:
                            invalid_events += 1
                    except ValueError:
                        invalid_events += 1
                else:
                    invalid_events += 1
            else:
                invalid_events += 1
        
        if not valid_events:
            raise HTTPException(status_code=400, detail="Nenhum evento válido encontrado no arquivo")
        
        # Fazer backup do arquivo atual
        backup_created = False
        if os.path.exists("analytics_data.json"):
            backup_name = f"analytics_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy2("analytics_data.json", backup_name)
            backup_created = True
            print(f"✅ Backup criado: {backup_name}")
        
        # Substituir arquivo atual com dados validados
        with open("analytics_data.json", 'w', encoding='utf-8') as f:
            json.dump(valid_events, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Importados {len(valid_events)} eventos válidos")
        
        # Executar análise pós-importação
        analysis = analytics_storage.get_log_info()
        
        # Sugerir compactação se necessário
        post_import_suggestions = []
        if analysis.get("needs_compaction", False):
            score = analysis.get("compaction_score", 0)
            post_import_suggestions.append(f"⚠️ Recomenda-se compactação (Score: {score})")
            
            if score > 70:
                post_import_suggestions.append("🔴 URGENTE: Execute compactação imediatamente")
        
        # Análise de qualidade dos dados importados
        event_types = analysis.get("event_types", {})
        total_events = len(valid_events)
        
        if event_types:
            most_common = max(event_types, key=event_types.get)
            post_import_suggestions.append(f"📊 Tipo mais comum: {most_common} ({event_types[most_common]} eventos)")
        
        result = {
            "success": True,
            "message": f"Dados importados com sucesso!",
            "import_summary": {
                "total_in_file": len(imported_data),
                "valid_events": len(valid_events),
                "invalid_events": invalid_events,
                "backup_created": backup_created,
                "file_size_kb": round(len(file_content) / 1024, 2)
            },
            "post_import_analysis": {
                "compaction_score": analysis.get("compaction_score", 0),
                "needs_compaction": analysis.get("needs_compaction", False),
                "estimated_reduction": analysis.get("estimated_reduction", "0%"),
                "file_size_after_import": analysis.get("file_size_kb", 0),
                "event_count": total_events,
                "oldest_event": analysis.get("oldest_event"),
                "newest_event": analysis.get("newest_event")
            },
            "suggestions": post_import_suggestions
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao importar dados: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao importar dados: {str(e)}")
