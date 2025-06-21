import sys
import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import scrolledtext, messagebox, filedialog, Toplevel
from collections import Counter
import textwrap

from Modulação.cortes import (
    agrupar_cortes,
    agrupar_resultados,
    gerar_barras_ideais,
    resolver_com_barras_livres,
    resolver_com_barras_fixas,
    sugerir_emendas_baseado_nas_sobras
)
from Modulação.formatacao import (
    gerar_resultado,
    gerar_resultado_com_barras_fixas,
    formatar_resultado,
    gerar_texto_minuta_para_pdf  # <--- ADICIONE ESTA LINHA
)
from Modulação.pdf_utils import gerar_pdf as gerar_pdf_func
from Modulação.utils import parse_entrada
from Modulação.validação import validar_ss, validar_sk, validar_cod_material

def resource_path(relative_path):
    """Retorna o caminho absoluto para recursos, compatível com PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, "..", relative_path)

def mostrar_resultado_otimizacao(root, texto):
    win = Toplevel(root)
    win.title("Resultado da Otimização")
    win.geometry("800x600")
    win.resizable(True, True)
    txt = scrolledtext.ScrolledText(win, font=("Consolas", 11), wrap="word")
    txt.pack(fill="both", expand=True, padx=10, pady=10)
    txt.insert("1.0", texto)
    txt.config(state="disabled")
    tb.Button(win, text="Fechar", command=win.destroy, bootstyle=SECONDARY).pack(pady=10)
    win.grab_set()

def otimizar(
    text_cortes, text_barras, entry_comprimento, modo_var, modo_emenda_var,
    entry_ss, entry_sk, entry_cod_material, combo_projeto, root
):
    cortes_str = text_cortes.get("1.0", "end").strip()
    barras_str = text_barras.get("1.0", "end").strip()
    comprimento_str = entry_comprimento.get().strip()
    ss = entry_ss.get().strip()
    sk = entry_sk.get().strip()
    cod_material = entry_cod_material.get().strip()
    projeto = combo_projeto.get().strip()
    modo = modo_var.get()
    modo_emenda = modo_emenda_var.get()

    if not cortes_str:
        messagebox.showerror("Erro", "Informe os cortes desejados.")
        return

    if modo == 1 and not comprimento_str:
        messagebox.showerror("Erro", "Informe o comprimento da barra padrão.")
        return

    if modo == 2 and not barras_str:
        messagebox.showerror("Erro", "Informe as barras disponíveis no modo manual.")
        return

    try:
        cortes = parse_entrada(cortes_str)
        if not cortes:
            raise ValueError
    except Exception:
        messagebox.showerror("Erro", "Cortes inválidos.")
        return

    agrupados = agrupar_cortes(cortes)

    if modo == 1:
        try:
            comprimento_barra = int(comprimento_str)
        except Exception:
            messagebox.showerror("Erro", "Comprimento da barra inválido.")
            return
        resultado = resolver_com_barras_livres(
            agrupados,
            comprimento_barra,
            lambda barras, comprimento_barra, invalidos: gerar_resultado(
                barras, comprimento_barra, invalidos,
                ss=ss, sk=sk, cod_material=cod_material, modo_var=modo
            )
        )
    else:
        try:
            barras = parse_entrada(barras_str)
            if not barras:
                raise ValueError
        except Exception:
            messagebox.showerror("Erro", "Barras inválidas.")
            return
        resultado = resolver_com_barras_fixas(
            agrupados,
            barras,
            lambda barras, comprimentos, invalidos=0: gerar_resultado_com_barras_fixas(
                barras, comprimentos, invalidos,
                ss=ss, sk=sk, cod_material=cod_material, modo_var=modo
            ),
            modo_emenda_var=modo_emenda_var,
            sugerir_emendas_func=sugerir_emendas_baseado_nas_sobras
        )

    mostrar_resultado_otimizacao(root, resultado)

def gerar_relatorio_minuta(
    text_cortes, entry_ss, entry_sk, entry_cod_material, combo_projeto, root
):
    cortes_str = text_cortes.get("1.0", "end").strip()
    ss = entry_ss.get().strip()
    sk = entry_sk.get().strip()
    cod_material = entry_cod_material.get().strip()
    projeto = combo_projeto.get().strip()

    # Validação básica dos campos obrigatórios
    
    try:
        cortes = parse_entrada(cortes_str)
        if not cortes:
            raise ValueError
    except Exception:
        messagebox.showerror("Erro", "Cortes inválidos.")
        return

    # Não permitir cortes maiores que 6000mm para minuta
    if any(c > 6000 for c in cortes):
        messagebox.showerror("Erro", "Não é possível gerar minuta se houver cortes maiores que 6000mm.")
        return

    texto = gerar_texto_minuta_para_pdf(cortes, ss, sk, cod_material)
    mostrar_resultado_otimizacao(root, texto)

def gerar_pdf(
    text_cortes, text_barras, entry_comprimento, modo_var, modo_emenda_var,
    entry_ss, entry_sk, entry_cod_material, combo_projeto, root
):
    cortes_str = text_cortes.get("1.0", "end").strip()
    barras_str = text_barras.get("1.0", "end").strip()
    comprimento_str = entry_comprimento.get().strip()
    ss = entry_ss.get().strip()
    sk = entry_sk.get().strip()
    cod_material = entry_cod_material.get().strip()
    projeto = combo_projeto.get().strip()
    modo = modo_var.get()
    modo_emenda = modo_emenda_var.get()

    # Validação básica dos campos obrigatórios
    if not (ss and sk and cod_material):
        messagebox.showerror("Erro", "Preencha SS, SK e Código do material para gerar o PDF.")
        return
    if not validar_ss(ss):
        messagebox.showerror("Erro", "SS inválido.")
        return
    if not validar_sk(sk):
        messagebox.showerror("Erro", "SK inválido.")
        return
    if not validar_cod_material(cod_material):
        messagebox.showerror("Erro", "Código do material inválido (deve ter 10 dígitos numéricos).")
        return

    if not cortes_str:
        messagebox.showerror("Erro", "Informe os cortes desejados.")
        return

    if modo == 1 and not comprimento_str:
        messagebox.showerror("Erro", "Informe o comprimento da barra padrão.")
        return

    if modo == 2 and not barras_str:
        messagebox.showerror("Erro", "Informe as barras disponíveis no modo manual.")
        return

    try:
        cortes = parse_entrada(cortes_str)
        if not cortes:
            raise ValueError
    except Exception:
        messagebox.showerror("Erro", "Cortes inválidos.")
        return

    tipo_pdf = perguntar_tipo_pdf(root)
    if tipo_pdf == "minuta":
        # Não permitir cortes maiores que 6000mm para minuta
        if any(c > 6000 for c in cortes):
            messagebox.showerror("Erro", "Não é possível gerar minuta se houver cortes maiores que 6000mm.")
            return
        resultado = gerar_texto_minuta_para_pdf(cortes, ss, sk, cod_material)
        titulo = "RELATÓRIO DE MINUTA"
        prefixo = "RELMIN"
    elif tipo_pdf == "corte":
        agrupados = agrupar_cortes(cortes)
        if modo == 1:
            try:
                comprimento_barra = int(comprimento_str)
            except Exception:
                messagebox.showerror("Erro", "Comprimento da barra inválido.")
                return
            resultado = resolver_com_barras_livres(
                agrupados,
                comprimento_barra,
                lambda barras, comprimento_barra, invalidos: gerar_resultado(
                    barras, comprimento_barra, invalidos,
                    ss=ss, sk=sk, cod_material=cod_material, modo_var=modo
                )
            )
        else:
            try:
                barras = parse_entrada(barras_str)
                if not barras:
                    raise ValueError
            except Exception:
                messagebox.showerror("Erro", "Barras inválidas.")
                return
            resultado = resolver_com_barras_fixas(
                agrupados,
                barras,
                lambda barras, comprimentos, invalidos=0: gerar_resultado_com_barras_fixas(
                    barras, comprimentos, invalidos,
                    ss=ss, sk=sk, cod_material=cod_material, modo_var=modo
                ),
                modo_emenda_var=modo_emenda_var,
                sugerir_emendas_func=sugerir_emendas_baseado_nas_sobras
            )
        titulo = "RELATÓRIO DE CORTES"
        prefixo = "RELCRT"
    else:
        return 

    if not resultado:
        messagebox.showerror("Erro", "Nenhum relatório para exportar!")
        return

    # Geração automática do nome do arquivo
    ultimos4 = cod_material[-4:] if len(cod_material) >= 4 else cod_material
    projeto_nome = projeto.replace("-", "_")
    ss_nome = ss.replace("/", "_")  # <-- agora separa por underline
    sk_nome = sk.replace("-", "_")
    nome_pdf = f"{prefixo}{ultimos4}_{projeto_nome}_SS{ss_nome}_{sk_nome}.pdf"

    caminho = filedialog.asksaveasfilename(
        parent=root,
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        title="Salvar relatório em PDF",
        initialfile=nome_pdf
    )
    if not caminho:
        return

    campos = [
        ("Projeto:", projeto),
        ("SS:", ss),
        ("SK:", sk),
        ("Material:", cod_material)
    ]
    try:
        gerar_pdf_func(
            caminho,
            resultado,
            campos,
            titulo=titulo
        )
        messagebox.showinfo("PDF", f"PDF gerado com sucesso em:\n{os.path.abspath(caminho)}")
    except Exception as e:
        messagebox.showerror("Erro ao gerar PDF", f"Ocorreu um erro ao gerar o PDF:\n{e}")

def perguntar_tipo_pdf(root):
    win = Toplevel(root)
    win.title("Escolha o tipo de PDF")
    win.geometry("400x160")
    win.resizable(False, False)
    win.update_idletasks()
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_w = root.winfo_width()
    root_h = root.winfo_height()
    win_w = 400
    win_h = 160
    pos_x = root_x + (root_w // 2) - (win_w // 2)
    pos_y = root_y + (root_h // 2) - (win_h // 2)
    win.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
    tb.Label(win, text="Qual PDF deseja gerar?", font=("Segoe UI", 12, "bold")).pack(pady=20)
    escolha = {"tipo": None}
    def escolher(tipo):
        escolha["tipo"] = tipo
        win.destroy()
    frame = tb.Frame(win)
    frame.pack(pady=10)
    tb.Button(frame, text="PDF da Minuta", bootstyle=WARNING, width=18, command=lambda: escolher("minuta")).pack(side=LEFT, padx=10)
    tb.Button(frame, text="PDF do Corte", bootstyle=SUCCESS, width=18, command=lambda: escolher("corte")).pack(side=LEFT, padx=10)
    tb.Button(win, text="Cancelar", bootstyle=SECONDARY, width=40, command=win.destroy).pack(pady=10)
    win.grab_set()
    win.wait_window()
    return escolha["tipo"]

def iniciar_interface(root):
    root.title("NETEX")
    try:
        root.iconbitmap(resource_path("netex.ico"))
    except Exception:
        pass
    largura = 1000
    altura = 750

    root.update_idletasks()
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    pos_x = (largura_tela // 2) - (largura // 2)
    pos_y = (altura_tela // 2) - (altura // 2)
    root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
    root.resizable(True, True)

    modo_emenda_var = tb.BooleanVar(value=True)

    # Frame Superior: Tutorial e Título
    frame_top = tb.Frame(root)
    frame_top.grid(row=0, column=0, columnspan=4, sticky="ew", padx=15, pady=(10, 0))
    frame_top.columnconfigure(0, weight=1)
    tb.Button(frame_top, text="Tutorial", command=lambda: abrir_tutorial(root), bootstyle=INFO, width=16).grid(row=0, column=1, sticky="e", padx=5)
    tb.Label(frame_top, text="Otimizador de Cortes", font=("Segoe UI", 22, "bold"), bootstyle=PRIMARY).grid(row=1, column=0, columnspan=2, pady=(0, 5), sticky="ew")

    # Frame Dados do Projeto
    frame_info = tb.LabelFrame(root, text="Dados do Projeto", bootstyle=PRIMARY)
    frame_info.grid(row=1, column=0, columnspan=4, sticky="ew", padx=15, pady=5)
    for i in range(8):
        frame_info.columnconfigure(i, weight=1)

    tb.Label(frame_info, text="Projeto:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=(10, 2), pady=5, sticky="e")
    projetos = [
        "P31-CAM", "P51-CAM", "P51-PAR", "P52-ACO", "P52-CAM", "P53-CAM",
        "P54-CAM", "P54-PAR", "P55-ACO", "P62-ACO", "P62-CAM", "P62-PAR", "PRA-1"
    ]
    combo_projeto = tb.Combobox(
        frame_info,
        values=projetos,
        state="readonly",
        width=12,
        font=("Segoe UI", 10),
        bootstyle="secondary"
    )
    combo_projeto.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    combo_projeto.configure(style="TEntry")

    tb.Label(frame_info, text="SS:", font=("Segoe UI", 11, "bold")).grid(row=0, column=2, padx=(15, 2), pady=5, sticky="e")
    entry_ss = tb.Entry(frame_info, width=12, font=("Segoe UI", 10), bootstyle="secondary")
    entry_ss.grid(row=0, column=3, padx=5, pady=5, sticky="w")
    entry_ss.bind("<KeyRelease>", lambda e: on_entry_uppercase(entry_ss))

    tb.Label(frame_info, text="SK:", font=("Segoe UI", 11, "bold")).grid(row=0, column=4, padx=(15, 2), pady=5, sticky="e")
    entry_sk = tb.Entry(frame_info, width=12, font=("Segoe UI", 10), bootstyle="secondary")
    entry_sk.grid(row=0, column=5, padx=5, pady=5, sticky="w")
    entry_sk.bind("<KeyRelease>", lambda e: on_entry_uppercase(entry_sk))

    tb.Label(frame_info, text="Código do material:", font=("Segoe UI", 11, "bold")).grid(row=0, column=6, padx=(15, 2), pady=5, sticky="e")
    entry_cod_material = tb.Entry(frame_info, width=12, font=("Segoe UI", 10), bootstyle="secondary")
    entry_cod_material.grid(row=0, column=7, padx=5, pady=5, sticky="w")
    entry_cod_material.bind("<KeyRelease>", lambda e: on_entry_digits(entry_cod_material, 10))

    # Frame Parâmetros
    frame_param = tb.LabelFrame(root, text="Parâmetros", bootstyle=INFO)
    frame_param.grid(row=2, column=0, columnspan=4, sticky="ew", padx=15, pady=5)
    for i in range(5):
        frame_param.columnconfigure(i, weight=1)

    modo_var = tb.IntVar(value=1)
    tb.Radiobutton(frame_param, text="Automático", variable=modo_var, value=1, bootstyle=SUCCESS).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    tb.Radiobutton(frame_param, text="Manual", variable=modo_var, value=2, bootstyle=INFO).grid(row=0, column=1, padx=10, pady=5, sticky="w")
    tb.Checkbutton(
        frame_param,
        text="Sugestão de Emenda",
        variable=modo_emenda_var,
        bootstyle="success-round-toggle"
    ).grid(row=0, column=2, padx=10, pady=5, sticky="w")
    tb.Label(frame_param, text="Comprimento da barra (mm):", font=("Segoe UI", 10, "bold")).grid(row=0, column=3, padx=5, pady=5, sticky="e")
    entry_comprimento = tb.Entry(frame_param, width=10, font=("Segoe UI", 10))
    entry_comprimento.insert(0, "6000")
    entry_comprimento.grid(row=0, column=4, padx=5, pady=5, sticky="w")

    # Frame Entradas
    frame_entrada = tb.Frame(root)
    frame_entrada.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=15, pady=10)
    frame_entrada.columnconfigure(0, weight=1)
    frame_entrada.columnconfigure(1, weight=1)
    frame_entrada.rowconfigure(0, weight=1)

    frame_cortes = tb.Labelframe(frame_entrada, text="Cortes (mm)", bootstyle=PRIMARY)
    frame_cortes.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="nsew")
    text_cortes = tb.Text(frame_cortes, height=15, width=40, font=("Consolas", 11))
    text_cortes.pack(fill="both", expand=True, padx=5, pady=5)

    frame_barras = tb.Labelframe(frame_entrada, text="Barras (modo manual)", bootstyle=INFO)
    frame_barras.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="nsew")
    text_barras = tb.Text(frame_barras, height=15, width=40, font=("Consolas", 11))
    text_barras.pack(fill="both", expand=True, padx=5, pady=5)

    # Frame Ações
    frame_botoes = tb.Frame(root)
    frame_botoes.grid(row=4, column=0, columnspan=4, pady=(10, 0))
    tb.Button(
        frame_botoes,
        text="Gerar Relatório de Corte",
        command=lambda: otimizar(
            text_cortes, text_barras, entry_comprimento, modo_var, modo_emenda_var,
            entry_ss, entry_sk, entry_cod_material, combo_projeto, root
        ),
        bootstyle=SUCCESS,
        width=25
    ).pack(side="left", padx=10)
    tb.Button(
        frame_botoes,
        text="Gerar Relatório de Minuta",
        command=lambda: gerar_relatorio_minuta(
            text_cortes, entry_ss, entry_sk, entry_cod_material, combo_projeto, root
        ),
        bootstyle=WARNING,
        width=25
    ).pack(side="left", padx=10)

    # Frame PDF
    frame_pdf = tb.Frame(root)
    frame_pdf.grid(row=5, column=0, columnspan=4, pady=(10, 30))
    tb.Button(
        frame_pdf,
        text="Gerar PDF",
        command=lambda: gerar_pdf(
            text_cortes, text_barras, entry_comprimento, modo_var, modo_emenda_var,
            entry_ss, entry_sk, entry_cod_material, combo_projeto, root
        ),
        bootstyle=PRIMARY,
        width=22
    ).pack()

    # Ajuste para expandir corretamente ao redimensionar
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)
    root.columnconfigure(3, weight=1)
    root.rowconfigure(3, weight=1)

def abrir_tutorial(root):
    texto = (
        "Bem-vindo ao Otimizador de Cortes!\n\n"
        "Este aplicativo foi desenvolvido para facilitar o planejamento e otimização de cortes de barras metálicas.\n\n"
        "FUNCIONALIDADES PRINCIPAIS:\n"
        "• Otimizar cortes: Informe os comprimentos desejados em 'Cortes (mm)' e clique em 'Otimizar'.\n"
        "• Gerar relatório de minuta: Gera uma sugestão de barras comerciais para solicitação de minuta.\n"
        "• Gerar PDF: Salva o relatório atual em PDF (preencha todos os campos obrigatórios corretamente antes).\n\n"
        "COMO USAR:\n"
        "1. Selecione o projeto, preencha SS (ex: 0123/2024 ou 0123P/2025), SK (ex: EST-001 ou TU-123) e o Código do material (exatamente 10 dígitos numéricos).\n"
        "2. Escolha o modo desejado:\n"
        "   - Modo Automático: Informe apenas os cortes e o comprimento da barra padrão.\n"
        "   - Modo Manual: Informe os cortes e as barras disponíveis.\n"
        "3. Clique em 'Otimizar' para gerar o relatório de cortes.\n"
        "4. Para gerar minuta, preencha os cortes necessários e clique em 'Gerar Relatório de Minuta'.\n"
        "5. Para salvar em PDF, clique em 'Gerar PDF' e escolha o tipo de relatório.\n\n"
        "DICAS IMPORTANTES:\n"
        "- Os campos SS, SK e Código do material são obrigatórios para gerar PDF.\n"
        "- O campo Código do material aceita apenas números e deve conter exatamente 10 dígitos.\n"
        "- No modo manual, preencha as barras antes de otimizar ou gerar PDF de corte.\n"
        "- Não é possível gerar minuta se houver cortes maiores que 6000mm.\n"
        "- Sempre revise os dados antes de gerar o PDF.\n\n"
        "Em caso de dúvidas, consulte o suporte técnico."
    )

    win = tb.Toplevel(root)
    win.title("Tutorial - Como usar o Otimizador de Cortes")
    win_w = 800
    win_h = 600
    win.geometry(f"{win_w}x{win_h}")
    win.resizable(False, False)
    win.update_idletasks()

    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_w = root.winfo_width()
    root_h = root.winfo_height()
    pos_x = root_x + (root_w // 2) - (win_w // 2)
    pos_y = root_y + (root_h // 2) - (win_h // 2)
    win.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

    tb.Label(win, text="Tutorial de Uso", font=("Segoe UI", 16, "bold"), bootstyle=PRIMARY).pack(pady=(15, 10))
    txt = scrolledtext.ScrolledText(win, font=("Segoe UI", 11), wrap="word", height=25, width=90)
    txt.pack(padx=25, pady=10, fill="both", expand=True)
    txt.insert("1.0", texto)
    txt.config(state="disabled")
    tb.Button(win, text="Fechar", command=win.destroy, bootstyle=SECONDARY).pack(pady=10)
    win.grab_set()

def on_entry_uppercase(entry):
    valor = entry.get()
    pos = entry.index("insert")
    entry.delete(0, "end")
    entry.insert(0, valor.upper())
    entry.icursor(pos)

def on_entry_digits(entry, maxlen=10):
    valor = ''.join(filter(str.isdigit, entry.get()))[:maxlen]
    pos = entry.index("insert")
    entry.delete(0, "end")
    entry.insert(0, valor)
    entry.icursor(pos)