"""
Este módulo proporciona funciones mejoradas para la comunicación con la API de Redpill
con soporte para incluir el contexto de los datos cargados en la aplicación.
"""

import streamlit as st
import requests
import pandas as pd
from typing import Dict, List, Any, Optional
from utils import get_api_key, get_api_url

def generar_contexto_datos() -> str:
    """
    Genera un texto descriptivo del contexto de datos cargados en la aplicación.
    
    Returns:
        str: Texto con descripción de los datos cargados
    """
    contexto = "Eres un asistente especializado en análisis de datos que ayuda a los usuarios a trabajar con archivos CSV, Excel y realizar cruces de datos."
    
    # Verificar si hay datos cargados en la sesión
    if 'base_df' in st.session_state and 'new_df' in st.session_state:
        base_df = st.session_state['base_df']
        new_df = st.session_state['new_df']
        
        # Verificar que sean DataFrames válidos
        if isinstance(base_df, pd.DataFrame) and isinstance(new_df, pd.DataFrame):
            contexto += "\n\nEl usuario ha cargado dos archivos de datos:"
            contexto += f"\n1. Archivo BASE con {len(base_df)} filas y columnas: {', '.join(base_df.columns.tolist())}"
            contexto += f"\n2. Archivo NUEVO con {len(new_df)} filas y columnas: {', '.join(new_df.columns.tolist())}"
            
            # Incluir ejemplos de datos para mejor contexto
            contexto += "\n\nEjemplo de 3 filas del Archivo BASE:"
            contexto += "\n" + base_df.head(3).to_string()
            
            contexto += "\n\nEjemplo de 3 filas del Archivo NUEVO:"
            contexto += "\n" + new_df.head(3).to_string()
            
            # Explicar las funciones de cruce disponibles
            contexto += "\n\nLa aplicación permite realizar cruces inteligentes entre los archivos utilizando fuzzy matching."
            contexto += "\nEl fuzzy matching permite encontrar coincidencias similares aunque no sean exactamente iguales."
            
            # Si existe un campo_clave seleccionado, incluirlo
            if 'campo_clave' in st.session_state:
                campo_clave = st.session_state['campo_clave']
                contexto += f"\n\nEl usuario ha seleccionado '{campo_clave}' como campo clave para el cruce."
            
            # Si existen coincidencias, incluirlas
            if 'coincidencias' in st.session_state and st.session_state['coincidencias']:
                coincidencias = st.session_state['coincidencias']
                contexto += f"\n\nSe han encontrado {len(coincidencias)} coincidencias entre los archivos."
                if len(coincidencias) > 0:
                    contexto += "\nEjemplos de coincidencias:"
                    for i, (val1, val2) in enumerate(coincidencias[:3]):
                        contexto += f"\n- '{val1}' coincide con '{val2}'"
                        if i >= 2:
                            break
    
    return contexto

def make_api_request_contexto(pregunta: str) -> dict:
    """
    Realiza una petición a la API de Redpill incluyendo el contexto de los datos cargados.
    
    Args:
        pregunta (str): Pregunta del usuario
        
    Returns:
        dict: Respuesta de la API
    """
    api_key = get_api_key("redpill")
    api_url = get_api_url("redpill")
    
    if not api_key:
        # Intentar obtener la clave API del usuario
        st.warning("🔑 No se ha encontrado la clave API de Redpill en la configuración.")
        
        # Mostrar información adicional para ayudar a solucionar el problema
        with st.expander("ℹ️ Información para solucionar problemas"):
            st.markdown("""
            ### Posibles causas:
            1. **Archivo de secretos no encontrado** - Verifica que existe el archivo `.streamlit/secrets.toml`
            2. **Formato incorrecto** - El archivo debe usar el formato TOML correcto:
            ```toml
            [redpill]
            api_key = "tu-clave-api"
            api_url = "https://api.redpill.ai/v1/chat/completions"
            ```
            3. **Permisos de archivo** - Verifica que la aplicación tiene permisos para leer el archivo
            
            ### Herramientas de diagnóstico:
            - Ejecuta `python debug_secrets.py` para diagnosticar problemas con el archivo de secretos
            - Ejecuta `python test_conexion_redpill_basic.py` para probar la conexión con la API
            """)
        
        # Obtener la API key y guardarla de forma persistente
        api_key = st.text_input(
            "Ingresa tu clave API de Redpill:",
            type="password",
            help="La clave API se guardará de forma permanente para futuros usos."
        )
        
        if not api_key:
            st.error("Se requiere una clave API para continuar con el asistente conversacional.")
            st.info("Puedes seguir usando otras funcionalidades de la aplicación que no requieren API.")
            st.info("También puedes configurar la API key en la sección de Administración.")
            st.stop()
        else:
            # Guardar en session_state para esta sesión
            st.session_state["redpill_api_key"] = api_key
            
            # Guardar de forma persistente para futuros usos
            try:
                from config_manager import save_api_key
                # La función save_api_key ya incluye mensajes informativos adecuados
                save_api_key(api_key, "redpill")
                # No mostramos aquí el mensaje de éxito porque la función ya lo hace si es necesario
            except ImportError as e:
                st.warning(f"No se pudo guardar la clave API de forma persistente: {e}")
                st.info("La clave se guardará solo para esta sesión.")
            except Exception as e:
                st.warning(f"Error al guardar la clave API: {e}")
                st.info("La clave se guardará solo para esta sesión, pero funcionará correctamente.")
    
    # Generar contexto basado en los datos cargados
    contexto = generar_contexto_datos()
    
    # Enriquecer la pregunta con el contexto de la aplicación
    pregunta_enriquecida = f"{contexto}\n\nPregunta del usuario: {pregunta}\n\nResponde a la pregunta del usuario en español, teniendo en cuenta el contexto proporcionado y las funcionalidades de la aplicación para el cruce inteligente de datos."
    
    try:
        # Uso de la biblioteca requests con verificación SSL desactivada
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "mistralai/ministral-8b",
            "messages": [
                {"role": "system", "content": "Eres un asistente especializado en análisis y cruce de datos que ayuda a los usuarios a trabajar con archivos CSV y Excel. Debes responder en español."},
                {"role": "user", "content": pregunta_enriquecida}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            verify=False,  # Desactivar verificación SSL
            timeout=30.0   # Timeout en segundos
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error de conexión: {str(e)}")
        raise

def make_api_request_agente(pregunta: str) -> dict:
    """
    Realiza una petición a la API de Redpill en modo agente, permitiendo un procesamiento
    más autónomo y orientado a tareas con los datos cargados.
    
    Args:
        pregunta (str): Pregunta o instrucción del usuario
        
    Returns:
        dict: Respuesta de la API
    """
    api_key = get_api_key("redpill")
    api_url = get_api_url("redpill")
    
    if not api_key:
        # Intentar obtener la clave API del usuario
        st.warning("🔑 No se ha encontrado la clave API de Redpill en la configuración.")
        
        # Mostrar información adicional para ayudar a solucionar el problema
        with st.expander("ℹ️ Información para solucionar problemas"):
            st.markdown("""
            ### Posibles causas:
            1. **Archivo de secretos no encontrado** - Verifica que existe el archivo `.streamlit/secrets.toml`
            2. **Formato incorrecto** - El archivo debe usar el formato TOML correcto:
            ```toml
            [redpill]
            api_key = "tu-clave-api"
            api_url = "https://api.redpill.ai/v1/chat/completions"
            ```
            3. **Permisos de archivo** - Verifica que la aplicación tiene permisos para leer el archivo
            
            ### Herramientas de diagnóstico:
            - Ejecuta `python debug_secrets.py` para diagnosticar problemas con el archivo de secretos
            - Ejecuta `python test_conexion_redpill_basic.py` para probar la conexión con la API
            """)
        
        # Obtener la API key y guardarla de forma persistente
        api_key = st.text_input(
            "Ingresa tu clave API de Redpill:",
            type="password",
            help="La clave API se guardará de forma permanente para futuros usos."
        )
        
        if not api_key:
            st.error("Se requiere una clave API para continuar con el asistente de datos.")
            st.info("Puedes seguir usando otras funcionalidades de la aplicación que no requieren API.")
            st.info("También puedes configurar la API key en la sección de Administración.")
            st.stop()
        else:            # Guardar en session_state para esta sesión
            st.session_state["redpill_api_key"] = api_key
            
            # Guardar de forma persistente para futuros usos
            try:
                from config_manager import save_api_key
                # La función save_api_key ya incluye mensajes informativos adecuados
                save_api_key(api_key, "redpill")
                # No mostramos aquí el mensaje de éxito porque la función ya lo hace si es necesario
            except ImportError as e:
                st.warning(f"No se pudo guardar la clave API de forma persistente: {e}")
                st.info("La clave se guardará solo para esta sesión.")
            except Exception as e:
                st.warning(f"Error al guardar la clave API: {e}")
                st.info("La clave se guardará solo para esta sesión, pero funcionará correctamente.")
    
    # Generar contexto basado en los datos cargados
    contexto = generar_contexto_datos()
    
    # Instrucciones específicas para el modo agente
    instrucciones_agente = """
    Actúa como un agente de análisis de datos que puede:
    1. Interpretar datos y realizar análisis básicos
    2. Buscar patrones, correlaciones y tendencias en los datos
    3. Sugerir acciones específicas basadas en el análisis
    4. Responder a consultas técnicas sobre los datos
    5. Explicar el significado de los resultados del cruce de datos
    6. Proponer nuevos análisis o cruces que podrían ser útiles
    
    Cuando respondas, sigue este formato:
    1. 📊 ANÁLISIS: Breve resumen de tu interpretación de los datos
    2. 🔍 HALLAZGOS: Enumera los principales hallazgos o conclusiones
    3. 📈 RECOMENDACIONES: Sugiere acciones concretas o análisis adicionales
    
    Usa lenguaje técnico pero comprensible y responde siempre en español.
    """
    
    # Enriquecer la pregunta con el contexto de la aplicación y las instrucciones del agente
    pregunta_enriquecida = f"{contexto}\n\n{instrucciones_agente}\n\nConsulta/Instrucción del usuario: {pregunta}\n\n"
    
    try:
        # Uso de la biblioteca requests con verificación SSL desactivada
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "mistralai/ministral-8b",
            "messages": [
                {"role": "system", "content": "Eres un agente inteligente especializado en análisis de datos que ayuda a los usuarios a trabajar con archivos CSV y Excel. Puedes analizar, interpretar y actuar sobre los datos proporcionados. Debes responder en español siguiendo un formato estructurado."},
                {"role": "user", "content": pregunta_enriquecida}
            ],
            "temperature": 0.5,  # Reducida para respuestas más precisas y estructuradas
            "max_tokens": 1500   # Aumentado para permitir respuestas más detalladas
        }
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            verify=False,  # Desactivar verificación SSL
            timeout=30.0   # Timeout en segundos
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error de conexión: {str(e)}")
        raise

def guardar_dataframes_en_sesion(base_df: pd.DataFrame, new_df: pd.DataFrame, campo_clave: Optional[str] = None, coincidencias: Optional[List] = None):
    """
    Guarda los DataFrames en la sesión para que puedan ser utilizados por el asistente conversacional.
    
    Args:
        base_df (pd.DataFrame): DataFrame base (existente)
        new_df (pd.DataFrame): DataFrame nuevo (a cruzar)
        campo_clave (str, optional): Campo clave seleccionado para el cruce
        coincidencias (List, optional): Lista de coincidencias encontradas
    """
    st.session_state["base_df"] = base_df
    st.session_state["new_df"] = new_df
    
    if campo_clave:
        st.session_state["campo_clave"] = campo_clave
    
    if coincidencias:
        st.session_state["coincidencias"] = coincidencias
