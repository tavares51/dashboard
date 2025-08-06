import pandas as pd
from datetime import datetime, timedelta
from data.silver.financeiro.data_fincance_silver import get_data

def carregar_dados():
    return get_data()

def obter_dados_filtrados(
    periodo: str = "Todos",
    fornecedores: list = None,
    mes=None, 
    ano=None, 
    semanas: int = None
):
    """
    Retorna os dados da camada gold com filtros opcionais:
    - motorista (str ou None)
    - periodo (str): "Hoje", "Última Semana", "Últimos 15 Dias", "Últimos 30 Dias", 
                     "Mês Atual", "Ano Atual", "Todos"
    - produtos (list): lista de produtos para filtrar
    - fornecedores (list): lista de fornecedores para filtrar
    - mes (int ou None)
    - ano (int ou None)
    - semanas (int ou None): número de semanas anteriores (se informado, ignora mês e ano)
    """

    df = carregar_dados()

    # Garantir datetime
    df['NFI_DATA_SAIDA'] = pd.to_datetime(df['NFI_DATA_SAIDA'], errors='coerce')

    if semanas:  # prioridade sobre mês/ano
        dias = semanas * 7
        limite_data = datetime.now() - timedelta(days=dias)
        df = df[df['NFI_DATA_SAIDA'] >= limite_data]
    else:
        hoje = datetime.now().date()
        if periodo == "Hoje":
            df = df[df['NFI_DATA_SAIDA'].dt.date == hoje]
        elif periodo == "Última Semana":
            df = df[df['NFI_DATA_SAIDA'] >= datetime.now() - timedelta(days=7)]
        elif periodo == "Últimos 15 Dias":
            df = df[df['NFI_DATA_SAIDA'] >= datetime.now() - timedelta(days=15)]
        elif periodo == "Últimos 30 Dias":
            df = df[df['NFI_DATA_SAIDA'] >= datetime.now() - timedelta(days=30)]
        elif periodo == "Mês Atual":
            df = df[df['NFI_DATA_SAIDA'].dt.month == datetime.now().month]
        elif periodo == "Ano Atual":
            df = df[df['NFI_DATA_SAIDA'].dt.year == datetime.now().year]
        elif periodo == "Todos":
            # mantém tudo
            pass
        else:
            # Caso use mes/ano antigos como antes
            if mes:
                df = df[df['MES_SAIDA'] == int(mes)]
            if ano:
                df = df[df['MES_SAIDA'] == int(ano)]

    if fornecedores:
        df = df[df['NFI_RAZAO'].isin(fornecedores)]

    df = df.sort_values(by='NFI_DATA_SAIDA', ascending=False)
    return df

