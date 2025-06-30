from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import base64
from decouple import config

from app.routers import cortes, relatorios, analytics

app = FastAPI(
    title="Corteus - Gestor de Cortes",
    description="Sistema de otimização de cortes para manufatura",
    version="2.0.0"
)

# Configurar arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Incluir routers
app.include_router(cortes.router, prefix="/api", tags=["cortes"])
app.include_router(relatorios.router, prefix="/api", tags=["relatorios"])
# Analytics router sem prefixo para aceitar tanto /track quanto /analytics-data
app.include_router(analytics.router, tags=["analytics"])

def get_base64_image(image_path):
    """Converte imagem para base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return ""

@app.get("/", response_class=HTMLResponse)
@app.head("/")
async def read_root(request: Request):
    """Página principal"""
    # Para requisições HEAD, retorna apenas os headers (para UptimeRobot)
    if request.method == "HEAD":
        return HTMLResponse("")
    
    logo_base64 = get_base64_image("app/static/images/IconeLogo.png")
    admin_password = config("ADMIN_PASSWORD", default="admin123")  # Senha padrão se não estiver definida
    
    # Verificar se há parâmetro de acesso negado
    access_denied = request.query_params.get('access_denied') == 'true'
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "logo_base64": logo_base64,
        "admin_password": admin_password,
        "projetos": [
            "P31-CAM", "P40-CAM", "P40-PAR" ,"P51-CAM", "P51-PAR", "P52-ACO", "P52-CAM", "P53-CAM",
            "P54-CAM", "P54-PAR", "P55-ACO", "P62-ACO", "P62-CAM", "P62-PAR", "PRA-1"
        ],
        "access_denied": access_denied,
        "access_denied_message": "⚠️ Acesso negado ao Dashboard. Faça login como administrador primeiro." if access_denied else None
    })

@app.get("/health")
@app.head("/health")
async def health_check():
    """Health check para monitoramento"""
    return {"status": "ok", "message": "Corteus API funcionando"}

@app.get("/debug", response_class=HTMLResponse)
async def debug_page(request: Request):
    """Página de debug"""
    return templates.TemplateResponse("debug.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def analytics_dashboard(request: Request):
    """Dashboard de Analytics - Requer autenticação de admin"""
    
    # Verificar se o usuário está autenticado como admin
    # O frontend define 'corteus_admin_mode=true' quando autenticado
    admin_auth = request.cookies.get('corteus_admin_mode')
    
    # Se não estiver autenticado, redirecionar para a página principal com mensagem de erro
    if admin_auth != 'true':
        # Retornar erro HTTP 403 ou redirecionar para página principal
        return RedirectResponse(url="/?access_denied=true", status_code=302)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Analytics Dashboard - Corteus"
    })

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
