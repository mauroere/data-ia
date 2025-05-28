import toml
import os
import sys

def main():
    print("=== DIAGNÓSTICO DE CARGA DE SECRETS PARA REDPILL API ===")
    print(f"Python versión: {sys.version}")
    print(f"Directorio actual: {os.getcwd()}")
    
    # Ruta al archivo de secretos
    secrets_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
    
    print(f"\nVerificando archivo: {secrets_path}")
    if not os.path.exists(secrets_path):
        print(f"❌ El archivo no existe en la ruta: {secrets_path}")
        return
    
    print("✅ El archivo existe")
    
    # Leer el contenido del archivo para verificar formato
    with open(secrets_path, 'r') as f:
        content = f.read()
        print("\nPrimeras líneas del archivo:")
        print("\n".join(content.split('\n')[:5]))
        
        if content.strip().startswith('//'):
            print("\n❌ ERROR: El archivo comienza con comentarios estilo JavaScript (//)")
            print("   Streamlit espera comentarios estilo TOML (#)")
        elif content.strip().startswith('#'):
            print("\n✅ El formato de comentarios es correcto (usa #)")
    
    # Cargar archivo con biblioteca toml
    try:
        secrets = toml.load(secrets_path)
        print("\n✅ Archivo TOML cargado correctamente")
        
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
    except Exception as e:
        print(f"\n❌ Error al cargar el archivo TOML: {e}")
        print("   Esto sugiere que el formato del archivo puede ser incorrecto")

if __name__ == "__main__":
    main()
