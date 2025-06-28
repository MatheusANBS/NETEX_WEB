from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.projeto import MinutaRequest, CorteResponse
from app.services.corte_service import CorteService
import os

router = APIRouter()
corte_service = CorteService()

# Dicionário para armazenar caminhos temporários dos PDFs
temp_files = {}

@router.post("/minuta/gerar", response_model=CorteResponse)
async def gerar_minuta(request: MinutaRequest):
    """Gera relatório de minuta"""
    try:
        caminho_pdf, nome_arquivo = corte_service.gerar_minuta(
            request.cortes_desejados,
            request.ss,
            request.sk,
            request.cod_material,
            request.projeto
        )
        
        # Armazenar o caminho temporário
        temp_files[nome_arquivo] = caminho_pdf
        
        return CorteResponse(
            sucesso=True,
            resultado="Relatório de minuta gerado com sucesso",
            nome_arquivo=nome_arquivo
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/minuta/download/{nome_arquivo}")
async def download_minuta(nome_arquivo: str):
    """Download do PDF de minuta"""
    if nome_arquivo not in temp_files:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    caminho_pdf = temp_files[nome_arquivo]
    
    if not os.path.exists(caminho_pdf):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no sistema")
    
    return FileResponse(
        path=caminho_pdf,
        filename=nome_arquivo,
        media_type='application/pdf'
    )
