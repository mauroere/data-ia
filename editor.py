import streamlit as st
import pandas as pd

st.set_page_config(page_title="✏️ Editor", layout="wide")
st.title("🛠️ Edición de Datos")

uploaded_file = st.file_uploader("📁 Cargá CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)

    fila = st.number_input("Fila a editar", min_value=0, max_value=len(df)-1)
    columna = st.selectbox("Columna", df.columns)
    nuevo_valor = st.text_input("Nuevo valor")

    if st.button("Actualizar"):
        df.at[fila, columna] = nuevo_valor
        st.success(f"Fila {fila}, columna {columna} actualizada.")

    st.download_button("📥 Descargar CSV", df.to_csv(index=False), "actualizado.csv", "text/csv")