import os
import sys
import toml
import streamlit as st

def check_streamlit_secrets():
    """Verifica si los secretos de Streamlit están configurados correctamente"""
    print("Verificando secretos de Streamlit...")
    
    # Verificar si existe el directorio .streamlit
    streamlit_dir = os.path.join(os.path.dirname(__file__), '.streamlit')
    if not os.path.exists(streamlit_dir):
        print("❌ No se encontró el directorio .streamlit")
        return False
    
    # Verificar si existe el archivo secrets.toml
    secrets_path = os.path.join(streamlit_dir, 'secrets.toml')
    if not os.path.exists(secrets_path):
        print("❌ No se encontró el archivo secrets.toml")
        return False
    
    # Leer el archivo de secretos
    try:
        secrets = toml.load(secrets_path)
        print("✅ Archivo secrets.toml cargado correctamente")
        
        # Verificar si existen las secciones necesarias
        if 'openai' not in secrets:
            print("❌ Falta la sección [openai] en secrets.toml")
        elif 'api_key' not in secrets['openai']:
            print("❌ Falta api_key en la sección [openai]")
        elif not secrets['openai']['api_key']:
            print("⚠️ La clave API de OpenAI está vacía")
        else:
            print(f"✅ Clave API de OpenAI: {secrets['openai']['api_key'][:5]}...")
        
        if 'redpill' not in secrets:
            print("❌ Falta la sección [redpill] en secrets.toml")
        elif 'api_key' not in secrets['redpill']:
            print("❌ Falta api_key en la sección [redpill]")
        elif not secrets['redpill']['api_key']:
            print("⚠️ La clave API de Redpill está vacía")
        else:
            print(f"✅ Clave API de Redpill: {secrets['redpill']['api_key'][:5]}...")
        
        return True
    
    except Exception as e:
        print(f"❌ Error al leer secrets.toml: {e}")
        return False

if __name__ == "__main__":
    print("=== Verificador de Claves API ===")
    check_streamlit_secrets()
    print("\nPara ejecutar la aplicación, utiliza:")
    print("streamlit run main.py")
