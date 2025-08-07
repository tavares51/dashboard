import os
import pyodbc
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import logging


load_dotenv()

DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

logger = logging.getLogger('error_logger')
logger.setLevel(logging.ERROR)

if not logger.handlers:
    handler = logging.FileHandler('error.log')
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_data(path="data/bronze/financeiro/dados_saida_financeiro.csv"):
    """
    Processa uma base de dados CSV e exporta um CSV resumido com colunas de data e informações derivadas.

    Args:
        path (str): Caminho do arquivo CSV de SAIDA.
    """
    try:
        
        QUERY = """
            select 
                NFI_NUMERO
                , NFI_RAZAO
                , NFI_CNPJ
                , NFI_DATA_EMISSAO
                , NFI_DATA_SAIDA
                , NFI_VALOR_TOTAL_PRODUTO
                , NFI_VALOR_TOTAL_PRODUTO_BRUTO
                , NFI_VALOR_TOTAL_NOTA
            from NOTA_FISCAL where NFI_TIPO = 0
                order by NFI_DATA_EMISSAO desc
        """

        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_DATABASE};"
            f"UID={DB_USER};"
            f"PWD={DB_PASSWORD}"
        )        
        
        df_resumido = pd.read_sql(QUERY, conn)

        datas = ['NFI_DATA_EMISSAO', 'NFI_DATA_SAIDA']
        for coluna in datas:
            df_resumido[coluna] = pd.to_datetime(
                df_resumido[coluna], errors='coerce')

        df_resumido['MES_EMISSAO'] = df_resumido['NFI_DATA_EMISSAO'].dt.month.astype(
            'Int64')
        df_resumido['ANO_EMISSAO'] = df_resumido['NFI_DATA_EMISSAO'].dt.year.astype(
            'Int64')
        df_resumido['DIA_SEMANA_EMISSAO'] = df_resumido['NFI_DATA_EMISSAO'].dt.day_name()
        df_resumido['DIA_EMISSAO'] = df_resumido['NFI_DATA_EMISSAO'].dt.day.astype(
            'Int64')

        df_resumido['MES_SAIDA'] = df_resumido['NFI_DATA_SAIDA'].dt.month.astype(
            'Int64')
        df_resumido['ANO_SAIDA'] = df_resumido['NFI_DATA_SAIDA'].dt.year.astype(
            'Int64')
        df_resumido['DIA_SEMANA_SAIDA'] = df_resumido['NFI_DATA_SAIDA'].dt.day_name()
        df_resumido['DIA_SAIDA'] = df_resumido['NFI_DATA_SAIDA'].dt.day.astype(
            'Int64')

        # Mapeamento dos dias da semana para números
        day_name_map = {
            'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4,
            'Friday': 5, 'Saturday': 6, 'Sunday': 7
        }

        df_resumido['DIA_SEMANA_EMISSAO'] = df_resumido['DIA_SEMANA_EMISSAO'].map(
            day_name_map)
        df_resumido['DIA_SEMANA_SAIDA'] = df_resumido['DIA_SEMANA_SAIDA'].map(
            day_name_map)

        return df_resumido

    except Exception as e:
        print(f"Erro: {str(e)}.")
        logger.error(f"Erro: {str(e)}.", exc_info=True)


if __name__ == "__main__":
    _ = get_data()
    print()
