import streamlit as st

from page_link import page_link


def home() -> None:
    """Display the home page of the Streamlit app."""
    # サイドバーにページリンクを表示
    page_link()

    st.title("DuckDBとStreamlitによるBIツール")


if __name__ == "__main__":
    home()
