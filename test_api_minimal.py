"""
Script muy básico para probar la API de Redpill con un contexto enriquecido
utilizando solo la biblioteca estándar de Python
"""
import urllib.request
import urllib.error
import ssl
import json
import os
import sys

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

def probar_api_con_contexto():
    """Prueba la API de Redpill con un contexto enriquecido"""
    # Cargar secretos
    secrets = cargar_secretos()
    if not secrets or 'redpill' not in secrets:
        print("❌ No se pudieron cargar los secretos de Redpill")
        return False
        
    api_key = secrets['redpill'].get('api_key')
    api_url = secrets['redpill'].get('api_url', 'https://api.redpill.ai/v1/chat/completions')
    
    # Verificar que tenemos los valores necesarios
    if not api_key:
        print("❌ No se especificó la clave API")
        return False
    
    if not api_url:
        print("❌ No se especificó la URL de la API")
        return False
    
    # Crear un contexto enriquecido (simulando los datos de la aplicación)
    contexto = """
    Eres un asistente especializado en análisis de datos que ayuda a los usuarios a trabajar con archivos CSV, Excel y realizar cruces de datos.

    El usuario ha cargado dos archivos de datos:
    1. Archivo BASE con 5 filas y columnas: id, nombre, edad, ciudad
    2. Archivo NUEVO con 4 filas y columnas: id, nombre, puntuacion, departamento

    Ejemplo de 3 filas del Archivo BASE:
       id        nombre  edad     ciudad
    0   1    Juan Pérez    35     Madrid
    1   2   María López    42  Barcelona
    2   3  Carlos Rodríguez  28    Sevilla

    Ejemplo de 3 filas del Archivo NUEVO:
       id   nombre  puntuacion departamento
    0  101  Juan P.          85       Ventas
    1  102  María L.          92    Marketing
    2  103 Carlos R.         78          IT

    La aplicación permite realizar cruces inteligentes entre los archivos utilizando fuzzy matching.
    El fuzzy matching permite encontrar coincidencias similares aunque no sean exactamente iguales.

    El usuario ha seleccionado 'nombre' como campo clave para el cruce.

    Se han encontrado 4 coincidencias entre los archivos.
    Ejemplos de coincidencias:
    - 'Juan P.' coincide con 'Juan Pérez'
    - 'María L.' coincide con 'María López'
    - 'Carlos R.' coincide con 'Carlos Rodríguez'
    """
    
    # Pregunta del usuario
    pregunta = "¿Qué personas coinciden en ambos archivos y cuáles son sus departamentos y ciudades?"
    
    # Enriquecer la pregunta con el contexto
    pregunta_enriquecida = f"{contexto}\n\nPregunta del usuario: {pregunta}\n\nResponde a la pregunta del usuario en español, teniendo en cuenta el contexto proporcionado y las funcionalidades de la aplicación para el cruce inteligente de datos."
    
    # Configurar headers y payload
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
    
    print(f"\nRealizando petición a: {api_url}")
    print(f"Usando clave API: {api_key[:5]}...{api_key[-5:]}")
    
    # Convertir payload a JSON
    data = json.dumps(payload).encode('utf-8')
    
    # Crear contexto SSL que no verifique certificados
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    # Crear la petición
    req = urllib.request.Request(api_url, data=data, headers=headers, method='POST')
    
    try:
        # Realizar la petición
        with urllib.request.urlopen(req, context=context, timeout=30) as response:
            status_code = response.getcode()
            print(f"\nCódigo de estado: {status_code}")
            
            if status_code == 200:
                print("✅ ¡Conexión exitosa!")
                try:
                    # Leer la respuesta
                    response_data = response.read().decode('utf-8')
                    json_response = json.loads(response_data)
                    
                    print("\n=== RESPUESTA DE LA API ===")
                    respuesta = json_response.get("choices", [{}])[0].get("message", {}).get("content", "")
                    print(respuesta)
                    return True
                except Exception as e:
                    print(f"❌ Error al procesar la respuesta JSON: {e}")
            else:
                print(f"❌ Error en la respuesta: Código {status_code}")
    
    except urllib.error.URLError as e:
        if isinstance(e.reason, ssl.SSLError):
            print("❌ Error SSL - Conexión segura fallida")
            print("Recomendación: Verificar la configuración SSL/TLS del sistema")
        else:
            print(f"❌ Error de conexión: {e.reason}")
            print("Recomendación: Verificar la conectividad de red y posibles restricciones de firewall")
    
    except urllib.error.HTTPError as e:
        print(f"❌ Error HTTP: {e.code} - {e.reason}")
        try:
            error_content = e.read().decode('utf-8')
            print(f"Detalles: {error_content}")
        except:
            pass
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    return False

def main():
    print("===== TEST DE API REDPILL CON CONTEXTO ENRIQUECIDO =====")
    probar_api_con_contexto()
    print("===== FIN DEL TEST =====")

if __name__ == "__main__":
    main()
