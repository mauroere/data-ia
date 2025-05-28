"""
Herramienta de diagnóstico unificada para la plataforma de análisis de datos.
Combina todas las utilidades de diagnóstico existentes en una sola interfaz.
"""

import streamlit as st
import os
import sys
import toml
import pandas as pd
import json
import requests
from pathlib import Path
import importlib
import socket
import ssl
import traceback
from typing import Dict, List, Any, Optional, Tuple

# Intentar importar módulos locales
try:
    from utils import get_api_key, get_api_url
    from api_fix import ensure_api_key_exists
    import api_diagnostico
    import ssl_diagnostico
except ImportError as e:
    st.error(f"Error al importar módulos: {e}")

# Configuración de la página
st.set_page_config(
    page_title="Diagnóstico del Sistema",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos
st.markdown("""
<style>
    .success-box {
        background-color: #E9F9EF;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #09AB3B;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #FFF8E6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #FFBD45;
        margin-bottom: 1rem;
    }
    .error-box {
        background-color: #FFEBEB;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #EBF0FF;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #3366FF;
        margin-bottom: 1rem;
    }
    .diagnostic-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
</style>
""")

# Función para verificar la estructura del proyecto
def verificar_estructura_proyecto() -> Dict[str, Any]:
    """Verifica que todos los archivos necesarios estén presentes."""
    archivos_requeridos = [
        "main.py", 
        "asistente_datos.py",
        "asistente_datos_mejorado.py",
        "utils.py", 
        "api_context.py", 
        "api_proxy.py",
        "ui_components.py",
        "ui_styles.py",
        "api_fix.py"
    ]
    
    resultado = {
        "status": "success",
        "faltantes": [],
        "mensaje": "Todos los archivos esenciales están presentes"
    }
    
    for archivo in archivos_requeridos:
        if not os.path.exists(archivo):
            resultado["faltantes"].append(archivo)
            resultado["status"] = "error"
    
    if resultado["faltantes"]:
        resultado["mensaje"] = f"Faltan archivos esenciales: {', '.join(resultado['faltantes'])}"
    
    return resultado

# Función para verificar la configuración de API keys
def verificar_api_keys() -> Dict[str, Any]:
    """Verifica la configuración de API keys."""
    resultado = {
        "status": "success",
        "mensaje": "API key configurada correctamente",
        "detalles": {}
    }
    
    # Verificar si existe el archivo .streamlit/secrets.toml
    secrets_path = Path('.streamlit') / 'secrets.toml'
    resultado["detalles"]["secrets_file_exists"] = secrets_path.exists()
    
    # Intentar leer la API key de varias fuentes
    api_key_sources = {
        "secrets_toml": None,
        "environment": None,
        "session_state": None,
        "api_fix_default": "sk-xYBWXr1epqP3Uq1A05qUql9tAyBsJE5F8PL5L66gBaE328VG"
    }
    
    # Desde secrets.toml
    if resultado["detalles"]["secrets_file_exists"]:
        try:
            secrets = toml.load(secrets_path)
            if "redpill" in secrets and "api_key" in secrets["redpill"]:
                api_key_sources["secrets_toml"] = secrets["redpill"]["api_key"]
        except Exception as e:
            resultado["detalles"]["secrets_error"] = str(e)
    
    # Desde variables de entorno
    if os.environ.get("REDPILL_API_KEY"):
        api_key_sources["environment"] = os.environ.get("REDPILL_API_KEY")
    
    # Desde session_state (requiere contexto de Streamlit)
    if "redpill_api_key" in st.session_state:
        api_key_sources["session_state"] = st.session_state["redpill_api_key"]
    
    # Evaluación general
    active_sources = [k for k, v in api_key_sources.items() if v]
    
    if not active_sources:
        resultado["status"] = "error"
        resultado["mensaje"] = "No se encontró una API key configurada en ninguna fuente"
    elif "secrets_toml" not in active_sources:
        resultado["status"] = "warning"
        resultado["mensaje"] = "API key disponible pero no configurada en secrets.toml"
    
    resultado["detalles"]["api_key_sources"] = {k: "✅ Configurada" if v else "❌ No configurada" for k, v in api_key_sources.items()}
    resultado["detalles"]["active_sources"] = active_sources
    
    return resultado

# Función para verificar SSL y conexión
def verificar_conexion() -> Dict[str, Any]:
    """Verifica la conexión a la API y configuración SSL."""
    resultado = {
        "status": "pending",
        "mensaje": "Verificando conexión...",
        "detalles": {}
    }
    
    # Obtener URL de la API
    try:
        api_url = get_api_url()
        resultado["detalles"]["api_url"] = api_url
    except:
        api_url = "https://redpill.io/api/v1"
        resultado["detalles"]["api_url"] = f"{api_url} (predeterminada)"
    
    # Verificar conectividad básica (sin SSL)
    try:
        hostname = api_url.replace("https://", "").replace("http://", "").split("/")[0]
        socket.create_connection((hostname, 443), timeout=5)
        resultado["detalles"]["socket_connection"] = "✅ Exitosa"
    except Exception as e:
        resultado["detalles"]["socket_connection"] = f"❌ Error: {str(e)}"
        resultado["status"] = "error"
        resultado["mensaje"] = f"No se puede conectar al servidor: {str(e)}"
        return resultado
    
    # Verificar SSL
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                resultado["detalles"]["ssl_connection"] = "✅ Exitosa"
                resultado["detalles"]["ssl_certificate"] = f"✅ Válido para {cert['subject'][0][0][1]}"
    except Exception as e:
        resultado["detalles"]["ssl_connection"] = f"❌ Error: {str(e)}"
        resultado["status"] = "error"
        resultado["mensaje"] = f"Error en la conexión SSL: {str(e)}"
        return resultado
    
    # Prueba de API con clave
    try:
        # Asegurar que hay una API key
        ensure_api_key_exists()
        api_key = st.session_state.get("redpill_api_key", "")
        
        # Intento básico de conexión a la API
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{api_url}/models", headers=headers, timeout=10)
        
        if response.status_code == 200:
            resultado["detalles"]["api_test"] = "✅ Exitosa"
            resultado["status"] = "success"
            resultado["mensaje"] = "Conexión a la API exitosa"
        else:
            resultado["detalles"]["api_test"] = f"❌ Error {response.status_code}: {response.text}"
            resultado["status"] = "error"
            resultado["mensaje"] = f"Error en la conexión a la API: {response.status_code}"
    except Exception as e:
        resultado["detalles"]["api_test"] = f"❌ Error: {str(e)}"
        resultado["status"] = "error"
        resultado["mensaje"] = f"Error al conectar con la API: {str(e)}"
    
    return resultado

# Función para verificar dependencias
def verificar_dependencias() -> Dict[str, Any]:
    """Verifica que todas las dependencias estén instaladas."""
    resultado = {
        "status": "success",
        "mensaje": "Todas las dependencias instaladas",
        "detalles": {}
    }
    
    # Lista de dependencias requeridas
    dependencias = [
        "streamlit",
        "pandas",
        "requests",
        "toml",
        "fuzzywuzzy",
        "altair",
        "openpyxl",
        "xlsxwriter"
    ]
    
    faltantes = []
    for dep in dependencias:
        try:
            importlib.import_module(dep)
            resultado["detalles"][dep] = "✅ Instalada"
        except ImportError:
            resultado["detalles"][dep] = "❌ No instalada"
            faltantes.append(dep)
    
    if faltantes:
        resultado["status"] = "error"
        resultado["mensaje"] = f"Faltan dependencias: {', '.join(faltantes)}"
    
    return resultado

# Función para solucionar problemas de API key
def solucionar_api_key() -> Dict[str, Any]:
    """Intenta solucionar problemas con la API key."""
    resultado = {
        "status": "pending",
        "mensaje": "Intentando solucionar...",
        "acciones": []
    }
    
    # Verificar si ya existe la carpeta .streamlit
    streamlit_dir = Path('.streamlit')
    if not streamlit_dir.exists():
        streamlit_dir.mkdir(exist_ok=True)
        resultado["acciones"].append("Creada carpeta .streamlit")
    
    # Verificar si existe secrets.toml
    secrets_path = streamlit_dir / 'secrets.toml'
    
    # Si no existe o está vacío, crear uno nuevo
    if not secrets_path.exists() or secrets_path.stat().st_size == 0:
        api_key = st.session_state.get("redpill_api_key", "")
        
        if not api_key:
            # Buscar en variables de entorno
            api_key = os.environ.get("REDPILL_API_KEY", "")
        
        if not api_key:
            # Usar la API key predeterminada
            api_key = "sk-xYBWXr1epqP3Uq1A05qUql9tAyBsJE5F8PL5L66gBaE328VG"
            resultado["acciones"].append("Usando API key predeterminada")
        
        # Crear el archivo secrets.toml
        try:
            with open(secrets_path, 'w') as f:
                f.write("[redpill]\n")
                f.write(f'api_key = "{api_key}"\n')
                f.write(f'api_url = "https://redpill.io/api/v1"\n')
            
            resultado["acciones"].append("Creado archivo secrets.toml con API key")
            resultado["status"] = "success"
            resultado["mensaje"] = "API key configurada correctamente"
        except Exception as e:
            resultado["acciones"].append(f"Error al crear secrets.toml: {str(e)}")
            resultado["status"] = "error"
            resultado["mensaje"] = f"No se pudo crear el archivo secrets.toml: {str(e)}"
            
            # Plan B: Guardar en session_state
            st.session_state["redpill_api_key"] = api_key
            resultado["acciones"].append("API key guardada en session_state como respaldo")
    else:
        # El archivo existe, verificar si tiene la sección redpill
        try:
            secrets = toml.load(secrets_path)
            if "redpill" not in secrets or "api_key" not in secrets["redpill"]:
                # Añadir la sección redpill con la API key
                api_key = st.session_state.get("redpill_api_key", "sk-xYBWXr1epqP3Uq1A05qUql9tAyBsJE5F8PL5L66gBaE328VG")
                
                # Intentar actualizar el archivo existente
                secrets.setdefault("redpill", {})["api_key"] = api_key
                secrets.setdefault("redpill", {})["api_url"] = "https://redpill.io/api/v1"
                
                with open(secrets_path, 'w') as f:
                    toml.dump(secrets, f)
                
                resultado["acciones"].append("Actualizado archivo secrets.toml con API key")
                resultado["status"] = "success"
                resultado["mensaje"] = "API key configurada correctamente"
            else:
                resultado["acciones"].append("El archivo secrets.toml ya contiene la API key")
                resultado["status"] = "success"
                resultado["mensaje"] = "API key ya estaba configurada"
                
                # Actualizar session_state para asegurar consistencia
                st.session_state["redpill_api_key"] = secrets["redpill"]["api_key"]
        except Exception as e:
            resultado["acciones"].append(f"Error al modificar secrets.toml: {str(e)}")
            resultado["status"] = "error"
            resultado["mensaje"] = f"No se pudo modificar el archivo secrets.toml: {str(e)}"
    
    # Asegurar que la API key esté en session_state
    ensure_api_key_exists()
    
    return resultado

# Función para probar la API key actual
def probar_api_key() -> Dict[str, Any]:
    """Realiza una prueba de conexión con la API key actual."""
    resultado = {
        "status": "pending",
        "mensaje": "Probando API key...",
        "detalles": {}
    }
    
    # Asegurar que hay una API key
    ensure_api_key_exists()
    api_key = st.session_state.get("redpill_api_key", "")
    
    if not api_key:
        resultado["status"] = "error"
        resultado["mensaje"] = "No hay API key configurada"
        return resultado
    
    # Obtener URL de la API
    try:
        api_url = get_api_url()
    except:
        api_url = "https://redpill.io/api/v1"
    
    # Probar la API key
    try:
        # Test 1: Obtener modelos disponibles
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{api_url}/models", headers=headers, timeout=10)
        
        if response.status_code == 200:
            resultado["detalles"]["models_test"] = "✅ Exitoso"
            modelos = response.json()
            resultado["detalles"]["available_models"] = [m.get("id", "Unknown") for m in modelos]
        else:
            resultado["detalles"]["models_test"] = f"❌ Error {response.status_code}: {response.text}"
            resultado["status"] = "error"
            resultado["mensaje"] = f"Error al obtener modelos: {response.status_code}"
            return resultado
        
        # Test 2: Prueba básica de chat completions
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hola, ¿cómo estás?"}],
            "max_tokens": 50
        }
        
        response = requests.post(
            f"{api_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=15
        )
        
        if response.status_code == 200:
            resultado["detalles"]["chat_test"] = "✅ Exitoso"
            resultado["status"] = "success"
            resultado["mensaje"] = "API key funciona correctamente"
            
            # Mostrar la respuesta del modelo
            try:
                respuesta = response.json()
                mensaje = respuesta.get("choices", [{}])[0].get("message", {}).get("content", "")
                resultado["detalles"]["model_response"] = mensaje
            except:
                resultado["detalles"]["model_response"] = "No se pudo obtener la respuesta"
        else:
            resultado["detalles"]["chat_test"] = f"❌ Error {response.status_code}: {response.text}"
            resultado["status"] = "error"
            resultado["mensaje"] = f"Error en la prueba de chat: {response.status_code}"
    except Exception as e:
        resultado["detalles"]["error"] = str(e)
        resultado["status"] = "error"
        resultado["mensaje"] = f"Error en la conexión: {str(e)}"
    
    return resultado

# Aplicación principal
def main():
    st.title("🔍 Diagnóstico del Sistema")
    st.markdown("Esta herramienta ayuda a diagnosticar y resolver problemas comunes en la plataforma.")
    
    # Inicializar ensure_api_key_exists() para asegurar que hay una clave
    ensure_api_key_exists()
    
    # Menú de diagnóstico
    st.sidebar.title("Opciones de Diagnóstico")
    opciones = [
        "Diagnóstico Completo",
        "Estructura del Proyecto",
        "Configuración de API Key",
        "Verificar Conexión",
        "Dependencias",
        "Prueba de API"
    ]
    
    seleccion = st.sidebar.radio("Seleccione una opción:", opciones)
    
    # Diagnóstico Completo
    if seleccion == "Diagnóstico Completo":
        st.header("Diagnóstico Completo del Sistema")
        
        col1, col2 = st.columns(2)
        
        # Estructura del proyecto
        with col1:
            with st.expander("Estructura del Proyecto", expanded=True):
                resultado = verificar_estructura_proyecto()
                if resultado["status"] == "success":
                    st.markdown(f"""<div class="success-box">
                        <div class="diagnostic-header">✅ Estructura Correcta</div>
                        {resultado["mensaje"]}
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="error-box">
                        <div class="diagnostic-header">❌ Problema en la Estructura</div>
                        {resultado["mensaje"]}
                    </div>""", unsafe_allow_html=True)
        
        # API Key
        with col2:
            with st.expander("Configuración de API Key", expanded=True):
                resultado = verificar_api_keys()
                if resultado["status"] == "success":
                    st.markdown(f"""<div class="success-box">
                        <div class="diagnostic-header">✅ API Key Configurada</div>
                        {resultado["mensaje"]}
                    </div>""", unsafe_allow_html=True)
                elif resultado["status"] == "warning":
                    st.markdown(f"""<div class="warning-box">
                        <div class="diagnostic-header">⚠️ API Key Parcialmente Configurada</div>
                        {resultado["mensaje"]}
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="error-box">
                        <div class="diagnostic-header">❌ Problema con API Key</div>
                        {resultado["mensaje"]}
                    </div>""", unsafe_allow_html=True)
        
        # Conexión
        st.subheader("Verificación de Conexión")
        with st.spinner("Verificando conexión..."):
            resultado = verificar_conexion()
            if resultado["status"] == "success":
                st.markdown(f"""<div class="success-box">
                    <div class="diagnostic-header">✅ Conexión Exitosa</div>
                    {resultado["mensaje"]}
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="error-box">
                    <div class="diagnostic-header">❌ Problema de Conexión</div>
                    {resultado["mensaje"]}
                </div>""", unsafe_allow_html=True)
        
        # Dependencias
        st.subheader("Verificación de Dependencias")
        resultado = verificar_dependencias()
        if resultado["status"] == "success":
            st.markdown(f"""<div class="success-box">
                <div class="diagnostic-header">✅ Dependencias Completas</div>
                {resultado["mensaje"]}
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="error-box">
                <div class="diagnostic-header">❌ Dependencias Faltantes</div>
                {resultado["mensaje"]}
            </div>""", unsafe_allow_html=True)
        
        # Acciones recomendadas
        st.subheader("Acciones Recomendadas")
        
        if (verificar_api_keys()["status"] != "success" or 
            verificar_conexion()["status"] != "success"):
            if st.button("🔧 Solucionar Problemas de API Key"):
                with st.spinner("Solucionando..."):
                    resultado = solucionar_api_key()
                    for accion in resultado["acciones"]:
                        st.write(f"- {accion}")
                    
                    if resultado["status"] == "success":
                        st.success(resultado["mensaje"])
                    else:
                        st.error(resultado["mensaje"])
            
            if st.button("🔄 Reiniciar Sesión"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.experimental_rerun()
    
    # Estructura del Proyecto
    elif seleccion == "Estructura del Proyecto":
        st.header("Verificación de Estructura del Proyecto")
        resultado = verificar_estructura_proyecto()
        
        if resultado["status"] == "success":
            st.success(resultado["mensaje"])
        else:
            st.error(resultado["mensaje"])
            st.write("Archivos faltantes:")
            for archivo in resultado["faltantes"]:
                st.write(f"- {archivo}")
    
    # Configuración de API Key
    elif seleccion == "Configuración de API Key":
        st.header("Verificación de API Key")
        resultado = verificar_api_keys()
        
        if resultado["status"] == "success":
            st.success(resultado["mensaje"])
        elif resultado["status"] == "warning":
            st.warning(resultado["mensaje"])
        else:
            st.error(resultado["mensaje"])
        
        st.subheader("Detalles")
        st.json(resultado["detalles"])
        
        # Opciones para solucionar problemas
        st.subheader("Solucionar Problemas")
        
        # Mostrar API key actual (oculta)
        api_key = st.session_state.get("redpill_api_key", "")
        st.text_input("API Key actual", value=api_key, type="password", disabled=True)
        
        # Opción para ingresar nueva API key
        nueva_key = st.text_input("Nueva API Key (opcional)", type="password")
        
        if st.button("Configurar API Key"):
            if nueva_key:
                st.session_state["redpill_api_key"] = nueva_key
            
            with st.spinner("Configurando API Key..."):
                resultado = solucionar_api_key()
                for accion in resultado["acciones"]:
                    st.write(f"- {accion}")
                
                if resultado["status"] == "success":
                    st.success(resultado["mensaje"])
                else:
                    st.error(resultado["mensaje"])
    
    # Verificar Conexión
    elif seleccion == "Verificar Conexión":
        st.header("Verificación de Conexión")
        
        with st.spinner("Verificando conexión..."):
            resultado = verificar_conexion()
            
            if resultado["status"] == "success":
                st.success(resultado["mensaje"])
            else:
                st.error(resultado["mensaje"])
            
            st.subheader("Detalles")
            st.json(resultado["detalles"])
        
        # Opciones adicionales para SSL
        if "ssl_connection" in resultado["detalles"] and "❌" in resultado["detalles"]["ssl_connection"]:
            st.subheader("Opciones para Solucionar SSL")
            
            if st.button("Ejecutar Diagnóstico SSL Detallado"):
                try:
                    with st.spinner("Ejecutando diagnóstico SSL..."):
                        from ssl_diagnostico import diagnosticar_ssl
                        resultados_ssl = diagnosticar_ssl()
                        st.json(resultados_ssl)
                except Exception as e:
                    st.error(f"Error al ejecutar diagnóstico SSL: {str(e)}")
    
    # Dependencias
    elif seleccion == "Dependencias":
        st.header("Verificación de Dependencias")
        resultado = verificar_dependencias()
        
        if resultado["status"] == "success":
            st.success(resultado["mensaje"])
        else:
            st.error(resultado["mensaje"])
        
        st.subheader("Detalles")
        for dep, status in resultado["detalles"].items():
            st.write(f"{dep}: {status}")
        
        # Opción para instalar dependencias faltantes
        if resultado["status"] != "success":
            if st.button("Instalar Dependencias Faltantes"):
                faltantes = [dep for dep, status in resultado["detalles"].items() if "❌" in status]
                comando = f"pip install {' '.join(faltantes)}"
                
                st.code(comando)
                st.info("Copia y ejecuta este comando en tu terminal para instalar las dependencias faltantes.")
    
    # Prueba de API
    elif seleccion == "Prueba de API":
        st.header("Prueba de API")
        
        # Mostrar API key actual (parcialmente oculta)
        api_key = st.session_state.get("redpill_api_key", "")
        if api_key:
            # Mostrar solo primeros y últimos 4 caracteres
            if len(api_key) > 8:
                displayed_key = f"{api_key[:4]}...{api_key[-4:]}"
            else:
                displayed_key = "****"
            st.info(f"Usando API key: {displayed_key}")
        else:
            st.warning("No hay API key configurada")
        
        if st.button("Probar Conexión a API"):
            with st.spinner("Probando conexión..."):
                resultado = probar_api_key()
                
                if resultado["status"] == "success":
                    st.success(resultado["mensaje"])
                else:
                    st.error(resultado["mensaje"])
                
                st.subheader("Detalles")
                st.json(resultado["detalles"])
                
                # Si hay respuesta del modelo, mostrarla
                if "model_response" in resultado["detalles"]:
                    st.subheader("Respuesta del Modelo")
                    st.write(resultado["detalles"]["model_response"])

if __name__ == "__main__":
    main()
