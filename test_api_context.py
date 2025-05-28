"""
Script para probar la generación de contexto para la API de Redpill
"""
import streamlit as st
import pandas as pd
import sys
import os

# Agregar el directorio actual al path para poder importar los módulos
sys.path.append(os.path.dirname(__file__))

from api_context import generar_contexto_datos, make_api_request_contexto

def main():
    print("=== TEST DE GENERACIÓN DE CONTEXTO PARA REDPILL API ===")
    
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
    
    # Simular la sesión de Streamlit
    if 'session_state' not in globals():
        st.session_state = {}
    
    # Guardar DataFrames en la sesión
    st.session_state['base_df'] = base_df
    st.session_state['new_df'] = new_df
    st.session_state['campo_clave'] = 'nombre'
    st.session_state['coincidencias'] = [
        ('Juan P.', 'Juan Pérez'),
        ('María L.', 'María López'),
        ('Carlos R.', 'Carlos Rodríguez'),
        ('Ana M.', 'Ana Martínez')
    ]
    
    # Generar contexto
    contexto = generar_contexto_datos()
    
    # Mostrar contexto generado
    print("\n=== CONTEXTO GENERADO ===")
    print(contexto)
    
    print("\n=== PROBANDO PETICIÓN API CON CONTEXTO ===")
    pregunta = "¿Qué personas coinciden en ambos archivos?"
    
    try:
        # Intentar hacer la petición a la API (solo si hay una clave API válida)
        from utils import get_api_key
        api_key = get_api_key("redpill")
        
        if api_key:
            print(f"API Key encontrada: {api_key[:5]}...")
            print("Realizando petición a la API...")
            
            try:
                response = make_api_request_contexto(pregunta)
                print("\n=== RESPUESTA DE LA API ===")
                respuesta = response["choices"][0]["message"]["content"]
                print(respuesta)
            except Exception as e:
                print(f"Error al hacer la petición a la API: {e}")
        else:
            print("No se encontró una clave API válida. Omitiendo la prueba de API.")
    except Exception as e:
        print(f"Error al cargar la clave API: {e}")
    
    print("\n=== TEST COMPLETADO ===")

if __name__ == "__main__":
    main()
