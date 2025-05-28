"""
Solución temporal para asegurar que siempre haya una API key disponible.
"""
import streamlit as st
import os
import toml
from pathlib import Path

def ensure_api_key_exists():
    """
    Asegura que la API key de Redpill esté disponible en la sesión.
    Si no existe, la crea con un valor predeterminado.
    """
    # API key predeterminada para desarrollo
    DEFAULT_API_KEY = "sk-xYBWXr1epqP3Uq1A05qUql9tAyBsJE5F8PL5L66gBaE328VG"
    
    # Si ya existe en session_state, no hacer nada
    if "redpill_api_key" in st.session_state and st.session_state["redpill_api_key"]:
        return
    
    # Intentar cargar de secrets.toml
    try:
        if "redpill" in st.secrets and "api_key" in st.secrets["redpill"]:
            api_key = st.secrets["redpill"]["api_key"]
            if api_key and len(api_key.strip()) > 0:
                st.session_state["redpill_api_key"] = api_key
                return
    except:
        pass
    
    # Intentar leer directamente del archivo secrets.toml
    try:
        secrets_path = Path('.streamlit') / 'secrets.toml'
        if secrets_path.exists():
            secrets = toml.load(secrets_path)
            if "redpill" in secrets and "api_key" in secrets["redpill"]:
                api_key = secrets["redpill"]["api_key"]
                if api_key and len(api_key.strip()) > 0:
                    st.session_state["redpill_api_key"] = api_key
                    return
    except:
        pass
    
    # Si todo falla, usar la API key predeterminada
    st.session_state["redpill_api_key"] = DEFAULT_API_KEY
