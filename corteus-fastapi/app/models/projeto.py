from pydantic import BaseModel, validator
from typing import List, Optional
import datetime

# Importar suas funções de validação
from Modulação.validação import validar_ss, validar_sk, validar_cod_material
from Modulação.utils import parse_entrada

class ProjetoRequest(BaseModel):
    projeto: str
    ss: str
    sk: str
    cod_material: str
    modo: str  # "Automático" ou "Manual"
    sugestao_emenda: bool = True
    comprimento_barra: Optional[int] = None
    barras_disponiveis: Optional[List[int]] = None
    cortes_desejados: List[int]

    @validator('ss')
    def validar_ss_field(cls, v):
        if not v:
            raise ValueError('SS é obrigatório')
        
        if not validar_ss(v):
            raise ValueError('SS deve ter o formato 0123/2024')
        
        # Validar ano
        ano_ss = int(v.split("/")[-1])
        ano_atual = datetime.datetime.now().year
        ano_min = ano_atual - 1
        ano_max = ano_atual + 4
        
        if not (ano_min <= ano_ss <= ano_max):
            raise ValueError(f'O ano da SS deve estar entre {ano_min} e {ano_max}')
        
        return v

    @validator('sk')
    def validar_sk_field(cls, v):
        if not v:
            raise ValueError('SK é obrigatório')
        
        if not validar_sk(v.upper()):
            raise ValueError('SK deve ter o formato EST-001')
        
        return v.upper()

    @validator('cod_material')
    def validar_cod_material_field(cls, v):
        if not v:
            raise ValueError('Código do material é obrigatório')
        
        if not validar_cod_material(v):
            raise ValueError('Código do material deve ter exatamente 10 dígitos')
        
        return v

    @validator('cortes_desejados')
    def validar_cortes(cls, v):
        if not v:
            raise ValueError('Cortes desejados são obrigatórios')
        
        if any(c <= 0 for c in v):
            raise ValueError('Todos os cortes devem ser maiores que zero')
        
        return v

class CorteResponse(BaseModel):
    sucesso: bool
    resultado: Optional[str] = None
    nome_arquivo: Optional[str] = None
    erro: Optional[str] = None

class MinutaRequest(BaseModel):
    ss: str
    sk: str
    cod_material: str
    projeto: str
    cortes_desejados: List[int]

    @validator('cortes_desejados')
    def validar_cortes_minuta(cls, v):
        if any(c > 6000 for c in v):
            raise ValueError('Não é possível gerar minuta com cortes maiores que 6000mm')
        return v
