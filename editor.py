import streamlit as st
import pandas as pd


def read_flexible_file(uploaded_file):
    import pandas as pd
    import chardet

    file_name = uploaded_file.name.lower()
    if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
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


st.set_page_config(page_title="✏️ Editor", layout="wide")
st.title("🛠️ Edición de Datos")

uploaded_file = st.file_uploader("📁 Cargá CSV o Excel", type=["csv", "xls", "xlsx"])
if uploaded_file:
    df = read_flexible_file(uploaded_file)
    st.dataframe(df)

    fila = st.number_input("Fila a editar", min_value=0, max_value=len(df)-1)
    columna = st.selectbox("Columna", df.columns)
    nuevo_valor = st.text_input("Nuevo valor")

    if st.button("Actualizar"):
        df.at[fila, columna] = nuevo_valor
        st.success(f"Fila {fila}, columna {columna} actualizada.")

    st.download_button("📥 Descargar CSV", df.to_csv(index=False), "actualizado.csv", "text/csv")