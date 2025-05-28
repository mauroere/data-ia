"""
Script para probar el asistente de cruce inteligente.

Ejecutar con: python test_asistente_cruce.py
"""

import pandas as pd
import sys
import os

# Añadir directorio actual al path para importar módulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from api_context import make_api_request_agente
    from api_fix import ensure_api_key_exists
    from asistente_cruce_inteligente import mostrar_analisis_estructurado
except ImportError as e:
    print(f"Error al importar módulos necesarios: {e}")
    sys.exit(1)

def crear_datos_prueba():
    """Crea datos de prueba para simular el cruce de archivos."""
    # Crear DataFrame BASE
    base_df = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'nombre': ['Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez', 'Pedro Sánchez'],
        'edad': [25, 30, 45, 35, 40],
        'ciudad': ['Madrid', 'Barcelona', 'Sevilla', 'Valencia', 'Bilbao']
    })
    
    # Crear DataFrame NUEVO
    new_df = pd.DataFrame({
        'id': [101, 102, 103, 104, 105],
        'nombre': ['Juan P.', 'Maria G', 'C. López', 'Ana M.', 'P. Sánchez'],
        'salario': [25000, 30000, 45000, 35000, 40000],
        'departamento': ['Ventas', 'Marketing', 'IT', 'RRHH', 'Finanzas']
    })
    
    # Simular coincidencias
    coincidencias = [
        ('Juan P.', 'Juan Pérez'),
        ('Maria G', 'María García'),
        ('C. López', 'Carlos López'),
        ('Ana M.', 'Ana Martínez'),
        ('P. Sánchez', 'Pedro Sánchez')
    ]
    
    return base_df, new_df, coincidencias

def test_asistente_cruce():
    """Prueba el funcionamiento del asistente de cruce inteligente."""
    print("=== Probando asistente de cruce inteligente ===")
    
    # Asegurar que la API key esté disponible
    ensure_api_key_exists()
    
    # Crear datos de prueba
    base_df, new_df, coincidencias = crear_datos_prueba()
    
    # Establecer variables de sesión simuladas
    import streamlit as st
    st.session_state = {}
    st.session_state["base_df"] = base_df
    st.session_state["new_df"] = new_df
    st.session_state["coincidencias"] = coincidencias
    st.session_state["campo_clave"] = "nombre"
    
    # Consulta de prueba
    consulta = "Analiza la calidad del cruce y sugiere mejoras"
    
    try:
        # Realizar la consulta al agente
        print(f"Enviando consulta: '{consulta}'")
        respuesta = make_api_request_agente(consulta)
        
        if respuesta and "choices" in respuesta and len(respuesta["choices"]) > 0:
            texto_respuesta = respuesta["choices"][0]["message"]["content"]
            
            print("\n=== RESPUESTA DEL AGENTE ===")
            print(texto_respuesta)
            print("===========================")
            
            # Verificar formato estructurado
            tiene_analisis = "📊 ANÁLISIS:" in texto_respuesta
            tiene_hallazgos = "🔍 HALLAZGOS:" in texto_respuesta
            tiene_recomendaciones = "📈 RECOMENDACIONES:" in texto_respuesta
            
            if tiene_analisis and tiene_hallazgos and tiene_recomendaciones:
                print("✅ La respuesta contiene las tres secciones esperadas")
                
                # Probar la función de procesamiento
                print("\nProbando la función mostrar_analisis_estructurado...")
                # Esta función normalmente muestra resultados en Streamlit, así que solo la llamamos
                # para verificar que no genera errores
                try:
                    mostrar_analisis_estructurado(texto_respuesta)
                    print("✅ La función mostrar_analisis_estructurado se ejecutó sin errores")
                except Exception as e:
                    print(f"❌ Error al procesar la respuesta: {str(e)}")
            else:
                print("⚠️ La respuesta no contiene todas las secciones esperadas")
        else:
            print("❌ No se pudo obtener una respuesta válida")
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")

if __name__ == "__main__":
    test_asistente_cruce()
