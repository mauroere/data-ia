import streamlit as st
import pandas as pd
import openai
from fuzzywuzzy import fuzz

def read_flexible_file(uploaded_file):
    import chardet
    import io

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

def are_similar(a, b, threshold=85):
    return fuzz.token_sort_ratio(str(a), str(b)) >= threshold

def normalize_column_names(columns):
    import re
    return [re.sub(r'[^a-zA-Z0-9]', '_', col.strip().lower()) for col in columns]

st.set_page_config(page_title="Cruce Inteligente", layout="wide")
st.title("🔄 Cruce Inteligente de Datos")

# Inicializar cliente OpenAI compatible con v1.0.0+
client = openai.OpenAI(api_key=st.secrets["openai"]["api_key"])

uploaded_file_1 = st.file_uploader("📁 Subí archivo BASE (existente)", type=["csv", "xls", "xlsx"])
uploaded_file_2 = st.file_uploader("📁 Subí archivo NUEVO (a cruzar)", type=["csv", "xls", "xlsx"])

if uploaded_file_1 and uploaded_file_2:
    base_df = read_flexible_file(uploaded_file_1)
    new_df = read_flexible_file(uploaded_file_2)

    new_df.columns = normalize_column_names(new_df.columns)
    base_df.columns = normalize_column_names(base_df.columns)
# Validación de columnas clave
# Validación de columnas clave (afuera de bloques anidados)
# Validación de columnas clave solo si hay datos
        # Validación de columnas clave solo si hay datos

# Validación de columnas requeridas


    campo_clave = st.selectbox("Seleccioná campo clave", new_df.columns)
    coincidencias = []
    if campo_clave not in base_df.columns:
        st.error(f"❌ La columna '{campo_clave}' no existe en la base cargada.")
        st.stop()

    for _, fila in new_df.iterrows():
        val = fila[campo_clave]
        for _, bfila in base_df.iterrows():
            if are_similar(val, bfila[campo_clave]):
                coincidencias.append((val, bfila[campo_clave]))
                break

    st.success(f"{len(coincidencias)} coincidencias encontradas.")
    st.dataframe(pd.DataFrame(coincidencias, columns=["Nuevo", "Base"]))

# Asistente conversacional
st.title("💬 Asistente Conversacional")
pregunta = st.text_input("Hacé una pregunta sobre la base cargada:")
if pregunta:
    with st.spinner("Procesando..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": pregunta}],
                temperature=0.3
            )
            respuesta = response.choices[0].message.content
            st.success("Respuesta del asistente:")
            st.text_area("", respuesta, height=200)
            # Guardar historial
            if 'historial' not in st.session_state:
                st.session_state.historial = []
            st.session_state.historial.append((pregunta, respuesta))
        except Exception as e:
            st.error(f"Error al procesar la pregunta: {e}")

# Historial de interacciones
if 'historial' in st.session_state and st.session_state.historial:
    st.title("🕓 Historial de Interacciones")
    for i, (p, r) in enumerate(st.session_state.historial):
        st.text(f"Pregunta {i+1}: {p}")
        st.text(f"Respuesta: {r}")
        st.markdown("---")
    if st.button("Descargar Historial"):
        df_historial = pd.DataFrame(st.session_state.historial, columns=["Pregunta", "Respuesta"])
        st.download_button("📥 Descargar CSV", df_historial.to_csv(index=False), "historial.csv", "text/csv")