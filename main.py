import streamlit as st
import pandas as pd
import httpx
import os
from typing import Optional
from utils import read_flexible_file, are_similar, normalize_column_names, get_api_key, get_api_url

def make_api_request(pregunta: str) -> dict:
    """Realiza una petición a la API de Redpill.io"""
    api_key = get_api_key("redpill")
    api_url = get_api_url("redpill")
    
    if not api_key:
        st.error("🔑 No se ha configurado la clave API de Redpill. Configúrala en .streamlit/secrets.toml")
        st.stop()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    payload = {
        "model": "redpill-1",
        "messages": [{"role": "user", "content": pregunta}],
        "temperature": 0.3
    }
    
    try:
        # Usar la conexión segura por defecto de httpx
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                api_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        st.error(f"Error de conexión: {str(e)}")
        raise

# Configuración de la página
st.set_page_config(page_title="Plataforma IA de Datos", layout="wide")

# Menú de navegación
def show_navigation():
    st.sidebar.title("🧭 Navegación")
    option = st.sidebar.radio(
        "Selecciona una función:",
        ["🔄 Cruce Inteligente", "📊 Dashboard", "✏️ Editor", "📤 Exportador", 
         "🤖 Enriquecimiento IA", "🗺️ Mapeo de Datos", "👥 Control de Accesos"]
    )
    return option

# Reinicio de sesión
if st.sidebar.button("🔄 Reiniciar Sesión"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.sidebar.success("Sesión reiniciada correctamente")
    st.experimental_rerun()

# Seleccionar función a mostrar
navegacion = show_navigation()

if navegacion == "🔄 Cruce Inteligente":
    st.title("🔄 Cruce Inteligente de Datos")

if navegacion == "🔄 Cruce Inteligente":
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

# Aquí comenzará el código para las otras páginas
elif navegacion == "📊 Dashboard":
    # Importar y ejecutar el código del dashboard
    from dashboard import run_dashboard
    run_dashboard()
    
elif navegacion == "✏️ Editor":
    # Importar y ejecutar el código del editor
    from editor import run_editor
    run_editor()
    
elif navegacion == "📤 Exportador":
    # Importar y ejecutar el código del exportador
    from exportador import run_exportador
    run_exportador()
    
elif navegacion == "🤖 Enriquecimiento IA":
    # Importar y ejecutar el código de enriquecimiento de IA
    from ia_enriquecimiento import run_ia_enriquecimiento
    run_ia_enriquecimiento()
    
elif navegacion == "🗺️ Mapeo de Datos":
    # Importar y ejecutar el código de mapeo de datos
    from mapping_ai import run_mapping_ai
    run_mapping_ai()
    
elif navegacion == "👥 Control de Accesos":
    # Importar y ejecutar el código de control de accesos
    from colaboracion import run_colaboracion
    run_colaboracion()