import streamlit as st
import os
import json
import toml
import requests
import urllib3

# Desactivar advertencias de solicitudes (por problemas con certificados en algunos entornos)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def debug_secrets():
    """
    Depura la carga de los secretos de Streamlit y crea un archivo de configuración
    nuevo si es necesario.
    """
    st.title("Diagnóstico de Secretos de Streamlit")
    
    # Directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    st.write(f"Directorio actual: {current_dir}")
    
    # Verificar si existe el directorio .streamlit
    streamlit_dir = os.path.join(os.path.dirname(current_dir), '.streamlit')
    if not os.path.exists(streamlit_dir):
        streamlit_dir = os.path.join(current_dir, '.streamlit')
    
    st.write(f"Directorio de Streamlit: {streamlit_dir}")
    st.write(f"¿Existe? {os.path.exists(streamlit_dir)}")
    
    # Verificar si existe el archivo secrets.toml
    secrets_path = os.path.join(streamlit_dir, 'secrets.toml')
    st.write(f"Ruta al archivo de secretos: {secrets_path}")
    st.write(f"¿Existe? {os.path.exists(secrets_path)}")
    
    # Intentar leer el archivo de secretos
    if os.path.exists(secrets_path):
        try:
            with open(secrets_path, 'r', encoding='utf-8') as f:
                content = f.read()
                st.code(content, language="toml")
            
            # Intentar cargar como TOML
            try:
                secrets = toml.loads(content)
                st.write("Contenido TOML parseado correctamente:")
                st.json(secrets)
            except Exception as e:
                st.error(f"Error al parsear TOML: {str(e)}")
                
        except Exception as e:
            st.error(f"Error al leer el archivo: {str(e)}")
    
    # Verificar si Streamlit cargó los secretos
    st.subheader("Estado actual de st.secrets")
    try:
        # Convertir st.secrets a diccionario
        secrets_dict = {key: st.secrets.get(key) for key in st.secrets.to_dict()}
        st.json(secrets_dict)
    except Exception as e:
        st.error(f"Error al acceder a st.secrets: {str(e)}")
    
    # Opción para crear un nuevo archivo de secretos
    st.subheader("Crear nuevo archivo de secretos")
    
    # API Key de Redpill
    redpill_api_key = st.text_input(
        "API Key de Redpill:",
        value="sk-xYBWXr1epqP3Uq1A05qUql9tAyBsJE5F8PL5L66gBaE328VG",
        type="password"
    )
    
    # URL de la API de Redpill
    redpill_api_url = st.text_input(
        "URL de la API de Redpill:",
        value="https://api.redpill.ai/v1/chat/completions"
    )
    
    # API Key de OpenAI
    openai_api_key = st.text_input(
        "API Key de OpenAI (opcional):",
        type="password"
    )
    
    # URL de la API de OpenAI
    openai_api_url = st.text_input(
        "URL de la API de OpenAI (opcional):",
        value="https://api.openai.com/v1/chat/completions"
    )
    
    if st.button("Crear/Actualizar archivo de secretos"):
        # Crear el contenido TOML
        content = ""
        
        if openai_api_key:
            content += "[openai]\n"
            content += f'api_key = "{openai_api_key}"\n'
            if openai_api_url:
                content += f'api_url = "{openai_api_url}"\n'
            content += "\n"
        
        if redpill_api_key:
            content += "[redpill]\n"
            content += f'api_key = "{redpill_api_key}"\n'
            if redpill_api_url:
                content += f'api_url = "{redpill_api_url}"\n'
            content += "\n"
        
        # Asegurarnos de que el directorio existe
        os.makedirs(streamlit_dir, exist_ok=True)
        
        # Escribir el archivo
        try:
            with open(secrets_path, 'w', encoding='utf-8') as f:
                f.write(content)
            st.success(f"¡Archivo de secretos creado/actualizado correctamente en {secrets_path}!")
            
            # También guardar en session_state
            st.session_state["redpill_api_key"] = redpill_api_key
            st.session_state["redpill_api_url"] = redpill_api_url
            if openai_api_key:
                st.session_state["openai_api_key"] = openai_api_key
            if openai_api_url:
                st.session_state["openai_api_url"] = openai_api_url
                
            st.info("Los cambios se aplicarán después de reiniciar la aplicación.")
            if st.button("Reiniciar aplicación"):
                st.experimental_rerun()
                
        except Exception as e:
            st.error(f"Error al escribir el archivo: {str(e)}")
            
    # Opción para probar directamente la API
    st.subheader("Probar conexión a la API")
    if st.button("Probar API de Redpill"):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {redpill_api_key}"
        }
        
        payload = {
            "model": "mistralai/ministral-8b",
            "messages": [{"role": "user", "content": "Hola, ¿cómo estás?"}],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        try:
            response = requests.post(
                redpill_api_url,
                headers=headers,
                json=payload,
                verify=False,
                timeout=10
            )
            
            st.write(f"Status code: {response.status_code}")
            if response.status_code == 200:
                st.success("✓ La API funciona correctamente")
                st.json(response.json())
            else:
                st.error(f"✗ Error: {response.text}")
        except Exception as e:
            st.error(f"✗ Excepción: {str(e)}")
    
def check_api_key_state():
    """Verifica y muestra el estado actual de la clave API en diferentes ubicaciones."""
    st.subheader("🔍 Estado de la API Key")
    
    # 1. Verificar session_state
    st.write("### Estado en session_state:")
    if "redpill_api_key" in st.session_state:
        key = st.session_state["redpill_api_key"]
        if key and len(key.strip()) > 0:
            st.success("✅ La clave está presente en session_state")
            st.code(f"Longitud: {len(key)} caracteres")
        else:
            st.warning("⚠️ La clave está en session_state pero está vacía")
    else:
        st.info("ℹ️ No hay clave en session_state")
    
    # 2. Verificar secrets.toml
    secrets_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
    st.write("### Estado en secrets.toml:")
    if os.path.exists(secrets_path):
        try:
            secrets = toml.load(secrets_path)
            if "redpill" in secrets and "api_key" in secrets["redpill"]:
                key = secrets["redpill"]["api_key"]
                if key and len(key.strip()) > 0:
                    st.success("✅ La clave está presente en secrets.toml")
                    st.code(f"Longitud: {len(key)} caracteres")
                else:
                    st.warning("⚠️ La clave está en secrets.toml pero está vacía")
            else:
                st.warning("⚠️ No se encontró la sección [redpill] o api_key en secrets.toml")
        except Exception as e:
            st.error(f"❌ Error al leer secrets.toml: {e}")
    else:
        st.error("❌ No se encontró el archivo secrets.toml")
    
    # 3. Verificar st.secrets
    st.write("### Estado en st.secrets:")
    try:
        if "redpill" in st.secrets and "api_key" in st.secrets["redpill"]:
            key = st.secrets["redpill"]["api_key"]
            if key and len(key.strip()) > 0:
                st.success("✅ La clave está presente en st.secrets")
                st.code(f"Longitud: {len(key)} caracteres")
            else:
                st.warning("⚠️ La clave está en st.secrets pero está vacía")
        else:
            st.warning("⚠️ No se encontró la sección [redpill] o api_key en st.secrets")
    except Exception as e:
        st.error(f"❌ Error al acceder a st.secrets: {e}")
    
    # Mostrar recomendaciones
    st.write("### 📋 Recomendaciones:")
    st.markdown("""
    1. Si la clave no está en ningún lugar, configúrala en el Panel de Administración
    2. Si la clave está en secrets.toml pero no en st.secrets, reinicia la aplicación
    3. Si la clave está pero no funciona, verifica que sea correcta en el Panel de Administración
    """)

if __name__ == "__main__":
    st.title("🔧 Diagnóstico de Configuración")
    
    # Agregar botón para ejecutar el diagnóstico de API key
    if st.button("Verificar estado de API Key"):
        check_api_key_state()
    
    # Separador
    st.markdown("---")
    
    # Mantener la función original de debug_secrets
    debug_secrets()
