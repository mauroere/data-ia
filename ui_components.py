"""
Componentes de UI reutilizables para toda la aplicación
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional, Union
import time
import base64
from io import BytesIO

# Componente para mostrar tarjetas de estadísticas
def stat_card(title: str, value: Union[str, int, float], delta: Optional[Union[str, float]] = None, 
              icon: str = "📊", help_text: str = None):
    """
    Muestra una tarjeta de estadísticas con título, valor y cambio opcional.
    
    Args:
        title: Título de la tarjeta
        value: Valor principal a mostrar
        delta: Valor de cambio (opcional)
        icon: Emoji o icono a mostrar
        help_text: Texto de ayuda al pasar el mouse
    """
    # Formateamos el valor si es numérico
    if isinstance(value, (int, float)):
        if value >= 1000:
            value_str = f"{value:,.0f}"
        else:
            value_str = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
    else:
        value_str = str(value)
    
    # Creamos el HTML para la tarjeta
    delta_html = ""
    if delta is not None:
        if isinstance(delta, (int, float)):
            is_positive = delta > 0
            delta_color = "#09AB3B" if is_positive else "#FF4B4B"
            delta_icon = "↑" if is_positive else "↓"
            delta_html = f"""
            <div style="color: {delta_color}; font-size: 0.9rem; margin-top: 0.3rem;">
                {delta_icon} {abs(delta):,.2f}%
            </div>
            """
        else:
            delta_html = f"""
            <div style="color: #0068C9; font-size: 0.9rem; margin-top: 0.3rem;">
                {delta}
            </div>
            """
    
    card_html = f"""
    <div class="card" style="text-align: center;" title="{help_text or ''}">
        <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="color: #6C757D; font-size: 0.9rem;">{title}</div>
        <div style="font-size: 1.8rem; font-weight: 600; color: #262730; margin-top: 0.3rem;">
            {value_str}
        </div>
        {delta_html}
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

# Componente para mostrar tarjetas de información
def info_card(title: str, content: str, icon: str = "ℹ️", style: str = "info"):
    """
    Muestra una tarjeta de información con título y contenido.
    
    Args:
        title: Título de la tarjeta
        content: Contenido a mostrar (puede ser HTML)
        icon: Emoji o icono a mostrar
        style: Estilo de la tarjeta (info, success, warning, error)
    """
    # Determinar colores según estilo
    colors = {
        "info": {"bg": "#EBF0FF", "border": "#3366FF", "text": "#0747A6"},
        "success": {"bg": "#E9F9EF", "border": "#09AB3B", "text": "#055A1C"},
        "warning": {"bg": "#FFF8E6", "border": "#FFBD45", "text": "#805E00"},
        "error": {"bg": "#FFEBEB", "border": "#FF4B4B", "text": "#80001D"}
    }
    
    style_data = colors.get(style, colors["info"])
    
    card_html = f"""
    <div style="background-color: {style_data['bg']}; border-left: 5px solid {style_data['border']}; 
                padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <div style="font-size: 1.3rem; margin-right: 0.5rem;">{icon}</div>
            <div style="font-weight: 600; color: {style_data['text']};">{title}</div>
        </div>
        <div style="color: {style_data['text']};">
            {content}
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

# Componente para mostrar tarjetas de características
def feature_card(title: str, description: str, icon: str = "🔍", button_text: str = None, 
                on_click=None, button_key: str = None):
    """
    Muestra una tarjeta de característica con título, descripción y botón opcional.
    
    Args:
        title: Título de la característica
        description: Descripción de la característica
        icon: Emoji o icono a mostrar
        button_text: Texto del botón (opcional)
        on_click: Función a ejecutar al hacer clic en el botón
        button_key: Clave única para el botón
    """
    with st.container():
        st.markdown(f"""
        <div class="card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem; text-align: center;">{icon}</div>
            <div class="card-header" style="text-align: center;">{title}</div>
            <p style="color: #6C757D;">{description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if button_text:
            st.button(button_text, on_click=on_click, key=button_key or f"btn_{title.lower().replace(' ', '_')}")

# Componente para mostrar un mensaje de carga animado
def loading_animation(message: str = "Procesando datos..."):
    """
    Muestra un mensaje de carga animado.
    
    Args:
        message: Mensaje a mostrar durante la carga
    """
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col2:
            with st.spinner(message):
                progress_bar = st.progress(0)
                for i in range(100):
                    # Actualizar la barra de progreso
                    progress_bar.progress(i + 1)
                    # Pequeña pausa para la animación
                    time.sleep(0.01)
                st.success("¡Completado!")

# Componente para mostrar una tabla mejorada con filtros
def enhanced_dataframe(df: pd.DataFrame, title: str = None, filters: List[str] = None, 
                      pagination: bool = True, page_size: int = 10):
    """
    Muestra un DataFrame con mejoras como filtros y paginación.
    
    Args:
        df: DataFrame a mostrar
        title: Título para la tabla (opcional)
        filters: Columnas que se pueden filtrar
        pagination: Activar paginación
        page_size: Tamaño de página para paginación
    """
    if title:
        st.markdown(f"<h3 class='subsection-header'>{title}</h3>", unsafe_allow_html=True)
    
    # Copiar el dataframe para no modificar el original
    filtered_df = df.copy()
    
    # Mostrar filtros si se especifican
    if filters:
        st.markdown("<p style='font-weight: 500;'>Filtros</p>", unsafe_allow_html=True)
        
        # Crear filtros basados en las columnas especificadas
        for column in filters:
            if column in df.columns:
                if df[column].dtype == 'object' or df[column].dtype == 'category':
                    # Para columnas categóricas o de texto
                    options = ["Todos"] + sorted(df[column].unique().tolist())
                    selected = st.selectbox(f"Filtrar por {column}", options, key=f"filter_{column}")
                    
                    if selected != "Todos":
                        filtered_df = filtered_df[filtered_df[column] == selected]
                else:
                    # Para columnas numéricas
                    min_val, max_val = float(df[column].min()), float(df[column].max())
                    step = (max_val - min_val) / 100.0 if min_val != max_val else 0.1
                    
                    selected_range = st.slider(
                        f"Rango de {column}",
                        min_value=min_val,
                        max_value=max_val,
                        value=(min_val, max_val),
                        step=step,
                        key=f"filter_range_{column}"
                    )
                    
                    filtered_df = filtered_df[
                        (filtered_df[column] >= selected_range[0]) & 
                        (filtered_df[column] <= selected_range[1])
                    ]
    
    # Paginación
    if pagination and len(filtered_df) > page_size:
        total_pages = (len(filtered_df) + page_size - 1) // page_size
        
        col1, col2 = st.columns([3, 1])
        with col2:
            page = st.number_input(
                "Página",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1,
                key=f"pagination_{id(df)}"
            )
        
        with col1:
            st.markdown(f"Mostrando página {page} de {total_pages} ({len(filtered_df)} registros en total)")
            
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_df))
        
        st.dataframe(filtered_df.iloc[start_idx:end_idx], use_container_width=True)
    else:
        st.dataframe(filtered_df, use_container_width=True)
    
    # Opción para descargar
    if not filtered_df.empty:
        col1, col2 = st.columns([1, 3])
        with col1:
            csv = filtered_df.to_csv(index=False)
            filename = f"datos_{int(time.time())}.csv"
            
            st.download_button(
                label="📥 Exportar datos",
                data=csv,
                file_name=filename,
                mime="text/csv"
            )
    
    return filtered_df

# Función para crear gráficos descargables
def download_chart(fig, filename="chart.png", button_text="Descargar gráfico"):
    """
    Crea un botón para descargar un gráfico como imagen.
    
    Args:
        fig: Figura (matplotlib, plotly, etc) a descargar
        filename: Nombre del archivo
        button_text: Texto para el botón de descarga
    """
    # Convertir a imagen
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)
    
    # Codificar en base64
    img_str = base64.b64encode(buf.read()).decode()
    
    # Botón de descarga HTML
    href = f'<a href="data:image/png;base64,{img_str}" download="{filename}" style="text-decoration:none;">'\
           f'<button style="background-color:#0068C9;color:white;padding:0.5rem 1rem;'\
           f'border:none;border-radius:0.5rem;cursor:pointer;font-weight:500;">'\
           f'📥 {button_text}</button></a>'
    
    st.markdown(href, unsafe_allow_html=True)

# Función para mostrar tarjetas para resultados de análisis
def analysis_card(title: str, content: str, icon: str = "📊"):
    """
    Muestra una tarjeta para resultados de análisis.
    
    Args:
        title: Título del análisis
        content: Contenido del análisis (puede ser HTML)
        icon: Emoji o icono a mostrar
    """
    st.markdown(f"""
    <div class="analysis-section">
        <div class="analysis-header">
            <i>{icon}</i> {title}
        </div>
        <div>
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Función para mostrar mensajes de chat estilizados
def chat_message(message: str, is_user: bool = False):
    """
    Muestra un mensaje de chat con estilo.
    
    Args:
        message: Contenido del mensaje
        is_user: True si el mensaje es del usuario, False si es del asistente
    """
    if is_user:
        st.markdown(f"""
        <div style="padding: 1.2rem; border-radius: 0.75rem; margin-bottom: 1rem; 
                    background-color: #F0F2F6; border-left: 5px solid #FF4B4B; 
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);">
            <div style="font-weight: bold; color: #FF4B4B; margin-bottom: 0.5rem;">👤 Usuario</div>
            <div>{message}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="padding: 1.2rem; border-radius: 0.75rem; margin-bottom: 1rem; 
                    background-color: #F8F9FD; border-left: 5px solid #0068C9; 
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);">
            <div style="font-weight: bold; color: #0068C9; margin-bottom: 0.5rem;">🤖 Asistente</div>
            <div>{message}</div>
        </div>
        """, unsafe_allow_html=True)

# Función para mostrar tarjetas de datos
def data_card(title: str, content: str, footer: str = None):
    """
    Muestra una tarjeta de datos con título y contenido.
    
    Args:
        title: Título de la tarjeta
        content: Contenido principal
        footer: Pie de la tarjeta (opcional)
    """
    footer_html = f"""<div style="margin-top: 0.75rem; font-size: 0.8rem; color: #6C757D;">{footer}</div>""" if footer else ""
    
    st.markdown(f"""
    <div style="border: 1px solid #E0E4EB; border-radius: 0.5rem; padding: 1rem; margin: 1rem 0;">
        <div style="font-weight: 600; margin-bottom: 0.75rem; color: #262730;">{title}</div>
        <div>{content}</div>
        {footer_html}
    </div>
    """, unsafe_allow_html=True)
