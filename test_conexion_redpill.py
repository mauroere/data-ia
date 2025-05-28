"""
Script para probar la conexión con la API de Redpill.ai
Este script es independiente de Streamlit y no requiere instalación adicional
"""
import requests
import urllib3
import os
import sys
import json

# Desactivar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cargar_secretos():
    """Carga los secretos desde el archivo .streamlit/secrets.toml"""
    secrets_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
    
    # Verificar si existe el archivo
    if not os.path.exists(secrets_path):
        print(f"❌ No se encontró el archivo de secretos en: {secrets_path}")
        return None
    
    # Leer el archivo manualmente
    result = {}
    current_section = None
    
    with open(secrets_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Saltar líneas vacías y comentarios
            if not line or line.startswith('#'):
                continue
                
            # Detectar secciones [section]
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                result[current_section] = {}
            
            # Detectar pares clave = valor
            elif '=' in line and current_section is not None:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Quitar comillas de los valores
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                
                result[current_section][key] = value
    
    return result

def probar_conexion(api_key=None, api_url=None):
    """Prueba la conexión con la API de Redpill"""
    # Si no se proporcionan valores, intentar cargarlos de los secretos
    if api_key is None or api_url is None:
        secrets = cargar_secretos()
        if not secrets or 'redpill' not in secrets:
            print("❌ No se pudieron cargar los secretos de Redpill")
            return False
        
        if api_key is None:
            api_key = secrets['redpill'].get('api_key')
        if api_url is None:
            api_url = secrets['redpill'].get('api_url', 'https://api.redpill.ai/v1/chat/completions')
    
    # Verificar que tenemos los valores necesarios
    if not api_key:
        print("❌ No se especificó la clave API")
        return False
    
    if not api_url:
        print("❌ No se especificó la URL de la API")
        return False
    
    # Configurar headers y payload
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "mistralai/ministral-8b",
        "messages": [{"role": "user", "content": "Hola, ¿cómo estás?"}],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    print(f"\nRealizando petición a: {api_url}")
    print(f"Usando clave API: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        # Realizar la petición
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            verify=False,  # Desactivar verificación SSL
            timeout=10     # Timeout en segundos
        )
        
        print(f"\nCódigo de estado: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ ¡Conexión exitosa!")
            try:
                json_response = response.json()
                print("\nRespuesta:")
                respuesta = json_response.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"Respuesta: {respuesta}")
                return True
            except Exception as e:
                print(f"❌ Error al procesar la respuesta JSON: {e}")
                print(f"Respuesta recibida: {response.text[:200]}...")
        else:
            print(f"❌ Error en la respuesta: {response.text}")
            
    except requests.exceptions.SSLError:
        print("❌ Error SSL - Conexión segura fallida")
        print("Recomendación: Verificar la configuración SSL/TLS del sistema")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - No se pudo establecer la conexión")
        print("Recomendación: Verificar la conectividad de red y posibles restricciones de firewall")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout - La solicitud tardó demasiado tiempo")
        print("Recomendación: Verificar la conectividad de red o si el servidor está sobrecargado")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    return False

def main():
    print("===== TEST DE CONEXIÓN API REDPILL =====")
    
    # Verificar si hay argumentos de línea de comandos
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        api_url = sys.argv[2] if len(sys.argv) > 2 else "https://api.redpill.ai/v1/chat/completions"
        probar_conexion(api_key, api_url)
    else:
        # Cargar desde secrets.toml
        probar_conexion()

if __name__ == "__main__":
    main()
