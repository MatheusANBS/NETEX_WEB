from collections import Counter

def agrupar_cortes(cortes):
    contagem = Counter(cortes)
    return [(t, q) for t, q in contagem.items()]

def agrupar_resultados(lista):
    agrupados = {}
    for qtd, cortes, desperdicio in lista:
        chave = tuple(sorted(cortes.items()))
        if chave not in agrupados:
            agrupados[chave] = [0, cortes, desperdicio, 0]
        agrupados[chave][0] += qtd
        agrupados[chave][3] += desperdicio
    return [(v[0], v[1], v[2]) for v in agrupados.values()]

def gerar_barras_ideais(cortes_restantes, comprimento_padrao=6000):
    comprimento_real = comprimento_padrao + 5  # Adiciona 5mm à barra comercial
    cortes = sorted(cortes_restantes, reverse=True)
    barras_ideais = []
    for corte in cortes:
        melhor_barra = None
        menor_sobra = None
        for barra in barras_ideais:
            ocupacao = sum(barra) + 5 * max(len(barra) - 1, 0)  # Folga só entre cortes
            folga_extra = 5 if barra else 0  # Folga só se já houver cortes na barra
            if ocupacao + corte + folga_extra <= comprimento_real:
                sobra = comprimento_real - (ocupacao + corte + folga_extra)
                if menor_sobra is None or sobra < menor_sobra:
                    melhor_barra = barra
                    menor_sobra = sobra
        if melhor_barra is not None:
            melhor_barra.append(corte)
        else:
            barras_ideais.append([corte])
    barras_ordenadas = []
    for i, barra in enumerate(barras_ideais):
        ocupacao = sum(barra) + 5 * max(len(barra) - 1, 0)
        if i == len(barras_ideais) - 1 and ocupacao < comprimento_real * 0.8:
            comprimento_ideal = ocupacao
        else:
            comprimento_ideal = comprimento_real
        barras_ordenadas.append((barra, comprimento_ideal))
    return barras_ordenadas

def resolver_com_barras_livres(cortes, comprimento_barra, gerar_resultado_func):
    lista_cortes = []
    invalidos = 0
    for t, q in cortes:
        if t > comprimento_barra:
            invalidos += q
            continue
        lista_cortes.extend([t] * q)
    cortes_grandes = [c for c in lista_cortes if c > 3000]
    cortes_pequenos = [c for c in lista_cortes if c <= 3000]
    cortes_grandes.sort(reverse=True)
    cortes_pequenos.sort(reverse=True)
    barras = []
    def tentar_colocar(corte):
        for barra in barras:
            ocupacao = sum(barra) + 5 * len(barra)
            if ocupacao + corte + 5 <= comprimento_barra:
                barra.append(corte)
                return True
        return False
    for corte in cortes_grandes:
        if not tentar_colocar(corte):
            barras.append([corte])
    for corte in cortes_pequenos:
        if not tentar_colocar(corte):
            barras.append([corte])
    return gerar_resultado_func(barras, comprimento_barra + 5, invalidos)

def resolver_com_barras_fixas(cortes, barras_disponiveis, gerar_resultado_com_barras_fixas_func, modo_emenda_var=None, sugerir_emendas_func=None):
    lista_cortes = []
    for t, q in cortes:
        lista_cortes.extend([t] * q)
    lista_cortes.sort(reverse=True)
    barras = [[] for _ in barras_disponiveis]
    ocupacoes = [0] * len(barras_disponiveis)
    sobras = []
    for corte in lista_cortes:
        indices_ordenados = sorted(
            range(len(barras_disponiveis)),
            key=lambda i: (barras_disponiveis[i] + 5) - (ocupacoes[i] + 5 * len(barras[i]))
        )
        colocado = False
        for i in indices_ordenados:
            comprimento = barras_disponiveis[i]
            ocupacao = ocupacoes[i] + 5 * len(barras[i])
            if ocupacao + corte + 5 <= comprimento + 5:
                barras[i].append(corte)
                ocupacoes[i] += corte
                colocado = True
                break
        if not colocado:
            sobras.append(corte)
    if sobras:
        sobras_restantes = []
        for corte in sobras:
            encaixado = False
            for i, barra in enumerate(barras):
                if not barra:
                    continue
                ocupacao = ocupacoes[i] + 5 * len(barra)
                sobra = (barras_disponiveis[i] + 5) - (ocupacao + corte + 5)
                if 0 > sobra >= -5:
                    barras_disponiveis[i] += abs(sobra)
                    barras[i].append(corte)
                    ocupacoes[i] += corte
                    encaixado = True
                    break
            if not encaixado:
                sobras_restantes.append(corte)
        sobras = sobras_restantes
    if sobras:
        relatorio = gerar_resultado_com_barras_fixas_func(barras, [b + 5 for b in barras_disponiveis])
        relatorio += "\n\nBarras insuficientes para todos os cortes."
        relatorio += f"\nFaltam {len(sobras)} corte(s) para serem alocados."
        barras_ideais = gerar_barras_ideais(sobras, comprimento_padrao=6000)
        relatorio += "\n  Sugestão de novas barras ideias para os cortes restantes   \n"
        for i, (barra, comprimento_ideal) in enumerate(barras_ideais, 1):
            sobra = max(comprimento_ideal - (sum(barra) + 5 * len(barra)), 0)
            cortes_contados = Counter(f"{c}mm" for c in barra)
            relatorio += f"  • Nova barra {i}: {int(comprimento_ideal)}mm ("
            relatorio += ", ".join(f"{q}x {c}" for c, q in cortes_contados.items()) + f") | Sobra: {sobra}mm\n"
        cortes_nao_alocados = list(sobras)
        sobras_barras_utilizadas = []
        barras_utilizadas = []
        for i, barra in enumerate(barras):
            if barra:
                ocupacao = sum(barra) + 5 * len(barra)
                sobra = (barras_disponiveis[i] + 5) - ocupacao
                sobras_barras_utilizadas.append(sobra)
                barras_utilizadas.append(barras_disponiveis[i])
        # NOVO: calcula barras não utilizadas
        barras_nao_utilizadas = [b for b in barras_disponiveis if b not in barras_utilizadas]
        if modo_emenda_var is not None and modo_emenda_var.get() and sugerir_emendas_func is not None:
            relatorio += sugerir_emendas_func(
                sobras_barras_utilizadas,
                cortes_nao_alocados,
                barras_nao_utilizadas=barras_nao_utilizadas
            )
        return relatorio
    return gerar_resultado_com_barras_fixas_func(barras, [b + 5 for b in barras_disponiveis])

def sugerir_emendas_baseado_nas_sobras(sobras_barras, cortes_nao_alocados, barras_nao_utilizadas=None, minimo_emenda=100):
    """
    Tenta sugerir emendas usando:
    1. Apenas sobras das barras já utilizadas
    2. Apenas barras não utilizadas (se fornecidas)
    3. Um mix das duas fontes
    """
    if not cortes_nao_alocados or (not sobras_barras and not barras_nao_utilizadas):
        return ""

    texto = "\nSugestão de Emendas para Cortes Não Alocados:\n"

    def tentar_emendar(cortes, fontes):
        sobras_disponiveis = sorted([s for s in fontes if s >= minimo_emenda], reverse=True)
        resultado = []
        cortes_faltando = []
        for corte in cortes:
            emenda = []
            corte_restante = corte
            sobras_usadas = []
            for sobra in sobras_disponiveis:
                if sobra >= minimo_emenda and corte_restante > 0:
                    pedaco = min(sobra, corte_restante)
                    if pedaco >= minimo_emenda:
                        emenda.append(pedaco)
                        corte_restante -= pedaco
                        sobras_usadas.append(sobra)
                if corte_restante <= 0:
                    break
            if corte_restante <= 0:
                sobra_total_barras_usadas = sum(sobras_usadas)
                sobra_emenda = sobra_total_barras_usadas - corte
                resultado.append((corte, emenda, sobra_emenda, True))
                for s in sobras_usadas:
                    sobras_disponiveis.remove(s)
            else:
                resultado.append((corte, emenda, 0, False))
                cortes_faltando.append(corte)
        return resultado, cortes_faltando

    # 1. Tenta só com as sobras das barras já utilizadas
    resultado1, faltando1 = tentar_emendar(cortes_nao_alocados, sobras_barras)
    if not faltando1:
        for corte, emenda, sobra_emenda, ok in resultado1:
            if ok:
                texto += f" • {corte}mm → {' + '.join(str(p) + 'mm' for p in emenda)} (sobra: {sobra_emenda}mm)\n"
            else:
                texto += f" • {corte}mm → Não foi possível emendar totalmente nas sobras\n"
        texto += "(Usando apenas sobras das barras já utilizadas)\n"
        return texto

    # 2. Se não conseguiu, tenta só com barras não utilizadas (se fornecidas)
    if barras_nao_utilizadas:
        resultado2, faltando2 = tentar_emendar(cortes_nao_alocados, barras_nao_utilizadas)
        if not faltando2:
            for corte, emenda, sobra_emenda, ok in resultado2:
                if ok:
                    texto += f" • {corte}mm → {' + '.join(str(p) + 'mm' for p in emenda)} (sobra: {sobra_emenda}mm)\n"
                else:
                    texto += f" • {corte}mm → Não foi possível emendar totalmente nas barras não utilizadas\n"
            texto += "(Usando apenas barras não utilizadas)\n"
            return texto

    # 3. Se ainda não conseguiu, tenta um mix das duas fontes
    fontes_mix = (sobras_barras or []) + (barras_nao_utilizadas or [])
    resultado3, faltando3 = tentar_emendar(cortes_nao_alocados, fontes_mix)
    for corte, emenda, sobra_emenda, ok in resultado3:
        if ok:
            texto += f" • {corte}mm → {' + '.join(str(p) + 'mm' for p in emenda)} (sobra: {sobra_emenda}mm)\n"
        else:
            texto += f" • {corte}mm → Não foi possível emendar totalmente (mesmo usando todas as fontes)\n"
    texto += "(Usando sobras + barras não utilizadas)\n"
    return texto