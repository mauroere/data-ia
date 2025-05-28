import streamlit as st
import os
import sys
import toml
import pprint

# Función para encontrar el archivo secrets.toml
def find_secrets_file():
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.streamlit', 'secrets.toml'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '.streamlit', 'secrets.toml'),
        os.path.join(os.getcwd(), '.streamlit', 'secrets.toml')
    ]
    
    found_paths = []
    for path in possible_paths:
        if os.path.exists(path):
            found_paths.append(path)
    
    return found_paths

# Función para mostrar estructura del directorio
def show_directory_structure(start_path):
    for root, dirs, files in os.walk(start_path):
        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for file in files:
            if '.streamlit' in root and 'secrets.toml' in file:
                print(f"{subindent}{file} <- ¡ARCHIVO DE SECRETS ENCONTRADO!")
            else:
                print(f"{subindent}{file}")

# Función para probar la carga de secrets con Streamlit
def test_streamlit_secrets():
    print("\n=== TEST DE SECRETS DE STREAMLIT ===")
    try:
        secrets = st.secrets
        print("✅ st.secrets cargado correctamente")
        
        # Intentar acceder a la clave de Redpill
        try:
            redpill_key = secrets["redpill"]["api_key"]
            print(f"✅ Clave API de Redpill encontrada en st.secrets: {redpill_key[:5]}...")
        except Exception as e:
            print(f"❌ Error al acceder a la clave API de Redpill en st.secrets: {e}")
        
        # Mostrar estructura completa de secrets (sin mostrar valores completos)
        print("\nEstructura de st.secrets:")
        secrets_dict = {k: {sk: f"{str(sv)[:5]}..." if isinstance(sv, str) and len(sv) > 10 else sv 
                          for sk, sv in v.items()} 
                      for k, v in secrets.items()}
        pprint.pprint(secrets_dict)
        
    except Exception as e:
        print(f"❌ Error al cargar st.secrets: {e}")

# Función para cargar el archivo secrets.toml manualmente
def load_secrets_manually(path):
    print(f"\n=== CARGA MANUAL DE {path} ===")
    try:
        secrets = toml.load(path)
        print("✅ Archivo cargado correctamente con toml.load()")
        
        # Intentar acceder a la clave de Redpill
        try:
            redpill_key = secrets["redpill"]["api_key"]
            print(f"✅ Clave API de Redpill encontrada: {redpill_key[:5]}...")
        except Exception as e:
            print(f"❌ Error al acceder a la clave API de Redpill: {e}")
        
        # Mostrar estructura completa (sin mostrar valores completos)
        print("\nEstructura del archivo:")
        secrets_dict = {k: {sk: f"{str(sv)[:5]}..." if isinstance(sv, str) and len(sv) > 10 else sv 
                          for sk, sv in v.items()} 
                      for k, v in secrets.items()}
        pprint.pprint(secrets_dict)
        
        # Verificar formato TOML
        print("\nVerificando formato TOML:")
        with open(path, 'r') as f:
            content = f.read()
            if content.strip().startswith('//'):
                print("❌ ERROR: El archivo comienza con comentarios estilo JavaScript (//)")
                print("   Streamlit espera comentarios estilo TOML (#)")
                print("   Esto podría ser la causa del problema!")
            else:
                print("✅ Formato de comentarios parece correcto")
        
    except Exception as e:
        print(f"❌ Error al cargar el archivo manualmente: {e}")

def main():
    print("=== DIAGNÓSTICO DE CARGA DE SECRETS PARA REDPILL API ===")
    print(f"Python version: {sys.version}")
    print(f"Directorio actual: {os.getcwd()}")
    
    # Buscar archivos secrets.toml
    print("\n=== BUSCANDO ARCHIVOS SECRETS.TOML ===")
    found_paths = find_secrets_file()
    if found_paths:
        print(f"✅ Encontrados {len(found_paths)} archivos secrets.toml:")
        for path in found_paths:
            print(f"  - {path}")
    else:
        print("❌ No se encontró ningún archivo secrets.toml en las rutas esperadas")
        
    # Mostrar estructura del directorio
    print("\n=== ESTRUCTURA DEL DIRECTORIO ===")
    show_directory_structure(os.path.dirname(os.path.abspath(__file__)))
    
    # Probar la carga de secrets con Streamlit
    test_streamlit_secrets()
    
    # Probar la carga manual de cada archivo encontrado
    for path in found_paths:
        load_secrets_manually(path)
    
    # Diagnosticar problemas comunes
    print("\n=== POSIBLES SOLUCIONES ===")
    print("1. Si el archivo secrets.toml comienza con // en lugar de #, cambia el formato de comentarios")
    print("2. Verifica que el archivo .streamlit/secrets.toml esté en el directorio raíz del proyecto")
    print("3. Asegúrate de que el archivo tenga el formato correcto:")
    print("""
    [redpill]
    api_key = "tu-clave-api"
    api_url = "https://api.redpill.ai/v1/chat/completions"
    """)
    print("4. Reinicia la aplicación Streamlit después de realizar cambios")

if __name__ == "__main__":
    main()
