import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

def grafico_pizza_produto(df):
    """
    Gera um gráfico de pizza mostrando a quantidade total por tipo de produto em estoque.

    Parâmetros:
        df (pd.DataFrame): DataFrame com colunas 
            ['CRE_PRO_DESCRICAO', 'CRE_PESO_LIQUIDO']

    Retorna:
        fig (plotly.graph_objs._figure.Figure): Figura interativa pronta para Streamlit
    """
    # Garantir colunas necessárias
    cols_needed = ['CRE_PRO_DESCRICAO', 'CRE_PESO_LIQUIDO']
    if not all(col in df.columns for col in cols_needed):
        raise ValueError("O DataFrame não possui todas as colunas necessárias.")

    # Garantir que peso seja numérico
    df['CRE_PESO_LIQUIDO'] = pd.to_numeric(df['CRE_PESO_LIQUIDO'], errors='coerce')

    # Agrupar por descrição do produto
    resumo = df.groupby('CRE_PRO_DESCRICAO', as_index=False)['CRE_PESO_LIQUIDO'].sum()

    # Ordenar para deixar maiores fatias destacadas
    resumo = resumo.sort_values('CRE_PESO_LIQUIDO', ascending=False)

    # Criar gráfico de pizza (donut)
    fig = px.pie(
        resumo,
        names='CRE_PRO_DESCRICAO',
        values='CRE_PESO_LIQUIDO',
        title='Distribuição Total por Tipo de Produto em Estoque',
        hole=0.3
    )

    # Mostrar rótulo e valor
    fig.update_traces(
        textinfo='label+value',
        pull=[0.05] * len(resumo)  # puxa levemente todas as fatias
    )

    # Ajustes visuais
    fig.update_layout(
        legend_title='Produto',
        height=400,
        margin=dict(t=50, b=20, l=20, r=20)
    )

    return fig
