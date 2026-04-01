import streamlit as st


def page_link() -> None:
    """Display the page links in the sidebar."""
    with st.sidebar:
        st.page_link("Home.py", label="ホーム", icon="🏠")
        st.page_link("pages/CSV_Upload.py", label="CSVアップロード", icon="📄")
        st.page_link("pages/s3_file_analyze.py", label="分析", icon="📊")
