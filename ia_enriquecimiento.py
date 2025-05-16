import streamlit as st
import openai

st.set_page_config(page_title="✨ IA Enriquecimiento", layout="wide")
st.title("🤖 Limpieza y Enriquecimiento de Datos con IA")

openai.api_key = st.secrets["openai"]["api_key"]

entrada = st.text_area("📝 Pegá los datos desordenados o incompletos aquí", height=200)

if st.button("Limpiar y enriquecer con GPT-4"):
    if not entrada.strip():
        st.warning("Por favor, ingresá datos para procesar.")
    else:
        with st.spinner("Procesando con inteligencia artificial..."):
            prompt = f"""Limpia y estructura profesionalmente los siguientes datos de empleados para que estén listos para importar a un sistema:

{entrada.strip()}
"""
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                salida = response['choices'][0]['message']['content']
                st.success("Resultado generado por IA:")
                st.text_area("🧠 Datos estructurados", salida, height=300)
            except Exception as e:
                st.error(f"Ocurrió un error al procesar con OpenAI: {e}")