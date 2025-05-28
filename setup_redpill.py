"""
Script de configuración para la aplicación de Redpill
Este script realiza las siguientes acciones:
1. Verifica que el archivo de secretos tenga el formato correcto
2. Prueba la conexión con la API de Redpill
3. Instala las dependencias necesarias si no están instaladas
"""
import os
import sys
import subprocess

def check_and_install_packages():
    """Verifica si los paquetes necesarios están instalados y los instala si no"""
    required_packages = ['streamlit', 'requests', 'toml', 'pandas', 'chardet']
    
    print("\n=== VERIFICANDO PAQUETES INSTALADOS ===")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: instalado")
        except ImportError:
            print(f"❌ {package}: no instalado")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nInstalando {len(missing_packages)} paquetes faltantes...")
        for package in missing_packages:
            print(f"Instalando {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} instalado correctamente")
    else:
        print("\nTodos los paquetes necesarios están instalados.")

def check_secrets_file():
    """Verifica si el archivo de secretos existe y tiene el formato correcto"""
    print("\n=== VERIFICANDO ARCHIVO DE SECRETOS ===")
    
    # Ruta al archivo de secretos
    streamlit_dir = os.path.join(os.path.dirname(__file__), '.streamlit')
    secrets_path = os.path.join(streamlit_dir, 'secrets.toml')
    
    # Verificar si existe el directorio
    if not os.path.exists(streamlit_dir):
        print(f"❌ El directorio {streamlit_dir} no existe")
        print(f"Creando directorio...")
        os.makedirs(streamlit_dir)
        print(f"✅ Directorio creado correctamente")
    
    # Verificar si existe el archivo
    if not os.path.exists(secrets_path):
        print(f"❌ El archivo {secrets_path} no existe")
        print(f"Creando archivo de secretos...")
        
        # Solicitar API key de Redpill
        redpill_api_key = input("Ingresa tu clave API de Redpill (deja en blanco para usar la predeterminada): ")
        if not redpill_api_key:
            redpill_api_key = "sk-xYBWXr1epqP3Uq1A05qUql9tAyBsJE5F8PL5L66gBaE328VG"
            print(f"Usando clave API predeterminada: {redpill_api_key[:5]}...")
        
        # Crear contenido del archivo
        content = f"""# Archivo de configuración para Redpill API
[redpill]
api_key = "{redpill_api_key}"
api_url = "https://api.redpill.ai/v1/chat/completions"

[openai]
api_key = "{redpill_api_key}"
api_url = "https://api.openai.com/v1/chat/completions"
"""
        
        # Escribir archivo
        with open(secrets_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Archivo de secretos creado correctamente")
    else:
        print(f"✅ El archivo {secrets_path} existe")
        
        # Verificar formato del archivo
        with open(secrets_path, 'r') as f:
            content = f.read()
            
            if content.strip().startswith('//'):
                print(f"❌ El archivo tiene formato de comentarios incorrecto (usa // en lugar de #)")
                print(f"Corrigiendo formato...")
                
                # Corregir formato
                content = content.replace('//', '#', 1)
                
                # Escribir archivo corregido
                with open(secrets_path, 'w') as f:
                    f.write(content)
                
                print(f"✅ Formato del archivo corregido")
            else:
                print(f"✅ El formato del archivo es correcto")

def test_api_connection():
    """Prueba la conexión con la API de Redpill"""
    print("\n=== PROBANDO CONEXIÓN CON LA API DE REDPILL ===")
    
    try:
        # Intentar importar el módulo
        sys.path.insert(0, os.path.dirname(__file__))
        from test_conexion_redpill_basic import probar_conexion
        
        # Probar conexión
        probar_conexion()
    except ImportError:
        print("❌ No se pudo importar el módulo test_conexion_redpill_basic")
        print("Verificando conexión manualmente...")
        
        # Ejecutar script manualmente
        script_path = os.path.join(os.path.dirname(__file__), 'test_conexion_redpill_basic.py')
        if os.path.exists(script_path):
            print(f"✅ El script {script_path} existe")
            print(f"Ejecutando script...")
            subprocess.check_call([sys.executable, script_path])
        else:
            print(f"❌ El script {script_path} no existe")
    except Exception as e:
        print(f"❌ Error al probar conexión: {e}")

def main():
    print("===== CONFIGURACIÓN DE REDPILL API =====")
    
    # Verificar y instalar paquetes
    check_and_install_packages()
    
    # Verificar archivo de secretos
    check_secrets_file()
    
    # Probar conexión
    test_api_connection()
    
    print("\n===== CONFIGURACIÓN COMPLETADA =====")
    print("La aplicación está lista para usarse.")
    print("Para iniciar la aplicación, ejecuta:")
    print("streamlit run main.py")

if __name__ == "__main__":
    main()
