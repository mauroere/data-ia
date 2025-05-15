import streamlit as st
import pandas as pd
import io



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

st.set_page_config(page_title="📤 Exportación", layout="wide")
st.title("📁 Exportador de Datos")

uploaded_file = st.file_uploader("📁 Base para exportar", type=[["csv", "xlsx"]])
if uploaded_file:
    df = read_flexible_file(uploaded_file)
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