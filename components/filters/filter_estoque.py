import pandas as pd
from datetime import datetime, timedelta


def aplicar_filtros_topo(
    df: pd.DataFrame,
    data_especifica,
    periodo: str,
    produtos: list[str] | None,
    fornecedores: list[str] | None
):
    """
    Aplica filtros de data, período, produtos e fornecedores no DataFrame de estoque.

    Parâmetros:
    - df: DataFrame com as colunas 'CRE_DATA_ENTRADA', 'CRE_PRO_DESCRICAO', 'CRE_PRODUTOR_NOME'.
    - data_especifica: data única selecionada (datetime.date ou datetime).
    - periodo: string com período ("Hoje", "Última Semana", "Mês Atual", etc.).
    - produtos: lista de produtos selecionados.
    - fornecedores: lista de fornecedores selecionados.

    Retorna:
    - DataFrame filtrado.
    """

    df_filtrado = df.copy()

    # Garantir datetime
    df_filtrado['CRE_DATA_ENTRADA'] = pd.to_datetime(df_filtrado['CRE_DATA_ENTRADA'], errors='coerce')
    df_filtrado['DATA_NORMALIZADA'] = df_filtrado['CRE_DATA_ENTRADA'].dt.normalize()

    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # ---------- Filtro por data específica ----------
    if data_especifica:
        data_especifica = pd.to_datetime(data_especifica).normalize()
        df_filtrado = df_filtrado[df_filtrado['DATA_NORMALIZADA'] == data_especifica]

    # ---------- Filtro por período ----------
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
            pass  # Não aplica filtro de período

    # ---------- Filtro por produtos ----------
    if produtos:
        df_filtrado = df_filtrado[df_filtrado['CRE_PRO_DESCRICAO'].isin(produtos)]

    # ---------- Filtro por fornecedores ----------
    if fornecedores:
        df_filtrado = df_filtrado[df_filtrado['CRE_PRODUTOR_NOME'].isin(fornecedores)]

    return df_filtrado
