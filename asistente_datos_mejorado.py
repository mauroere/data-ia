"""
Módulo de Asistente de Datos con UI/UX mejorada
Implementa las mejores prácticas de UX/UI para una experiencia más profesional y usable.
"""

import streamlit as st
import pandas as pd
import time
import json
import random
import requests
from typing import Dict, List, Any, Optional, Tuple
from api_context_fixed import make_api_request_agente, generar_contexto_datos
from api_fix import ensure_api_key_exists

# Asegurar que la API key esté disponible
ensure_api_key_exists()

# Estilos y configuración de UI
COLORS = {
    "primary": "#FF4B4B",      # Rojo Streamlit
    "secondary": "#0068C9",    # Azul
    "success": "#09AB3B",      # Verde
    "warning": "#FFBD45",      # Amarillo
    "info": "#3366FF",         # Azul claro
    "light": "#F0F2F6",        # Gris claro
    "dark": "#262730",         # Gris oscuro
}

CSS = """
<style>
    /* Estilos generales */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Estilos de chat */
    .chat-message {
        padding: 1.2rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        display: flex;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    .chat-message:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
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
        width: 45px;
        height: 45px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .chat-message .message {
        flex: 1;
    }
    
    /* Estilos de secciones de análisis */
    .analysis-section {
        border-radius: 0.75rem;
        padding: 1.2rem;
        margin: 1.2rem 0;
        background-color: white;
        border: 1px solid #E0E4EB;
        box-shadow: 0 1px 5px rgba(0, 0, 0, 0.05);
    }
    .analysis-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #0068C9;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }
    .analysis-header i {
        margin-right: 0.5rem;
    }
    
    /* Iconos y etiquetas */
    .tag {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .tag.primary { background-color: #FFE9E9; color: #FF4B4B; }
    .tag.secondary { background-color: #E6F0FF; color: #0068C9; }
    .tag.success { background-color: #E9F9EF; color: #09AB3B; }
    
    /* Botones y controles */
    .action-button {
        border: none;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
    }
    .action-button.primary { background-color: #FF4B4B; }
    .action-button.primary:hover { background-color: #FF6B6B; }
    .action-button.secondary { background-color: #0068C9; }
    .action-button.secondary:hover { background-color: #0078E9; }
    
    /* Animaciones */
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .animate-fade-in {
        animation: fadeIn 0.5s ease forwards;
    }
    
    /* Responsive */
    @media screen and (max-width: 768px) {
        .chat-message {
            flex-direction: column;
        }
        .chat-message .avatar {
            margin-bottom: 0.5rem;
            margin-right: 0;
        }
    }
</style>
"""

# Función para mostrar mensajes de chat con un diseño atractivo
def show_chat_message(is_user: bool, message: str, avatar_url: str = None):
    if is_user:
        avatar = "👤" if not avatar_url else f"<img src='{avatar_url}' class='avatar'>"
        st.markdown(f"""
        <div class="chat-message user animate-fade-in">
            <div style="display: flex; align-items: center; font-weight: bold; color: {COLORS['primary']};">
                {avatar} Tú
            </div>
            <div class="message">{message}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        avatar = "🤖" if not avatar_url else f"<img src='{avatar_url}' class='avatar'>"
        st.markdown(f"""
        <div class="chat-message assistant animate-fade-in">
            <div style="display: flex; align-items: center; font-weight: bold; color: {COLORS['secondary']};">
                {avatar} Asistente de Datos
            </div>
            <div class="message">{message}</div>
        </div>
        """, unsafe_allow_html=True)

# Función para mostrar los resultados del análisis de forma estructurada
def show_analysis_result(response_text: str):
    # Separar secciones si el formato lo permite
    sections = {}
    
    try:
        if "📊 ANÁLISIS:" in response_text:
            parts = response_text.split("📊 ANÁLISIS:")
            if len(parts) > 1:
                analysis_and_rest = parts[1].split("🔍 HALLAZGOS:", 1)
                sections["analysis"] = analysis_and_rest[0].strip()
                
                if len(analysis_and_rest) > 1:
                    findings_and_recommendations = analysis_and_rest[1].split("📈 RECOMENDACIONES:", 1) 
                    sections["findings"] = findings_and_recommendations[0].strip()
                    
                    if len(findings_and_recommendations) > 1:
                        sections["recommendations"] = findings_and_recommendations[1].strip()
        
        # Si se pudieron separar las secciones, mostrarlas de forma estructurada
        if sections:
            with st.container():
                st.markdown(f"""
                <div class="analysis-section">
                    <div class="analysis-header">
                        <i>📊</i> Análisis de Datos
                    </div>
                    <p>{sections.get("analysis", "")}</p>
                </div>
                """, unsafe_allow_html=True)
                
            with st.container():
                st.markdown(f"""
                <div class="analysis-section">
                    <div class="analysis-header">
                        <i>🔍</i> Hallazgos Principales
                    </div>
                    <p>{sections.get("findings", "")}</p>
                </div>
                """, unsafe_allow_html=True)
                
            with st.container():
                st.markdown(f"""
                <div class="analysis-section">
                    <div class="analysis-header">
                        <i>📈</i> Recomendaciones
                    </div>
                    <p>{sections.get("recommendations", "")}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Si no se pudieron separar, mostrar la respuesta completa
            st.markdown(f"""
            <div class="analysis-section">
                <div class="analysis-header">
                    <i>📊</i> Resultado del Análisis
                </div>
                <p>{response_text}</p>
            </div>
            """, unsafe_allow_html=True)
    except Exception:
        # En caso de error, mostrar la respuesta completa
        st.markdown(f"""
        <div class="analysis-section">
            <div class="analysis-header">
                <i>📊</i> Resultado del Análisis
            </div>
            <p>{response_text}</p>
        </div>
        """, unsafe_allow_html=True)

# Función para mostrar el efecto "escribiendo..."
def show_typing_animation(duration=1.0):
    with st.empty():
        for dots in [".", "..", "..."]:
            st.markdown(f"""
            <div class="chat-message assistant" style="opacity: 0.7;">
                <div style="display: flex; align-items: center; font-weight: bold; color: {COLORS['secondary']};">
                    🤖 Asistente de Datos
                </div>
                <div class="message">Analizando{dots}</div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(duration / 3)

# Función para inicializar el historial de chat
def initialize_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

# Función para agregar mensaje al historial
def add_message(is_user: bool, message: str):
    st.session_state.chat_history.append({"is_user": is_user, "message": message})

# Función para guardar/exportar el historial
def export_chat_history():
    if st.session_state.chat_history:
        # Convertir historial a formato descargable
        chat_export = []
        for msg in st.session_state.chat_history:
            role = "Usuario" if msg["is_user"] else "Asistente"
            chat_export.append(f"{role}: {msg['message']}")
        
        export_str = "\n\n".join(chat_export)
        
        # Ofrecer descarga
        st.download_button(
            label="📥 Descargar Historial",
            data=export_str,
            file_name=f"analisis_datos_{time.strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# Función principal del asistente de datos
def run_data_assistant():
    # Inyectar CSS personalizado
    st.markdown(CSS, unsafe_allow_html=True)
    
    # Encabezado y descripción
    st.markdown("""
    <h1 style="color: #FF4B4B; font-size: 2.2rem;">🧠 Asistente de Datos IA</h1>
    <p style="font-size: 1.1rem; margin-bottom: 2rem;">
        Analiza, interpreta y obtén insights de tus datos con la ayuda de inteligencia artificial.
    </p>
    """, unsafe_allow_html=True)
    
    # Inicializar el historial
    initialize_chat_history()
    
    # Contenedor para las opciones y ajustes
    with st.expander("⚙️ Opciones del asistente", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 🧰 Capacidades del asistente
            - Análisis exploratorio de datos
            - Detección de patrones y anomalías
            - Recomendaciones para cruces de datos
            - Interpretación de resultados
            """)
            
        with col2:
            mode = st.selectbox(
                "Modo de análisis",
                ["Estándar", "Detallado", "Resumido"],
                index=0,
                help="El modo determina el nivel de detalle en las respuestas"
            )
            
            show_typing = st.checkbox(
                "Mostrar animación de escritura", 
                value=True,
                help="Muestra una animación mientras el asistente procesa la respuesta"
            )
            
            if st.button("🗑️ Limpiar historial"):
                st.session_state.chat_history = []
                st.rerun()
    
    # Mostrar historial de chat
    for message in st.session_state.chat_history:
        show_chat_message(message["is_user"], message["message"])
    
    # Input para nueva consulta
    with st.container():
        input_col, button_col = st.columns([4, 1])
        
        with input_col:
            user_input = st.text_area(
                "Realiza tu consulta sobre los datos",
                placeholder="Ej: ¿Qué patrones puedes identificar en los datos? o ¿Qué recomendaciones tienes para el cruce?",
                height=80,
                key="user_query",
                help="Puedes preguntar sobre análisis, patrones, recomendaciones o solicitar visualizaciones"
            )
            
        with button_col:
            st.write("")  # Espaciado
            submit_button = st.button("Analizar", use_container_width=True)
    
    # Procesar la consulta
    if submit_button and user_input.strip():
        # Agregar mensaje del usuario al historial
        add_message(is_user=True, message=user_input)
        
        # Mostrar el mensaje del usuario
        show_chat_message(is_user=True, message=user_input)
        
        # Mostrar animación de escritura
        if show_typing:
            show_typing_animation(1.5)
        
        try:
            # Realizar la consulta a la API
            with st.spinner("Analizando datos..."):
                response_data = make_api_request_agente(user_input)
                
                if response_data and "choices" in response_data and len(response_data["choices"]) > 0:
                    response_text = response_data["choices"][0]["message"]["content"]
                    
                    # Agregar respuesta al historial
                    add_message(is_user=False, message=response_text)
                    
                    # Mostrar resultados con formato mejorado
                    show_analysis_result(response_text)
                else:
                    st.error("No se pudo obtener una respuesta válida. Por favor, intenta nuevamente.")
        except Exception as e:
            st.error(f"Ocurrió un error durante el análisis: {str(e)}")
    
    # Opción para exportar el historial
    if st.session_state.chat_history:
        st.sidebar.markdown("### 📑 Historial")
        export_chat_history()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Asistente de Datos IA",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    run_data_assistant()
