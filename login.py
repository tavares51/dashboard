import streamlit as st
from app import run_dashboard

# ==============================
# CONFIG
# ==============================
st.set_page_config(page_title="Login - Estoque Biomax", layout="wide")

# Usuário e senha (pode ler do .env futuramente)
USUARIO = "admin"
SENHA = "123456"

# Inicializa sessão
if "logado" not in st.session_state:
    st.session_state.logado = False


# ==============================
# Login
# ==============================
def tela_login():
    st.markdown("<h2 style='text-align:center'>🔐 Login no Dashboard Biomax</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            if usuario == USUARIO and senha == SENHA:
                st.session_state.logado = True
            else:
                st.error("❌ Usuário ou senha inválidos.")


# ==============================
# App Principal
# ==============================
if not st.session_state.logado:
    tela_login()
else:
    run_dashboard()
    st.divider()
    if st.button("Sair"):
        st.session_state.logado = False
