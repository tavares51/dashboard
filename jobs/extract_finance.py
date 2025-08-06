import os
import pyodbc
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# ===========================
# 1. Carregar variáveis do .env
# ===========================
load_dotenv()

DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
BRONZE_PATH = "data/bronze/financeiro"

# Cria a pasta Bronze se não existir
os.makedirs(BRONZE_PATH, exist_ok=True)

# Query para extrair dados
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

# Nome do arquivo CSV com timestamp
nome_arquivo = "dados_saida_financeiro.csv"
caminho_arquivo = os.path.join(BRONZE_PATH, nome_arquivo)

# ===========================
# 2. Extrair e salvar CSV
# ===========================
try:
    print("🔹 Conectando ao SQL Server...")
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_DATABASE};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD}"
    )

    print("🔹 Executando query...")
    df = pd.read_sql(QUERY, conn)

    print(f"🔹 Salvando CSV em {caminho_arquivo}...")
    df.to_csv(caminho_arquivo, index=False, sep=';', encoding='utf-8-sig')

    print(f"✅ Job finalizado! Arquivo salvo: {caminho_arquivo}")

except Exception as e:
    print("❌ Erro ao executar job:", e)

finally:
    try:
        conn.close()
    except:
        pass
