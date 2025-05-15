import streamlit as st
import openai

st.set_page_config(page_title="✨ Enriquecimiento IA", layout="wide")
st.title("🤖 Datos Caóticos → Datos Limpios")

openai.api_key = st.secrets["openai"]["api_key"]

texto = st.text_area("Pega datos caóticos o sucios")
if st.button("Limpiar con IA") and texto:
    prompt = f"Limpiá estos datos:
{texto}"
    r = openai.ChatCompletion.create(model="gpt-4", messages=[{"role":"user","content":prompt}])
    st.text_area("Resultado IA", r['choices'][0]['message']['content'], height=300)