import pandas as pd
import streamlit as st
from datetime import datetime, timedelta


def aplicar_filtros_topo(df: pd.DataFrame, data_especifica, periodo, cliente):
    """Exibe filtros no topo e retorna DataFrame filtrado."""
    df_filtrado = df.copy()

    if data_especifica:
        df_filtrado = df_filtrado[df_filtrado['NFI_DATA_SAIDA'].dt.date ==
                                  data_especifica]
    else:
        hoje = datetime.now().date()
        if periodo == "Hoje":
            df_filtrado = df_filtrado[df_filtrado['NFI_DATA_SAIDA'].dt.date == hoje]
        elif periodo == "Última Semana":
            df_filtrado = df_filtrado[df_filtrado['NFI_DATA_SAIDA'] >= datetime.now(
            ) - timedelta(days=7)]
        elif periodo == "Últimos 15 Dias":
            df_filtrado = df_filtrado[df_filtrado['NFI_DATA_SAIDA'] >= datetime.now(
            ) - timedelta(days=15)]
        elif periodo == "Últimos 30 Dias":
            df_filtrado = df_filtrado[df_filtrado['NFI_DATA_SAIDA'] >= datetime.now(
            ) - timedelta(days=30)]
        elif periodo == "Mês Atual":
            df_filtrado = df_filtrado[df_filtrado['NFI_DATA_SAIDA'].dt.month == datetime.now(
            ).month]
        elif periodo == "Ano Atual":
            df_filtrado = df_filtrado[df_filtrado['NFI_DATA_SAIDA'].dt.year == datetime.now(
            ).year]

    if cliente:
        df_filtrado = df_filtrado[df_filtrado['NFI_RAZAO'].isin(
            cliente)]

    return df_filtrado
