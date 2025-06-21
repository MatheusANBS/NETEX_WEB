import textwrap
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def gerar_pdf(
    caminho, texto_relatorio, campos, titulo="RELATÓRIO DE CORTES",
    fonte_normal="TimesNewRoman", fonte_bold="TimesNewRoman"
):
    pdfmetrics.registerFont(TTFont('TimesNewRoman', 'times.ttf'))
    try:
        pdfmetrics.registerFont(TTFont('Calibri', 'calibri.ttf'))
        fonte_calibri = 'Calibri'
    except:
        fonte_calibri = 'Helvetica'

    c = canvas.Canvas(caminho, pagesize=A4)
    largura, altura = A4
    x = 40
    y = altura - 60
    max_width = largura - 2 * x

    tamanho_titulo = 18
    tamanho_subtitulo = 14
    tamanho_normal = 12
    line_height = 18

    linhas = texto_relatorio.splitlines()
    linhas_filtradas = []
    for linha in linhas:
        if (linha.strip().upper() == titulo) or \
           (linha.strip().startswith("SS:") and "SK:" in linha and "Material:" in linha):
            continue
        linhas_filtradas.append(linha)
    linhas = linhas_filtradas

    c.rect(30, 30, largura - 60, altura - 60, stroke=1, fill=0)
    numero_pagina = c.getPageNumber()
    texto_pagina = f"Página {numero_pagina}"
    c.setFont(fonte_normal, 10)
    largura_texto = stringWidth(texto_pagina, fonte_normal, 10)
    c.drawString((largura - largura_texto) / 2, 15, texto_pagina)

    caixa_altura = 22
    caixa_largura = 130
    margem = 30
    num_caixas = 4
    largura_util = largura - 2 * margem
    espacamento_caixas = (largura_util - num_caixas * caixa_largura) / (num_caixas - 1)
    x_caixa = margem
    y_caixa = altura - 50

    c.setFont(fonte_normal, 11)
    for rotulo, valor in campos:
        c.roundRect(x_caixa, y_caixa - caixa_altura, caixa_largura, caixa_altura, 5, stroke=1, fill=0)
        c.drawString(x_caixa + 8, y_caixa - caixa_altura + 6, f"{rotulo} {valor}")
        x_caixa += caixa_largura + espacamento_caixas

    y_titulo = y_caixa - caixa_altura - 40
    c.setFont(fonte_bold, tamanho_titulo)
    largura_titulo = stringWidth(titulo, fonte_bold, tamanho_titulo)
    c.drawString((largura - largura_titulo) / 2, y_titulo, titulo)
    y = y_titulo - 2 * line_height

    c.setFont(fonte_normal, tamanho_normal)
    i = 0

    if any(linha.lower().startswith("barra 1") for linha in linhas):
        if y < margem + 60:
            c.showPage()
            c.rect(margem, margem, largura - 2 * margem, altura - 2 * margem, stroke=1, fill=0)
            numero_pagina = c.getPageNumber()
            texto_pagina = f"Página {numero_pagina}"
            c.setFont(fonte_normal, 10)
            largura_texto = stringWidth(texto_pagina, fonte_normal, 10)
            c.drawString((largura - largura_texto) / 2, margem - 15, texto_pagina)
            y = altura - 80
            c.setFont(fonte_normal, tamanho_normal)
        c.setFont(fonte_bold, tamanho_subtitulo)
        c.drawString(x, y, "Cortes Realizados")
        y -= line_height * 1.2
        c.setFont(fonte_normal, tamanho_normal)
    while i < len(linhas):
        linha = linhas[i]

        if linha.lower().startswith("resumo final") or \
           linha.lower().startswith("sugestão de barras") or \
           linha.lower().startswith("sugestão de barras para a rm") or \
           linha.lower().startswith("sugestão de novas barras") or \
           linha.lower().startswith("relatório de minuta"):
            if y < margem + 60:
                c.showPage()
                c.rect(margem, margem, largura - 2 * margem, altura - 2 * margem, stroke=1, fill=0)
                numero_pagina = c.getPageNumber()
                texto_pagina = f"Página {numero_pagina}"
                c.setFont(fonte_normal, 10)
                largura_texto = stringWidth(texto_pagina, fonte_normal, 10)
                c.drawString((largura - largura_texto) / 2, margem - 15, texto_pagina)
                y = altura - 80
                c.setFont(fonte_normal, tamanho_normal)
            y -= line_height
            c.setFont(fonte_bold, tamanho_subtitulo)
            c.drawString(x, y, linha)
            c.setFont(fonte_normal, tamanho_normal)
            y -= line_height
            i += 1
            continue

        if linha == "":
            y -= line_height // 2
            i += 1
            continue

        if linha.strip().startswith("• Nova barra"):
            import re
            match = re.match(r"• Nova barra (\d+): (\d+)mm \((.*?)\) \| Sobra: (.*)", linha.strip())
            if match:
                barra_num = match.group(1)
                barra_comp = match.group(2)
                cortes_str = match.group(3)
                sobra = match.group(4)
                if y < margem + 60:
                    c.showPage()
                    c.rect(margem, margem, largura - 2 * margem, altura - 2 * margem, stroke=1, fill=0)
                    numero_pagina = c.getPageNumber()
                    texto_pagina = f"Página {numero_pagina}"
                    c.setFont(fonte_normal, 10)
                    largura_texto = stringWidth(texto_pagina, fonte_normal, 10)
                    c.drawString((largura - largura_texto) / 2, margem - 15, texto_pagina)
                    y = altura - 80
                    c.setFont(fonte_normal, tamanho_normal)
                c.drawString(x, y, f"• Nova barra {barra_num}: {barra_comp}mm")
                y -= line_height
                cortes_lista = [corte.strip() for corte in cortes_str.split(",")]
                for corte in cortes_lista:
                    if corte:
                        if y < margem + 60:
                            c.showPage()
                            c.rect(margem, margem, largura - 2 * margem, altura - 2 * margem, stroke=1, fill=0)
                            numero_pagina = c.getPageNumber()
                            texto_pagina = f"Página {numero_pagina}"
                            c.setFont(fonte_normal, 10)
                            largura_texto = stringWidth(texto_pagina, fonte_normal, 10)
                            c.drawString((largura - largura_texto) / 2, margem - 15, texto_pagina)
                            y = altura - 80
                            c.setFont(fonte_normal, tamanho_normal)
                        c.drawString(x + 20, y, f"• {corte}")
                        y -= line_height
                if y < margem + 60:
                    c.showPage()
                    c.rect(margem, margem, largura - 2 * margem, altura - 2 * margem, stroke=1, fill=0)
                    numero_pagina = c.getPageNumber()
                    texto_pagina = f"Página {numero_pagina}"
                    c.setFont(fonte_normal, 10)
                    largura_texto = stringWidth(texto_pagina, fonte_normal, 10)
                    c.drawString((largura - largura_texto) / 2, margem - 15, texto_pagina)
                    y = altura - 80
                    c.setFont(fonte_normal, tamanho_normal)
                c.drawString(x + 20, y, f"• Sobra: {sobra}")
                y -= line_height * 1.2
                i += 1
                continue

        for sublinha in textwrap.wrap(linha, width=110):
            if y < margem + 60:
                c.showPage()
                c.rect(margem, margem, largura - 2 * margem, altura - 2 * margem, stroke=1, fill=0)
                numero_pagina = c.getPageNumber()
                texto_pagina = f"Página {numero_pagina}"
                c.setFont(fonte_normal, 10)
                largura_texto = stringWidth(texto_pagina, fonte_normal, 10)
                c.drawString((largura - largura_texto) / 2, margem - 15, texto_pagina)
                y = altura - 80
                c.setFont(fonte_normal, tamanho_normal)
            c.drawString(x, y, sublinha)
            y -= line_height
        i += 1

    numero_pagina = c.getPageNumber()
    texto_pagina = f"Página {numero_pagina}"
    c.setFont(fonte_normal, 10)
    largura_texto = stringWidth(texto_pagina, fonte_normal, 10)
    c.drawString((largura - largura_texto) / 2, margem - 15, texto_pagina)

    c.save()