import csv
import os
from typing import Dict, Optional

class MaterialService:
    def __init__(self):
        self.materiais_db = {}
        self._carregar_materiais()
    
    def _carregar_materiais(self):
        """Carrega a base de dados de materiais do CSV"""
        # Usar caminho relativo ao arquivo atual
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Tentar diferentes caminhos possíveis
        possible_paths = [
            os.path.join(current_dir, '..', '..', 'materiais_unidade_M_descresumida.csv'),  # Pasta raiz do projeto
            os.path.join(current_dir, '..', '..', '..', 'materiais_unidade_M_descresumida.csv'),  # Raiz do workspace
            "./materiais_unidade_M_descresumida.csv",  # Diretório atual da aplicação
            "../materiais_unidade_M_descresumida.csv",  # Um nível acima
            "materiais_unidade_M_descresumida.csv",  # Diretório de execução
        ]
        
        csv_path = None
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                csv_path = abs_path
                break
        
        if not csv_path:
            print(f"Arquivo CSV não encontrado em nenhum dos caminhos: {[os.path.abspath(p) for p in possible_paths]}")
            return
        
        print(f"Carregando materiais de: {csv_path}")
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    codigo = row['Código'].strip('"')
                    descricao = row['Descrição Resumida'].strip('"')
                    self.materiais_db[codigo] = descricao
            
            print(f"Carregados {len(self.materiais_db)} materiais da base de dados")
            
        except Exception as e:
            print(f"Erro ao carregar materiais: {e}")
            print("Continuando sem base de materiais (validação básica)")
    
    def validar_codigo_material(self, codigo: str) -> bool:
        """Valida se o código do material existe na base de dados"""
        if not self.materiais_db:
            print("Base de materiais não carregada, retornando True")
            return True
        return codigo in self.materiais_db
    
    def obter_descricao_material(self, codigo: str) -> Optional[str]:
        """Obtém a descrição do material pelo código"""
        return self.materiais_db.get(codigo)
    
    def buscar_materiais(self, termo: str, limite: int = 10) -> Dict[str, str]:
        """Busca materiais por termo (código ou descrição)"""
        termo = termo.lower()
        resultados = {}
        
        for codigo, descricao in self.materiais_db.items():
            if (termo in codigo.lower() or 
                termo in descricao.lower()) and len(resultados) < limite:
                resultados[codigo] = descricao
        
        return resultados
    
    def obter_todos_codigos(self) -> list:
        """Retorna todos os códigos de materiais disponíveis"""
        return list(self.materiais_db.keys())

# Instância global do serviço
material_service = MaterialService()
