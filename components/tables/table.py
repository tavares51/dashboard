import streamlit as st
import pandas as pd


def exibir_tabela_resumida(df):
    df_tabela = df[['CRE_ID', 'CRE_DATA_ENTRADA', 'CRE_PRODUTOR_NOME',
                    'CRE_MOTORISTA_NOME', 'CRE_PRO_DESCRICAO', 'TIPO', 'CRE_PESO_LIQUIDO']].copy()
    df_tabela['CRE_DATA_ENTRADA'] = df_tabela['CRE_DATA_ENTRADA'].dt.strftime('%d/%m/%Y')

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
    st.dataframe(df_tabela, hide_index=True)


def exibir_saidas(df):
    df_tabela = df[['NFI_DATA_EMISSAO', 'NFI_CNPJ', 'NFI_RAZAO',
                    'NFI_DATA_SAIDA', 'NFI_VALOR_TOTAL_NOTA']].copy()
    df_tabela['NFI_DATA_EMISSAO'] = df_tabela['NFI_DATA_EMISSAO'].dt.strftime('%d/%m/%Y')
    df_tabela['NFI_DATA_SAIDA'] = df_tabela['NFI_DATA_SAIDA'].dt.strftime('%d/%m/%Y')

    df_tabela = df_tabela.rename(columns={
        'NFI_DATA_EMISSAO': 'Emissão',
        'NFI_CNPJ': 'CNPJ',
        'NFI_RAZAO': 'Razão Social',
        'NFI_DATA_SAIDA': 'Saída',
        'NFI_VALOR_TOTAL_NOTA': 'Valor da Nota (R$)'
    })

    st.subheader("Saídas")
    st.dataframe(df_tabela, hide_index=True)
