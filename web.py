import streamlit as st
import tempfile
import os
import time
import base64
import datetime
from PIL import Image

#streamlit run web.py

st.set_page_config(layout="wide")

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
    gerar_texto_minuta_para_pdf
)
from Modulação.pdf_utils import gerar_pdf as gerar_pdf_func
from Modulação.utils import parse_entrada
from Modulação.validação import validar_ss, validar_sk, validar_cod_material

class FakeVar:
    def __init__(self, value):
        self.value = value
    def get(self):
        return self.value

# --- Função utilitária para base64 ---
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- CSS customizado ---
st.markdown("""
    <style>
        body {background-color: #f4f6fa;}
        .main {background-color: #f4f6fa;}
        .block-container {padding-top: 2rem;}
        h1, h2, h3, h4 {color: #3a506b;}
        .stButton>button {
            background: linear-gradient(90deg, #5bc0be 0%, #3a506b 100%);
            color: white;
            border-radius: 8px;
            font-weight: bold;
            border: none;
            padding: 0.5em 1.5em;
            margin-top: 8px;
            transition: background 0.3s;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #3a506b 0%, #5bc0be 100%);
            color: #fff;
        }
        .stTextInput>div>div>input, .stTextArea>div>textarea {
            background-color: #e9ecef !important;
            color: #222 !important;
            border-radius: 6px;
            border: 1px solid #bfc9d1;
        }
        .stTextInput>div>div>input::placeholder, .stTextArea>div>textarea::placeholder {
            color: #7b8794 !important;
        }
        .stRadio>div>label, .stCheckbox>label {color: #3a506b;}
        .sidebar .sidebar-content {background-color: #e9ecef;}
        .sidebar .sidebar-content h2, .sidebar .sidebar-content h3 {color: #3a506b;}
        .sidebar .sidebar-content {color: #222;}
        .stDownloadButton>button {
            background: #5bc0be;
            color: #fff;
            border-radius: 8px;
            font-weight: bold;
            border: none;
            padding: 0.5em 1.5em;
            transition: background 0.3s;
        }
        .stDownloadButton>button:hover {
            background: #3a506b;
            color: #fff;
        }
        /* Ajuste para o logo e títulos */
        img, span {
            filter: none !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    '<link rel="stylesheet" href="webfonts/Montserrat-Alt1.css">',
    unsafe_allow_html=True
)

# --- Sidebar (Menu Lateral) ---
logo_base64 = get_base64_image("webfonts/IconeLogo.png")
st.sidebar.markdown(f"""
<div style='
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
'>
    <img src="data:image/png;base64,{logo_base64}" width="60" style="margin-bottom: 8px;" />
    <span style="
        font-family: 'Montserrat-Alt1', Arial, sans-serif;
        font-size: 32px;
        font-weight: 700;
        color: #ff4b4b;
        text-align: center;
    ">Corteus</span>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("**Desenvolvido por Matheus Araújo**")
st.sidebar.markdown("<small style='color:#888;'>v1.0.6</small>", unsafe_allow_html=True)

# --- Cabeçalho principal ---
logo_base64 = get_base64_image("webfonts/IconeLogo.png")
st.markdown(f"""
<div style='
    background: #ff4b4b;
    padding: 48px 0 24px 0;
    border-radius: 12px;
    margin-bottom: 32px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
'>
    <img src="data:image/png;base64,{logo_base64}" width="80" style="margin-bottom: 16px;" />
    <span style="
        font-family: 'Montserrat-Alt1', Arial, sans-serif;
        font-size: 56px;
        font-weight: 700;
        color: #18191a;
        letter-spacing: -2px;
        text-align: center;
        margin-bottom: 8px;
    ">Corteus</span>
    <span style="
        font-family: 'Montserrat-Alt1', Arial, sans-serif;
        font-size: 22px;
        font-weight: 400;
        color: #18191a;
        text-align: center;
        opacity: 0.85;
        margin-top: 0;
        max-width: 90vw;
        word-break: break-word;
    ">
        Otimizador de cortes para manufatura inteligente
    </span>
</div>
""", unsafe_allow_html=True)

# --- 1. Dados do Projeto ---
def sk_to_upper():
    sk = st.session_state["sk_input"]
    st.session_state["sk_input"] = sk.upper()
    
st.markdown("#### <span style='color:#ff4b4b'>1. Dados do Projeto</span>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    projeto = st.selectbox("Projeto", [
        "P31-CAM", "P51-CAM", "P51-PAR", "P52-ACO", "P52-CAM", "P53-CAM",
        "P54-CAM", "P54-PAR", "P55-ACO", "P62-ACO", "P62-CAM", "P62-PAR", "PRA-1"
    ])
with col2:
    ss = st.text_input("SS (ex: 0123/2024)", max_chars=9)
    ano_atual = datetime.datetime.now().year
    ano_min = ano_atual - 1
    ano_max = ano_atual + 4
    ss_valido = validar_ss(ss)
    ano_valido = False
    if ss and ss_valido:
        try:
            ano_ss = int(ss.split("/")[-1])
            if ano_min <= ano_ss <= ano_max:
                ano_valido = True
            else:
                st.warning(f"O ano da SS deve estar entre {ano_min} e {ano_max}.")
        except Exception:
            st.warning("Ano inválido na SS.")
    elif ss and not ss_valido:
        st.warning("SS inválido. Use o formato 0123/2024.")

with col3:
    sk = st.text_input(
        "SK (ex: EST-001)",
        max_chars=7,
        key="sk_input",
        on_change=sk_to_upper
    )
    sk = st.session_state["sk_input"]
    if sk and not validar_sk(sk):
        st.warning("SK inválido. Use o formato EST-001.")

with col4:
    cod_material = st.text_input("Código do material (10 dígitos)", max_chars=10)
    if not cod_material.isdigit() and cod_material != "":
        st.warning("Digite apenas números no código do material.")

st.markdown("---")

# --- 2. Parâmetros de Corte ---
st.markdown("#### <span style='color:#ff4b4b'>2. Parâmetros de Corte</span>", unsafe_allow_html=True)
colp1, colp2 = st.columns(2)
with colp1:
    modo = st.radio("Modo", ["Automático", "Manual"])
with colp2:
    sugestao_emenda = st.checkbox("Sugestão de Emenda (modo manual)", value=True)

comprimento_barra = ""
barras_str = ""
if modo == "Automático":
    comprimento_barra = st.text_input("Comprimento da barra (mm)", value="6000")
else:
    barras_str = st.text_area("Barras disponíveis (mm, separadas por espaço ou vírgula)", height=80)

st.markdown("---")

# --- 3. Entradas de Cortes ---
st.markdown("#### <span style='color:#ff4b4b'>3. Entradas de Cortes</span>", unsafe_allow_html=True)
cortes_str = st.text_area("Cortes desejados (mm, separados por espaço ou vírgula)", height=120)

st.markdown("---")

# --- 4. Otimização ---
if st.button("🚀 Otimizar"):
    if not cortes_str:
        st.error("Informe os cortes desejados.")
    elif not ss or not validar_ss(ss):
        st.error("SS inválido. Exemplo: 0123/2024")
    elif not sk or not validar_sk(sk):
        st.error("SK inválido. Exemplo: EST-001")
    elif not cod_material or not validar_cod_material(cod_material):
        st.error("Código do material inválido (deve ter 10 dígitos numéricos).")
    elif modo == "Automático" and not comprimento_barra:
        st.error("Informe o comprimento da barra.")
    elif modo == "Manual" and not barras_str:
        st.error("Informe as barras disponíveis no modo manual.")
    else:
        try:
            cortes = parse_entrada(cortes_str)
            agrupados = agrupar_cortes(cortes)
            if modo == "Automático":
                resultado = resolver_com_barras_livres(
                    agrupados,
                    int(comprimento_barra),
                    lambda barras, comprimento_barra, invalidos: gerar_resultado(
                        barras, comprimento_barra, invalidos,
                        ss=ss, sk=sk, cod_material=cod_material, modo_var=1
                    )
                )
                titulo = "RELATÓRIO DE CORTES"
                prefixo = "RELCRT"
            else:
                barras = parse_entrada(barras_str)
                if sugestao_emenda:
                    resultado = resolver_com_barras_fixas(
                        agrupados,
                        barras,
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
                        barras,
                        lambda barras, comprimentos, invalidos=0: gerar_resultado_com_barras_fixas(
                            barras, comprimentos, invalidos,
                            ss=ss, sk=sk, cod_material=cod_material, modo_var=2
                        )
                    )
                titulo = "RELATÓRIO DE CORTES"
                prefixo = "RELCRT"

            campos = [
                ("Projeto:", projeto),
                ("SS:", ss),
                ("SK:", sk),
                ("Material:", cod_material)
            ]
            ultimos4 = cod_material[-4:] if len(cod_material) >= 4 else cod_material
            projeto_nome = projeto.replace("-", "_")
            ss_nome = ss.replace("/", "_")
            sk_nome = sk.replace("-", "_")
            nome_pdf = f"{prefixo}{ultimos4}_{projeto_nome}_SS{ss_nome}_{sk_nome}.pdf"

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp_path = tmp.name

            gerar_pdf_func(
                tmp_path,
                resultado,
                campos,
                titulo=titulo
            )

            with open(tmp_path, "rb") as f:
                pdf_bytes = f.read()
                st.download_button(
                    label="Baixar PDF do Relatório de Cortes",
                    data=pdf_bytes,
                    file_name=nome_pdf,
                    mime="application/pdf"
                )

            os.unlink(tmp_path)
            st.success("Otimização concluída!")
        except Exception as e:
            st.error(f"Erro: {e}")

# --- 5. Relatório de Minuta ---
st.markdown("#### <span style='color:#ff4b4b'>Relatório de Minuta</span>", unsafe_allow_html=True)
if st.button("Gerar Relatório de Minuta"):
    if not cortes_str:
        st.error("Informe os cortes desejados.")
    else:
        try:
            cortes = parse_entrada(cortes_str)
            if any(c > 6000 for c in cortes):
                st.error("Não é possível gerar minuta se houver cortes maiores que 6000mm.")
            else:
                texto = gerar_texto_minuta_para_pdf(cortes, ss, sk, cod_material)
                titulo = "RELATÓRIO DE MINUTA"
                prefixo = "RELMIN"
                campos = [
                    ("Projeto:", projeto),
                    ("SS:", ss),
                    ("SK:", sk),
                    ("Material:", cod_material)
                ]
                ultimos4 = cod_material[-4:] if len(cod_material) >= 4 else cod_material
                projeto_nome = projeto.replace("-", "_")
                ss_nome = ss.replace("/", "_")
                sk_nome = sk.replace("-", "_")
                nome_pdf = f"{prefixo}{ultimos4}_{projeto_nome}_SS{ss_nome}_{sk_nome}.pdf"

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp_path = tmp.name

                gerar_pdf_func(
                    tmp_path,
                    texto,
                    campos,
                    titulo=titulo
                )

                with open(tmp_path, "rb") as f:
                    pdf_bytes = f.read()
                    st.download_button(
                        label="Baixar PDF da Minuta",
                        data=pdf_bytes,
                        file_name=nome_pdf,
                        mime="application/pdf"
                    )

                st.success("Relatório de minuta gerado com sucesso!")
                os.unlink(tmp_path)
        except Exception as e:
            st.error(f"Erro: {e}")

# --- Seletor de Tema ---
tema = st.sidebar.radio("Tema", ["Claro", "Escuro"], horizontal=True)

# --- CSS customizado com suporte a tema ---
if tema == "Claro":
    st.markdown("""
        <style>
            body {background-color: #f6f8fa;}
            .main {background-color: #f6f8fa;}
            .block-container {padding-top: 2rem;}
            h1, h2, h3, h4 {color: #2d3a4a;}
            .stButton>button, .stDownloadButton>button {
                background: linear-gradient(90deg, #b5d0e6 0%, #6ea8c6 100%);
                color: #223;
                border-radius: 8px;
                font-weight: bold;
                border: none;
                padding: 0.5em 1.5em;
                margin-top: 8px;
                transition: background 0.3s;
            }
            .stButton>button:hover, .stDownloadButton>button:hover {
                background: linear-gradient(90deg, #6ea8c6 0%, #b5d0e6 100%);
                color: #223;
            }
            .stTextInput>div>div>input, .stTextArea>div>textarea {
                background-color: #e9ecef !important;
                color: #222 !important;
                border-radius: 6px;
                border: 1px solid #bfc9d1;
            }
            .stTextInput>div>div>input::placeholder, .stTextArea>div>textarea::placeholder {
                color: #7b8794 !important;
            }
            .stRadio>div>label, .stCheckbox>label {color: #2d3a4a;}
            .sidebar .sidebar-content {background-color: #e9ecef;}
            .sidebar .sidebar-content h2, .sidebar .sidebar-content h3 {color: #2d3a4a;}
            .sidebar .sidebar-content {color: #222;}
            /* Cabeçalho principal */
            .element-container:has(> div[style*="background: #ff4b4b"]) > div {
                background: #b5d0e6 !important;
                border-radius: 12px;
            }
            /* Ajuste para o logo e títulos */
            img, span {
                filter: none !important;
            }
            /* Título Corteus */
            span[style*="font-size: 56px"] {
                color: #2d3a4a !important;
            }
            /* Subtítulo */
            span[style*="font-size: 22px"] {
                color: #223 !important;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            body {background-color: #181c22;}
            .main {background-color: #181c22;}
            .block-container {padding-top: 2rem;}
            h1, h2, h3, h4 {color: #b5d0e6;}
            .stButton>button, .stDownloadButton>button {
                background: linear-gradient(90deg, #22303c 0%, #3a506b 100%);
                color: #e9ecef;
                border-radius: 8px;
                font-weight: bold;
                border: none;
                padding: 0.5em 1.5em;
                margin-top: 8px;
                transition: background 0.3s;
            }
            .stButton>button:hover, .stDownloadButton>button:hover {
                background: linear-gradient(90deg, #3a506b 0%, #22303c 100%);
                color: #b5d0e6;
            }
            .stTextInput>div>div>input, .stTextArea>div>textarea {
                background-color: #232a34 !important;
                color: #e9ecef !important;
                border-radius: 6px;
                border: 1px solid #3a506b;
            }
            .stTextInput>div>div>input::placeholder, .stTextArea>div>textarea::placeholder {
                color: #7b8794 !important;
            }
            .stRadio>div>label, .stCheckbox>label {color: #b5d0e6;}
            .sidebar .sidebar-content {background-color: #232a34;}
            .sidebar .sidebar-content h2, .sidebar .sidebar-content h3 {color: #b5d0e6;}
            .sidebar .sidebar-content {color: #e9ecef;}
            /* Cabeçalho principal */
            .element-container:has(> div[style*="background: #ff4b4b"]) > div {
                background: #22303c !important;
                border-radius: 12px;
            }
            /* Ajuste para o logo e títulos */
            img, span {
                filter: none !important;
            }
            /* Título Corteus */
            span[style*="font-size: 56px"] {
                color: #b5d0e6 !important;
            }
            /* Subtítulo */
            span[style*="font-size: 22px"] {
                color: #e9ecef !important;
            }
        </style>
    """, unsafe_allow_html=True)

# --- 7. Tutorial ---
with st.sidebar.expander("Tutorial de Uso"):
    st.markdown("""
    <h3 style='color:#ff4b4b;'>Como usar o Otimizador de Cortes:</h3>
    <ol>
        <li>Preencha os dados do projeto (Projeto, SS, SK, Código do material).</li>
        <li>Escolha o modo de operação (Automático ou Manual).</li>
        <li>Informe os cortes desejados e, se necessário, as barras disponíveis.</li>
        <li>Clique em <b>Otimizar</b> para ver o resultado.</li>
        <li>Gere o relatório de minuta se desejar comparar barras comerciais.</li>
        <li>Exporte o relatório em PDF para salvar ou compartilhar.</li>
    </ol>
    <b>Dicas:</b>
    <ul>
        <li>O campo Código do material aceita apenas números e deve conter exatamente 10 dígitos.</li>
        <li>No modo manual, preencha as barras antes de otimizar ou gerar PDF de corte.</li>
        <li>Não é possível gerar minuta se houver cortes maiores que 6000mm.</li>
        <li>Sempre revise os dados antes de gerar o PDF.</li>
    </ul>
    """, unsafe_allow_html=True)



