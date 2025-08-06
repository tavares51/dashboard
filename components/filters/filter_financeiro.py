import pandas as pd
from datetime import datetime, timedelta


def aplicar_filtros_topo(df: pd.DataFrame, data_especifica, periodo: str, cliente: list[str] | None):
    df_filtrado = df.copy()

    # Garantir datetime
    df_filtrado['NFI_DATA_SAIDA'] = pd.to_datetime(df_filtrado['NFI_DATA_SAIDA'], errors='coerce')
    df_filtrado['DATA_NORMALIZADA'] = df_filtrado['NFI_DATA_SAIDA'].dt.normalize()

    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    if data_especifica:
        data_especifica = pd.to_datetime(data_especifica).normalize()
        df_filtrado = df_filtrado[df_filtrado['DATA_NORMALIZADA'] == data_especifica]

    elif periodo:
        if periodo == "Hoje":
            df_filtrado = df_filtrado[df_filtrado['DATA_NORMALIZADA'] == hoje]
        elif periodo == "Última Semana":
            inicio = hoje - timedelta(days=7)
            df_filtrado = df_filtrado[df_filtrado['DATA_NORMALIZADA'] >= inicio]
        elif periodo == "Últimos 15 Dias":
            inicio = hoje - timedelta(days=15)
            df_filtrado = df_filtrado[df_filtrado['DATA_NORMALIZADA'] >= inicio]
        elif periodo == "Últimos 30 Dias":
            inicio = hoje - timedelta(days=30)
            df_filtrado = df_filtrado[df_filtrado['DATA_NORMALIZADA'] >= inicio]
        elif periodo == "Mês Atual":
            df_filtrado = df_filtrado[
                (df_filtrado['DATA_NORMALIZADA'].dt.month == hoje.month) &
                (df_filtrado['DATA_NORMALIZADA'].dt.year == hoje.year)
            ]
        elif periodo == "Ano Atual":
            df_filtrado = df_filtrado[df_filtrado['DATA_NORMALIZADA'].dt.year == hoje.year]
        elif periodo == "Todos":
            pass  # não filtra nada

    if cliente:
        df_filtrado = df_filtrado[df_filtrado['NFI_RAZAO'].isin(cliente)]

    return df_filtrado

