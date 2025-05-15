import streamlit as st
import pandas as pd
import openai
from fuzzywuzzy import fuzz

def are_similar(a, b, threshold=85):
    return fuzz.token_sort_ratio(str(a), str(b)) >= threshold

def normalize_column_names(columns):
    import re
    return [re.sub(r'[^a-zA-Z0-9]', '_', col.strip().lower()) for col in columns]

st.set_page_config(page_title="Cruce Inteligente", layout="wide")
st.title("🔄 Cruce Inteligente de Datos")

openai.api_key = st.secrets["openai"]["api_key"]

uploaded_file_1 = st.file_uploader("📁 Subí archivo BASE (existente)", type=["csv"])
uploaded_file_2 = st.file_uploader("📁 Subí archivo NUEVO (a cruzar)", type=["csv"])

if uploaded_file_1 and uploaded_file_2:
    base_df = pd.read_csv(uploaded_file_1)
    new_df = pd.read_csv(uploaded_file_2)

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