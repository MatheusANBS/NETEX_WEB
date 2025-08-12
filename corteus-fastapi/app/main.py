from fastapi import FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
import os
import base64
import hashlib
from decouple import config

from app.routers import cortes, relatorios, analytics, materiais
from app.auth import auth_manager

app = FastAPI(
    title="Corteus - Gestor de Cortes",
    description="Sistema de otimização de cortes para manufatura",
    version="2.0.0"
)

#oi

# Configurar arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Incluir routers
app.include_router(cortes.router, prefix="/api", tags=["cortes"])
app.include_router(relatorios.router, prefix="/api", tags=["relatorios"])
app.include_router(materiais.router, prefix="/api", tags=["materiais"])
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
    
    # Verificar se há erro de login
    login_error = request.query_params.get('login_error') == 'true'
    error_message = request.query_params.get('message', 'Erro de autenticação')
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "logo_base64": logo_base64,
        "admin_password": admin_password,
        "projetos": [
            "P31-CAM", "P40-CAM", "P40-PAR" ,"P51-CAM", "P51-PAR", "P52-ACO", "P52-CAM", "P53-CAM",
            "P54-CAM", "P54-PAR", "P55-ACO", "P62-ACO", "P62-CAM", "P62-PAR", "PRA-1"
        ],
        "access_denied": access_denied,
        "access_denied_message": "⚠️ Acesso negado ao Dashboard. Faça login como administrador primeiro." if access_denied else None,
        "login_error": login_error,
        "login_error_message": f"❌ {error_message}" if login_error else None
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

@app.post("/admin/login")
async def admin_login(request: Request):
    """Endpoint para login do administrador"""
    try:
        # Obter dados do formulário
        form_data = await request.form()
        provided_password_hash = form_data.get("password_hash", "")
        
        # Obter senha do admin das configurações e fazer hash
        admin_password = config("ADMIN_PASSWORD", default="admin123")
        import hashlib
        expected_hash = hashlib.sha256(admin_password.encode()).hexdigest()
        
        # Comparar hashes (proteção contra senha em logs)
        if provided_password_hash != expected_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas"
            )
        
        # Criar token JWT usando senha original (só para criação do token)
        token = auth_manager.create_admin_token(admin_password, admin_password)
        
        # Criar resposta de redirecionamento para o dashboard
        response = RedirectResponse(url="/dashboard", status_code=302)
        
        # Detectar se está em produção (Render)
        is_production = os.environ.get("RENDER") == "true" or request.url.scheme == "https"
        
        # Definir cookie seguro com o token JWT
        response.set_cookie(
            key="corteus_admin_token",
            value=token,
            httponly=True,  # Impede acesso via JavaScript
            secure=is_production,  # True em produção (HTTPS), False em desenvolvimento (HTTP)
            samesite="lax", # Proteção CSRF
            max_age=86400   # 24 horas em segundos
        )
        
        return response
        
    except HTTPException as e:
        # Senha incorreta ou outro erro de autenticação
        return RedirectResponse(
            url=f"/?login_error=true&message={e.detail}", 
            status_code=302
        )
    except Exception as e:
        # Erro interno do servidor
        return RedirectResponse(
            url="/?login_error=true&message=Erro interno do servidor", 
            status_code=302
        )

@app.post("/admin/logout")
async def admin_logout():
    """Endpoint para logout do administrador"""
    response = RedirectResponse(url="/", status_code=302)
    
    # Detectar se está em produção
    is_production = os.environ.get("RENDER") == "true"
    
    # Remover cookie de autenticação
    response.delete_cookie(
        key="corteus_admin_token",
        httponly=True,
        secure=is_production,  # True em produção, False em desenvolvimento
        samesite="lax"
    )
    
    return response

@app.get("/dashboard", response_class=HTMLResponse)
@app.head("/dashboard")
async def analytics_dashboard(request: Request):
    """Dashboard de Analytics - Requer autenticação de admin"""
    
    # Verificar se o usuário está autenticado como admin usando JWT
    if not auth_manager.is_admin_authenticated(request):
        # Para requisições HEAD, retornar status 401
        if request.method == "HEAD":
            raise HTTPException(status_code=401, detail="Não autenticado")
        
        # Para requisições GET, redirecionar para a página principal com mensagem de erro
        return RedirectResponse(url="/?access_denied=true", status_code=302)
    
    # Para requisições HEAD, retornar apenas status 200
    if request.method == "HEAD":
        return HTMLResponse("")
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Analytics Dashboard - Corteus"
    })

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
