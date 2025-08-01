import pandas as pd
from datetime import datetime, timedelta
from data.silver.estoque.data_silver import get_data

def carregar_dados():
    return get_data()

def obter_dados_filtrados(
    motorista=None, 
    periodo: str = "Todos",
    produtos: list = None,
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
    df['CRE_DATA_ENTRADA'] = pd.to_datetime(df['CRE_DATA_ENTRADA'], errors='coerce')

    # ---------------------
    # 1) Filtro Motorista
    # ---------------------
    if motorista:
        df = df[df['CRE_MOTORISTA_NOME'].str.contains(motorista, case=False, na=False)]

    # ---------------------
    # 2) Filtro de Período
    # ---------------------
    if semanas:  # prioridade sobre mês/ano
        dias = semanas * 7
        limite_data = datetime.now() - timedelta(days=dias)
        df = df[df['CRE_DATA_ENTRADA'] >= limite_data]
    else:
        hoje = datetime.now().date()
        if periodo == "Hoje":
            df = df[df['CRE_DATA_ENTRADA'].dt.date == hoje]
        elif periodo == "Última Semana":
            df = df[df['CRE_DATA_ENTRADA'] >= datetime.now() - timedelta(days=7)]
        elif periodo == "Últimos 15 Dias":
            df = df[df['CRE_DATA_ENTRADA'] >= datetime.now() - timedelta(days=15)]
        elif periodo == "Últimos 30 Dias":
            df = df[df['CRE_DATA_ENTRADA'] >= datetime.now() - timedelta(days=30)]
        elif periodo == "Mês Atual":
            df = df[df['CRE_DATA_ENTRADA'].dt.month == datetime.now().month]
        elif periodo == "Ano Atual":
            df = df[df['CRE_DATA_ENTRADA'].dt.year == datetime.now().year]
        elif periodo == "Todos":
            # mantém tudo
            pass
        else:
            # Caso use mes/ano antigos como antes
            if mes:
                df = df[df['MES_ENTRADA'] == int(mes)]
            if ano:
                df = df[df['ANO_ENTRADA'] == int(ano)]

    # ---------------------
    # 3) Filtro Produto
    # ---------------------
    if produtos:
        df = df[df['CRE_PRO_DESCRICAO'].isin(produtos)]

    # ---------------------
    # 4) Filtro Fornecedor
    # ---------------------
    if fornecedores:
        df = df[df['CRE_PRODUTOR_NOME'].isin(fornecedores)]

    # ---------------------
    # Ordenação final
    # ---------------------
    df = df.sort_values(by='CRE_DATA_ENTRADA', ascending=False)
    return df


def obter_quantidade_saida(hoje=True):
    pass


def obter_quantidade_entrada(hoje=False):
    pass
