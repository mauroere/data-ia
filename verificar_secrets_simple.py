import os
import sys

def parse_toml_manually(file_path):
    """Analiza un archivo TOML de manera básica sin depender de la biblioteca toml"""
    result = {}
    current_section = None
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Saltar líneas vacías y comentarios
            if not line or line.startswith('#'):
                continue
                
            # Detectar secciones [section]
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                result[current_section] = {}
            
            # Detectar pares clave = valor
            elif '=' in line and current_section is not None:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Quitar comillas de los valores
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                
                result[current_section][key] = value
    
    return result

def main():
    print("=== DIAGNÓSTICO DE CARGA DE SECRETS PARA REDPILL API ===")
    print(f"Python versión: {sys.version}")
    print(f"Directorio actual: {os.getcwd()}")
    
    # Ruta al archivo de secretos
    secrets_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
    
    print(f"\nVerificando archivo: {secrets_path}")
    if not os.path.exists(secrets_path):
        print(f"❌ El archivo no existe en la ruta: {secrets_path}")
        # Verificar si existe el directorio .streamlit
        streamlit_dir = os.path.dirname(secrets_path)
        if not os.path.exists(streamlit_dir):
            print(f"❌ El directorio .streamlit no existe en: {streamlit_dir}")
            print("Creando directorio .streamlit...")
            os.makedirs(streamlit_dir)
            print("✅ Directorio .streamlit creado")
            
        # Crear archivo de secretos con contenido básico
        print("Creando archivo secrets.toml con configuración básica...")
        with open(secrets_path, 'w') as f:
            f.write('[redpill]\n')
            f.write('api_key = ""\n')
            f.write('api_url = "https://api.redpill.ai/v1/chat/completions"\n')
        print("✅ Archivo secrets.toml creado con configuración básica")
        return
    
    print("✅ El archivo existe")
    
    # Leer y verificar el contenido del archivo
    try:
        secrets = parse_toml_manually(secrets_path)
        print("\nContenido del archivo:")
        for section, values in secrets.items():
            print(f"\n[{section}]")
            for key, value in values.items():
                print(f"{key} = {value}")
        
        # Verificar sección redpill
        if "redpill" not in secrets:
            print("\n❌ No se encontró la sección [redpill]")
            print("Agregando sección [redpill]...")
            secrets["redpill"] = {
                "api_key": "",
                "api_url": "https://api.redpill.ai/v1/chat/completions"
            }
            with open(secrets_path, 'w') as f:
                for section, values in secrets.items():
                    f.write(f"[{section}]\n")
                    for key, value in values.items():
                        f.write(f'{key} = "{value}"\n')
                    f.write("\n")
            print("✅ Sección [redpill] agregada")
        
        # Verificar api_key en sección redpill
        elif "api_key" not in secrets["redpill"]:
            print("\n❌ No se encontró api_key en la sección [redpill]")
            print("Agregando api_key vacía...")
            secrets["redpill"]["api_key"] = ""
            with open(secrets_path, 'w') as f:
                for section, values in secrets.items():
                    f.write(f"[{section}]\n")
                    for key, value in values.items():
                        f.write(f'{key} = "{value}"\n')
                    f.write("\n")
            print("✅ api_key agregada")
        
        # Verificar permisos del archivo
        import stat
        st = os.stat(secrets_path)
        perms = oct(st.st_mode)[-3:]
        print(f"\nPermisos del archivo: {perms}")
        if not os.access(secrets_path, os.W_OK):
            print("❌ El archivo no tiene permisos de escritura")
        else:
            print("✅ El archivo tiene permisos de escritura")
        
    except Exception as e:
        print(f"\n❌ Error al leer el archivo: {str(e)}")
        print("Contenido actual del archivo:")
        with open(secrets_path, 'r') as f:
            print(f.read())
    with open(secrets_path, 'r') as f:
        content = f.read()
        print("\nPrimeras líneas del archivo:")
        print("\n".join(content.split('\n')[:5]))
        
        if content.strip().startswith('//'):
            print("\n❌ ERROR: El archivo comienza con comentarios estilo JavaScript (//)")
            print("   Streamlit espera comentarios estilo TOML (#)")
        elif content.strip().startswith('#'):
            print("\n✅ El formato de comentarios es correcto (usa #)")
    
    # Cargar archivo manualmente
    try:
        secrets = parse_toml_manually(secrets_path)
        print("\n✅ Archivo TOML analizado correctamente")
        
        # Verificar sección redpill
        if 'redpill' in secrets:
            print("✅ Sección 'redpill' encontrada")
            
            # Verificar api_key
            if 'api_key' in secrets['redpill']:
                api_key = secrets['redpill']['api_key']
                masked_key = f"{api_key[:5]}...{api_key[-5:]}" if len(api_key) > 10 else api_key
                print(f"✅ Clave API encontrada: {masked_key}")
            else:
                print("❌ No se encontró 'api_key' en la sección 'redpill'")
            
            # Verificar api_url
            if 'api_url' in secrets['redpill']:
                print(f"✅ URL API encontrada: {secrets['redpill']['api_url']}")
            else:
                print("❌ No se encontró 'api_url' en la sección 'redpill'")
        else:
            print("❌ No se encontró la sección 'redpill' en el archivo")
            
        print("\nContenido completo parseado:")
        for section, values in secrets.items():
            print(f"[{section}]")
            for key, value in values.items():
                if key == "api_key":
                    masked = f"{value[:5]}...{value[-5:]}" if len(value) > 10 else value
                    print(f"  {key} = {masked}")
                else:
                    print(f"  {key} = {value}")
    except Exception as e:
        print(f"\n❌ Error al analizar el archivo TOML: {e}")
        print("   Esto sugiere que el formato del archivo puede ser incorrecto")

if __name__ == "__main__":
    main()
