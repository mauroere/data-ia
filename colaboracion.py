import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Definir roles y permisos
ROLES = {
    "Lectura": {
        "permisos": ["ver_datos", "exportar_datos"],
        "descripcion": "Puede ver y exportar datos sin modificarlos"
    },
    "Edición": {
        "permisos": ["ver_datos", "editar_datos", "exportar_datos"],
        "descripcion": "Puede ver, editar y exportar datos"
    },
    "Admin": {
        "permisos": ["ver_datos", "editar_datos", "exportar_datos", "gestionar_usuarios", "ver_auditoria"],
        "descripcion": "Acceso completo al sistema incluyendo gestión de usuarios"
    }
}

# Funciones de gestión de usuarios
def cargar_usuarios():
    """Carga los usuarios desde el almacenamiento o crea un admin por defecto"""
    if "usuarios" in st.session_state:
        return st.session_state.usuarios
        
    # Inicializar con un admin por defecto
    usuarios_default = {
        "admin": {
            "password": "admin123",  # En producción usar hashing
            "nombre": "Administrador",
            "rol": "Admin",
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    
    # Guardar en session_state
    st.session_state.usuarios = usuarios_default
    return usuarios_default

def verificar_acceso(permiso):
    """Verifica si el usuario actual tiene un permiso específico"""
    if "usuario_actual" not in st.session_state:
        return False
        
    usuario = st.session_state.usuario_actual
    rol = st.session_state.usuarios[usuario]["rol"]
    return permiso in ROLES[rol]["permisos"]

def registrar_actividad(accion, detalles=""):
    """Registra una actividad en el log de auditoría"""
    if "log_auditoria" not in st.session_state:
        st.session_state.log_auditoria = []
        
    if "usuario_actual" in st.session_state:
        usuario = st.session_state.usuario_actual
    else:
        usuario = "anónimo"
        
    log_entry = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "usuario": usuario,
        "accion": accion,
        "detalles": detalles
    }
    
    st.session_state.log_auditoria.append(log_entry)

def run_colaboracion():
    st.title("👥 Control de Accesos")
    
    # Cargar usuarios
    usuarios = cargar_usuarios()
    
    # Inicializar variables de sesión
    if "usuario_actual" not in st.session_state:
        st.session_state.usuario_actual = None
    
    # Mostrar sección de login o panel de administración
    if st.session_state.usuario_actual is None:
        mostrar_login()
    else:
        mostrar_panel_usuario()

def mostrar_login():
    """Muestra el formulario de login"""
    st.subheader("🔐 Iniciar sesión")
    
    # Formulario de login
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit_login = st.form_submit_button("Iniciar sesión")
    
    # Procesar login
    if submit_login:
        if not username or not password:
            st.error("Por favor, completa todos los campos")
        elif username not in st.session_state.usuarios:
            st.error("Usuario no encontrado")
        elif st.session_state.usuarios[username]["password"] != password:
            st.error("Contraseña incorrecta")
            registrar_actividad("intento_login_fallido", f"Usuario: {username}")
        else:            # Login exitoso
            st.session_state.usuario_actual = username
            registrar_actividad("login_exitoso")
            st.success(f"Bienvenido, {st.session_state.usuarios[username]['nombre']}!")
            st.rerun()
    
    # Opción para registrarse
    st.markdown("---")
    st.subheader("🆕 Registrarse")
    st.write("Por favor contacta al administrador para obtener una cuenta.")

def mostrar_panel_usuario():
    """Muestra el panel de usuario según el rol"""
    usuario_actual = st.session_state.usuario_actual
    datos_usuario = st.session_state.usuarios[usuario_actual]
      # Información de usuario
    st.sidebar.success(f"Usuario: {datos_usuario['nombre']}")
    st.sidebar.info(f"Rol: {datos_usuario['rol']}")
    if st.sidebar.button("Cerrar sesión"):
        registrar_actividad("logout")
        st.session_state.usuario_actual = None
        st.rerun()
    
    # Mostrar diferentes secciones según el rol
    tabs = ["Mi perfil"]
    
    if verificar_acceso("gestionar_usuarios"):
        tabs.append("Gestión de usuarios")
    
    if verificar_acceso("ver_auditoria"):
        tabs.append("Log de auditoría")
        
    # Crear pestañas
    seccion = st.tabs(tabs)
    
    # Tab Mi perfil
    with seccion[0]:
        st.subheader("👤 Mi perfil")
        st.write(f"Nombre: {datos_usuario['nombre']}")
        st.write(f"Usuario: {usuario_actual}")
        st.write(f"Rol: {datos_usuario['rol']}")
        st.write(f"Fecha de creación: {datos_usuario['fecha_creacion']}")
        
        # Permisos
        st.subheader("🔑 Mis permisos")
        for permiso in ROLES[datos_usuario["rol"]]["permisos"]:
            st.write(f"✅ {permiso}")
    
    # Tab Gestión de usuarios (solo para admins)
    if verificar_acceso("gestionar_usuarios"):
        with seccion[1]:
            st.subheader("👥 Gestión de usuarios")
            
            # Tabla de usuarios
            usuarios_df = pd.DataFrame([
                {
                    "Usuario": user,
                    "Nombre": data["nombre"],
                    "Rol": data["rol"],
                    "Fecha creación": data["fecha_creacion"]
                } 
                for user, data in st.session_state.usuarios.items()
            ])
            
            st.dataframe(usuarios_df)
            
            # Crear nuevo usuario
            with st.expander("➕ Crear nuevo usuario"):
                with st.form("new_user_form"):
                    new_username = st.text_input("Usuario")
                    new_password = st.text_input("Contraseña", type="password")
                    new_name = st.text_input("Nombre completo")
                    new_role = st.selectbox("Rol", list(ROLES.keys()))
                    submit_new = st.form_submit_button("Crear usuario")
                
                if submit_new:
                    if not new_username or not new_password or not new_name:
                        st.error("Todos los campos son obligatorios")
                    elif new_username in st.session_state.usuarios:
                        st.error("El nombre de usuario ya existe")
                    else:
                        # Crear nuevo usuario
                        st.session_state.usuarios[new_username] = {
                            "password": new_password,
                            "nombre": new_name,
                            "rol": new_role,
                            "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }                        
                        registrar_actividad("crear_usuario", f"Usuario creado: {new_username}, Rol: {new_role}")
                        st.success(f"Usuario {new_username} creado correctamente")
                        st.rerun()
    
    # Tab Log de auditoría (solo para admins)
    if verificar_acceso("ver_auditoria") and "ver_auditoria" in tabs:
        with seccion[2]:
            st.subheader("📋 Log de auditoría")
            
            if "log_auditoria" in st.session_state and st.session_state.log_auditoria:
                # Mostrar tabla de logs
                log_df = pd.DataFrame(st.session_state.log_auditoria)
                st.dataframe(log_df)
                
                # Exportar logs
                if st.button("Exportar logs"):
                    csv = log_df.to_csv(index=False)
                    fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        "📥 Descargar CSV", 
                        csv, 
                        f"log_auditoria_{fecha_actual}.csv", 
                        "text/csv"
                    )
            else:
                st.info("No hay actividades registradas aún")

if __name__ == "__main__":
    st.set_page_config(page_title="🔐 Seguridad", layout="wide")
    run_colaboracion()