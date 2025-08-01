import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

def exibir_tabela_resumida(df):
    df_tabela = df[['CRE_ID', 'CRE_DATA_ENTRADA', 'CRE_PRODUTOR_NOME',
                    'CRE_MOTORISTA_NOME', 'CRE_PRO_DESCRICAO','TIPO', 'CRE_PESO_LIQUIDO']].copy()
    df_tabela['CRE_DATA_ENTRADA'] = df_tabela['CRE_DATA_ENTRADA'].dt.strftime(
        '%d/%m/%Y')

    df_tabela = df_tabela.rename(columns={
        'CRE_ID': 'Número',
        'CRE_DATA_ENTRADA': 'Data de Entrada',
        'CRE_PESO_LIQUIDO': 'Peso Líq (kg)',
        'CRE_MOTORISTA_NOME': 'Motorista',
        'TIPO': 'Tipo',
        'CRE_PRO_DESCRICAO': 'Produto',
        'CRE_PRODUTOR_NOME': 'Fornecedor'
    })

    st.subheader("Lançamentos")
    st.data_editor(
        data=df_tabela,
        hide_index=True,
        disabled=True
    )