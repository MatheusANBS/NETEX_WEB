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
    try:
        from app.services.material_service import material_service
        # Primeiro verifica o formato
        if not validar_cod_material(cod):
            return False
        # Depois verifica se existe na base
        return material_service.validar_codigo_material(cod)
    except:
        # Se não conseguir importar o serviço, usa apenas validação de formato
        return validar_cod_material(cod)