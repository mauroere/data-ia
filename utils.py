import pandas as pd
import chardet
import io
import re
from fuzzywuzzy import fuzz
import os
import streamlit as st

def are_similar(a, b, threshold=85):
    """
    Compara dos strings utilizando fuzzy matching para determinar si son similares.
    
    Args:
        a (str): Primer string a comparar
        b (str): Segundo string a comparar
        threshold (int): Umbral de similitud (0-100)
        
    Returns:
        bool: True si la similitud es igual o mayor al umbral, False en caso contrario
    """
    return fuzz.token_sort_ratio(str(a), str(b)) >= threshold

def normalize_column_names(columns):
    """
    Normaliza los nombres de las columnas eliminando caracteres especiales y espacios.
    
    Args:
        columns (list): Lista de nombres de columnas
        
    Returns:
        list: Lista de nombres de columnas normalizados
    """
    return [re.sub(r'[^a-zA-Z0-9]', '_', col.strip().lower()) for col in columns]

def read_flexible_file(uploaded_file):
    """
    Lee un archivo CSV o Excel con detección automática de separadores y encoding.
    
    Args:
        uploaded_file: Archivo subido a través de st.file_uploader
        
    Returns:
        pandas.DataFrame: DataFrame con los datos cargados
    """
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

def get_api_key(service="openai"):
    """
    Obtiene la clave API desde los secretos de Streamlit.
    Si no está disponible, verifica la configuración persistente o solicita al usuario que la ingrese.
    
    Args:
        service (str): Nombre del servicio ('openai' o 'redpill')
        
    Returns:
        str: Clave API
    """
    # Valores por defecto para la clave API (uso en desarrollo/pruebas)
    default_keys = {
        "redpill": "sk-xYBWXr1epqP3Uq1A05qUql9tAyBsJE5F8PL5L66gBaE328VG",
        "openai": ""  # No establecemos una clave por defecto para OpenAI
    }
    
    # Primero, verificar si está en la sesión (prioridad más alta)
    if f"{service}_api_key" in st.session_state:
        key = st.session_state[f"{service}_api_key"]
        if key and len(key.strip()) > 0:  # Asegurarse de que no sea una cadena vacía
            return key
    
    # Segundo, intentar obtener de la configuración persistente
    try:
        from config_manager import get_api_key_from_config
        api_key = get_api_key_from_config(service)
        if api_key and len(api_key.strip()) > 0:  # Verificar que no sea una cadena vacía
            # Guardar en session_state para futuras llamadas
            st.session_state[f"{service}_api_key"] = api_key
            return api_key
    except Exception:
        # No mostrar errores aquí, intentar otras fuentes
        pass
    
    # Tercero, intentar obtener del archivo secrets.toml
    try:
        api_key = st.secrets[service]["api_key"]
        if api_key and len(api_key.strip()) > 0:
            # Guardar en session_state para futuras llamadas
            st.session_state[f"{service}_api_key"] = api_key
            return api_key
    except Exception:
        # No mostrar errores aquí, intentar otras fuentes
        pass
    
    # Cuarto, intentar leer directamente del archivo secrets.toml
    try:
        import toml
        import os
        
        # Ruta al archivo de secretos (probar múltiples ubicaciones)
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), '.streamlit', 'secrets.toml')
        ]
        
        for secrets_path in possible_paths:
            if os.path.exists(secrets_path):
                try:
                    secrets = toml.load(secrets_path)
                    if service in secrets and "api_key" in secrets[service]:
                        # Guardar en session_state para futuras llamadas
                        api_key = secrets[service]["api_key"]
                        if api_key and len(api_key.strip()) > 0:
                            st.session_state[f"{service}_api_key"] = api_key
                            return api_key
                except Exception:
                    # Si hay error al leer el archivo, continuar con la siguiente fuente
                    continue
    except Exception:
        # No mostrar errores aquí, intentar otras fuentes
        pass
    
    # Si estamos en modo desarrollo o pruebas, usar la clave por defecto para redpill
    if service in default_keys and default_keys[service]:
        # Guardar en session_state para futuras llamadas
        st.session_state[f"{service}_api_key"] = default_keys[service]
        return default_keys[service]
    
    # Si todo falla, devolver vacío (se manejará en la UI)
    return ""

def get_api_url(service="redpill"):
    """
    Obtiene la URL de la API desde los secretos de Streamlit.
    
    Args:
        service (str): Nombre del servicio
        
    Returns:
        str: URL de la API
    """
    # Valores por defecto para URLs de API
    default_urls = {
        "redpill": "https://api.redpill.ai/v1/chat/completions",
        "openai": "https://api.openai.com/v1/chat/completions"
    }
    
    # Primero, verificar si está en la sesión
    if f"{service}_api_url" in st.session_state:
        url = st.session_state[f"{service}_api_url"]
        if url and len(url.strip()) > 0:  # Asegurarse de que no sea una cadena vacía
            return url
    
    # Segundo, intentar obtener de st.secrets
    try:
        url = st.secrets[service]["api_url"]
        if url and len(url.strip()) > 0:
            return url
    except Exception:
        # No mostrar errores aquí, usar el valor por defecto
        pass
    
    # Tercero, usar valores por defecto
    if service in default_urls:
        return default_urls[service]
    
    return ""

def confirmar_continuar(mensaje="¿Desea continuar con la iteración?", key=None):
    """
    Muestra un mensaje de confirmación al usuario y retorna su respuesta.
    
    Args:
        mensaje (str): El mensaje a mostrar al usuario
        key (str): Clave única para el componente de Streamlit (opcional)
    
    Returns:
        bool: True si el usuario confirma, False en caso contrario
    """
    col1, col2, col3 = st.columns([2,1,1])
    
    with col1:
        st.write(mensaje)
    
    with col2:
        if key:
            continuar = st.button("✅ Continuar", key=f"continuar_{key}")
        else:
            continuar = st.button("✅ Continuar")
    
    with col3:
        if key:
            cancelar = st.button("❌ Cancelar", key=f"cancelar_{key}")
        else:
            cancelar = st.button("❌ Cancelar")
    
    if cancelar:
        return False
    
    return continuar