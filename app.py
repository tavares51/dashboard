import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime as dt, timedelta
from typing import Optional, Tuple, List, Union

from data.gold.estoque.data_gold import obter_dados_filtrados
from data.gold.financeiro.data_finance_gold import obter_dados_filtrados as obter_dados_financeiro_filtrados

from components.charts.bar import (
    grafico_produtor,
    grafico_barras_produto,
    grafico_financeiro_por_data
)
from components.tables.table import exibir_tabela_resumida, exibir_saidas
from components.filters.filter_estoque import aplicar_filtros_topo as filtro_estoque
from components.filters.filter_financeiro import aplicar_filtros_topo as filtro_financeiro
from components.cards.card import card


def _coerce_datetime(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _coerce_numeric(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _safe_unique(df: pd.DataFrame, col: str) -> List:
    if col in df.columns:
        return sorted(pd.Series(df[col]).dropna().unique().tolist())
    return []


@st.cache_data(show_spinner=False)
def carregar_dados_cached(_refresh_key: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = obter_dados_filtrados()
    df_fin = obter_dados_financeiro_filtrados()
    df = _coerce_datetime(df, "CRE_DATA_ENTRADA")
    # financeiro usa EMISSÃO
    df_fin = _coerce_datetime(df_fin, "NFI_DATA_EMISSAO")
    df_fin = _coerce_numeric(df_fin, ["VALOR_FINAL"])
    return df, df_fin


def _periodo_para_intervalo(periodo: str) -> Tuple[Optional[date], Optional[date]]:
    hoje = dt.now().date()
    if periodo == "Hoje":
        return hoje, hoje
    if periodo == "Última Semana":
        return hoje - timedelta(days=6), hoje
    if periodo == "Últimos 15 Dias":
        return hoje - timedelta(days=14), hoje
    if periodo == "Últimos 30 Dias":
        return hoje - timedelta(days=29), hoje
    if periodo == "Mês Atual":
        ini = hoje.replace(day=1)
        fim = (ini + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        if fim > hoje:
            fim = hoje
        return ini, fim
    if periodo == "Ano Atual":
        ini = hoje.replace(month=1, day=1)
        fim = hoje
        return ini, fim
    return None, None


def run_dashboard():
    st.set_page_config(page_title="Controle de Estoque Biomax", layout="wide")

    with st.sidebar:
        st.subheader("Dados")
        if st.button("🔄 Atualizar agora", use_container_width=True):
            st.cache_data.clear()
            st.success("Cache limpo. Os dados serão recarregados.")

    df, df_financeiro = carregar_dados_cached(_refresh_key=None)

    st.markdown(
        """
        <style>
            .block-container { padding-top: 3%; padding-bottom: 0rem; }
            header[data-testid="stHeader"] { height: 0rem; }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Controle Estoque Biomax")
    st.session_state.setdefault("filtro_modo", "Período")
    st.session_state["filtro_modo"] = st.radio(
        "Como deseja filtrar?",
        ["Período", "Intervalo"],
        horizontal=True,
        index=0 if st.session_state["filtro_modo"] == "Período" else 1,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        periodo = st.selectbox(
            "Período",
            ["---", "Hoje", "Última Semana", "Últimos 15 Dias",
                "Últimos 30 Dias", "Mês Atual", "Ano Atual"],
            disabled=(st.session_state["filtro_modo"] == "Intervalo"), index=1
        )

    def _min_max_dataframes() -> Tuple[Optional[date], Optional[date]]:
        datas = []
        if "CRE_DATA_ENTRADA" in df.columns:
            datas.append(pd.to_datetime(
                df["CRE_DATA_ENTRADA"], errors="coerce"))
        if "NFI_DATA_EMISSAO" in df_financeiro.columns:
            datas.append(pd.to_datetime(
                df_financeiro["NFI_DATA_EMISSAO"], errors="coerce"))
        if not datas:
            return None, None
        serie = pd.concat(datas).dropna()
        if serie.empty:
            return None, None
        return serie.min().date(), serie.max().date()

    data_min, data_max = _min_max_dataframes()
    hoje = dt.now().date()
    if data_min is None or data_max is None:
        # fallback: últimos 30 dias até hoje
        data_min = hoje - timedelta(days=30)
        data_max = hoje

    default_inicio = max(hoje - timedelta(days=6), data_min)
    default_fim = min(hoje, data_max)

    with col2:
        intervalo_datas: Tuple[date, date] = st.date_input(
            "Intervalo de Datas",
            value=(default_inicio, default_fim),
            min_value=data_min,
            max_value=data_max,
            format="DD/MM/YYYY",
            disabled=(st.session_state["filtro_modo"] == "Período"),
        )

    di: Optional[date] = None
    df_: Optional[date] = None

    if st.session_state["filtro_modo"] == "Intervalo":
        if isinstance(intervalo_datas, tuple) and len(intervalo_datas) == 2:
            di, df_ = intervalo_datas
            if di and df_ and di > df_:
                di, df_ = df_, di
    else:
        di, df_ = _periodo_para_intervalo(periodo)

    with col3:
        produtos = st.multiselect(
            "Produto", options=_safe_unique(df, "CRE_PRO_DESCRICAO"))
    with col4:
        clientes = st.multiselect(
            "Cliente", options=_safe_unique(df_financeiro, "NFI_RAZAO"))

    df_filtrado = filtro_estoque(df, None, None, produtos, None)
    df_filtro_financeiro = filtro_financeiro(
        df_financeiro, None, None, clientes)

    if di and df_:
        if not df_filtrado.empty and "CRE_DATA_ENTRADA" in df_filtrado.columns:
            df_filtrado["CRE_DATA_ENTRADA"] = pd.to_datetime(
                df_filtrado["CRE_DATA_ENTRADA"], errors="coerce"
            ).dt.normalize()
            df_filtrado = df_filtrado[
                (df_filtrado["CRE_DATA_ENTRADA"].dt.date >= di)
                & (df_filtrado["CRE_DATA_ENTRADA"].dt.date <= df_)
            ]

        if not df_filtro_financeiro.empty and "NFI_DATA_EMISSAO" in df_filtro_financeiro.columns:
            df_filtro_financeiro["NFI_DATA_EMISSAO"] = pd.to_datetime(
                df_filtro_financeiro["NFI_DATA_EMISSAO"], errors="coerce"
            ).dt.normalize()
            df_filtro_financeiro = df_filtro_financeiro[
                (df_filtro_financeiro["NFI_DATA_EMISSAO"].dt.date >= di)
                & (df_filtro_financeiro["NFI_DATA_EMISSAO"].dt.date <= df_)
            ]

    if df_filtrado.empty and df_filtro_financeiro.empty:
        st.warning(
            "Nenhum dado encontrado para os filtros selecionados (Estoque e Financeiro).")
        return
    elif df_filtrado.empty:
        st.warning(
            "Nenhum dado encontrado no **Estoque** para os filtros selecionados.")
    elif df_filtro_financeiro.empty:
        st.warning(
            "Nenhum dado encontrado no **Financeiro** para os filtros selecionados.")

    if not df_filtrado.empty:
        c1, c2 = st.columns([0.4, 0.6])
        with c1:
            fig_produto = grafico_barras_produto(df_filtrado, top_n=5)
            if fig_produto:
                st.plotly_chart(fig_produto, use_container_width=True)
        with c2:
            fig_produtor = grafico_produtor(df_filtrado, 5)
            if fig_produtor:
                st.plotly_chart(fig_produtor, use_container_width=True)

    total = 0.0
    total_produto = 0.0
    col_card1, col_card2 = st.columns(2)

    with col_card1:
        if not df_filtro_financeiro.empty and "VALOR_FINAL" in df_filtro_financeiro.columns:
            df_filtro_financeiro["VALOR_FINAL"] = pd.to_numeric(
                df_filtro_financeiro["VALOR_FINAL"], errors="coerce"
            ).fillna(0)
            total = float(df_filtro_financeiro["VALOR_FINAL"].sum())
        card("Total Faturado", f"R$ {total:,.2f}")

    with col_card2:
        total_produto = 0.0
        if not df_filtrado.empty and "CRE_PESO_LIQUIDO" in df_filtrado.columns:
            total_produto = float(df_filtrado["CRE_PESO_LIQUIDO"].sum())
        card("Total Produto", f"{total_produto:,.0f} Kg")

    fig_data_financeiro = None
    if not df_filtro_financeiro.empty:
        fig_data_financeiro = grafico_financeiro_por_data(
            df_filtro_financeiro, dias=None)

    if fig_data_financeiro:
        st.plotly_chart(fig_data_financeiro, use_container_width=True)
    else:
        st.info("Não há dados para o intervalo selecionado no gráfico financeiro.")


if __name__ == "__main__":
    run_dashboard()
    
