import streamlit as st

st.set_page_config(page_title="🔐 Seguridad", layout="wide")
st.title("👥 Control de Accesos")

# Definir roles y permisos
roles = {
    "Lectura": ["Ver datos", "Exportar datos"],
    "Edición": ["Ver datos", "Editar datos", "Exportar datos"],
    "Admin": ["Ver datos", "Editar datos", "Exportar datos", "Gestionar usuarios"]
}

# Selección de rol
rol = st.selectbox("Seleccioná un rol", list(roles.keys()))

# Mostrar permisos del rol seleccionado
st.subheader("Permisos del rol seleccionado:")
for permiso in roles[rol]:
    st.write(f"- {permiso}")

# Próximas funcionalidades
st.markdown("### Próximas funcionalidades:")
st.markdown("- Logs y auditoría")