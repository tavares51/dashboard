import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from data.gold.estoque.data_gold import obter_dados_filtrados
from components.charts.bar import grafico_entrada_saida_por_data, grafico_produtor, grafico_barras_produto
from components.tables.table import exibir_tabela_resumida
from components.cards.card import card

# =============================
# CONFIG STREAMLIT
# =============================

@st.cache_data(show_spinner=False)
def carregar_dados():
    """Carrega os dados da camada gold apenas uma vez para melhorar desempenho."""
    df = obter_dados_filtrados()
    df['CRE_DATA_ENTRADA'] = pd.to_datetime(
        df['CRE_DATA_ENTRADA'], errors='coerce')
    return df


def aplicar_filtros_topo(df: pd.DataFrame):
    """Exibe filtros no topo e retorna DataFrame filtrado."""
    col1, col2, col3, col4 = st.columns([0.2, 0.2, 0.3, 0.3])

    with col1:
        periodo = st.selectbox(
            "Período:",
            ["Hoje", "Última Semana", "Últimos 15 Dias",
                "Últimos 30 Dias", "Mês Atual", "Ano Atual", "Todos"],
            index=1
        )

    with col2:
        data_especifica = st.date_input("Data", value=None)

    with col3:
        produtos = st.multiselect(
            "Produto:",
            options=sorted(df['CRE_PRO_DESCRICAO'].dropna().unique())
        )

    with col4:
        fornecedores = st.multiselect(
            "Fornecedor:",
            options=sorted(df['CRE_PRODUTOR_NOME'].dropna().unique())
        )

    df_filtrado = df.copy()

    if data_especifica:
        df_filtrado = df_filtrado[df_filtrado['CRE_DATA_ENTRADA'].dt.date == data_especifica]
    else:
        hoje = datetime.now().date()
        if periodo == "Hoje":
            df_filtrado = df_filtrado[df_filtrado['CRE_DATA_ENTRADA'].dt.date == hoje]
        elif periodo == "Última Semana":
            df_filtrado = df_filtrado[df_filtrado['CRE_DATA_ENTRADA'] >= datetime.now(
            ) - timedelta(days=7)]
        elif periodo == "Últimos 15 Dias":
            df_filtrado = df_filtrado[df_filtrado['CRE_DATA_ENTRADA'] >= datetime.now(
            ) - timedelta(days=15)]
        elif periodo == "Últimos 30 Dias":
            df_filtrado = df_filtrado[df_filtrado['CRE_DATA_ENTRADA'] >= datetime.now(
            ) - timedelta(days=30)]
        elif periodo == "Mês Atual":
            df_filtrado = df_filtrado[df_filtrado['CRE_DATA_ENTRADA'].dt.month == datetime.now(
            ).month]
        elif periodo == "Ano Atual":
            df_filtrado = df_filtrado[df_filtrado['CRE_DATA_ENTRADA'].dt.year == datetime.now(
            ).year]

    if produtos:
        df_filtrado = df_filtrado[df_filtrado['CRE_PRO_DESCRICAO'].isin(
            produtos)]

    if fornecedores:
        df_filtrado = df_filtrado[df_filtrado['CRE_PRODUTOR_NOME'].isin(
            fornecedores)]

    return df_filtrado


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
    
    data_atual = datetime.now().strftime("%d/%m/%Y")
    st.title(f"Controle Estoque Biomax")

    df = carregar_dados()
    df_filtrado = aplicar_filtros_topo(df)

    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
        return

    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        fig_produto = grafico_barras_produto(df_filtrado, top_n=5)
        if fig_produto:
            st.plotly_chart(fig_produto, use_container_width=True)

    with col2:
        fig_produtor = grafico_produtor(df_filtrado, 5)
        if fig_produtor:
            st.plotly_chart(fig_produtor, use_container_width=True)

    fig_data = grafico_entrada_saida_por_data(df_filtrado)
    if fig_data:
        st.plotly_chart(fig_data, use_container_width=True)

    exibir_tabela_resumida(df_filtrado)


if __name__ == "__main__":
    run_dashboard()
