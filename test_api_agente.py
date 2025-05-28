"""
Script para probar la función de modo agente de la API de Redpill.
Este script verifica que la función make_api_request_agente funciona correctamente.
"""

import streamlit as st
import pandas as pd
import json
import os
import requests
import warnings
from typing import Dict, Any, Optional
from api_context import make_api_request_agente
from utils import get_api_key, get_api_url

# Desactivar advertencias SSL para pruebas
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
requests.packages.urllib3.disable_warnings()

def main():
    print("=== Test de API en modo agente ===")
    
    # Crear algunos datos de prueba en la sesión
    st.session_state["base_df"] = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "nombre": ["Juan Pérez", "María García", "Carlos López", "Ana Martínez", "Luis Rodríguez"],
        "edad": [25, 30, 45, 22, 33],
        "ciudad": ["Madrid", "Barcelona", "Sevilla", "Valencia", "Bilbao"]
    })
    
    st.session_state["new_df"] = pd.DataFrame({
        "id": [101, 102, 103, 104, 105],
        "nombre": ["Juan P.", "Maria G", "C. López", "Ana M.", "L. Rodríguez"],
        "salario": [25000, 30000, 45000, 22000, 33000],
        "departamento": ["Ventas", "Marketing", "IT", "RRHH", "Finanzas"]
    })
    
    st.session_state["campo_clave"] = "nombre"
    st.session_state["coincidencias"] = [
        ("Juan P.", "Juan Pérez"),
        ("Maria G", "María García"),
        ("C. López", "Carlos López"),
        ("Ana M.", "Ana Martínez"),
        ("L. Rodríguez", "Luis Rodríguez")
    ]
    
    print("Datos de prueba cargados en la sesión")
    
    # Probar la función de agente
    try:
        pregunta = "Analiza las coincidencias entre los dos conjuntos de datos y recomienda acciones"
        print(f"Enviando pregunta al agente: '{pregunta}'")
        
        respuesta = make_api_request_agente(pregunta)
        contenido = respuesta["choices"][0]["message"]["content"]
        
        print("\n=== RESPUESTA DEL AGENTE ===")
        print(contenido)
        print("===========================")
        print("\nTest completado con éxito.")
        
        return True
    except Exception as e:
        print(f"\n❌ Error al probar el modo agente: {str(e)}")
        return False

if __name__ == "__main__":
    main()
