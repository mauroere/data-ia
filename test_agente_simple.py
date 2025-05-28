"""
Script simple para probar la funcionalidad de modo agente sin dependencias externas.
Esta versión actualizada verifica el formato estructurado de la respuesta.
"""

import requests
import warnings
import json
import os
import re
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

def verificar_formato_agente(respuesta: Dict[str, Any]) -> bool:
    """
    Verifica que la respuesta tenga el formato estructurado del modo agente.
    
    Args:
        respuesta: Respuesta de la API
        
    Returns:
        bool: True si la respuesta tiene el formato esperado, False en caso contrario
    """
    if "choices" not in respuesta or len(respuesta["choices"]) == 0:
        print("Error: La respuesta no contiene choices")
        return False
    
    # Obtener el texto de la respuesta
    texto_respuesta = respuesta["choices"][0]["message"]["content"]
    
    # Verificar que contenga las tres secciones esperadas
    tiene_analisis = "📊 ANÁLISIS:" in texto_respuesta
    tiene_hallazgos = "🔍 HALLAZGOS:" in texto_respuesta
    tiene_recomendaciones = "📈 RECOMENDACIONES:" in texto_respuesta
    
    # Contar el número de secciones encontradas
    secciones_encontradas = sum([tiene_analisis, tiene_hallazgos, tiene_recomendaciones])
    
    if secciones_encontradas == 3:
        print("✅ La respuesta contiene las tres secciones esperadas")
        return True
    else:
        print(f"⚠️ La respuesta solo contiene {secciones_encontradas} de 3 secciones esperadas")
        
        # Mostrar qué secciones faltan
        if not tiene_analisis:
            print("  - Falta la sección 📊 ANÁLISIS")
        if not tiene_hallazgos:
            print("  - Falta la sección 🔍 HALLAZGOS")
        if not tiene_recomendaciones:
            print("  - Falta la sección 📈 RECOMENDACIONES")
            
        return False

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
      # Instrucciones específicas para el modo agente - versión actualizada más explícita
    instrucciones_agente = """
    Actúa como un agente de análisis de datos especializado que puede:
    1. Interpretar datos y realizar análisis básicos
    2. Buscar patrones, correlaciones y tendencias en los datos
    3. Sugerir acciones específicas basadas en el análisis
    4. Responder a consultas técnicas sobre los datos
    5. Explicar el significado de los resultados del cruce de datos
    6. Proponer nuevos análisis o cruces que podrían ser útiles
    
    IMPORTANTE: DEBES responder SIEMPRE utilizando EXACTAMENTE el siguiente formato estructurado:

    📊 ANÁLISIS:
    [Breve resumen de tu interpretación de los datos]

    🔍 HALLAZGOS:
    1. [Primer hallazgo importante]
    2. [Segundo hallazgo importante]
    3. [Más hallazgos si corresponde]

    📈 RECOMENDACIONES:
    - [Primera recomendación concreta]
    - [Segunda recomendación concreta]
    - [Más recomendaciones si corresponde]
    
    No omitas ninguna de las tres secciones y mantén siempre este formato estructurado. No utilices formato de chat informal.
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
        }        payload = {            "model": "mistralai/ministral-8b",
            "messages": [
                {"role": "system", "content": "Eres un agente inteligente especializado en análisis de datos que ayuda a los usuarios a trabajar con archivos CSV y Excel. Puedes analizar, interpretar y actuar sobre los datos proporcionados. DEBES responder SIEMPRE utilizando un formato ESTRUCTURADO con tres secciones: ANÁLISIS, HALLAZGOS y RECOMENDACIONES. Nunca respondas en formato de chat informal."},
                {"role": "user", "content": pregunta_enriquecida}
            ],
            "temperature": 0.3,  # Temperatura más baja para respuestas más determinísticas
            "max_tokens": 1500,   # Aumentado para permitir respuestas más detalladas
            "response_format": {"type": "text"}  # Asegurar que la respuesta sea texto
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
    print("=== Test de API en modo agente (versión mejorada) ===")
    
    # Probar la función de agente
    pregunta = "Analiza las coincidencias entre los dos conjuntos de datos y recomienda acciones"
    print(f"Enviando pregunta al agente: '{pregunta}'")
    
    respuesta = make_api_request_agente(pregunta)
    
    if respuesta:
        # Verificar el formato de la respuesta
        formato_correcto = verificar_formato_agente(respuesta)
        
        contenido = respuesta["choices"][0]["message"]["content"]
        
        print("\n=== RESPUESTA DEL AGENTE ===")
        print(contenido)
        print("===========================")
        
        if formato_correcto:
            print("\n✅ PRUEBA EXITOSA: El modo agente está funcionando correctamente con formato estructurado")
        else:
            print("\n⚠️ ADVERTENCIA: La respuesta no sigue completamente el formato estructurado esperado")
    else:
        print("\n❌ No se pudo obtener una respuesta del agente.")

if __name__ == "__main__":
    main()
