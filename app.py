import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# === Seus imports existentes ===
from data.gold.estoque.data_gold import obter_dados_filtrados
from data.gold.financeiro.data_finance_gold import obter_dados_filtrados as obter_dados_financeiro_filtrados

from components.charts.bar import (
    grafico_entrada_saida_por_data,
    grafico_produtor,
    grafico_barras_produto,
    grafico_financeiro_por_data,
)
from components.tables.table import exibir_tabela_resumida, exibir_saidas
from components.filters.filter_estoque import aplicar_filtros_topo as filtro_estoque
from components.filters.filter_financeiro import aplicar_filtros_topo as filtro_financeiro
from components.cards.card import card


# =========================================
# Cache dos dados da BASE INTEIRA
# (sem TTL; só atualiza quando você mandar)
# =========================================
@st.cache_data(show_spinner=False)
def carregar_dados_cached(_refresh_key: str | None = None):
    """
    Busca a BASE INTEIRA do banco e cacheia.
    _refresh_key é apenas um parâmetro "inútil" para permitir
    invalidar o cache se você quiser, mas aqui usamos clear().
    """
    df = obter_dados_filtrados()  # pega TUDO do estoque
    df_fin = obter_dados_financeiro_filtrados()  # pega TUDO do financeiro

    # Normalizações mínimas
    if "CRE_DATA_ENTRADA" in df.columns:
        df["CRE_DATA_ENTRADA"] = pd.to_datetime(df["CRE_DATA_ENTRADA"], errors="coerce")
    if "NFI_DATA_SAIDA" in df_fin.columns:
        df_fin["NFI_DATA_SAIDA"] = pd.to_datetime(df_fin["NFI_DATA_SAIDA"], errors="coerce")

    return df, df_fin


def run_dashboard():
    st.set_page_config(page_title="Controle de Estoque Biomax", layout="wide")

    # ============================
    # Barra lateral: Refresh
    # ============================
    with st.sidebar:
        st.subheader("Dados")
      
        if st.button("🔄 Atualizar agora", use_container_width=True):
                # Limpa TODO o cache de dados → no próximo rerun baixa tudo de novo
            st.cache_data.clear()
            st.success("Cache limpo. Os dados serão recarregados.")

    # Se o usuário habilitou "F5 atualiza", limpamos o cache a cada reload
    if st.session_state.get("__refresh_on_reload__", False):
        # Observação: isto limpa o cache em todo rerun. É o comportamento desejado quando a opção está ativa.
        st.cache_data.clear()

    # ------------------------------------------------------
    # Carrega a base inteira do cache (ou do banco se limpo)
    # ------------------------------------------------------
    df, df_financeiro = carregar_dados_cached(_refresh_key=None)

    # ============================
    # Estilo visual
    # ============================
    st.markdown(
        """
        <style>
            .block-container { padding-top: 1rem; padding-bottom: 0rem; }
            header[data-testid="stHeader"] { height: 0rem; }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Controle Estoque Biomax")

    # ============================
    # Filtros (locais, sobre a base completa)
    # ============================
    col1_filtro, col2_filtro, col3_filtro, col4_filtro, col5_filtro = st.columns([0.2, 0.2, 0.2, 0.2, 0.2])

    with col1_filtro:
        periodo = st.selectbox(
            "Período:",
            ["Hoje", "Última Semana", "Últimos 15 Dias", "Últimos 30 Dias", "Mês Atual", "Ano Atual", "Todos"],
            index=0
        )

    with col2_filtro:
        data_especifica = st.date_input("Data", value=None)

    with col3_filtro:
        produtos = st.multiselect(
            "Produto:",
            options=sorted(df['CRE_PRO_DESCRICAO'].dropna().unique()) if 'CRE_PRO_DESCRICAO' in df.columns else []
        )

    with col4_filtro:
        fornecedores = st.multiselect(
            "Fornecedor:",
            options=sorted(df['CRE_PRODUTOR_NOME'].dropna().unique()) if 'CRE_PRODUTOR_NOME' in df.columns else []
        )

    with col5_filtro:
        cliente = st.multiselect(
            "Cliente:",
            options=sorted(df_financeiro['NFI_RAZAO'].dropna().unique()) if 'NFI_RAZAO' in df_financeiro.columns else []
        )

    # Aplica suas funções de filtro (locais, sem ir ao banco)
    df_filtrado = filtro_estoque(df, data_especifica, periodo, produtos, fornecedores)
    df_filtro_financeiro = filtro_financeiro(df_financeiro, data_especifica, periodo, cliente)

    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
        return

    # ============================
    # Gráficos e informações
    # ============================
    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        fig_produto = grafico_barras_produto(df_filtrado, top_n=5)
        if fig_produto:
            st.plotly_chart(fig_produto, use_container_width=True)

    with col2:
        fig_produtor = grafico_produtor(df_filtrado, 5)
        if fig_produtor:
            st.plotly_chart(fig_produtor, use_container_width=True)

    total = 0.0
    if "NFI_VALOR_TOTAL_NOTA" in df_filtro_financeiro.columns:
        total = float(pd.to_numeric(df_filtro_financeiro['NFI_VALOR_TOTAL_NOTA'], errors='coerce').sum())
    card('', f"Total Faturado: R$ {total:,.2f}")

    fig_data_financeiro = grafico_financeiro_por_data(df_filtro_financeiro)
    if fig_data_financeiro:
        st.plotly_chart(fig_data_financeiro, use_container_width=True)

    exibir_tabela_resumida(df_filtrado)
    exibir_saidas(df_filtro_financeiro)


if __name__ == "__main__":
    run_dashboard()
