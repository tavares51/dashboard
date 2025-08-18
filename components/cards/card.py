import streamlit as st


def card_html(title, content, title_size="12px", content_size="16px"):
    """
    Cria um card com tamanho de fonte customizável.

    Args:
        title (str): Título do card
        content (str): Conteúdo do card
        title_size (str): Tamanho da fonte do título (ex: "18px", "1.2em")
        content_size (str): Tamanho da fonte do conteúdo (ex: "24px", "2em")
    """
    st.markdown(
        f"""
        <div style="
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
        ">
            <div style="font-size:{title_size}; font-weight:bold;">{title}</div>
            <div style="font-size:{content_size};">{content}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def card(title, content):
    with st.container(border=True):
        st.write(title)
        st.subheader(content)
