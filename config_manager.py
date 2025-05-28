"""
Módulo para gestionar configuraciones persistentes en la aplicación.
Almacena configuraciones como las claves API de forma segura en archivos locales.
"""

import os
import json
import streamlit as st
from typing import Dict, Any, Optional
import toml

# Ruta base para almacenar configuraciones
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'app_config.json')
SECRETS_FILE = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')

def ensure_config_dir():
    """Asegura que el directorio de configuración exista."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

def load_config() -> Dict[str, Any]:
    """
    Carga la configuración desde el archivo JSON.
    
    Returns:
        Dict[str, Any]: Diccionario con la configuración
    """
    ensure_config_dir()
    if not os.path.exists(CONFIG_FILE):
        return {}
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error al cargar la configuración: {e}")
        return {}

def save_config(config: Dict[str, Any]) -> bool:
    """
    Guarda la configuración en un archivo JSON.
    
    Args:
        config (Dict[str, Any]): Diccionario con la configuración a guardar
        
    Returns:
        bool: True si se guardó correctamente, False en caso contrario
    """
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error al guardar la configuración: {e}")
        return False

def update_secrets_file(api_key: str, service: str = "redpill") -> bool:
    """
    Actualiza el archivo de secretos con la clave API proporcionada.
    
    Args:
        api_key (str): Clave API a guardar
        service (str): Servicio al que pertenece la clave (redpill, openai, etc.)
        
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario
    """
    try:
        # Asegurarse de que existe el directorio .streamlit
        streamlit_dir = os.path.join(os.path.dirname(__file__), '.streamlit')
        if not os.path.exists(streamlit_dir):
            os.makedirs(streamlit_dir)
        
        # Cargar el archivo existente si existe
        secrets = {}
        if os.path.exists(SECRETS_FILE):
            try:
                secrets = toml.load(SECRETS_FILE)
            except Exception:
                # Si hay error al leer, empezar con un archivo vacío
                secrets = {}
        
        # Actualizar o agregar la sección del servicio
        if service not in secrets:
            secrets[service] = {}
        
        # Actualizar la clave API
        secrets[service]["api_key"] = api_key
        
        # Si es redpill, asegurar que tenga una URL por defecto
        if service == "redpill" and "api_url" not in secrets[service]:
            secrets[service]["api_url"] = "https://api.redpill.ai/v1/chat/completions"
        
        # Guardar el archivo
        with open(SECRETS_FILE, 'w', encoding='utf-8') as f:
            toml.dump(secrets, f)
        
        return True
    except Exception as e:
        st.error(f"Error al actualizar el archivo de secretos: {e}")
        return False

def get_api_key_from_config(service: str = "redpill") -> Optional[str]:
    """
    Obtiene la clave API desde la configuración persistente.
    
    Args:
        service (str): Servicio del que obtener la clave API
        
    Returns:
        Optional[str]: Clave API o None si no se encuentra
    """
    config = load_config()
    
    # Verificar si existe en la configuración persistente
    if "api_keys" in config and service in config["api_keys"]:
        return config["api_keys"][service]
    
    # Si no está en la configuración, intentar leer del archivo de secretos
    try:
        if os.path.exists(SECRETS_FILE):
            secrets = toml.load(SECRETS_FILE)
            if service in secrets and "api_key" in secrets[service]:
                # Si se encuentra en secretos, guardarla también en la configuración persistente
                if "api_keys" not in config:
                    config["api_keys"] = {}
                config["api_keys"][service] = secrets[service]["api_key"]
                save_config(config)
                return secrets[service]["api_key"]
    except Exception:
        pass
    
    return None

def save_api_key(api_key: str, service: str = "redpill") -> bool:
    """
    Guarda la clave API en la configuración persistente y en el archivo de secretos.
    
    Args:
        api_key (str): Clave API a guardar
        service (str): Servicio al que pertenece la clave
        
    Returns:
        bool: True si se guardó correctamente, False en caso contrario
    """
    # Guardar en la configuración persistente
    config = load_config()
    if "api_keys" not in config:
        config["api_keys"] = {}
    config["api_keys"][service] = api_key
    config_saved = save_config(config)
    
    # Guardar en el archivo de secretos
    secrets_saved = update_secrets_file(api_key, service)
    
    # También guardar en session_state para uso inmediato
    st.session_state[f"{service}_api_key"] = api_key
    
    return config_saved and secrets_saved
