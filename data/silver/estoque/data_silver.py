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


def get_data(path="data/bronze/estoque/dados_entrada_estoque.csv"):
    """
    Processa uma base de dados CSV e exporta um CSV resumido com colunas de data e informações derivadas.

    Args:
        path (str): Caminho do arquivo CSV de entrada.
    """
    try:
        df = pd.read_csv(path, sep=';', engine='python')

        # Seleção das colunas relevantes
        colunas = [
            'CRE_ID', 'CRE_PESO_ENTRADA',
            'CRE_PESO_SAIDA', 'CRE_PESO_LIQUIDO', 'TIPO', 'CRE_DATAINC',
            'CRE_DATA_ENTRADA', 'CRE_DATA_ROMANEIO', 'CRE_DATA_SAIDA',
            'TIPO_COBRANCA_ARMAZENAGEM', 'STATUS_ROMANEIO', 'CRE_MOTORISTA_NOME',    
            'CRE_PRODUTOR_CODIGO', 'CRE_PRODUTOR_NOME', 'CRE_PRODUTOR_CIDADE',
            'CRE_PRO_DESCRICAO'
        ]
        df_resumido = df[colunas].copy()

        # Conversões de data
        datas = ['CRE_DATAINC', 'CRE_DATA_ENTRADA',
                 'CRE_DATA_ROMANEIO', 'CRE_DATA_SAIDA']
        for coluna in datas:
            df_resumido[coluna] = pd.to_datetime(
                df_resumido[coluna], errors='coerce')

        # Derivação de informações da entrada
        df_resumido['MES_ENTRADA'] = df_resumido['CRE_DATA_ENTRADA'].dt.month.astype(
            'Int64')
        df_resumido['ANO_ENTRADA'] = df_resumido['CRE_DATA_ENTRADA'].dt.year.astype(
            'Int64')
        df_resumido['DIA_SEMANA_ENTRADA'] = df_resumido['CRE_DATA_ENTRADA'].dt.day_name()
        df_resumido['DIA_ENTRADA'] = df_resumido['CRE_DATA_ENTRADA'].dt.day.astype(
            'Int64')

        # Derivação de informações da saída
        df_resumido['MES_SAIDA'] = df_resumido['CRE_DATA_SAIDA'].dt.month.astype(
            'Int64')
        df_resumido['ANO_SAIDA'] = df_resumido['CRE_DATA_SAIDA'].dt.year.astype(
            'Int64')
        df_resumido['DIA_SEMANA_SAIDA'] = df_resumido['CRE_DATA_SAIDA'].dt.day_name()
        df_resumido['DIA_SAIDA'] = df_resumido['CRE_DATA_SAIDA'].dt.day.astype(
            'Int64')

        # Mapeamento dos dias da semana para números
        day_name_map = {
            'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4,
            'Friday': 5, 'Saturday': 6, 'Sunday': 7
        }

        df_resumido['DIA_SEMANA_ENTRADA'] = df_resumido['DIA_SEMANA_ENTRADA'].map(
            day_name_map)
        df_resumido['DIA_SEMANA_SAIDA'] = df_resumido['DIA_SEMANA_SAIDA'].map(
            day_name_map)
        
        df_resumido = df_resumido[df_resumido['TIPO'] == 'ENTRADA']

        return df_resumido

    except Exception as e:
        logger.error(f"Erro: {str(e)}.", exc_info=True)


if __name__ == "__main__":
    _ = get_data("data/bronze/estoque/dados_entrada_estoque.csv")
