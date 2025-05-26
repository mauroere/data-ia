import streamlit as st
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from utils import read_flexible_file

def suggest_mapping(df1, df2, threshold=80):
    """
    Sugiere mapeo entre columnas de dos DataFrames basado en:
    1. Nombres de columnas similares
    2. Contenido similar
    
    Args:
        df1: Primer DataFrame
        df2: Segundo DataFrame
        threshold: Umbral de similitud (0-100)
        
    Returns:
        dict: Mapeo sugerido {columna_df1: columna_df2}
    """
    mapeo = {}
    
    # Obtener una muestra de datos para comparar contenido
    sample_rows = min(100, min(len(df1), len(df2)))
    df1_sample = df1.head(sample_rows)
    df2_sample = df2.head(sample_rows)
    
    # Para cada columna en df1, encontrar la mejor coincidencia en df2
    for col1 in df1.columns:
        mejor_score = 0
        mejor_col2 = None
        
        for col2 in df2.columns:
            # Similitud por nombre de columna (peso: 0.5)
            nombre_score = fuzz.token_sort_ratio(str(col1), str(col2)) * 0.5
            
            # Similitud por contenido (peso: 0.5)
            contenido_score = 0
            # Solo comparar si ambas columnas tienen contenido
            if not (df1_sample[col1].isna().all() or df2_sample[col2].isna().all()):
                # Convertir a string para comparación
                values1 = df1_sample[col1].astype(str).tolist()
                values2 = df2_sample[col2].astype(str).tolist()
                # Calcular similitud promedio entre valores
                similitudes = []
                for i in range(min(10, len(values1), len(values2))):
                    similitudes.append(fuzz.token_sort_ratio(values1[i], values2[i]))
                if similitudes:
                    contenido_score = (sum(similitudes) / len(similitudes)) * 0.5
            
            # Score total
            score_total = nombre_score + contenido_score
            
            if score_total > mejor_score and score_total >= threshold:
                mejor_score = score_total
                mejor_col2 = col2
        
        if mejor_col2:
            mapeo[col1] = {"columna": mejor_col2, "score": mejor_score}
    
    return mapeo

def run_mapping_ai():
    st.title("🤖 Sugerencia de Mapeo de Datos")
    
    # Cargar archivos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Primer archivo")
        uploaded_file_1 = st.file_uploader("📁 Subí el primer archivo", type=["csv", "xls", "xlsx"])
        if uploaded_file_1:
            df1 = read_flexible_file(uploaded_file_1)
            st.write(f"Columnas: {len(df1.columns)} - Filas: {len(df1)}")
            st.dataframe(df1.head())
    
    with col2:
        st.subheader("Segundo archivo")
        uploaded_file_2 = st.file_uploader("📁 Subí el segundo archivo", type=["csv", "xls", "xlsx"])
        if uploaded_file_2:
            df2 = read_flexible_file(uploaded_file_2)
            st.write(f"Columnas: {len(df2.columns)} - Filas: {len(df2)}")
            st.dataframe(df2.head())
    
    if uploaded_file_1 and uploaded_file_2:
        st.subheader("Configuración de mapeo")
        threshold = st.slider("Umbral de similitud", 50, 100, 80)
        
        if st.button("Sugerir Mapeo Automático"):
            with st.spinner("Analizando datos..."):
                mapeo = suggest_mapping(df1, df2, threshold)
                
                if mapeo:
                    st.success(f"Se encontraron {len(mapeo)} mapeos posibles")
                    
                    # Crear tabla de mapeo
                    mapeo_df = pd.DataFrame([
                        {"Columna Origen": col1, "Columna Destino": info["columna"], "Coincidencia (%)": int(info["score"])}
                        for col1, info in mapeo.items()
                    ])
                    
                    # Ordenar por score descendente
                    mapeo_df = mapeo_df.sort_values("Coincidencia (%)", ascending=False)
                    
                    # Mostrar tabla con colores
                    st.dataframe(mapeo_df.style.background_gradient(subset=["Coincidencia (%)"], cmap="Greens"))
                    
                    # Opción para exportar mapeo
                    csv = mapeo_df.to_csv(index=False)
                    st.download_button("📥 Descargar Mapeo CSV", csv, "mapeo_columnas.csv", "text/csv")
                    
                    # Previsualización de datos integrados
                    st.subheader("Previsualización de datos integrados")
                    
                    # Crear dataframe resultante con las columnas mapeadas
                    resultado = pd.DataFrame()
                    for col1, info in mapeo.items():
                        col2 = info["columna"]
                        resultado[f"{col1} → {col2}"] = pd.Series([
                            f"{str(df1[col1].iloc[i])} → {str(df2[col2].iloc[i])}" 
                            for i in range(min(5, len(df1), len(df2)))
                        ])
                    
                    st.dataframe(resultado)
                else:
                    st.warning("No se encontraron columnas con similitud suficiente. Intenta reducir el umbral.")
        
        # Opción de mapeo manual
        st.subheader("Mapeo Manual")
        st.write("Selecciona columnas para mapear manualmente:")
        
        col_origen = st.selectbox("Columna origen", df1.columns)
        col_destino = st.selectbox("Columna destino", df2.columns)
        
        if st.button("Verificar compatibilidad"):
            # Verificar compatibilidad de tipos
            tipo1 = df1[col_origen].dtype
            tipo2 = df2[col_destino].dtype
            
            if tipo1 == tipo2:
                st.success(f"✅ Tipos compatibles: ambas columnas son {tipo1}")
            else:
                st.warning(f"⚠️ Tipos diferentes: {col_origen} es {tipo1}, {col_destino} es {tipo2}")
            
            # Mostrar valores de muestra
            muestra = pd.DataFrame({
                col_origen: df1[col_origen].head(5).values,
                col_destino: df2[col_destino].head(5).values
            })
            st.write("Muestra de valores:")
            st.dataframe(muestra)
            
            # Calcular similitud
            similitud = fuzz.token_sort_ratio(
                str(df1[col_origen].head(10).tolist()), 
                str(df2[col_destino].head(10).tolist())
            )
            
            st.write(f"Similitud de contenido: {similitud}%")

if __name__ == "__main__":
    st.set_page_config(page_title="🗺️ Mapeo de Datos", layout="wide")
    run_mapping_ai()