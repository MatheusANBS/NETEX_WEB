import tempfile
import os
from typing import List, Tuple

# Importar suas funções existentes da pasta Modulação
from Modulação.cortes import (
    agrupar_cortes,
    resolver_com_barras_livres,
    resolver_com_barras_fixas,
    sugerir_emendas_baseado_nas_sobras
)
from Modulação.formatacao import (
    gerar_resultado,
    gerar_resultado_com_barras_fixas,
    gerar_texto_minuta_para_pdf
)
from Modulação.pdf_utils import gerar_pdf as gerar_pdf_func
from Modulação.utils import parse_entrada
from app.services.material_service import material_service

class FakeVar:
    def __init__(self, value):
        self.value = value
    def get(self):
        return self.value

class CorteService:
    def __init__(self):
        pass

    def processar_corte_automatico(
        self, 
        cortes: List[int], 
        comprimento_barra: int,
        ss: str,
        sk: str, 
        cod_material: str,
        projeto: str
    ) -> Tuple[str, str]:
        """Processa corte no modo automático"""
        
        agrupados = agrupar_cortes(cortes)
        resultado = resolver_com_barras_livres(
            agrupados,
            comprimento_barra,
            lambda barras, comprimento_barra, invalidos: gerar_resultado(
                barras, comprimento_barra, invalidos,
                ss=ss, sk=sk, cod_material=cod_material, modo_var=1
            )
        )
        
        # Gerar PDF
        nome_arquivo = self._gerar_nome_arquivo("RELCRT", cod_material, projeto, ss, sk)
        caminho_pdf = self._gerar_pdf_temporario(resultado, ss, sk, cod_material, projeto, "RELATÓRIO DE CORTES")
        
        return caminho_pdf, nome_arquivo

    def processar_corte_manual(
        self,
        cortes: List[int],
        barras_disponiveis: List[int],
        sugestao_emenda: bool,
        ss: str,
        sk: str,
        cod_material: str,
        projeto: str
    ) -> Tuple[str, str]:
        """Processa corte no modo manual"""
        
        agrupados = agrupar_cortes(cortes)
        if sugestao_emenda:
            resultado = resolver_com_barras_fixas(
                agrupados,
                barras_disponiveis,
                lambda barras, comprimentos, invalidos=0: gerar_resultado_com_barras_fixas(
                    barras, comprimentos, invalidos,
                    ss=ss, sk=sk, cod_material=cod_material, modo_var=2
                ),
                modo_emenda_var=FakeVar(True),
                sugerir_emendas_func=sugerir_emendas_baseado_nas_sobras
            )
        else:
            resultado = resolver_com_barras_fixas(
                agrupados,
                barras_disponiveis,
                lambda barras, comprimentos, invalidos=0: gerar_resultado_com_barras_fixas(
                    barras, comprimentos, invalidos,
                    ss=ss, sk=sk, cod_material=cod_material, modo_var=2
                )
            )
        
        nome_arquivo = self._gerar_nome_arquivo("RELCRT", cod_material, projeto, ss, sk)
        caminho_pdf = self._gerar_pdf_temporario(resultado, ss, sk, cod_material, projeto, "RELATÓRIO DE CORTES")
        
        return caminho_pdf, nome_arquivo

    def gerar_minuta(
        self,
        cortes: List[int],
        ss: str,
        sk: str,
        cod_material: str,
        projeto: str
    ) -> Tuple[str, str]:
        """Gera relatório de minuta"""
        
        texto = gerar_texto_minuta_para_pdf(cortes, ss, sk, cod_material)
        
        nome_arquivo = self._gerar_nome_arquivo("RELMIN", cod_material, projeto, ss, sk)
        caminho_pdf = self._gerar_pdf_temporario(texto, ss, sk, cod_material, projeto, "RELATÓRIO DE MINUTA")
        
        return caminho_pdf, nome_arquivo

    def _gerar_nome_arquivo(self, prefixo: str, cod_material: str, projeto: str, ss: str, sk: str) -> str:
        """Gera nome do arquivo PDF"""
        ultimos4 = cod_material[-4:] if len(cod_material) >= 4 else cod_material
        projeto_nome = projeto.replace("-", "_")
        ss_nome = ss.replace("/", "_")
        sk_nome = sk.replace("-", "_")
        return f"{prefixo}{ultimos4}_{projeto_nome}_SS{ss_nome}_{sk_nome}.pdf"

    def _gerar_pdf_temporario(self, conteudo: str, ss: str, sk: str, cod_material: str, projeto: str, titulo: str) -> str:
        """Gera PDF temporário e retorna o caminho"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp_path = tmp.name

        campos = [
            ("Projeto:", projeto),
            ("SS:", ss),
            ("SK:", sk),
            ("Material:", cod_material)
        ]
        
        # Obter descrição do material
        descricao_material = material_service.obter_descricao_material(cod_material)
        
        gerar_pdf_func(tmp_path, conteudo, campos, titulo=titulo, descricao_material=descricao_material)
        
        return tmp_path
