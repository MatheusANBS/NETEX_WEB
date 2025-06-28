from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
import base64

from app.routers import cortes, relatorios

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

def get_base64_image(image_path):
    """Converte imagem para base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return ""

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Página principal"""
    logo_base64 = get_base64_image("app/static/images/IconeLogo.png")
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "logo_base64": logo_base64,
        "projetos": [
            "P31-CAM", "P51-CAM", "P51-PAR", "P52-ACO", "P52-CAM", "P53-CAM",
            "P54-CAM", "P54-PAR", "P55-ACO", "P62-ACO", "P62-CAM", "P62-PAR", "PRA-1"
        ]
    })

@app.get("/health")
async def health_check():
    """Health check para monitoramento"""
    return {"status": "ok", "message": "Corteus API funcionando"}

@app.get("/debug", response_class=HTMLResponse)
async def debug_page(request: Request):
    """Página de debug"""
    return templates.TemplateResponse("debug.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
