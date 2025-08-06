import pandas as pd
import logging

# Configuração do logger
logger = logging.getLogger('error_logger')
logger.setLevel(logging.ERROR)

# Evita adicionar múltiplos handlers se o script for executado mais de uma vez
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
        df = pd.read_csv(path, sep=';', engine='python')

        df_resumido = df.copy()

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