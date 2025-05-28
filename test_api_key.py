import streamlit as st
from utils import get_api_key, get_api_url
import requests
import urllib3
import json

# Desactivar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.title("Prueba de API Key de Redpill")

# Obtener la clave API de Redpill
api_key = get_api_key("redpill")
api_url = get_api_url("redpill")

# Mostrar información actual
st.subheader("Configuración actual")
st.write(f"API Key: {api_key[:8]}...{api_key[-5:] if api_key else 'No encontrada'}")
st.write(f"API URL: {api_url}")

# Permitir cambiar la API key
st.subheader("Actualizar API Key")
new_api_key = st.text_input(
    "Nueva API Key:",
    type="password",
    help="Deja en blanco para mantener la actual"
)

if new_api_key:
    st.session_state["redpill_api_key"] = new_api_key
    st.success("API Key actualizada en la sesión")
    api_key = new_api_key

# Permitir cambiar la URL de la API
st.subheader("Actualizar URL de la API")
new_api_url = st.text_input(
    "Nueva URL de la API:",
    value=api_url,
    help="Por defecto: https://api.redpill.ai/v1/chat/completions"
)

if new_api_url and new_api_url != api_url:
    st.session_state["redpill_api_url"] = new_api_url
    st.success("URL de la API actualizada en la sesión")
    api_url = new_api_url

# Prueba de la API
st.subheader("Probar la API")
prompt = st.text_input("Pregunta de prueba:", value="Hola, ¿cómo estás?")

if st.button("Probar API"):
    st.write("Realizando prueba con la configuración actual...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "mistralai/ministral-8b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    with st.spinner("Realizando solicitud..."):
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                verify=False,
                timeout=15
            )
            
            st.write(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                st.success("✓ La API funciona correctamente")
                
                # Mostrar respuesta formateada
                response_data = response.json()
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    content = response_data["choices"][0].get("message", {}).get("content", "")
                    st.info(f"Respuesta: {content}")
                
                # Mostrar respuesta completa
                with st.expander("Ver respuesta completa"):
                    st.json(response_data)
                
            else:
                st.error(f"✗ Error: {response.status_code}")
                st.code(response.text)
                
        except Exception as e:
            st.error(f"✗ Excepción: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
