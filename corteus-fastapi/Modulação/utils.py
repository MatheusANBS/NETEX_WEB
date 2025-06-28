import re

def parse_entrada(texto):
    partes = re.split(r'[\s,]+', texto.strip())
    return [int(p) for p in partes if p.isdigit()]