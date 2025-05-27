import http.client
import json
import ssl
import sys
import urllib.parse

def test_endpoints(api_key):
    """
    Prueba diferentes endpoints para encontrar el correcto usando http.client
    que viene incorporado en Python.
    """
    base_host = "api.redpill.ai"
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
    
    # Crear contexto SSL que ignora la verificación de certificado
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    # Probar el endpoint de modelos primero
    print("Probando endpoint /v1/models para listar modelos disponibles:")
    try:
        conn = http.client.HTTPSConnection(base_host, context=context)
        conn.request("GET", "/v1/models", headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        response = conn.getresponse()
        status = response.status
        data = response.read().decode('utf-8')
        
        print(f"  Status code: {status}")
        if status == 200:
            models_data = json.loads(data)
            print("  Modelos disponibles:")
            for model in models_data.get("data", []):
                print(f"    - {model.get('id')}")
        else:
            print(f"  Error: {data}")
    except Exception as e:
        print(f"  Error al consultar modelos: {str(e)}")
    finally:
        conn.close()
    
    # Probar diferentes endpoints para completions
    print("\nProbando diferentes endpoints para completions:")
    results = {}
    
    for endpoint in endpoints:
        # Payload para /v1/completions
        completion_payload = json.dumps({
            "model": "mistralai/ministral-8b",
            "prompt": "Hola, ¿cómo estás?",
            "max_tokens": 100,
            "temperature": 0.7
        })
        
        # Payload para /v1/chat/completions
        chat_payload = json.dumps({
            "model": "mistralai/ministral-8b",
            "messages": [{"role": "user", "content": "Hola, ¿cómo estás?"}],
            "max_tokens": 100,
            "temperature": 0.7
        })
        
        # Determinar qué payload usar basado en el endpoint
        payload = chat_payload if "chat" in endpoint else completion_payload
        
        try:
            print(f"Probando {endpoint}...")
            conn = http.client.HTTPSConnection(base_host, context=context)
            conn.request("POST", endpoint, body=payload, headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            response = conn.getresponse()
            status = response.status
            data = response.read().decode('utf-8')
            
            results[endpoint] = {
                "status": status,
                "success": status == 200
            }
            
            print(f"  Status code: {status}")
            if status == 200:
                print("  ✓ ÉXITO - El endpoint funciona correctamente")
                try:
                    resp_data = json.loads(data)
                    print(f"  Respuesta: {json.dumps(resp_data, indent=2, ensure_ascii=False)[:150]}...")
                except:
                    print(f"  Respuesta no es JSON válido: {data[:150]}...")
            else:
                print(f"  ✗ ERROR - {data[:150]}")
        except Exception as e:
            results[endpoint] = {
                "status": "error",
                "error": str(e)
            }
            print(f"  ✗ EXCEPCIÓN: {str(e)}")
        finally:
            conn.close()
    
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
        
        # Mostrar cómo configurar la aplicación
        print("\nPara configurar la aplicación, actualiza estos archivos:")
        print("1. .streamlit/secrets.toml:")
        print(f"""   [redpill]
   api_key = "tu-api-key"
   api_url = "https://api.redpill.ai{success_endpoints[0]}"
   """)
        
        print("2. utils.py (función get_api_url):")
        print("""   if service == "redpill":
       return "https://api.redpill.ai""" + success_endpoints[0] + """\"
   """)
    else:
        print("\n❌ No se encontró ningún endpoint funcionando correctamente.")
        print("Recomendación: Verificar la documentación de la API o contactar al soporte.")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = "sk-xYBWXr1epqP3Uq1A05qUql9tAyBsJE5F8PL5L66gBaE328VG"
    
    print("Herramienta de diagnóstico de API de Redpill")
    print("===========================================")
    print(f"Usando API key: {api_key[:8]}...{api_key[-5:]}")
    test_endpoints(api_key)
