import streamlit as st
import pandas as pd
import altair as alt
from utils import read_flexible_file

def run_dashboard():
    st.title("📈 Visualización de Datos")

    uploaded_file = st.file_uploader("📁 Subí la base", type=["csv", "xls", "xlsx"])
    if uploaded_file:
        df = read_flexible_file(uploaded_file)
        
        # Mostrar estadísticas básicas
        st.subheader("📊 Estadísticas básicas")
        st.write(f"Filas: {df.shape[0]}, Columnas: {df.shape[1]}")
        
        # Filtrado por columna
        col = st.selectbox("Filtrar por columna", df.columns)
        if df[col].nunique() > 50:
            # Si hay muchos valores, usar un text_input para buscar
            val_input = st.text_input(f"Escribe un valor para filtrar en '{col}':")
            if val_input:
                subset = df[df[col].astype(str).str.contains(val_input, case=False)]
            else:
                subset = df
        else:
            # Si hay pocos valores, usar un selectbox
            val = st.selectbox("Seleccioná un valor", ["Todos"] + list(df[col].dropna().unique()))
            if val == "Todos":
                subset = df
            else:
                subset = df[df[col] == val]
        
        st.dataframe(subset)

        # Métricas para gráficos
        st.subheader("📈 Visualización")
        metric_cols = st.multiselect("Selecciona columnas para visualizar", df.columns)
        
        for metric in metric_cols:
            if df[metric].dtype in ['int64', 'float64']:
                # Para columnas numéricas
                st.write(f"Histograma de {metric}")
                chart = alt.Chart(df).mark_bar().encode(
                    alt.X(f"{metric}:Q", bin=True),
                    y='count()'
                ).properties(width=600)
                st.altair_chart(chart, use_container_width=True)
            else:
                # Para columnas categóricas
                value_counts = df[metric].value_counts().reset_index()
                value_counts.columns = ["Valor", "Cantidad"]
                
                if len(value_counts) > 20:
                    # Mostrar solo los 20 más frecuentes
                    value_counts = value_counts.head(20)
                    st.write(f"Top 20 valores más frecuentes en {metric}")
                else:
                    st.write(f"Distribución de valores en {metric}")
                
                chart = alt.Chart(value_counts).mark_bar().encode(
                    x=alt.X("Valor:N", sort='-y'),
                    y="Cantidad:Q",
                    tooltip=["Valor", "Cantidad"]
                ).properties(width=600)
                st.altair_chart(chart, use_container_width=True)
        
        # Exportar subset
        if st.button("Exportar datos filtrados"):
            st.download_button(
                "📥 Descargar CSV", 
                subset.to_csv(index=False), 
                "datos_filtrados.csv", 
                "text/csv"
            )

if __name__ == "__main__":
    st.set_page_config(page_title="📊 Dashboard", layout="wide")
    run_dashboard()