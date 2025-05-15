import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="📊 Dashboard", layout="wide")
st.title("📈 Visualización de Datos")

uploaded_file = st.file_uploader("📁 Subí la base", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    col = st.selectbox("Filtrar por columna", df.columns)
    val = st.selectbox("Seleccioná un valor", df[col].dropna().unique())
    subset = df[df[col] == val]
    st.dataframe(subset)

    metric = st.selectbox("Métrica para gráfico", df.columns)
    chart = alt.Chart(df[metric].value_counts().reset_index()).mark_bar().encode(
        x="index", y=metric, tooltip=["index", metric]
    )
    st.altair_chart(chart, use_container_width=True)