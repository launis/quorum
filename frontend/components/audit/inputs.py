import streamlit as st


def render_file_inputs():
    """Renders the file upload section for the 3 required audit artifacts.
    Returns a dictionary suitable for API submission:
    { 'history_text': (name, bytes), ... }.
    """
    st.header("1. Syötä Todistusaineisto (Evidence)")

    col1, col2 = st.columns(2)
    with col1:
        history_file = st.file_uploader("Keskusteluhistoria (Chat Logs)", type=["txt", "pdf", "docx"])
    with col2:
        product_file = st.file_uploader("Lopputuote (Final Product)", type=["txt", "pdf", "docx"])
        reflection_file = st.file_uploader("Itsearviointi (Reflection)", type=["txt", "pdf", "docx"])

    files = {}
    if history_file:
        files["history_text"] = (history_file.name, history_file.getvalue())
    if product_file:
        files["product_text"] = (product_file.name, product_file.getvalue())
    if reflection_file:
        files["reflection_text"] = (reflection_file.name, reflection_file.getvalue())

    return files
