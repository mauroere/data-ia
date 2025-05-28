"""
Asistente especializado para el cruce inteligente de datos.
Implementa un modo agente para proporcionar análisis estructurado y recomendaciones.
"""

import streamlit as st
import pandas as pd
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from api_context import make_api_request_agente, generar_contexto_datos
from api_fix import ensure_api_key_exists
from ui_components import chat_message, stat_card, data_card, loading_animation

# Asegurar que la API key esté disponible
ensure_api_key_exists()

# Estilos para el asistente de cruce
CSS_CRUCE = """
<style>
    .cruce-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #FF4B4B;
        margin-bottom: 1rem;
    }
    
    .analysis-container {
        border-radius: 0.75rem;
        border: 1px solid #E0E4EB;
        background-color: white;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .analysis-section {
        margin-bottom: 1.5rem;
        border-left: 4px solid #0068C9;
        padding-left: 1rem;
    }
    
    .analysis-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #0068C9;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
    }
    
    .analysis-title i {
        margin-right: 0.5rem;
    }
    
    .recommendation-item {
        background-color: #F0F7FF;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .finding-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 0.75rem;
    }
    
    .finding-number {
        min-width: 24px;
        height: 24px;
        background-color: #0068C9;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        margin-right: 0.75rem;
        font-size: 0.8rem;
    }
    
    .action-buttons {
        display: flex;
        gap: 0.75rem;
        margin-top: 1.5rem;
    }
</style>
"""

def inicializar_historial_cruce():
    """Inicializa el historial de consultas y respuestas del cruce inteligente."""
    if "cruce_historial" not in st.session_state:
        st.session_state.cruce_historial = []

def agregar_consulta_cruce(consulta: str, respuesta: Dict[str, Any]):
    """
    Agrega una consulta y su respuesta al historial del cruce inteligente.
    
    Args:
        consulta: La consulta realizada por el usuario
        respuesta: La respuesta completa del API (incluyendo metadatos)
    """
    if "cruce_historial" not in st.session_state:
        inicializar_historial_cruce()
    
    # Extraer el texto de la respuesta
    texto_respuesta = ""
    if "choices" in respuesta and len(respuesta["choices"]) > 0:
        texto_respuesta = respuesta["choices"][0]["message"]["content"]
    
    # Crear entrada en el historial
    entrada = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "consulta": consulta,
        "respuesta_texto": texto_respuesta,
        "respuesta_completa": respuesta
    }
    
    st.session_state.cruce_historial.append(entrada)

def mostrar_analisis_estructurado(respuesta_texto: str):
    """
    Muestra el análisis de datos estructurado con un formato mejorado.
    
    Args:
        respuesta_texto: El texto de respuesta del agente
    """
    # Intentar separar las secciones del análisis
    secciones = {}
    
    try:
        if "📊 ANÁLISIS:" in respuesta_texto:
            # Separar análisis
            partes = respuesta_texto.split("📊 ANÁLISIS:")
            if len(partes) > 1:
                analisis_y_resto = partes[1].split("🔍 HALLAZGOS:", 1)
                secciones["analisis"] = analisis_y_resto[0].strip()
                
                # Separar hallazgos y recomendaciones
                if len(analisis_y_resto) > 1:
                    hallazgos_y_recomendaciones = analisis_y_resto[1].split("📈 RECOMENDACIONES:", 1)
                    secciones["hallazgos"] = hallazgos_y_recomendaciones[0].strip()
                    
                    # Separar recomendaciones
                    if len(hallazgos_y_recomendaciones) > 1:
                        secciones["recomendaciones"] = hallazgos_y_recomendaciones[1].strip()
        
        # Si se pudieron extraer las secciones, mostrarlas con formato mejorado
        if "analisis" in secciones:
            st.markdown(f"""
            <div class="analysis-container">
                <div class="analysis-section">
                    <div class="analysis-title"><i>📊</i> Análisis de los Datos</div>
                    <div>{secciones['analisis']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Mostrar hallazgos si existen
            if "hallazgos" in secciones:
                # Intentar separar los hallazgos individuales
                hallazgos_texto = secciones["hallazgos"]
                hallazgos_items = []
                
                # Buscar items numerados o con viñetas
                import re
                hallazgos_items = re.split(r'\n\s*\d+[\.\)-]\s*|\n\s*[-•*]\s*', hallazgos_texto)
                hallazgos_items = [h for h in hallazgos_items if h.strip()]
                
                if not hallazgos_items and hallazgos_texto:
                    # Si no se pudieron separar, usar el texto completo
                    hallazgos_items = [hallazgos_texto]
                
                st.markdown("""
                <div class="analysis-section">
                    <div class="analysis-title"><i>🔍</i> Hallazgos Principales</div>
                """, unsafe_allow_html=True)
                
                for i, hallazgo in enumerate(hallazgos_items, 1):
                    st.markdown(f"""
                    <div class="finding-item">
                        <div class="finding-number">{i}</div>
                        <div>{hallazgo.strip()}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Mostrar recomendaciones si existen
            if "recomendaciones" in secciones:
                # Intentar separar las recomendaciones individuales
                recomendaciones_texto = secciones["recomendaciones"]
                recomendaciones_items = []
                
                # Buscar items numerados o con viñetas
                import re
                recomendaciones_items = re.split(r'\n\s*\d+[\.\)-]\s*|\n\s*[-•*]\s*', recomendaciones_texto)
                recomendaciones_items = [r for r in recomendaciones_items if r.strip()]
                
                if not recomendaciones_items and recomendaciones_texto:
                    # Si no se pudieron separar, usar el texto completo
                    recomendaciones_items = [recomendaciones_texto]
                
                st.markdown("""
                <div class="analysis-section">
                    <div class="analysis-title"><i>📈</i> Recomendaciones</div>
                """, unsafe_allow_html=True)
                
                for recomendacion in recomendaciones_items:
                    if recomendacion.strip():
                        st.markdown(f"""
                        <div class="recommendation-item">
                            {recomendacion.strip()}
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Si no se pudieron extraer las secciones, mostrar la respuesta completa
            st.markdown(f"""
            <div class="analysis-container">
                <div class="analysis-section">
                    <div class="analysis-title"><i>📋</i> Resultado del Análisis</div>
                    <div>{respuesta_texto}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        # En caso de error, mostrar la respuesta completa
        st.error(f"Error al formatear la respuesta: {str(e)}")
        st.markdown(f"""
        <div class="analysis-container">
            <div class="analysis-section">
                <div class="analysis-title"><i>📋</i> Resultado del Análisis</div>
                <div>{respuesta_texto}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def exportar_historial_cruce():
    """Permite exportar el historial de análisis de cruce inteligente."""
    if "cruce_historial" in st.session_state and st.session_state.cruce_historial:
        # Preparar datos para exportación
        datos_exportacion = []
        
        for entrada in st.session_state.cruce_historial:
            datos_exportacion.append({
                "Fecha y Hora": entrada["timestamp"],
                "Consulta": entrada["consulta"],
                "Respuesta": entrada["respuesta_texto"]
            })
        
        # Convertir a DataFrame para facilitar la exportación
        df_exportacion = pd.DataFrame(datos_exportacion)
        
        # Ofrecer botones de descarga
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Descargar como CSV",
                data=df_exportacion.to_csv(index=False),
                file_name=f"historial_cruce_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            buffer = pd.ExcelWriter(f"historial_cruce_{time.strftime('%Y%m%d_%H%M%S')}.xlsx", engine="xlsxwriter")
            df_exportacion.to_excel(buffer, index=False, sheet_name="Historial")
            buffer.close()
            
            with open(f"historial_cruce_{time.strftime('%Y%m%d_%H%M%S')}.xlsx", "rb") as f:
                st.download_button(
                    label="📥 Descargar como Excel",
                    data=f,
                    file_name=f"historial_cruce_{time.strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

def run_asistente_cruce_inteligente():
    """Ejecuta el asistente de cruce inteligente en modo agente."""
    # Inyectar CSS personalizado
    st.markdown(CSS_CRUCE, unsafe_allow_html=True)
    
    # Inicializar historial
    inicializar_historial_cruce()
    
    # Verificar si hay datos cargados
    if 'base_df' not in st.session_state or 'new_df' not in st.session_state:
        st.warning("⚠️ Carga primero los archivos BASE y NUEVO para utilizar el asistente de cruce inteligente.")
        return
    
    # Encabezado del asistente
    st.markdown("<div class='cruce-header'>🧠 Asistente de Cruce Inteligente</div>", unsafe_allow_html=True)
    st.markdown("""
    Este asistente te ayudará a analizar los datos cargados y obtener recomendaciones 
    para optimizar el cruce de información. Funciona en modo agente para proporcionar 
    análisis estructurados y detallados.
    """)
    
    # Sección de estadísticas
    with st.expander("📊 Estadísticas de los datos cargados", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        base_df = st.session_state['base_df']
        new_df = st.session_state['new_df']
        
        with col1:
            stat_card(
                title="Registros en archivo BASE", 
                value=len(base_df), 
                icon="📋"
            )
        
        with col2:
            stat_card(
                title="Registros en archivo NUEVO", 
                value=len(new_df), 
                icon="📄"
            )
        
        with col3:
            # Calcular porcentaje de coincidencias si existe
            if 'coincidencias' in st.session_state and st.session_state['coincidencias']:
                coincidencias = len(st.session_state['coincidencias'])
                porcentaje = (coincidencias / len(new_df)) * 100
                stat_card(
                    title="Coincidencias encontradas", 
                    value=coincidencias, 
                    delta=f"{porcentaje:.1f}%", 
                    icon="🔍"
                )
            else:
                stat_card(
                    title="Coincidencias encontradas", 
                    value="No disponible", 
                    icon="🔍"
                )
    
    # Separador
    st.divider()
    
    # Sección de consulta al agente
    st.markdown("### 💬 Consulta al Agente de Datos")
    
    # Preguntas sugeridas
    with st.expander("🔍 Preguntas sugeridas", expanded=True):
        sugerencias = [
            "Analiza las columnas de ambos archivos y sugiere los mejores campos para realizar el cruce",
            "¿Qué calidad tienen los datos para realizar un cruce efectivo?",
            "Identifica posibles problemas en los datos que puedan afectar al cruce",
            "Sugiere estrategias para mejorar el porcentaje de coincidencias",
            "¿Qué pre-procesamiento recomiendas aplicar a los datos antes del cruce?",
            "Analiza las diferencias entre los registros no coincidentes"
        ]
        
        cols = st.columns(2)
        for i, sugerencia in enumerate(sugerencias):
            col = cols[i % 2]
            if col.button(sugerencia, key=f"sugerencia_{i}", use_container_width=True):
                # Guardar la sugerencia seleccionada para procesarla después
                st.session_state["consulta_seleccionada"] = sugerencia
                st.rerun()
    
    # Input para la consulta
    consulta = st.text_area(
        "Escribe tu consulta o instrucción para el agente",
        value=st.session_state.get("consulta_seleccionada", ""),
        height=100,
        placeholder="Ejemplo: Analiza los datos y sugiere la mejor estrategia para el cruce"
    )
    
    # Botón para enviar consulta
    if st.button("🧠 Analizar con IA", use_container_width=True, type="primary"):
        if not consulta.strip():
            st.warning("Por favor, escribe una consulta o selecciona una de las sugerencias.")
        else:
            # Mostrar indicador de carga
            with st.spinner("El agente está analizando tus datos..."):
                try:
                    # Realizar la consulta a la API en modo agente
                    respuesta = make_api_request_agente(consulta.strip())
                    
                    # Guardar en el historial
                    agregar_consulta_cruce(consulta.strip(), respuesta)
                    
                    # Obtener texto de respuesta
                    if "choices" in respuesta and len(respuesta["choices"]) > 0:
                        respuesta_texto = respuesta["choices"][0]["message"]["content"]
                        
                        # Mostrar la consulta y respuesta
                        st.subheader("📝 Tu consulta")
                        st.info(consulta)
                        
                        st.subheader("🧠 Análisis del agente")
                        mostrar_analisis_estructurado(respuesta_texto)
                    else:
                        st.error("No se pudo obtener una respuesta válida del agente.")
                except Exception as e:
                    st.error(f"Error al procesar la consulta: {str(e)}")
    
    # Historial de análisis
    if st.session_state.cruce_historial:
        st.divider()
        with st.expander("📜 Historial de análisis", expanded=False):
            st.markdown("### Análisis anteriores")
            
            # Mostrar entradas del historial (las 5 más recientes)
            for i, entrada in enumerate(reversed(st.session_state.cruce_historial[-5:])):
                with st.container():
                    st.markdown(f"**Consulta {len(st.session_state.cruce_historial) - i}** ({entrada['timestamp']})")
                    st.info(entrada["consulta"])
                    
                    if st.button(f"Ver análisis completo #{len(st.session_state.cruce_historial) - i}", key=f"ver_{i}"):
                        mostrar_analisis_estructurado(entrada["respuesta_texto"])
                
                st.divider()
            
            # Opción para exportar
            st.markdown("### Exportar historial")
            exportar_historial_cruce()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Asistente de Cruce Inteligente",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    run_asistente_cruce_inteligente()