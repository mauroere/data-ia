import http.client
import json
import ssl
import sys
import urllib.parse

def test_chat_completions(api_key):
    """
    Prueba el endpoint /v1/chat/completions con el modelo mistralai/ministral-8b
    """
    print("Herramienta de prueba de API de Redpill - /v1/chat/completions")
    print("==========================================================")
    print(f"Usando API key: {api_key[:8]}...{api_key[-5:]}")
    
    host = "api.redpill.ai"
    endpoint = "/v1/chat/completions"
    
    # Crear contexto SSL que ignora la verificación de certificado
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    payload = json.dumps({
        "model": "mistralai/ministral-8b",
        "messages": [{"role": "user", "content": "Hola, ¿cómo estás? Por favor, responde en español."}],
        "temperature": 0.7,
        "max_tokens": 500
    })
    
    try:
        conn = http.client.HTTPSConnection(host, context=context)
        conn.request("POST", endpoint, body=payload, headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        response = conn.getresponse()
        status = response.status
        data = response.read().decode('utf-8')
        
        print(f"\nStatus code: {status}")
        if status == 200:
            print("✓ ÉXITO - La API funciona correctamente")
            resp_data = json.loads(data)
            
            # Extraer y mostrar la respuesta del modelo
            if "choices" in resp_data and len(resp_data["choices"]) > 0:
                message = resp_data["choices"][0].get("message", {})
                content = message.get("content", "")
                print("\nRespuesta del modelo:")
                print(f"{content}")
                
                print("\nDetalles técnicos:")
                model_used = resp_data.get("model", "")
                tokens_used = resp_data.get("usage", {}).get("total_tokens", 0)
                print(f"- Modelo: {model_used}")
                print(f"- Tokens utilizados: {tokens_used}")
            else:
                print("\nNo se pudo extraer la respuesta del modelo.")
                print(f"Respuesta completa: {json.dumps(resp_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"✗ ERROR - {data}")
            
            # Sugerencias específicas basadas en el código de error
            if status == 401:
                print("\nSugerencia: La API key parece ser inválida o ha expirado.")
                print("Verifica tu API key o contacta con el soporte de Redpill.")
            elif status == 404:
                print("\nSugerencia: El endpoint no existe o ha cambiado.")
                print("Verifica la documentación de la API para el endpoint correcto.")
            elif status == 429:
                print("\nSugerencia: Has excedido el límite de solicitudes.")
                print("Espera un tiempo o verifica tu plan de suscripción.")
            
    except Exception as e:
        print(f"✗ EXCEPCIÓN: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = "sk-xYBWXr1epqP3Uq1A05qUql9tAyBsJE5F8PL5L66gBaE328VG"
    
    test_chat_completions(api_key)
