"""
Script simplificado para probar la generación de contexto para la API de Redpill
sin depender de Streamlit
"""
import pandas as pd
import sys
import os
import json
import urllib.request
import urllib.error
import ssl
import json

# Crear DataFrames de ejemplo
base_df = pd.DataFrame({
    'id': [1, 2, 3, 4, 5],
    'nombre': ['Juan Pérez', 'María López', 'Carlos Rodríguez', 'Ana Martínez', 'Luis González'],
    'edad': [35, 42, 28, 39, 45],
    'ciudad': ['Madrid', 'Barcelona', 'Sevilla', 'Valencia', 'Bilbao']
})

new_df = pd.DataFrame({
    'id': [101, 102, 103, 104],
    'nombre': ['Juan P.', 'María L.', 'Carlos R.', 'Ana M.'],
    'puntuacion': [85, 92, 78, 88],
    'departamento': ['Ventas', 'Marketing', 'IT', 'RRHH']
})

def generar_contexto_manual():
    """
    Genera un texto descriptivo del contexto de datos manualmente
    """
    contexto = "Eres un asistente especializado en análisis de datos que ayuda a los usuarios a trabajar con archivos CSV, Excel y realizar cruces de datos."
    
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
    
    # Incluir campo clave y coincidencias de ejemplo
    campo_clave = 'nombre'
    coincidencias = [
        ('Juan P.', 'Juan Pérez'),
        ('María L.', 'María López'),
        ('Carlos R.', 'Carlos Rodríguez'),
        ('Ana M.', 'Ana Martínez')
    ]
    
    contexto += f"\n\nEl usuario ha seleccionado '{campo_clave}' como campo clave para el cruce."
    contexto += f"\n\nSe han encontrado {len(coincidencias)} coincidencias entre los archivos."
    contexto += "\nEjemplos de coincidencias:"
    for i, (val1, val2) in enumerate(coincidencias[:3]):
        contexto += f"\n- '{val1}' coincide con '{val2}'"
        if i >= 2:
            break
            
    return contexto

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

def hacer_peticion_api(pregunta, contexto):
    """Realiza una petición a la API de Redpill con el contexto proporcionado"""
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
                    return respuesta
                except Exception as e:
                    print(f"❌ Error al procesar la respuesta JSON: {e}")
            else:
                print(f"❌ Error en la respuesta: Código {status_code}")
    
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
    
    return None

def main():
    print("=== TEST DE GENERACIÓN DE CONTEXTO PARA REDPILL API ===")
    
    # Generar contexto
    contexto = generar_contexto_manual()
    
    # Mostrar contexto generado
    print("\n=== CONTEXTO GENERADO ===")
    print(contexto)
    
    print("\n=== PROBANDO PETICIÓN API CON CONTEXTO ===")
    pregunta = "¿Qué personas coinciden en ambos archivos?"
    
    # Hacer petición a la API
    hacer_peticion_api(pregunta, contexto)
    
    print("\n=== TEST COMPLETADO ===")

if __name__ == "__main__":
    main()
