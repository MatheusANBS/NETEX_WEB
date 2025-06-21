import re

def validar_ss(ss):
    return bool(re.fullmatch(r"\d{4}P?/\d{4}", ss))

def validar_sk(sk):
    return bool(re.fullmatch(r"(EST|TU)-\d{3}", sk))

def validar_cod_material(cod):
    return cod.isdigit() and len(cod) == 10