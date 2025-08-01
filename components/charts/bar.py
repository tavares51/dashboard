import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta


def grafico_entrada_saida_por_data(df, dias: int = 15):
    """
    Gera e exibe um gráfico de barras com o peso líquido total de Entradas e Saídas por data,
    considerando apenas os últimos X dias.

    Args:
        df (pd.DataFrame): DataFrame contendo as colunas 
            'TIPO', 'CRE_DATA_ENTRADA', 'CRE_PESO_LIQUIDO'
        dias (int): Número de dias anteriores a considerar (padrão: 15)
    """
    # Garantir tipos corretos
    df['CRE_DATA_ENTRADA'] = pd.to_datetime(df['CRE_DATA_ENTRADA'], errors='coerce')
    df['CRE_PESO_LIQUIDO'] = pd.to_numeric(df['CRE_PESO_LIQUIDO'], errors='coerce')
    df['TIPO'] = df['TIPO'].str.strip().str.lower().replace({
        'entrada': 'Entrada',
        'saida': 'Saída'
    })

    # Filtrar pelos últimos X dias
    limite_data = datetime.now() - timedelta(days=dias)
    df = df[df['CRE_DATA_ENTRADA'] >= limite_data]

    if df.empty:
        st.warning(f"Nenhum dado encontrado nos últimos {dias} dias.")
        return None

    # Agrupar por data e tipo, somando o peso líquido
    df_tipo_dia = (
        df.groupby([df['CRE_DATA_ENTRADA'].dt.date, 'TIPO'])['CRE_PESO_LIQUIDO']
        .sum()
        .reset_index(name='Peso_Liquido')
        .rename(columns={'CRE_DATA_ENTRADA': 'Data'})
    )

    # Cores personalizadas
    cores_personalizadas = {
        'Entrada': '#1f77b4',  # azul
        'Saída': "#a04b00"     # laranja
    }

    # Criar gráfico de barras
    fig = px.bar(
        df_tipo_dia,
        x='Data',
        y='Peso_Liquido',
        color='TIPO',
        height=350,
        color_discrete_map=cores_personalizadas,
        title=f'Peso Líquido de Entradas e Saídas por Data (últimos {dias} dias)',
        labels={'TIPO': 'Tipo', 'Peso_Liquido': 'Peso Líquido (kg)'}
    )

    # Ajustes visuais
    fig.update_traces(texttemplate='%{y:.0f}', textposition='outside')
    fig.update_layout(
        xaxis_title='Data',
        yaxis_title='Peso Líquido (kg)',
        barmode='group',
        xaxis_tickformat='%d/%m/%Y',
        legend_title=''
    )
    fig.update_traces(textposition='inside' )

    return fig


def grafico_produtor(df, top_n=5):
    """
    Gera um gráfico de barras horizontal com os principais produtores
    pelo peso líquido movimentado (Entrada + Saída somados).

    Parâmetros:
        df (pd.DataFrame): DataFrame com colunas
            ['CRE_PRODUTOR_CODIGO', 'CRE_PRODUTOR_NOME', 'CRE_PESO_LIQUIDO']
        top_n (int): Quantidade de produtores no ranking.
                     Se None ou 0, retorna todos.

    Retorna:
        fig (plotly.graph_objs._figure.Figure): Figura interativa pronta para Streamlit
    """
    # Garantir colunas necessárias
    cols_needed = ['CRE_PRODUTOR_CODIGO',
                   'CRE_PRODUTOR_NOME', 'CRE_PESO_LIQUIDO']
    if not all(col in df.columns for col in cols_needed):
        raise ValueError(
            "O DataFrame não possui todas as colunas necessárias.")

    # Garantir que peso seja numérico
    df['CRE_PESO_LIQUIDO'] = pd.to_numeric(
        df['CRE_PESO_LIQUIDO'], errors='coerce')

    # Agrupar por produtor (código + nome)
    agg_df = df.groupby(['CRE_PRODUTOR_CODIGO', 'CRE_PRODUTOR_NOME'])[
        'CRE_PESO_LIQUIDO'].sum().reset_index()

    # Ordenar pelo total movimentado
    agg_df = agg_df.sort_values('CRE_PESO_LIQUIDO', ascending=False)

    # Aplicar top_n se definido
    if top_n and top_n > 0:
        agg_df = agg_df.head(top_n)

    # Criar gráfico horizontal interativo
    fig = px.bar(
        agg_df,
        x='CRE_PESO_LIQUIDO',
        y='CRE_PRODUTOR_NOME',
        orientation='h',
        text='CRE_PESO_LIQUIDO',
        title=f'Maiores Fornecedores ',
        color_discrete_sequence=['#1f77b4']  # cor azul padrão
    )

    # Ajustes visuais
    fig.update_layout(
        xaxis_title='Peso Líquido (kg)',
        yaxis_title='Fornecedor',
        height=max(200, 50 * len(agg_df)),
        yaxis={'categoryorder': 'total ascending'},
        bargap=0.1,
        margin=dict(l=200, r=20, t=50, b=50)
    )
    fig.update_traces(texttemplate='%{text:.0f}', textposition='inside',
                      insidetextanchor='end', )

    return fig


def grafico_barras_produto(df, top_n=None):
    """
    Gera um gráfico de barras horizontal mostrando a quantidade total por tipo de produto em estoque.

    Parâmetros:
        df (pd.DataFrame): DataFrame com colunas 
            ['CRE_PRO_DESCRICAO', 'CRE_PESO_LIQUIDO']
        top_n (int, opcional): Quantidade máxima de produtos exibidos. 
                               Se None, mostra todos.

    Retorna:
        fig (plotly.graph_objs._figure.Figure): Figura interativa pronta para Streamlit
    """
    # Garantir colunas necessárias
    cols_needed = ['CRE_PRO_DESCRICAO', 'CRE_PESO_LIQUIDO']
    if not all(col in df.columns for col in cols_needed):
        raise ValueError(
            "O DataFrame não possui todas as colunas necessárias.")

    # Garantir que peso seja numérico
    df['CRE_PESO_LIQUIDO'] = pd.to_numeric(
        df['CRE_PESO_LIQUIDO'], errors='coerce')

    # Agrupar por produto
    resumo = df.groupby('CRE_PRO_DESCRICAO', as_index=False)[
        'CRE_PESO_LIQUIDO'].sum()

    # Ordenar do maior para o menor
    resumo = resumo.sort_values('CRE_PESO_LIQUIDO', ascending=False)

    # Aplicar top_n se definido
    if top_n and top_n > 0:
        resumo = resumo.head(top_n)

    # Criar gráfico de barras horizontal
    fig = px.bar(
        resumo,
        x='CRE_PESO_LIQUIDO',
        y='CRE_PRO_DESCRICAO',
        orientation='h',
        text='CRE_PESO_LIQUIDO',
        title=f'Distribuição Total por Tipo de Produto em Estoque',
        color_discrete_sequence=['#1f77b4']  # cor azul padrão
    )

    # Ajustes visuais
    fig.update_layout(
        xaxis_title='Peso Líquido (kg)',
        yaxis_title='Produto',
        height=max(200, 50 * len(resumo)),  # altura dinâmica
        yaxis={'categoryorder': 'total ascending'},
        bargap=0.1,
        margin=dict(l=180, r=20, t=50, b=50),
        overwrite=True
    )

    fig.update_traces(
        texttemplate='%{text:.0f}',
        textposition='inside',
        insidetextanchor='end',  # alinha à esquerda dentro da barra
        textfont=dict(color='white')
    )

    return fig
