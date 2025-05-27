import requests
import urllib3
import json
import ssl
from urllib.parse import urljoin

# Suprimir advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_session():
    """
    Crea una sesión de requests simplificada con SSL permisivo
    """
    session = requests.Session()
    
    # Desactivar verificación SSL
    session.verify = False
    
    # Configurar el User-Agent para simular un navegador moderno
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    return session

def test_endpoints(api_key):
    """
    Prueba diferentes endpoints para encontrar el correcto
    """
    base_url = "https://api.redpill.ai"
    endpoints = [
        "/v1/models",
        "/v1/completions",
        "/v1/chat/completions",
        "/completions",
        "/chat/completions",
        "/v1/completion",
        "/v1/chat/completion",
        "/api/v1/completions",
        "/api/v1/chat/completions"
    ]
    
    session = create_session()
    results = {}
    
    print("Probando endpoint /v1/models para listar modelos disponibles:")
    try:
        models_url = urljoin(base_url, "/v1/models")
        models_response = session.get(
            models_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0
        )
        print(f"  Status code: {models_response.status_code}")
        if models_response.status_code == 200:
            models_data = models_response.json()
            print("  Modelos disponibles:")
            for model in models_data.get("data", []):
                print(f"    - {model.get('id')}")
        else:
            print(f"  Error: {models_response.text}")
    except Exception as e:
        print(f"  Error al consultar modelos: {str(e)}")
    
    print("\nProbando diferentes endpoints para completions:")
    for endpoint in endpoints:
        full_url = urljoin(base_url, endpoint)
        
        # Payload para /v1/completions
        completion_payload = {
            "model": "mistralai/ministral-8b",
            "prompt": "Hola, ¿cómo estás?",
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        # Payload para /v1/chat/completions
        chat_payload = {
            "model": "mistralai/ministral-8b",
            "messages": [{"role": "user", "content": "Hola, ¿cómo estás?"}],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        # Determinar qué payload usar basado en el endpoint
        payload = chat_payload if "chat" in endpoint else completion_payload
        
        try:
            print(f"Probando {full_url}...")
            response = session.post(
                full_url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=10.0
            )
            
            status = response.status_code
            results[endpoint] = {
                "status": status,
                "success": status == 200
            }
            
            print(f"  Status code: {status}")
            if status == 200:
                print("  ✓ ÉXITO - El endpoint funciona correctamente")
                try:
                    resp_data = response.json()
                    print(f"  Respuesta: {json.dumps(resp_data, indent=2, ensure_ascii=False)[:150]}...")
                except:
                    print(f"  Respuesta no es JSON válido: {response.text[:150]}...")
            else:
                print(f"  ✗ ERROR - {response.text[:150]}")
        except Exception as e:
            results[endpoint] = {
                "status": "error",
                "error": str(e)
            }
            print(f"  ✗ EXCEPCIÓN: {str(e)}")
    
    print("\nResumen de resultados:")
    success_endpoints = []
    for endpoint, result in results.items():
        status = "✓" if result.get("success", False) else "✗"
        print(f"{status} {endpoint}: {result.get('status')}")
        if result.get("success", False):
            success_endpoints.append(endpoint)
    
    if success_endpoints:
        print("\n🎉 Endpoints funcionando correctamente:")
        for endpoint in success_endpoints:
            print(f"- {endpoint}")
        print(f"\nRecomendación: Usar {success_endpoints[0]}")
    else:
        print("\n❌ No se encontró ningún endpoint funcionando correctamente.")
        print("Recomendación: Verificar la documentación de la API o contactar al soporte.")
    
    return results

if __name__ == "__main__":
    # Reemplazar con tu API key real
    api_key = "sk-xYBWXr1epqP3Uq1A05qUql9tAyBsJE5F8PL5L66gBaE328VG"
    test_endpoints(api_key)
