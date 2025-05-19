import streamlit as st
import pandas as pd
import httpx
from fuzzywuzzy import fuzz
import urllib3
import os
from typing import Optional

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

def make_api_request(pregunta: str) -> dict:
    """Realiza una petición a la API de Redpill.io"""
    headers = {
        "Authorization": f"Bearer {REDPILL_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    payload = {
        "model": "redpill-1",
        "messages": [{"role": "user", "content": pregunta}],
        "temperature": 0.3
    }
    
    try:
        # Configuración específica para manejar el error SSL
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        transport = httpx.HTTPTransport(verify=False)
        with httpx.Client(timeout=30.0, transport=transport, verify=False) as client:
            response = client.post(
                REDPILL_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        st.error(f"Error de conexión: {str(e)}")
        raise

# Configuración de Redpill.io
REDPILL_API_KEY = "sk-xYBWXr1epqP3Uq1A05qUql9tAyBsJE5F8PL5L66gBaE328VG"
REDPILL_API_URL = "https://api.redpill.io/v1/chat/completions"

# Configuración de requests para manejar problemas SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="Cruce Inteligente", layout="wide")
st.title("🔄 Cruce Inteligente de Datos")

uploaded_file_1 = st.file_uploader("📁 Subí archivo BASE (existente)", type=["csv", "xls", "xlsx"])
uploaded_file_2 = st.file_uploader("📁 Subí archivo NUEVO (a cruzar)", type=["csv", "xls", "xlsx"])

if uploaded_file_1 and uploaded_file_2:
    base_df = read_flexible_file(uploaded_file_1)
    new_df = read_flexible_file(uploaded_file_2)

    new_df.columns = normalize_column_names(new_df.columns)
    base_df.columns = normalize_column_names(base_df.columns)

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
            response_data = make_api_request(pregunta)
            respuesta = response_data["choices"][0]["message"]["content"]
            st.success("Respuesta del asistente:")
            st.text_area("", respuesta, height=200)
            
            # Guardar historial
            if 'historial' not in st.session_state:
                st.session_state.historial = []
            st.session_state.historial.append((pregunta, respuesta))
            
        except httpx.HTTPError as e:
            error_message = str(e)
            if "429" in error_message:
                st.error("""
                ❌ Se ha excedido el límite de uso de la API de Redpill.io. 
                
                Para resolver esto:
                1. Verifica tu saldo en el panel de control de Redpill.io
                2. Actualiza tu plan o agrega fondos a tu cuenta
                3. Si estás usando una API key de prueba, considera obtener una nueva
                
                Mientras tanto, puedes seguir usando las otras funcionalidades de la aplicación.
                """)
            else:
                st.error(f"Error al procesar la pregunta: {error_message}")

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