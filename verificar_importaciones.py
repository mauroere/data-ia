#!/usr/bin/env python
"""
Script de prueba para verificar que los módulos se importan correctamente.
"""

print("Verificando importaciones...")

try:
    from utils import get_api_url, get_api_key
    print("✓ utils.py importado correctamente")
except Exception as e:
    print(f"✗ Error al importar utils.py: {str(e)}")

try:
    from api_proxy import make_api_request_proxy
    print("✓ api_proxy.py importado correctamente")
except Exception as e:
    print(f"✗ Error al importar api_proxy.py: {str(e)}")

try:
    from api_diagnostico import test_api_connection
    print("✓ api_diagnostico.py importado correctamente")
except Exception as e:
    print(f"✗ Error al importar api_diagnostico.py: {str(e)}")

print("\nTodos los módulos verificados. Si no hay errores, la aplicación debería funcionar correctamente.")
