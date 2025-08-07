from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.projeto import ProjetoRequest, CorteResponse
from app.services.corte_service import CorteService
import os
import tempfile

router = APIRouter()
corte_service = CorteService()

# Dicionário para armazenar caminhos temporários dos PDFs
temp_files = {}

@router.post("/cortes/gerar", response_model=CorteResponse)
async def gerar_corte(request: ProjetoRequest):
    """Gera relatório de corte (automático ou manual)"""
    print(f"Recebido request: {request}")
    
    try:
        if request.modo == "Automático":
            if not request.comprimento_barra:
                raise HTTPException(status_code=400, detail="Comprimento da barra é obrigatório no modo automático")
            
            caminho_pdf, nome_arquivo = corte_service.processar_corte_automatico(
                request.cortes_desejados,
                request.comprimento_barra,
                request.ss,
                request.sk,
                request.cod_material,
                request.projeto
            )
        else:
            if not request.barras_disponiveis:
                raise HTTPException(status_code=400, detail="Barras disponíveis são obrigatórias no modo manual")
            
            caminho_pdf, nome_arquivo = corte_service.processar_corte_manual(
                request.cortes_desejados,
                request.barras_disponiveis,
                request.sugestao_emenda,
                request.ss,
                request.sk,
                request.cod_material,
                request.projeto
            )
        
        print(f"Resultado: caminho={caminho_pdf}, nome={nome_arquivo}")
        
        # Armazenar o caminho temporário
        temp_files[nome_arquivo] = caminho_pdf
        
        return CorteResponse(
            sucesso=True,
            resultado="Relatório gerado com sucesso",
            nome_arquivo=nome_arquivo
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cortes/download/{nome_arquivo}")
async def download_corte(nome_arquivo: str):
    """Download do PDF gerado"""
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

@router.get("/cortes/preview/{nome_arquivo}")
async def preview_corte(nome_arquivo: str):
    """Preview do PDF gerado no navegador"""
    if nome_arquivo not in temp_files:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    caminho_pdf = temp_files[nome_arquivo]
    
    if not os.path.exists(caminho_pdf):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no sistema")
    
    return FileResponse(
        path=caminho_pdf,
        media_type='application/pdf',
        headers={"Content-Disposition": "inline"}
    )
