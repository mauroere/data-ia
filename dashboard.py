import streamlit as st
import pandas as pd
import altair as alt



def read_flexible_file(uploaded_file):
    import pandas as pd
    import chardet
    import io

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)

    rawdata = uploaded_file.read()
    uploaded_file.seek(0)
    result = chardet.detect(rawdata)
    encoding = result['encoding']

    try_separators = [',', ';', '\t']
    for sep in try_separators:
        try:
            df = pd.read_csv(uploaded_file, sep=sep, encoding=encoding)
            if df.shape[1] > 1:
                return df
        except Exception:
            uploaded_file.seek(0)
    uploaded_file.seek(0)
    return pd.read_csv(uploaded_file, encoding=encoding)

    rawdata = uploaded_file.read()
    uploaded_file.seek(0)
    result = chardet.detect(rawdata)
    encoding = result['encoding']

    try_separators = [',', ';', '\t']
    for sep in try_separators:
        try:
            df = pd.read_csv(uploaded_file, sep=sep, encoding=encoding)
            if df.shape[1] > 1:
                return df
        except Exception:
            uploaded_file.seek(0)
    uploaded_file.seek(0)
    return pd.read_csv(uploaded_file, encoding=encoding)

st.set_page_config(page_title="📊 Dashboard", layout="wide")
st.title("📈 Visualización de Datos")

uploaded_file = st.file_uploader("📁 Subí la base", type=[[["csv", "xlsx"], "xlsx"]])
if uploaded_file:
    df = read_flexible_file(uploaded_file)
    col = st.selectbox("Filtrar por columna", df.columns)
    val = st.selectbox("Seleccioná un valor", df[col].dropna().unique())
    subset = df[df[col] == val]
    st.dataframe(subset)

    metric = st.selectbox("Métrica para gráfico", df.columns)
    chart = alt.Chart(df[metric].value_counts().reset_index()).mark_bar().encode(
        x="index", y=metric, tooltip=["index", metric]
    )
    st.altair_chart(chart, use_container_width=True)