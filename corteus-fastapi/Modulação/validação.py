import re

def validar_ss(ss):
    return bool(re.fullmatch(r"\d{4}P?/\d{4}", ss))

def validar_sk(sk):
    return bool(re.fullmatch(r"(EST|TU)-\d{3}", sk))

def validar_cod_material(cod):
    """Validação básica de formato do código do material"""
    return cod.isdigit() and len(cod) == 10

def validar_cod_material_com_base(cod):
    """Validação completa usando a base de dados de materiais"""
    # Primeiro verifica o formato básico
    if not validar_cod_material(cod):
        return False
    
    try:
        from app.services.material_service import material_service
        # Se não há materiais carregados, usa validação básica
        if not material_service.materiais_db:
            print("Base de materiais vazia, usando validação básica")
            return True
        # Verifica se existe na base
        return material_service.validar_codigo_material(cod)
    except Exception as e:
        print(f"Erro na validação com base: {e}")
        # Se não conseguir importar o serviço ou houver erro, usa apenas validação básica
        return True  # Permite passar para não bloquear usuário