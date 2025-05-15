import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📤 Exportación", layout="wide")
st.title("📁 Exportador de Datos")

uploaded_file = st.file_uploader("📁 Base para exportar", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    col = st.selectbox("Filtrar por columna", df.columns)
    val = st.selectbox("Valor", df[col].dropna().unique())
    filtrado = df[df[col] == val]
    formato = st.selectbox("Formato", ["CSV", "Excel", "JSON"])

    if formato == "CSV":
        st.download_button("Descargar CSV", filtrado.to_csv(index=False), "datos.csv", "text/csv")
    elif formato == "Excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output) as writer:
            filtrado.to_excel(writer, index=False)
        st.download_button("Descargar Excel", output.getvalue(), "datos.xlsx")
    else:
        st.download_button("Descargar JSON", filtrado.to_json(orient="records"), "datos.json", "application/json")