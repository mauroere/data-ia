import streamlit as st
import pandas as pd
import openai
from fuzzywuzzy import fuzz

def are_similar(a, b, threshold=85):
    return fuzz.token_sort_ratio(str(a), str(b)) >= threshold

def normalize_column_names(columns):
    import re
    return [re.sub(r'[^a-zA-Z0-9]', '_', col.strip().lower()) for col in columns]



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

st.set_page_config(page_title="Cruce Inteligente", layout="wide")
st.title("🔄 Cruce Inteligente de Datos")

openai.api_key = st.secrets["openai"]["api_key"]

uploaded_file_1 = st.file_uploader("📁 Subí archivo BASE (existente)", type=[["csv", "xlsx"]])
uploaded_file_2 = st.file_uploader("📁 Subí archivo NUEVO (a cruzar)", type=[["csv", "xlsx"]])

if uploaded_file_1 and uploaded_file_2:
    base_df = read_flexible_file(uploaded_file_1)
    new_df = read_flexible_file(uploaded_file_2)

    new_df.columns = normalize_column_names(new_df.columns)
    base_df.columns = normalize_column_names(base_df.columns)

    campo_clave = st.selectbox("Seleccioná campo clave", new_df.columns)
    coincidencias = []

    for _, fila in new_df.iterrows():
        val = fila[campo_clave]
        for _, bfila in base_df.iterrows():
            if are_similar(val, bfila[campo_clave]):
                coincidencias.append((val, bfila[campo_clave]))
                break

    st.success(f"{len(coincidencias)} coincidencias encontradas.")
    st.dataframe(pd.DataFrame(coincidencias, columns=["Nuevo", "Base"]))