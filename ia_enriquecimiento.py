import streamlit as st
from openai import OpenAI
from utils import get_api_key

def run_ia_enriquecimiento():
    st.title("🤖 Limpieza y Enriquecimiento de Datos con IA")
    
    # Obtener API key
    api_key = get_api_key("openai")
    
    # Verificar si existe API key
    if not api_key:
        st.warning("⚠️ No se ha configurado la clave API de OpenAI.")
        api_key = st.text_input("Ingresa tu clave API de OpenAI:", type="password")
        if not api_key:
            st.error("Se requiere una clave API para continuar.")
            st.stop()
        else:
            # Guardar en session_state para uso futuro
            st.session_state["openai_api_key"] = api_key
    
    # Configuración
    cliente = OpenAI(api_key=api_key)
    modelo = st.selectbox("Modelo de IA:", ["gpt-3.5-turbo", "gpt-4", "gpt-4o"])
    
    # Instrucciones personalizadas
    st.subheader("Instrucciones para la IA")
    instruccion_default = "Limpia y estructura profesionalmente los siguientes datos para que estén listos para importar a un sistema."
    instruccion = st.text_area("Instrucciones personalizadas:", instruccion_default, height=100)
    
    # Entrada de datos
    st.subheader("Datos a procesar")
    entrada = st.text_area("📝 Pegá los datos desordenados o incompletos aquí:", height=200, 
                          placeholder="Ejemplo: Juan Perez - gerente, 38 años, Bs As\nMaria Gomez 45a coordinadora CABA\n...")
    
    # Formato de salida
    formato_salida = st.selectbox("Formato de salida deseado:", ["CSV", "JSON", "Excel", "Tabla", "Auto-detectar"])
    
    if st.button("Limpiar y enriquecer con IA"):
        if not entrada.strip():
            st.warning("Por favor, ingresá datos para procesar.")
        else:
            with st.spinner("Procesando con inteligencia artificial..."):
                # Construir el prompt completo
                formato_instruccion = ""
                if formato_salida != "Auto-detectar":
                    formato_instruccion = f"El resultado debe estar en formato {formato_salida}."
                
                prompt = f"""{instruccion}

{formato_instruccion}

DATOS:
{entrada.strip()}
"""
                try:
                    # Llamada a la API de OpenAI con la nueva librería
                    response = cliente.chat.completions.create(
                        model=modelo,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3
                    )
                    salida = response.choices[0].message.content
                    
                    st.success("Resultado generado por IA:")
                    st.text_area("🧠 Datos estructurados", salida, height=300)
                    
                    # Guardar en historial
                    if 'historial_ia_enriq' not in st.session_state:
                        st.session_state.historial_ia_enriq = []
                    st.session_state.historial_ia_enriq.append({
                        "entrada": entrada.strip(),
                        "salida": salida,
                        "modelo": modelo
                    })
                    
                    # Ofrecer opciones para exportar el resultado
                    if st.button("Exportar resultado"):
                        # Detectar si es CSV y ofrecer descarga directa
                        if formato_salida == "CSV" or "," in salida.split("\n")[0]:
                            st.download_button("📥 Descargar CSV", salida, "datos_estructurados.csv", "text/csv")
                        else:
                            st.download_button("📥 Descargar como archivo de texto", salida, "datos_estructurados.txt", "text/plain")
                    
                except Exception as e:
                    st.error(f"Ocurrió un error al procesar con OpenAI: {e}")
    
    # Mostrar historial de procesamiento
    if 'historial_ia_enriq' in st.session_state and st.session_state.historial_ia_enriq:
        with st.expander("Ver historial de procesamiento"):
            for i, item in enumerate(st.session_state.historial_ia_enriq):
                st.subheader(f"Procesamiento #{i+1} - Modelo: {item['modelo']}")
                st.text_area("Entrada:", item["entrada"], height=100, key=f"in_{i}")
                st.text_area("Salida:", item["salida"], height=150, key=f"out_{i}")
                st.divider()

if __name__ == "__main__":
    st.set_page_config(page_title="✨ IA Enriquecimiento", layout="wide")
    run_ia_enriquecimiento()