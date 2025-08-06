import pandas as pd
import streamlit as st
from datetime import datetime, timedelta


def aplicar_filtros_topo(df: pd.DataFrame, data_especifica, periodo, produtos, fornecedores):
    """Exibe filtros no topo e retorna DataFrame filtrado."""
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
