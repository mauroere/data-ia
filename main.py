# filepath: c:\Users\rementeriama\Downloads\Code\data-ia\main.py.nuevo
import streamlit as st
import pandas as pd
import json
import os
import warnings
import requests
from typing import Optional
from utils import read_flexible_file, are_similar, normalize_column_names, get_api_key, get_api_url
from api_proxy import make_api_request_proxy
from api_context import make_api_request_contexto, make_api_request_agente, guardar_dataframes_en_sesion
# Importar el arreglo para la API key
from api_fix import ensure_api_key_exists

# Configuración de la página
st.set_page_config(
    page_title="Plataforma IA de Datos",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Asegurar que la API key esté disponible (solución temporal)
ensure_api_key_exists()

# Aplicar estilos globales mejorados
from ui_styles import apply_styles
apply_styles()

# Estilos adicionales específicos para el main
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 600;
        color: #FF4B4B;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0068C9;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
    }
    .success-box {
        background-color: #F0FFF4;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #09AB3B;
    }
</style>
""", unsafe_allow_html=True)

# Menú de navegación
def show_navigation():
    st.sidebar.markdown("# 🧭 Navegación")
    option = st.sidebar.radio(
        "Selecciona una función:",
        ["🔄 Cruce Inteligente", "📊 Dashboard", "✏️ Editor", "📤 Exportador", 
         "🧠 Enriquecimiento IA", "🗺️ Mapeo de Datos", "🔐 Control de Accesos", "⚙️ Administración"]
    )
    return option

# Reinicio de sesión
with st.sidebar.expander("🔄 Opciones de sesión"):
    if st.button("Reiniciar Sesión", key="reiniciar_session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Sesión reiniciada correctamente")
        st.rerun()

# Información de la aplicación
with st.sidebar.expander("ℹ️ Acerca de", expanded=False):
    st.markdown("""
    **Plataforma IA de Datos**  
    Versión: 1.2.0
    
    Desarrollado por Redpill.ai
    
    Esta plataforma integra inteligencia artificial para el análisis, 
    cruce y enriquecimiento de datos.
    """)

# Seleccionar función a mostrar
navegacion = show_navigation()

if navegacion == "🔄 Cruce Inteligente":
    st.markdown("<h1 class='main-header'>🔄 Cruce Inteligente de Datos</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Archivo BASE (existente)")
        uploaded_file_1 = st.file_uploader("Subir archivo BASE", type=["csv", "xls", "xlsx"],
                                          accept_multiple_files=False,
                                          key="upload_base")
    
    with col2:
        st.markdown("### 📄 Archivo NUEVO (a cruzar)")
        uploaded_file_2 = st.file_uploader("Subir archivo NUEVO", type=["csv", "xls", "xlsx"],
                                          accept_multiple_files=False,
                                          key="upload_nuevo")
    
    if uploaded_file_1 and uploaded_file_2:
        with st.spinner("Cargando archivos..."):
            base_df = read_flexible_file(uploaded_file_1)
            new_df = read_flexible_file(uploaded_file_2)

            # Normalizar columnas
            new_df.columns = normalize_column_names(new_df.columns)
            base_df.columns = normalize_column_names(base_df.columns)

            # Guardar los DataFrames en la sesión para uso del asistente de datos
            guardar_dataframes_en_sesion(base_df, new_df)
        
        st.markdown("<h3 class='section-header'>📋 Información de los archivos</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Archivo BASE:** {uploaded_file_1.name}")
            st.write(f"Filas: {len(base_df):,} | Columnas: {len(base_df.columns):,}")
            with st.expander("Ver muestra"):
                st.dataframe(base_df.head(5), use_container_width=True)
        
        with col2:
            st.markdown(f"**Archivo NUEVO:** {uploaded_file_2.name}")
            st.write(f"Filas: {len(new_df):,} | Columnas: {len(new_df.columns):,}")
            with st.expander("Ver muestra"):
                st.dataframe(new_df.head(5), use_container_width=True)
        
        st.markdown("<h3 class='section-header'>🔑 Selección de campo clave</h3>", unsafe_allow_html=True)
        
        campo_clave = st.selectbox("Selecciona el campo para el cruce de datos:", new_df.columns)
        if campo_clave not in base_df.columns:
            st.error(f"❌ La columna '{campo_clave}' no existe en el archivo BASE.")
            st.stop()
        
        # Guardar campo clave en sesión
        st.session_state["campo_clave"] = campo_clave
        
        if st.button("Realizar cruce de datos", key="realizar_cruce"):
            with st.spinner("Buscando coincidencias..."):
                coincidencias = []
                for _, fila in new_df.iterrows():
                    val = fila[campo_clave]
                    for _, bfila in base_df.iterrows():
                        if are_similar(val, bfila[campo_clave]):
                            coincidencias.append((val, bfila[campo_clave]))
                            break

                # Guardar coincidencias en sesión
                st.session_state["coincidencias"] = coincidencias
            
            st.markdown(f"""
            <div class='success-box'>
                <h3>✅ Cruce completado</h3>
                <p>Se encontraron {len(coincidencias):,} coincidencias de {len(new_df):,} registros ({len(coincidencias)/len(new_df)*100:.1f}%).</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar coincidencias en una tabla 
            st.markdown("<h3 class='section-header'>🔍 Resultados del cruce</h3>", unsafe_allow_html=True)
            
            # Crear un dataframe con los resultados
            result_df = pd.DataFrame(coincidencias, columns=["Valor Nuevo", "Valor Base"])
            st.dataframe(result_df, use_container_width=True, hide_index=False)
            
            # Botón para descargar resultados
            col1, col2 = st.columns([1, 3])
            with col1:
                st.download_button(
                    label="📥 Exportar resultados",
                    data=result_df.to_csv(index=False),
                    file_name=f"resultados_cruce_{uploaded_file_1.name}_{uploaded_file_2.name}.csv",
                    mime="text/csv"
                )
      # Separador antes del asistente de cruce inteligente
    st.divider()
    
    # Usar el asistente especializado para el cruce inteligente
    try:
        from asistente_cruce_inteligente import run_asistente_cruce_inteligente
        run_asistente_cruce_inteligente()
    except ImportError as e:
        st.error(f"Error al cargar el asistente de cruce inteligente: {str(e)}")
        # Si el módulo especializado no está disponible, usar el asistente estándar
        try:
            from asistente_datos_mejorado import run_data_assistant
            run_data_assistant()
        except ImportError:
            from asistente_datos import run_asistente_datos
            run_asistente_datos()

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
    
elif navegacion == "🧠 Enriquecimiento IA":
    # Importar y ejecutar el código de enriquecimiento de IA
    from ia_enriquecimiento import run_ia_enriquecimiento
    run_ia_enriquecimiento()
    
elif navegacion == "🗺️ Mapeo de Datos":
    # Importar y ejecutar el código de mapeo de datos
    from mapping_ai import run_mapping_ai
    run_mapping_ai()
    
elif navegacion == "🔐 Control de Accesos":
    # Importar y ejecutar el código de control de accesos
    from colaboracion import run_colaboracion
    run_colaboracion()
    
elif navegacion == "⚙️ Administración":
    # Importar y ejecutar el código del panel de administración
    from admin_panel import run_admin_panel
    run_admin_panel()
