"""
Script para verificar que las importaciones funcionan correctamente.
"""
print("Probando importaciones...")

try:
    # Importar desde utils.py
    from utils import read_flexible_file, are_similar, normalize_column_names, get_api_key, get_api_url
    print("✓ Importaciones de utils.py funcionan correctamente")
except Exception as e:
    print(f"✗ Error al importar desde utils.py: {str(e)}")

try:
    # Importar desde api_proxy.py
    from api_proxy import make_api_request_proxy
    print("✓ Importaciones de api_proxy.py funcionan correctamente")
except Exception as e:
    print(f"✗ Error al importar desde api_proxy.py: {str(e)}")

print("Pruebas de importación completadas.")
