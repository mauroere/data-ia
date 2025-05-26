import streamlit as st
import pandas as pd
import io
from utils import read_flexible_file

def run_exportador():
    st.title("📁 Exportador de Datos")

    uploaded_file = st.file_uploader("📁 Base para exportar", type=["csv", "xls", "xlsx"])
    if uploaded_file:
        df = read_flexible_file(uploaded_file)
        
        # Opciones de filtrado
        st.subheader("Filtrar datos")
        filtro_tabs = st.tabs(["Filtro simple", "Filtro avanzado"])
        
        with filtro_tabs[0]:
            # Filtro simple por una columna
            col = st.selectbox("Filtrar por columna", df.columns)
            
            if df[col].nunique() > 30:
                # Si hay muchos valores únicos, usar un campo de texto
                val_input = st.text_input(f"Filtrar '{col}' que contenga:")
                if val_input:
                    filtrado = df[df[col].astype(str).str.contains(val_input, case=False)]
                else:
                    filtrado = df
            else:
                # Si hay pocos valores, mostrar un selectbox
                opciones = ["Todos"] + list(df[col].dropna().unique())
                val = st.selectbox("Valor", opciones)
                if val == "Todos":
                    filtrado = df
                else:
                    filtrado = df[df[col] == val]
        
        with filtro_tabs[1]:
            # Filtro avanzado con múltiples condiciones
            st.write("Filtrado por múltiples columnas")
            
            # Permitir seleccionar hasta 3 condiciones
            filtros_activos = []
            
            for i in range(3):
                col1, col2, col3 = st.columns([2, 1, 2])
                
                with col1:
                    col_name = st.selectbox(f"Columna {i+1}", ["Ninguna"] + list(df.columns), key=f"col_{i}")
                
                if col_name != "Ninguna":
                    with col2:
                        operador = st.selectbox(f"Operador {i+1}", ["=", "!=", ">", "<", "contiene"], key=f"op_{i}")
                    
                    with col3:
                        if df[col_name].dtype in ['int64', 'float64']:
                            # Para columnas numéricas
                            val_filter = st.number_input(f"Valor {i+1}", value=0, key=f"val_{i}")
                        else:
                            # Para columnas de texto
                            val_filter = st.text_input(f"Valor {i+1}", key=f"val_{i}")
                    
                    filtros_activos.append((col_name, operador, val_filter))
            
            # Aplicar filtros avanzados
            if filtros_activos:
                filtrado = df.copy()
                for col_name, operador, valor in filtros_activos:
                    if operador == "=":
                        filtrado = filtrado[filtrado[col_name] == valor]
                    elif operador == "!=":
                        filtrado = filtrado[filtrado[col_name] != valor]
                    elif operador == ">":
                        filtrado = filtrado[filtrado[col_name] > valor]
                    elif operador == "<":
                        filtrado = filtrado[filtrado[col_name] < valor]
                    elif operador == "contiene":
                        filtrado = filtrado[filtrado[col_name].astype(str).str.contains(valor, case=False)]
            else:
                filtrado = df
        
        # Mostrar resultado del filtrado
        st.subheader("Datos filtrados")
        st.write(f"{len(filtrado)} filas después del filtrado")
        st.dataframe(filtrado)
        
        # Opciones de exportación
        st.subheader("Opciones de exportación")
        formato = st.selectbox("Formato", ["CSV", "Excel", "JSON"])
        
        if formato == "CSV":
            separador = st.selectbox("Separador", [",", ";", "\t"])
            encoding = st.selectbox("Codificación", ["utf-8", "latin-1", "ISO-8859-1"])
            
            if st.button("Exportar CSV"):
                csv_data = filtrado.to_csv(index=False, sep=separador, encoding=encoding)
                st.download_button("📥 Descargar CSV", csv_data, "datos_exportados.csv", "text/csv")
        
        elif formato == "Excel":
            if st.button("Exportar Excel"):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    filtrado.to_excel(writer, index=False)
                st.download_button("📥 Descargar Excel", output.getvalue(), "datos_exportados.xlsx", 
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        elif formato == "JSON":
            orient = st.selectbox("Formato JSON", ["records", "columns", "values"])
            
            if st.button("Exportar JSON"):
                json_data = filtrado.to_json(orient=orient)
                st.download_button("📥 Descargar JSON", json_data, "datos_exportados.json", "application/json")

if __name__ == "__main__":
    st.set_page_config(page_title="📤 Exportación", layout="wide")
    run_exportador()