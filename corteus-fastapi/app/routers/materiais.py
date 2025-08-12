from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Optional
from app.services.material_service import material_service
import os

router = APIRouter()

@router.get("/materiais/status")
async def status_materiais():
    """Status da base de dados de materiais (para debug)"""
    return {
        "total_materiais": len(material_service.materiais_db),
        "status": "carregado" if material_service.materiais_db else "vazio",
        "primeiros_5": dict(list(material_service.materiais_db.items())[:5]) if material_service.materiais_db else {}
    }

@router.get("/materiais/validar/{codigo}")
async def validar_material(codigo: str):
    """Valida se um código de material existe na base de dados"""
    try:
        is_valid = material_service.validar_codigo_material(codigo)
        descricao = material_service.obter_descricao_material(codigo) if is_valid else None
        
        return {
            "codigo": codigo,
            "valido": is_valid,
            "descricao": descricao
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/materiais/buscar")
async def buscar_materiais(
    termo: str = Query(..., min_length=1, description="Termo de busca"),
    limite: int = Query(10, ge=1, le=50, description="Limite de resultados")
):
    """Busca materiais por código ou descrição"""
    try:
        resultados = material_service.buscar_materiais(termo, limite)
        return {
            "termo": termo,
            "total": len(resultados),
            "materiais": resultados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/materiais/descricao/{codigo}")
async def obter_descricao(codigo: str):
    """Obtém a descrição completa de um material"""
    try:
        descricao = material_service.obter_descricao_material(codigo)
        
        if not descricao:
            raise HTTPException(status_code=404, detail="Material não encontrado")
        
        return {
            "codigo": codigo,
            "descricao": descricao
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/materiais/autocomplete")
async def autocomplete_materiais(
    q: str = Query(..., min_length=2, description="Query de busca"),
    limit: int = Query(5, ge=1, le=20, description="Limite de sugestões")
):
    """Endpoint para autocomplete de materiais"""
    try:
        resultados = material_service.buscar_materiais(q, limit)
        
        # Formato otimizado para autocomplete
        sugestoes = [
            {
                "codigo": codigo,
                "descricao": descricao,
                "label": f"{codigo} - {descricao[:50]}{'...' if len(descricao) > 50 else ''}"
            }
            for codigo, descricao in resultados.items()
        ]
        
        return {
            "query": q,
            "suggestions": sugestoes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
