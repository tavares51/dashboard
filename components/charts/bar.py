import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta


def grafico_entrada_saida_por_data(df, dias: int = 15, data_filtro=None):
    """
    Gera e exibe um gráfico de barras com o peso líquido total de Entradas e Saídas por data.
    - Se data_filtro for informado, mostra apenas aquele dia.
    - Caso contrário, mostra os últimos X dias.

    Args:
        df (pd.DataFrame): DataFrame contendo as colunas 
            'TIPO', 'CRE_DATA_ENTRADA', 'CRE_PESO_LIQUIDO'
        dias (int): Número de dias anteriores a considerar (padrão: 15)
        data_filtro (str|datetime.date, opcional): Filtra apenas uma data específica.
    """
    # Garantir tipos corretos
    df['CRE_DATA_ENTRADA'] = pd.to_datetime(
        df['CRE_DATA_ENTRADA'], errors='coerce')
    df['CRE_PESO_LIQUIDO'] = pd.to_numeric(
        df['CRE_PESO_LIQUIDO'], errors='coerce')
    df['TIPO'] = df['TIPO'].str.strip().str.lower().replace({
        'entrada': 'Entrada',
        'saida': 'Saída'
    })

    # Filtro de data
    if data_filtro:
        data_filtro = pd.to_datetime(data_filtro).date()
        df = df[df['CRE_DATA_ENTRADA'].dt.date == data_filtro]
        titulo = f"Peso Líquido de Entradas"
    else:
        limite_data = datetime.now() - timedelta(days=dias)
        df = df[df['CRE_DATA_ENTRADA'] >= limite_data]
        titulo = f"Peso Líquido de Entradas"

    if df.empty:
        st.warning("Nenhum dado encontrado para o filtro aplicado.")
        return None

    # Agrupar por data e tipo
    df_tipo_dia = (
        df.groupby([df['CRE_DATA_ENTRADA'].dt.date, 'TIPO'])[
            'CRE_PESO_LIQUIDO']
        .sum()
        .reset_index(name='Peso_Liquido')
        .rename(columns={'CRE_DATA_ENTRADA': 'Data'})
    )

    # Criar gráfico de barras
    fig = px.bar(
        df_tipo_dia,
        x='Data',
        y='Peso_Liquido',
        height=400,
        title=titulo,
        labels={'TIPO': 'Tipo', 'Peso_Liquido': 'Peso Líquido (kg)'}
    )

    # Ajustes visuais
    fig.update_layout(
        xaxis_title='Data',
        yaxis_title='Peso Líquido (kg)',
        barmode='group',
        xaxis_tickformat='%d/%m/%Y',
        legend_title='',
        overwrite=True
    )
    fig.update_traces(texttemplate='%{y:.0f}', textposition='inside')

    return fig


def grafico_produtor(df, top_n=None):
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
        title=f'Fornecedores ',
        color_discrete_sequence=['#1f77b4']  # cor azul padrão
    )

    # Ajustes visuais
    fig.update_layout(
        xaxis_title='Peso Líquido (kg)',
        yaxis_title='Fornecedor',
        height=max(250, 50 * len(agg_df)),
        yaxis={'categoryorder': 'total ascending'},
        bargap=0.1,
        margin=dict(l=200, r=20, t=50, b=30)
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
        title=f'Produtos',
        color_discrete_sequence=['#1f77b4']  # cor azul padrão
    )

    # Ajustes visuais
    fig.update_layout(
        xaxis_title='Peso Líquido (kg)',
        yaxis_title='Produto',
        height=max(250, 50 * len(resumo)),  # altura dinâmica
        yaxis={'categoryorder': 'total ascending'},
        bargap=0.1,
        margin=dict(l=180, r=20, t=50, b=30),
        overwrite=True
    )

    fig.update_traces(
        texttemplate='%{text:.0f}',
        textposition='inside',
        insidetextanchor='end',  # alinha à esquerda dentro da barra
        textfont=dict(color='white')
    )

    return fig


def grafico_financeiro_por_data(
    df: pd.DataFrame,
    *,
    dias: int | None = 15,
    data_filtro: str | datetime | None = None,
):
    # Requisitos mínimos
    req = {"VALOR_FINAL", "NFI_RAZAO", "NFI_DATA_EMISSAO"}
    if df is None or df.empty or any(c not in df.columns for c in req):
        return

    df = df.copy()

    # Datas (emissão)
    df["NFI_DATA_EMISSAO"] = pd.to_datetime(df["NFI_DATA_EMISSAO"], errors="coerce")
    try:
        df["NFI_DATA_EMISSAO"] = df["NFI_DATA_EMISSAO"].dt.tz_localize(None)
    except Exception:
        pass
    df["NFI_DATA_EMISSAO"] = df["NFI_DATA_EMISSAO"].dt.normalize()

    # Valor
    df["VALOR_FINAL"] = pd.to_numeric(df["VALOR_FINAL"], errors="coerce").fillna(0)

    titulo = "Faturamento por Cliente"

    # Se dia específico, filtra por igualdade
    if data_filtro is not None:
        alvo = pd.to_datetime(data_filtro, errors="coerce")
        if pd.isna(alvo):
            return
        try:
            alvo = alvo.tz_localize(None)
        except Exception:
            pass
        alvo = pd.to_datetime(alvo).normalize()
        df = df[df["NFI_DATA_EMISSAO"] == alvo]
    else:
        # Se vier 'dias', ancora no MÁXIMO da série (normalmente seu data_fim)
        if dias is not None:
            try:
                dias_int = max(int(dias), 0)
            except Exception:
                dias_int = 15

            if dias_int > 0:
                ref = df["NFI_DATA_EMISSAO"].max()
                if pd.isna(ref):
                    return
                ref = pd.to_datetime(ref).normalize()
                limite = ref - timedelta(days=dias_int - 1)
                df = df[df["NFI_DATA_EMISSAO"] >= limite]


    if df.empty:
        return

    dados = (
        df.groupby("NFI_RAZAO", as_index=False)["VALOR_FINAL"]
          .sum()
          .rename(columns={"NFI_RAZAO": "Cliente", "VALOR_FINAL": "Valor_Total"})
          .sort_values("Valor_Total", ascending=False)
    )
    if dados.empty or dados["Valor_Total"].sum() == 0:
        return

    fig = px.bar(
        dados,
        x="Cliente",
        y="Valor_Total",
        text="Valor_Total",
        color="Cliente",
        title=titulo,
        labels={"Valor_Total": "Valor Total (R$)", "Cliente": "Cliente"},
    )
    fig.update_traces(texttemplate="R$ %{y:,.2f}", textposition="outside", cliponaxis=False)
    fig.update_layout(
        xaxis_title="Cliente",
        yaxis_title="Valor Total (R$)",
        xaxis_tickangle=-15,
        height=520,
        margin=dict(l=0, r=0, t=60, b=0),
        showlegend=True,
        uniformtext_minsize=8,
        uniformtext_mode="hide",
    )
    return fig