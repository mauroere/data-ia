"""
Script para verificar y corregir la configuración de secretos de Streamlit.
"""
import streamlit as st
import os
import toml
import shutil
from pathlib import Path

def fix_secrets():
    st.title("🔧 Reparación de Secretos de Streamlit")
    
    # 1. Verificar directorio .streamlit
    streamlit_dir = Path('.streamlit')
    if not streamlit_dir.exists():
        st.warning("📁 Creando directorio .streamlit...")
        streamlit_dir.mkdir(exist_ok=True)
        st.success("✅ Directorio .streamlit creado")
    else:
        st.success("✅ Directorio .streamlit existe")
    
    # 2. Verificar archivo secrets.toml
    secrets_file = streamlit_dir / 'secrets.toml'
    st.write("### Estado del archivo secrets.toml:")
    
    secrets_content = None
    if secrets_file.exists():
        try:
            with open(secrets_file, 'r', encoding='utf-8') as f:
                secrets_content = f.read()
                st.code(secrets_content, language='toml')
        except Exception as e:
            st.error(f"❌ Error al leer secrets.toml: {e}")
            secrets_content = None
    
    # 3. Verificar y corregir el contenido
    if not secrets_content or '[redpill]' not in secrets_content:
        st.warning("⚠️ El archivo secrets.toml necesita ser actualizado")
        
        # Crear respaldo si existe
        if secrets_file.exists():
            backup_file = streamlit_dir / 'secrets.toml.backup'
            shutil.copy2(secrets_file, backup_file)
            st.info(f"📑 Se ha creado un respaldo en {backup_file}")
        
        # Crear nuevo contenido
        new_secrets = {
            'redpill': {
                'api_key': 'sk-xYBWXr1epqP3Uq1A05qUql9tAyBsJE5F8PL5L66gBaE328VG',
                'api_url': 'https://api.redpill.ai/v1/chat/completions'
            }
        }
        
        # Guardar el nuevo contenido
        try:
            with open(secrets_file, 'w', encoding='utf-8') as f:
                toml.dump(new_secrets, f)
            st.success("✅ Archivo secrets.toml actualizado correctamente")
            st.code(toml.dumps(new_secrets), language='toml')
        except Exception as e:
            st.error(f"❌ Error al escribir secrets.toml: {e}")
    else:
        st.success("✅ El archivo secrets.toml está correctamente configurado")
    
    # 4. Verificar permisos
    try:
        st.write("### Verificando permisos:")
        if os.access(secrets_file, os.R_OK):
            st.success("✅ El archivo tiene permisos de lectura")
        else:
            st.error("❌ No hay permisos de lectura")
        
        if os.access(secrets_file, os.W_OK):
            st.success("✅ El archivo tiene permisos de escritura")
        else:
            st.error("❌ No hay permisos de escritura")
    except Exception as e:
        st.error(f"❌ Error al verificar permisos: {e}")
    
    # 5. Verificar st.secrets
    st.write("### Verificando st.secrets:")
    try:
        if 'redpill' in st.secrets and 'api_key' in st.secrets['redpill']:
            st.success("✅ La clave API está correctamente cargada en st.secrets")
        else:
            st.warning("⚠️ No se encuentra la clave API en st.secrets")
            st.info("💡 Intenta reiniciar la aplicación después de los cambios")
    except Exception as e:
        st.error(f"❌ Error al acceder a st.secrets: {e}")
    
    # 6. Instrucciones adicionales
    st.write("### Próximos pasos:")
    st.info("""
    1. Si se realizaron cambios, reinicia la aplicación
    2. Verifica que la clave API funciona en el Panel de Administración
    3. Si el problema persiste, verifica la conexión a internet y los certificados SSL
    """)

if __name__ == "__main__":
    fix_secrets()
