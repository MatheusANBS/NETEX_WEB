from collections import Counter

def gerar_resultado_com_barras_fixas(
    barras, comprimentos, invalidos=0, ss="", sk="", cod_material="", modo_var=1, comprimento_barra=None
):
    resultado = []
    desperdicio_total = 0
    for i, barra in enumerate(barras):
        if not barra:
            continue
        cortes_por_barra = Counter(barra)
        ocupacao = sum(barra) + 5 * len(barra)
        desperdicio = comprimentos[i] - ocupacao
        resultado.append((1, cortes_por_barra, desperdicio, comprimentos[i]))
        desperdicio_total += desperdicio
    total_usadas = len([b for b in barras if b])
    total_comprimento = sum(comprimentos[i] for i, b in enumerate(barras) if b)
    eficiencia = 100 * (total_comprimento - desperdicio_total) / total_comprimento if total_comprimento else 0
    return formatar_resultado(
        resultado, total_usadas, desperdicio_total, eficiencia, len(comprimentos) - total_usadas, invalidos,
        ss=ss, sk=sk, cod_material=cod_material, modo_var=modo_var, comprimento_barra=comprimento_barra
    )

def gerar_resultado(
    barras, comprimento_barra, invalidos=0, ss="", sk="", cod_material="", modo_var=1
):
    resultado = []
    desperdicio_total = 0
    for barra in barras:
        cortes_por_barra = Counter(barra)
        ocupacao = sum(barra) + 5 * len(barra)
        desperdicio = comprimento_barra - ocupacao
        resultado.append((1, cortes_por_barra, desperdicio, comprimento_barra))
        desperdicio_total += desperdicio
    total_usadas = len(barras)
    total_comprimento = comprimento_barra * total_usadas
    eficiencia = 100 * (total_comprimento - desperdicio_total) / total_comprimento if total_comprimento else 0
    return formatar_resultado(
        resultado, total_usadas, desperdicio_total, eficiencia, 0, invalidos,
        ss=ss, sk=sk, cod_material=cod_material, modo_var=modo_var, comprimento_barra=comprimento_barra
    )

def formatar_resultado(
    barras_final, total_barras, total_desperdicio, eficiencia, restantes=0, invalidos=0,
    ss="", sk="", cod_material="", modo_var=1, comprimento_barra=None
):
    texto = ""
    if invalidos:
        texto += f"CORTES_INVÁLIDOS:{invalidos}\n"
    texto += "\nRELATÓRIO DE CORTES\n"
    texto += f"SS: {ss}   SK: {sk}   Material: {cod_material}\n"
    if modo_var == 1 and comprimento_barra:
        texto += f"Comprimento da barra: {comprimento_barra} mm\n"
    for idx, (qtd, cortes, desperdicio, comprimento_barra) in enumerate(barras_final, 1):
        if modo_var == 2:
            texto += f"\nBarra {idx} ({comprimento_barra} mm):\n"
        else:
            texto += f"\nBarra {idx}:\n"
        for corte, q in cortes.items():
            texto += f" • {q}x {corte} mm\n"
        texto += f" • Sobra: {desperdicio} mm\n"
    texto += "\nResumo Final\n"
    texto += f"• Barras utilizadas: {total_barras}\n"
    if restantes:
        texto += f"• Barras restantes: {restantes}\n"
    texto += f"• Sobra total: {total_desperdicio} mm\n"
    texto += f"• Eficiência global: {eficiencia:.2f}%\n"
    return texto

def gerar_texto_minuta_para_pdf(cortes, ss, sk, cod_material):
    if not cortes or any(c > 6000 for c in cortes):
        return ""
    from Modulação.cortes import gerar_barras_ideais
    barras_ideais_6 = gerar_barras_ideais(cortes, comprimento_padrao=6000)
    barras_usadas_6 = len(barras_ideais_6)
    total_rm_6 = barras_usadas_6 * 6000
    desperdicio_6 = sum(6000 - (sum(barra) + 5 * max(len(barra) - 1, 0)) for barra, _ in barras_ideais_6)
    eficiencia_6 = 100 * (total_rm_6 - desperdicio_6) / total_rm_6 if total_rm_6 else 0
    eficiencia_6 = min(eficiencia_6, 100)

    barras_ideais_12 = gerar_barras_ideais(cortes, comprimento_padrao=12000)
    barras_usadas_12 = len(barras_ideais_12)
    total_rm_12 = barras_usadas_12 * 12000
    desperdicio_12 = sum(12000 - (sum(barra) + 5 * max(len(barra) - 1, 0)) for barra, _ in barras_ideais_12)
    eficiencia_12 = 100 * (total_rm_12 - desperdicio_12) / total_rm_12 if total_rm_12 else 0
    eficiencia_12 = min(eficiencia_12, 100)

    relatorio = (
        "\nRELATÓRIO DE MINUTA\n"
        f"SS: {ss}   SK: {sk}   Material: {cod_material}\n"
        f"Total a ser Minutado: {sum(cortes)} mm\n"
    )

    # Bloco RM 6000mm
    relatorio += (
        "\nRM COM BARRA DE 6000mm\n"
        f"Barras comerciais sugeridas: {barras_usadas_6}\n"
        f"Total da RM: {total_rm_6} mm\n"
        f"Eficiência: {eficiencia_6:.2f}%\n"
        f"\nSugestão de barras para a RM (6000mm):\n"
    )
    for i, (barra, _) in enumerate(barras_ideais_6, 1):
        cortes_contados = Counter(f"{c}mm" for c in barra)
        sobra = 6000 - (sum(barra) + 5 * max(len(barra) - 1, 0))
        sobra = max(sobra, 0)
        relatorio += f"Barra {i} (6000 mm):\n"
        for c, q in cortes_contados.items():
            relatorio += f" • {q}x {c}\n"
        relatorio += f" • Sobra: {sobra} mm\n"

    # Bloco RM 12000mm
    relatorio += (
        "\nRM COM BARRA DE 12000mm\n"
        f"Barras comerciais sugeridas: {barras_usadas_12}\n"
        f"Total da RM: {total_rm_12} mm\n"
        f"Eficiência: {eficiencia_12:.2f}%\n"
        f"\nSugestão de barras para a RM (12000mm):\n"
    )
    for i, (barra, _) in enumerate(barras_ideais_12, 1):
        cortes_contados = Counter(f"{c}mm" for c in barra)
        sobra = 12000 - (sum(barra) + 5 * max(len(barra) - 1, 0))
        sobra = max(sobra, 0)
        relatorio += f"Barra {i} (12000 mm):\n"
        for c, q in cortes_contados.items():
            relatorio += f" • {q}x {c}\n"
        relatorio += f" • Sobra: {sobra} mm\n"

    return relatorio