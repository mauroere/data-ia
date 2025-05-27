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
    Si no está disponible, solicita al usuario que la ingrese.
    
    Args:
        service (str): Nombre del servicio ('openai' o 'redpill')
        
    Returns:
        str: Clave API
    """
    # Intentar obtener del archivo secrets.toml
    try:
        return st.secrets[service]["api_key"]
    except (KeyError, FileNotFoundError):
        # Si no está en los secretos, verificar si está en la sesión
        if f"{service}_api_key" in st.session_state:
            return st.session_state[f"{service}_api_key"]
        
        # Si no está en la sesión, intentar leer directamente del archivo
        try:
            import toml
            import os
            
            # Ruta al archivo de secretos
            secrets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.streamlit', 'secrets.toml')
            
            if os.path.exists(secrets_path):
                secrets = toml.load(secrets_path)
                if service in secrets and "api_key" in secrets[service]:
                    # Guardar en session_state para futuras llamadas
                    api_key = secrets[service]["api_key"]
                    st.session_state[f"{service}_api_key"] = api_key
                    return api_key
        except Exception as e:
            st.warning(f"Error al leer archivo de secretos: {e}")
        
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
    try:
        return st.secrets[service]["api_url"]
    except (KeyError, FileNotFoundError):
        # Valores por defecto si no se encuentran en los secretos
        if service == "redpill":
            return "https://api.redpill.ai/v1/chat/completions"
        elif service == "openai":
            return "https://api.openai.com/v1/chat/completions"
        return ""