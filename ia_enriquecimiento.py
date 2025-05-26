import streamlit as st
from openai import OpenAI
from utils import get_api_key, read_flexible_file
import pandas as pd
import io

def run_ia_enriquecimiento():
    st.title("🤖 Limpieza y Enriquecimiento de Datos con IA")
      # Obtener API key
    api_key = get_api_key("openai")
    
    # Verificar si existe API key
    if not api_key:
        st.warning("⚠️ No se ha encontrado la clave API de OpenAI en la configuración.")
        api_key = st.text_input(
            "Ingresa tu clave API de OpenAI:",
            type="password",
            help="La clave API se guardará solo para esta sesión."
        )
        if not api_key:
            st.error("Se requiere una clave API para continuar.")
            st.stop()
        else:
            # Guardar en session_state para uso futuro
            st.session_state["openai_api_key"] = api_key
            st.success("✅ Clave API guardada para esta sesión.")
    
    # Configuración
    cliente = OpenAI(api_key=api_key)
    modelo = st.selectbox("Modelo de IA:", ["gpt-3.5-turbo", "gpt-4", "gpt-4o"])
    
    # Instrucciones personalizadas
    st.subheader("Instrucciones para la IA")
    instruccion_default = "Limpia y estructura profesionalmente los siguientes datos para que estén listos para importar a un sistema."
    instruccion = st.text_area("Instrucciones personalizadas:", instruccion_default, height=100)
    
    # Opciones de entrada: Archivo o texto manual
    entrada_tipo = st.radio("Selecciona el origen de los datos:", ["Cargar archivo", "Ingresar datos manualmente"])
    
    if entrada_tipo == "Cargar archivo":
        # Cargar archivo
        uploaded_file = st.file_uploader("📁 Selecciona un archivo para procesar", type=["csv", "xls", "xlsx", "txt"])
        
        if uploaded_file:
            try:
                # Determinar cómo leer el archivo según su extensión
                if uploaded_file.name.endswith(".txt"):
                    # Para archivos de texto
                    texto_archivo = uploaded_file.getvalue().decode("utf-8")
                    st.subheader("Vista previa del archivo:")
                    st.text_area("Contenido del archivo:", texto_archivo[:1000] + ("..." if len(texto_archivo) > 1000 else ""), height=150)
                    entrada = texto_archivo
                else:
                    # Para archivos CSV, Excel
                    df = read_flexible_file(uploaded_file)
                    st.subheader("Vista previa del archivo:")
                    st.dataframe(df.head(10))
                    
                    # Opciones de preprocesamiento
                    col1, col2 = st.columns(2)
                    with col1:
                        include_headers = st.checkbox("Incluir encabezados", value=True)
                    with col2:
                        max_rows = st.number_input("Máximo de filas a procesar", min_value=10, max_value=1000, value=100)
                    
                    # Convertir DataFrame a texto
                    buffer = io.StringIO()
                    if include_headers:
                        df.head(max_rows).to_csv(buffer, index=False)
                    else:
                        df.head(max_rows).to_csv(buffer, index=False, header=False)
                    entrada = buffer.getvalue()
                
                # Instrucciones específicas para este archivo
                st.subheader("¿Qué deseas hacer con estos datos?")
                accion = st.multiselect("Selecciona las acciones a realizar:", [
                    "Normalizar nombres de columnas", 
                    "Limpiar valores nulos", 
                    "Estandarizar formatos", 
                    "Extraer información adicional",
                    "Categorizar datos",
                    "Detectar y corregir errores",
                    "Enriquecer con información externa"
                ])
                
                # Construir instrucciones basadas en las acciones seleccionadas
                if accion:
                    instruccion_adicional = "Además, debes:\n" + "\n".join([f"- {a}" for a in accion])
                    instruccion = f"{instruccion}\n\n{instruccion_adicional}"
            
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")
                entrada = ""
        else:
            entrada = ""
    else:
        # Entrada manual
        entrada = st.text_area("📝 Pegá los datos desordenados o incompletos aquí:", height=200, 
                              placeholder="Ejemplo: Juan Perez - gerente, 38 años, Bs As\nMaria Gomez 45a coordinadora CABA\n...")
    
    # Formato de salida
    formato_salida = st.selectbox("Formato de salida deseado:", ["CSV", "JSON", "Excel", "Tabla", "Auto-detectar"])
    
    # Botón de procesamiento
    procesar_btn = st.button("Limpiar y enriquecer con IA")
    
    if procesar_btn:
        if not entrada or entrada.strip() == "":
            st.warning("Por favor, ingresa datos o carga un archivo para procesar.")
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
                        "entrada": entrada.strip()[:500] + ("..." if len(entrada.strip()) > 500 else ""),
                        "salida": salida,
                        "modelo": modelo
                    })
                    
                    # Opciones de exportación
                    st.subheader("Exportar resultado")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Detectar si es CSV y ofrecer descarga directa
                        if formato_salida == "CSV" or "," in salida.split("\n")[0]:
                            st.download_button("📥 Descargar CSV", salida, "datos_estructurados.csv", "text/csv")
                        else:
                            st.download_button("📥 Descargar como archivo de texto", salida, "datos_estructurados.txt", "text/plain")
                    
                    with col2:
                        # Intentar cargar como DataFrame para visualización
                        if formato_salida in ["CSV", "Tabla"] or "," in salida.split("\n")[0]:
                            try:
                                df_result = pd.read_csv(io.StringIO(salida))
                                if st.button("Visualizar como tabla"):
                                    st.dataframe(df_result)
                            except:
                                pass
                    
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