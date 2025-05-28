"""
Ejemplo de uso de la función de confirmación.
"""

import streamlit as st
from utils import confirmar_continuar

def main():
    st.title("🔄 Prueba de Confirmación")
    
    st.write("Este es un ejemplo de cómo usar la función de confirmación.")
    
    # Ejemplo 1: Confirmación simple
    if confirmar_continuar():
        st.success("¡Has confirmado continuar!")
    
    # Ejemplo 2: Confirmación con mensaje personalizado
    if confirmar_continuar("¿Quieres procesar los datos?", key="procesar"):
        st.success("¡Procesando datos!")
    
    # Ejemplo 3: Confirmación en un loop
    if 'iteracion' not in st.session_state:
        st.session_state.iteracion = 0
    
    if st.session_state.iteracion > 0:
        st.write(f"Iteración actual: {st.session_state.iteracion}")
    
    if confirmar_continuar("¿Realizar otra iteración?", key="loop"):
        st.session_state.iteracion += 1
        st.experimental_rerun()

if __name__ == "__main__":
    main()
