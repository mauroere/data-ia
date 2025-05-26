import streamlit as st
import pandas as pd
from utils import read_flexible_file

def run_editor():
    st.title("🛠️ Edición de Datos")

    uploaded_file = st.file_uploader("📁 Cargá CSV o Excel", type=["csv", "xls", "xlsx"])
    if uploaded_file:
        df = read_flexible_file(uploaded_file)
        
        # Opciones de visualización
        st.subheader("Vista previa de datos")
        show_mode = st.radio("Mostrar", ["Todo", "Primeras filas", "Últimas filas"])
        
        if show_mode == "Primeras filas":
            n_rows = st.slider("Cantidad de filas", 5, 100, 10)
            st.dataframe(df.head(n_rows))
        elif show_mode == "Últimas filas":
            n_rows = st.slider("Cantidad de filas", 5, 100, 10)
            st.dataframe(df.tail(n_rows))
        else:
            st.dataframe(df)
        
        # Mostrar información de la estructura
        if st.checkbox("Mostrar información del DataFrame"):
            buffer = pd.io.StringIO()
            df.info(buf=buffer)
            info_str = buffer.getvalue()
            st.text(info_str)
        
        st.subheader("Edición de datos")
        edit_tabs = st.tabs(["Editar celda", "Editar columna", "Agregar/Eliminar columna"])
        
        with edit_tabs[0]:
            # Edición de celda individual
            col1, col2 = st.columns(2)
            with col1:
                fila = st.number_input("Fila a editar", min_value=0, max_value=len(df)-1 if len(df) > 0 else 0)
            with col2:
                columna = st.selectbox("Columna", df.columns)
            
            # Mostrar valor actual
            if len(df) > 0:
                st.write(f"Valor actual: {df.at[fila, columna]}")
                nuevo_valor = st.text_input("Nuevo valor")
                
                if st.button("Actualizar celda"):
                    df.at[fila, columna] = nuevo_valor
                    st.success(f"Fila {fila}, columna {columna} actualizada.")
        
        with edit_tabs[1]:
            # Edición de columna completa
            col_to_edit = st.selectbox("Columna a editar", df.columns, key="col_edit")
            edit_type = st.radio("Tipo de edición", ["Reemplazar valor", "Aplicar función"])
            
            if edit_type == "Reemplazar valor":
                valor_viejo = st.text_input("Valor a reemplazar")
                valor_nuevo = st.text_input("Nuevo valor para reemplazar")
                
                if st.button("Reemplazar valores"):
                    if valor_viejo:
                        df[col_to_edit] = df[col_to_edit].replace(valor_viejo, valor_nuevo)
                        st.success(f"Valores reemplazados en columna {col_to_edit}")
            else:
                funcion = st.selectbox("Función a aplicar", ["Mayúsculas", "Minúsculas", "Título", "Eliminar espacios"])
                
                if st.button("Aplicar función"):
                    if funcion == "Mayúsculas":
                        df[col_to_edit] = df[col_to_edit].astype(str).str.upper()
                    elif funcion == "Minúsculas":
                        df[col_to_edit] = df[col_to_edit].astype(str).str.lower()
                    elif funcion == "Título":
                        df[col_to_edit] = df[col_to_edit].astype(str).str.title()
                    elif funcion == "Eliminar espacios":
                        df[col_to_edit] = df[col_to_edit].astype(str).str.strip()
                    st.success(f"Función aplicada a columna {col_to_edit}")
        
        with edit_tabs[2]:
            # Agregar/Eliminar columna
            action = st.radio("Acción", ["Agregar columna", "Eliminar columna"])
            
            if action == "Agregar columna":
                nueva_col = st.text_input("Nombre de la nueva columna")
                valor_default = st.text_input("Valor por defecto")
                
                if st.button("Agregar columna") and nueva_col:
                    df[nueva_col] = valor_default
                    st.success(f"Columna {nueva_col} agregada")
            else:
                col_to_delete = st.selectbox("Columna a eliminar", df.columns)
                
                if st.button("Eliminar columna"):
                    df = df.drop(columns=[col_to_delete])
                    st.success(f"Columna {col_to_delete} eliminada")
        
        # Exportar datos modificados
        st.subheader("Exportar datos")
        formato = st.selectbox("Formato de exportación", ["CSV", "Excel", "JSON"])
        
        if formato == "CSV":
            separador = st.selectbox("Separador", [",", ";", "\t"])
            encoding = st.selectbox("Codificación", ["utf-8", "latin-1", "ISO-8859-1"])
            
            if st.button("Generar CSV"):
                csv = df.to_csv(index=False, sep=separador, encoding=encoding)
                st.download_button("📥 Descargar CSV", csv, "datos_editados.csv", "text/csv")
        
        elif formato == "Excel":
            if st.button("Generar Excel"):
                buffer = pd.io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Datos', index=False)
                st.download_button("📥 Descargar Excel", buffer.getvalue(), "datos_editados.xlsx")
        
        else:  # JSON
            orient = st.selectbox("Orientación JSON", ["records", "columns", "index"])
            
            if st.button("Generar JSON"):
                json = df.to_json(orient=orient)
                st.download_button("📥 Descargar JSON", json, "datos_editados.json", "application/json")

if __name__ == "__main__":
    st.set_page_config(page_title="✏️ Editor", layout="wide")
    run_editor()