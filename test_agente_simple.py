"""
Script simple para probar la funcionalidad de modo agente sin dependencias externas.
"""

import requests
import warnings
import json
import os
from typing import Dict, Any

# Desactivar advertencias SSL para pruebas
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
requests.packages.urllib3.disable_warnings()

def get_api_key():
    """Obtiene la clave API de una variable de entorno o un archivo de configuración."""
    try:
        # Intentar leer del archivo .streamlit/secrets.toml
        with open('.streamlit/secrets.toml', 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('api_key'):
                    return line.split('=')[1].strip().strip('"').strip("'")
        
        # Si no se encuentra, usar un valor de prueba
        return "sk-xYBWXr1epqP3Uq1A05qUql9tAyBsJE5F8PL5L66gBaE328VG"
    except Exception as e:
        print(f"Error al obtener la clave API: {str(e)}")
        return "sk-xYBWXr1epqP3Uq1A05qUql9tAyBsJE5F8PL5L66gBaE328VG"  # API key de prueba

def make_api_request_agente(pregunta: str):
    """
    Realiza una petición a la API de Redpill en modo agente.
    
    Args:
        pregunta (str): Pregunta o instrucción del usuario
        
    Returns:
        dict: Respuesta de la API
    """
    api_key = get_api_key()
    api_url = "https://api.redpill.ai/v1/chat/completions"
    
    # Contexto mínimo para simular datos
    contexto = """
    Eres un asistente especializado en análisis de datos que ayuda a los usuarios a trabajar con archivos CSV, Excel y realizar cruces de datos.
    
    El usuario ha cargado dos archivos de datos:
    1. Archivo BASE con 5 filas y columnas: id, nombre, edad, ciudad
    2. Archivo NUEVO con 5 filas y columnas: id, nombre, salario, departamento
    
    Ejemplo de filas del Archivo BASE:
    id | nombre        | edad | ciudad
    1  | Juan Pérez    | 25   | Madrid
    2  | María García  | 30   | Barcelona
    3  | Carlos López  | 45   | Sevilla
    
    Ejemplo de filas del Archivo NUEVO:
    id  | nombre      | salario | departamento
    101 | Juan P.     | 25000   | Ventas
    102 | Maria G     | 30000   | Marketing
    103 | C. López    | 45000   | IT
    
    El usuario ha seleccionado 'nombre' como campo clave para el cruce.
    Se han encontrado 5 coincidencias entre los archivos.
    """
    
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
    
    # Enriquecer la pregunta con el contexto y las instrucciones del agente
    pregunta_enriquecida = f"{contexto}\n\n{instrucciones_agente}\n\nConsulta/Instrucción del usuario: {pregunta}\n\n"
    
    try:
        print("Enviando solicitud a la API...")
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
            "temperature": 0.5,
            "max_tokens": 1500
        }
        
        print(f"URL de la API: {api_url}")
        print(f"Longitud de la pregunta: {len(pregunta_enriquecida)} caracteres")
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            verify=False,  # Desactivar verificación SSL
            timeout=30.0   # Timeout en segundos
        )
        
        print(f"Código de estado HTTP: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error: {response.text}")
            return None
            
        return response.json()
    except Exception as e:
        print(f"Error al hacer la solicitud: {str(e)}")
        return None

def main():
    print("=== Test de API en modo agente (versión simple) ===")
    
    # Probar la función de agente
    pregunta = "Analiza las coincidencias entre los dos conjuntos de datos y recomienda acciones"
    print(f"Enviando pregunta al agente: '{pregunta}'")
    
    respuesta = make_api_request_agente(pregunta)
    
    if respuesta:
        contenido = respuesta["choices"][0]["message"]["content"]
        
        print("\n=== RESPUESTA DEL AGENTE ===")
        print(contenido)
        print("===========================")
        print("\nTest completado con éxito.")
    else:
        print("\n❌ No se pudo obtener una respuesta del agente.")

if __name__ == "__main__":
    main()
