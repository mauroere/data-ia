"""
Panel de administración para gestionar configuraciones de la aplicación.
Permite configurar API keys, URLs y otras configuraciones persistentes.
"""

import streamlit as st
import os
from typing import Dict, Any, Optional
from config_manager import load_config, save_config, save_api_key, get_api_key_from_config

def run_admin_panel():
    """Ejecuta el panel de administración."""
    st.title("👤 Panel de Administración")
    
    # Tabs para diferentes secciones de configuración
    tab1, tab2, tab3 = st.tabs(["🔑 API Keys", "🌐 URLs", "⚙️ Configuración General"])
    
    with tab1:
        manage_api_keys()
    
    with tab2:
        manage_urls()
    
    with tab3:
        manage_general_settings()

def show_api_key_debug():
    """Muestra un botón para diagnosticar problemas con la API key."""
    from debug_secrets import check_api_key_state
    
    with st.expander("🔧 Diagnóstico de API Key"):
        st.info("Si la API key no funciona correctamente, puedes usar esta herramienta para diagnosticar el problema.")
        if st.button("Ejecutar diagnóstico"):
            check_api_key_state()

def manage_api_keys():
    """Gestiona las claves API."""
    st.header("🔑 Gestión de Claves API")
    st.write("Configura las claves API para los diferentes servicios utilizados por la aplicación.")
    
    # Mostrar herramienta de diagnóstico al principio
    show_api_key_debug()
    
    # Redpill API Key
    st.subheader("Redpill API")
    current_redpill_key = get_api_key_from_config("redpill") or ""
    
    # Si la clave está en session_state, usarla (tiene prioridad)
    if "redpill_api_key" in st.session_state and st.session_state["redpill_api_key"]:
        current_redpill_key = st.session_state["redpill_api_key"]
    
    masked_key = mask_api_key(current_redpill_key) if current_redpill_key else ""
    
    st.write("Esta clave se utiliza para el asistente de datos y el análisis con IA.")
    
    # Mostrar la clave actual enmascarada
    if current_redpill_key and len(current_redpill_key.strip()) > 0:
        st.success(f"✅ Clave API configurada: {masked_key}")
        # Asegurarse de que esté en session_state
        if "redpill_api_key" not in st.session_state:
            st.session_state["redpill_api_key"] = current_redpill_key
    else:
        st.warning("⚠️ No hay clave API configurada para Redpill.")
    
    # Opción para cambiar la clave    change_key = st.checkbox("Cambiar clave API de Redpill", key="change_redpill_key")
    
    if change_key:
        new_key = st.text_input(
            "Nueva clave API de Redpill:", 
            type="password",
            help="La clave API se guardará de forma permanente."
        )
        
        if st.button("Guardar clave API", key="save_redpill_key"):
            if new_key:
                # Intentar guardar la clave API
                result = save_api_key(new_key, "redpill")
                
                # Si la función devuelve True, la clave se guardó con éxito (parcial o total)
                if result:
                    st.session_state["redpill_api_key"] = new_key
                    # El mensaje de éxito parcial se mostrará desde la función save_api_key si es necesario
                    st.success("✅ Clave API guardada correctamente.")
                    st.rerun()  # Recargar la página para mostrar la nueva clave
                else:
                    st.error("❌ Error al guardar la clave API.")
                    st.info("Verifica los permisos de escritura o contacta al administrador del sistema.")
            else:
                st.error("❌ La clave API no puede estar vacía.")
    
    # OpenAI API Key (si se utiliza)
    st.divider()
    st.subheader("OpenAI API (opcional)")
    current_openai_key = get_api_key_from_config("openai") or ""
    masked_openai_key = mask_api_key(current_openai_key)
    
    st.write("Esta clave se utiliza como alternativa para algunos servicios de IA (opcional).")
    
    # Mostrar la clave actual enmascarada
    if current_openai_key:
        st.success(f"✅ Clave API configurada: {masked_openai_key}")
    else:
        st.info("ℹ️ No hay clave API configurada para OpenAI (opcional).")
    
    # Opción para cambiar la clave
    change_openai_key = st.checkbox("Cambiar clave API de OpenAI", key="change_openai_key")
    
    if change_openai_key:
        new_openai_key = st.text_input(
            "Nueva clave API de OpenAI:", 
            type="password",
            help="La clave API se guardará de forma permanente."
        )        if st.button("Guardar clave API", key="save_openai_key"):
            if new_openai_key:
                # Intentar guardar la clave API
                result = save_api_key(new_openai_key, "openai")
                
                # Si la función devuelve True, la clave se guardó con éxito (parcial o total)
                if result:
                    st.session_state["openai_api_key"] = new_openai_key
                    # El mensaje de éxito parcial se mostrará desde la función save_api_key si es necesario
                    st.success("✅ Clave API guardada correctamente.")
                    st.rerun()  # Recargar la página para mostrar la nueva clave
                else:
                    st.error("❌ Error al guardar la clave API.")
                    st.info("Verifica los permisos de escritura o contacta al administrador del sistema.")
            else:
                st.error("❌ La clave API no puede estar vacía.")

def manage_urls():
    """Gestiona las URLs de los servicios."""
    st.header("🌐 Gestión de URLs")
    st.write("Configura las URLs de los servicios utilizados por la aplicación.")
    
    config = load_config()
    if "api_urls" not in config:
        config["api_urls"] = {}
    
    # Redpill API URL
    st.subheader("Redpill API URL")
    current_url = config["api_urls"].get("redpill", "https://api.redpill.ai/v1/chat/completions")
    
    new_url = st.text_input(
        "URL de la API de Redpill:", 
        value=current_url,
        help="URL del endpoint de la API de Redpill."
    )
    
    if st.button("Guardar URL", key="save_redpill_url"):
        config["api_urls"]["redpill"] = new_url
        if save_config(config):
            st.success("✅ URL guardada correctamente.")
        else:
            st.error("❌ Error al guardar la URL.")
    
    # Información adicional
    with st.expander("ℹ️ Información sobre las URLs"):
        st.markdown("""
        ### Redpill API
        
        La URL por defecto de la API de Redpill es:
        ```
        https://api.redpill.ai/v1/chat/completions
        ```
        
        Solo cambia esta URL si estás utilizando una implementación personalizada o si el proveedor
        del servicio ha cambiado la dirección del endpoint.
        """)

def manage_general_settings():
    """Gestiona la configuración general de la aplicación."""
    st.header("⚙️ Configuración General")
    st.write("Configura opciones generales de la aplicación.")
    
    config = load_config()
    if "general" not in config:
        config["general"] = {}
    
    # Caché de la API
    st.subheader("Caché de la API")
    cache_enabled = config["general"].get("cache_enabled", True)
    
    new_cache_enabled = st.toggle(
        "Habilitar caché de la API", 
        value=cache_enabled,
        help="Almacena en caché las respuestas de la API para mejorar el rendimiento y reducir costos."
    )
    
    cache_expiration = config["general"].get("cache_expiration_days", 7)
    new_cache_expiration = st.slider(
        "Días de expiración de la caché", 
        min_value=1, 
        max_value=30, 
        value=cache_expiration,
        help="Número de días que se mantendrán las respuestas en caché antes de ser eliminadas."
    )
    
    if st.button("Guardar configuración de caché", key="save_cache_config"):
        config["general"]["cache_enabled"] = new_cache_enabled
        config["general"]["cache_expiration_days"] = new_cache_expiration
        if save_config(config):
            st.success("✅ Configuración guardada correctamente.")
        else:
            st.error("❌ Error al guardar la configuración.")
    
    # Limpiar caché
    st.divider()
    st.subheader("Mantenimiento")
    
    if st.button("Limpiar caché", key="clean_cache"):
        # Implementar limpieza de caché
        cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
        if os.path.exists(cache_dir):
            try:
                for filename in os.listdir(cache_dir):
                    file_path = os.path.join(cache_dir, filename)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                st.success("✅ Caché limpiada correctamente.")
            except Exception as e:
                st.error(f"❌ Error al limpiar la caché: {e}")
        else:
            st.info("ℹ️ No hay caché para limpiar.")

def mask_api_key(api_key: str) -> str:
    """
    Enmascara una clave API para mostrarla en la interfaz.
    
    Args:
        api_key (str): Clave API a enmascarar
        
    Returns:
        str: Clave API enmascarada
    """
    if not api_key:
        return ""
    
    # Mostrar solo los primeros 4 y últimos 4 caracteres
    if len(api_key) <= 8:
        return "*" * len(api_key)
    else:
        return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]

if __name__ == "__main__":
    st.set_page_config(page_title="Panel de Administración", layout="wide")
    run_admin_panel()
