import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from data.gold.estoque.data_gold import obter_dados_filtrados
from data.gold.financeiro.data_finance_gold import obter_dados_filtrados as obter_dados_financeiro_filtrados
from components.charts.bar import grafico_entrada_saida_por_data, grafico_produtor, grafico_barras_produto, grafico_financeiro_por_data
from components.tables.table import exibir_tabela_resumida
from components.filters.filter_estoque import aplicar_filtros_topo as filtro_estoque
from components.filters.filter_financeiro import aplicar_filtros_topo as filtro_financeiro
from components.cards.card import card


@st.cache_data(show_spinner=False)
def carregar_dados():
    """Carrega os dados da camada gold apenas uma vez para melhorar desempenho."""
    df = obter_dados_filtrados()
    df_financeiro = obter_dados_financeiro_filtrados()

    df['CRE_DATA_ENTRADA'] = pd.to_datetime(
        df['CRE_DATA_ENTRADA'], errors='coerce')

    return df, df_financeiro


def run_dashboard():
    st.set_page_config(page_title="Controle de Estoque Biomax", layout="wide")
    st.markdown(
        """
        <style>
            .block-container { padding-top: 1rem; padding-bottom: 0rem; }
            header[data-testid="stHeader"] { height: 0rem; }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title(f"Controle Estoque Biomax")
    df, df_financeiro = carregar_dados()

    col1_filtro, col2_filtro, col3_filtro, col4_filtro, col5_filtro = st.columns(
        [0.2, 0.2, 0.2, 0.2, 0.2])

    with col1_filtro:
        periodo = st.selectbox(
            "Período:",
            ["Hoje", "Última Semana", "Últimos 15 Dias",
                "Últimos 30 Dias", "Mês Atual", "Ano Atual", "Todos"],
            index=0
        )

    with col2_filtro:
        data_especifica = st.date_input("Data", value=None)

    with col3_filtro:
        produtos = st.multiselect(
            "Produto:",
            options=sorted(df['CRE_PRO_DESCRICAO'].dropna().unique())
        )

    with col4_filtro:
        fornecedores = st.multiselect(
            "Fornecedor:",
            options=sorted(df['CRE_PRODUTOR_NOME'].dropna().unique())
        )

    with col5_filtro:
        cliente = st.multiselect(
            "Cliente:",
            options=sorted(df_financeiro['NFI_RAZAO'].dropna().unique())
        )

    df_filtrado = filtro_estoque(
        df, data_especifica, periodo, produtos, fornecedores)

    df_filtro_financeiro = filtro_financeiro(df_financeiro, data_especifica, periodo, cliente)

    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
        return

    col1, col2, col3 = st.columns([0.5, 0.5, 0.3])

    with col1:
        fig_produto = grafico_barras_produto(df_filtrado, top_n=5)
        if fig_produto:
            st.plotly_chart(fig_produto, use_container_width=True)

    with col2:
        fig_produtor = grafico_produtor(df_filtrado, 5)
        if fig_produtor:
            st.plotly_chart(fig_produtor, use_container_width=True)

    with col3:
        fig_data = grafico_entrada_saida_por_data(df_filtrado)
        if fig_data:
            st.plotly_chart(fig_data, use_container_width=True)

    fig_data_financeiro = grafico_financeiro_por_data(df_filtro_financeiro)
    if fig_data_financeiro:
        st.plotly_chart(fig_data_financeiro, use_container_width=True)

    exibir_tabela_resumida(df_filtrado)


if __name__ == "__main__":
    run_dashboard()
