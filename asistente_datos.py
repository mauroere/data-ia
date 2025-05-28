"""
Asistente de Datos con IA mejorado
Este módulo proporciona la interfaz mejorada para el Asistente de Datos basado en IA.
"""
import streamlit as st
import pandas as pd
import time
import json
import requests
from typing import Dict, List, Any, Optional, Tuple
import random
from api_context import make_api_request_agente, generar_contexto_datos

# Colores y estilos personalizados
COLORS = {
    "primary": "#FF4B4B",      # Rojo Streamlit
    "secondary": "#0068C9",    # Azul
    "success": "#09AB3B",      # Verde
    "warning": "#FFBD45",      # Amarillo
    "info": "#3366FF",         # Azul claro
    "light": "#F0F2F6",        # Gris claro
    "dark": "#262730",         # Gris oscuro
    "gradient": "linear-gradient(90deg, #FF4B4B 0%, #FF7373 100%)",
}

CSS = """
<style>
.chat-message {
    padding: 1.0rem;
    border-radius: 0.75rem;
    margin-bottom: 1rem;
    display: flex;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.chat-message.user {
    background-color: #F0F2F6;
    border-left: 5px solid #FF4B4B;
}
.chat-message.assistant {
    background-color: #F8F9FD;
    border-left: 5px solid #0068C9;
}
.chat-message .avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    object-fit: cover;
    margin-right: 1rem;
}
.chat-message .message {
    flex: 1;
}
.chat-message .message p {
    margin: 0;
}
.answer-section {
    border-radius: 0.75rem;
    padding: 1.0rem;
    margin: 1rem 0;
    border-left: 5px solid #09AB3B;
    background-color: #F9FFFA;
}
.highlight-box {
    padding: 1rem;
    border-radius: 0.75rem;
    margin: 1rem 0;
    background-color: #F0F7FF;
    border: 1px solid #0068C9;
}
.highlight-box h3 {
    margin-top: 0;
    color: #0068C9;
}
.charts-section {
    padding: 1rem;
    background-color: white;
    border-radius: 0.75rem;
    margin: 1rem 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.category {
    font-weight: 600;
    color: #0068C9;
    margin-right: 0.5rem;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    border-radius: 5px 5px 0 0;
    padding: 0 20px;
    white-space: normal;
}
.stTabs [aria-selected="true"] {
    background-color: #F0F2F6;
    border-left: 5px solid #FF4B4B;
}
</style>
"""

def init_chat_history():
    """Inicializa el historial de chat si no existe."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chat_log" not in st.session_state:
        st.session_state.chat_log = []


def display_chat_message(is_user: bool, text: str, avatar: str):
    """Muestra un mensaje de chat con estilo mejorado."""
    role = "user" if is_user else "assistant"
    container = st.container()
    with container:
        st.markdown(f"""
        <div class="chat-message {role}">
            <img src="{avatar}" class="avatar" alt="{'Usuario' if is_user else 'Asistente'}">
            <div class="message">{text}</div>
        </div>
        """, unsafe_allow_html=True)
    return container


def display_chat_history():
    """Muestra el historial completo del chat."""
    # Si hay mensajes en el historial, mostrarlos
    for message in st.session_state.messages:
        avatar = "https://ui-avatars.com/api/?name=User&background=FF4B4B&color=fff" if message["role"] == "user" else "https://ui-avatars.com/api/?name=AI&background=0068C9&color=fff"
        display_chat_message(message["role"] == "user", message["content"], avatar)


def process_response(response_text: str) -> str:
    """
    Procesa la respuesta del modelo para mejorar su formato y presentación.
    """
    # Aplicar formato mejorado a los emojis y secciones
    processed = response_text
    
    # Convertir encabezados con emojis a HTML estilizado
    emoji_headers = {
        "📊 ANÁLISIS:": "<h3 style='color:#0068C9;'>📊 ANÁLISIS</h3>",
        "🔍 HALLAZGOS:": "<h3 style='color:#09AB3B;'>🔍 HALLAZGOS</h3>",
        "📈 RECOMENDACIONES:": "<h3 style='color:#FF4B4B;'>📈 RECOMENDACIONES</h3>",
        "📊 Análisis:": "<h3 style='color:#0068C9;'>📊 ANÁLISIS</h3>",
        "🔍 Hallazgos:": "<h3 style='color:#09AB3B;'>🔍 HALLAZGOS</h3>",
        "📈 Recomendaciones:": "<h3 style='color:#FF4B4B;'>📈 RECOMENDACIONES</h3>",
    }
    
    for original, styled in emoji_headers.items():
        processed = processed.replace(original, styled)
    
    return processed


def handle_chat_input(prompt: str):
    """
    Maneja la entrada del usuario, envía la consulta al asistente y muestra la respuesta.
    """
    # Validar que haya datos cargados
    if 'base_df' not in st.session_state or 'new_df' not in st.session_state:
        st.warning("⚠️ Por favor carga primero los archivos de datos para usar el asistente.")
        return
    
    if not prompt.strip():
        st.warning("⚠️ Por favor ingresa una consulta.")
        return
    
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    user_avatar = "https://ui-avatars.com/api/?name=User&background=FF4B4B&color=fff"
    display_chat_message(True, prompt, user_avatar)
    
    # Mostrar indicador de carga
    with st.spinner("💭 Analizando tus datos..."):
        try:
            response_data = make_api_request_agente(prompt)
            response_text = response_data["choices"][0]["message"]["content"]
            
            # Procesar la respuesta para mejorar su formato
            formatted_response = process_response(response_text)
            
            # Agregar respuesta del asistente al historial
            st.session_state.messages.append({"role": "assistant", "content": formatted_response})
            
            # Guardar en el historial completo (para exportación)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.chat_log.append({
                "timestamp": timestamp,
                "prompt": prompt,
                "response": response_text
            })
            
            # Mostrar respuesta
            assistant_avatar = "https://ui-avatars.com/api/?name=AI&background=0068C9&color=fff"
            response_container = display_chat_message(False, formatted_response, assistant_avatar)
            
        except Exception as e:
            st.error(f"❌ Error al procesar tu consulta: {str(e)}")


def export_chat_history():
    """
    Permite exportar el historial de chat en diferentes formatos.
    """
    if not st.session_state.chat_log:
        st.warning("No hay conversaciones para exportar.")
        return
    
    # Crear un DataFrame con el historial
    df = pd.DataFrame(st.session_state.chat_log)
    
    # Opciones de exportación
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="📥 Exportar como CSV",
            data=df.to_csv(index=False),
            file_name=f"asistente_datos_historial_{time.strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    
    with col2:
        st.download_button(
            label="📥 Exportar como JSON",
            data=json.dumps(st.session_state.chat_log, indent=2, ensure_ascii=False),
            file_name=f"asistente_datos_historial_{time.strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )
    
    with col3:
        st.download_button(
            label="📥 Exportar como Excel",
            data=df.to_excel(index=False).getvalue(),
            file_name=f"asistente_datos_historial_{time.strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


def clear_chat_history():
    """Limpia el historial de chat."""
    st.session_state.messages = []
    st.session_state.chat_log = []
    st.success("✅ Historial de chat eliminado.")
    time.sleep(0.5)
    st.rerun()


def show_data_insights():
    """
    Muestra información útil sobre los datos cargados.
    """
    if 'base_df' not in st.session_state or 'new_df' not in st.session_state:
        st.warning("⚠️ No hay datos cargados para mostrar.")
        return
    
    base_df = st.session_state['base_df']
    new_df = st.session_state['new_df']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 Archivo BASE")
        st.write(f"Filas: {len(base_df):,}")
        st.write(f"Columnas: {len(base_df.columns):,}")
        st.markdown("##### Primeras columnas:")
        st.write(", ".join(base_df.columns[:5]))
    
    with col2:
        st.markdown("#### 📄 Archivo NUEVO")
        st.write(f"Filas: {len(new_df):,}")
        st.write(f"Columnas: {len(new_df.columns):,}")
        st.markdown("##### Primeras columnas:")
        st.write(", ".join(new_df.columns[:5]))
    
    # Mostrar coincidencias si existen
    if 'coincidencias' in st.session_state and st.session_state['coincidencias']:
        coincidencias = st.session_state['coincidencias']
        st.markdown(f"#### 🔗 Coincidencias: {len(coincidencias):,}")
        
        if len(coincidencias) > 0:
            st.dataframe(
                pd.DataFrame(coincidencias[:10], columns=["Nuevo", "Base"]),
                use_container_width=True,
                hide_index=True
            )
            if len(coincidencias) > 10:
                st.caption(f"Mostrando 10 de {len(coincidencias):,} coincidencias")


def show_sample_questions():
    """
    Muestra ejemplos de preguntas que el usuario puede hacer.
    """
    st.markdown("### Ejemplos de consultas que puedes hacer:")
    
    questions = [
        "¿Cuáles son las principales diferencias entre los dos archivos?",
        "Encuentra registros duplicados en el archivo BASE",
        "¿Qué columnas tienen valores faltantes en ambos archivos?",
        "Analiza la distribución de valores en la columna clave",
        "Identifica posibles errores en los datos",
        "¿Cuál es la calidad general de las coincidencias encontradas?",
        "Sugiere mejoras para el cruce de datos",
        "Compara los valores numéricos entre ambos archivos",
    ]
    
    for i, question in enumerate(questions):
        if st.button(f"{i+1}. {question}", key=f"sample_q_{i}"):
            handle_chat_input(question)


def run_asistente_datos():
    """
    Función principal para ejecutar el Asistente de Datos mejorado.
    """
    st.markdown(CSS, unsafe_allow_html=True)
    
    # Inicializar historial de chat
    init_chat_history()
    
    # Encabezado principal
    st.markdown("""
    <h1 style='text-align: center; margin-bottom: 1.5rem;'>
        <span style='color: #FF4B4B;'>🤖 Asistente</span> 
        <span style='color: #0068C9;'>de Datos</span>
    </h1>
    """, unsafe_allow_html=True)
    
    # Pestañas para organizar la interfaz
    tab1, tab2, tab3 = st.tabs(["💬 Asistente", "📊 Datos", "ℹ️ Ayuda"])
    
    with tab1:
        # Mostrar el historial de chat
        display_chat_history()
        
        # Contenedor para el input y botones
        input_col, button_col = st.columns([4, 1])
        
        with input_col:
            prompt = st.text_input(
                "💭 Haz una pregunta sobre tus datos...",
                key="chat_input",
                placeholder="Ej: ¿Cuáles son las principales diferencias entre los archivos?",
                label_visibility="collapsed"
            )
        
        with button_col:
            submit = st.button("Enviar", use_container_width=True)
        
        if submit and prompt:
            handle_chat_input(prompt)
        
        # Botones para gestionar la conversación
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Limpiar chat", use_container_width=True):
                clear_chat_history()
        with col2:
            if st.button("📥 Exportar historial", use_container_width=True):
                export_chat_history()
    
    with tab2:
        show_data_insights()
    
    with tab3:
        st.markdown("### 🚀 Cómo usar el Asistente de Datos")
        
        with st.expander("📋 Instrucciones básicas", expanded=True):
            st.markdown("""
            1. **Carga tus archivos** en la sección "Cruce Inteligente"
            2. **Selecciona el campo clave** para el cruce de datos
            3. **Escribe tu consulta** en el campo de texto y presiona "Enviar"
            4. El asistente analizará tus datos y te dará una respuesta detallada
            """)
        
        with st.expander("💡 Capacidades del asistente"):
            st.markdown("""
            El Asistente de Datos puede:
            - Analizar la estructura y contenido de tus archivos
            - Identificar diferencias y similitudes entre datasets
            - Encontrar valores atípicos o problemas en los datos
            - Sugerir acciones para mejorar la calidad del cruce
            - Responder preguntas técnicas sobre formatos y tipos de datos
            - Generar recomendaciones basadas en el análisis
            """)
        
        show_sample_questions()


if __name__ == "__main__":
    st.set_page_config(page_title="Asistente de Datos IA", layout="wide")
    run_asistente_datos()
