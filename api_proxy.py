import requests
import json
import os
import streamlit as st
import urllib3
import ssl
import socket
from urllib3.poolmanager import PoolManager
from requests.adapters import HTTPAdapter

# Suprimir advertencias SSL para evitar mensajes molestos en la consola
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

def resolve_ip(hostname):
    """Resuelve la IP de un nombre de host"""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        # Si no se puede resolver, devolver el hostname original
        return hostname

def make_api_request_proxy(api_key, api_url, messages, model="mistralai/ministral-8b", temperature=0.3, use_cache=True):
    """
    Realiza una petición a la API usando una configuración SSL personalizada
    
    Args:
        api_key: Clave API
        api_url: URL del endpoint de la API
        messages: Lista de mensajes para la API
        model: Modelo a usar
        temperature: Temperatura para la generación
        use_cache: Si se debe usar caché para evitar peticiones repetidas
        
    Returns:
        dict: Respuesta JSON de la API
    """
    import hashlib
    import os
    from datetime import datetime, timedelta
    
    # Generar una clave de caché basada en los mensajes y parámetros
    if use_cache:
        # Crear directorio de caché si no existe
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Crear hash para usar como nombre de archivo
        cache_key = hashlib.md5(
            json.dumps({
                "messages": messages,
                "model": model,
                "temperature": temperature,
            }, sort_keys=True).encode()
        ).hexdigest()
        
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        
        # Verificar si existe caché válida (menos de 24 horas)
        if os.path.exists(cache_file):
            try:
                file_modified_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
                if datetime.now() - file_modified_time < timedelta(hours=24):
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        print(f"Usando respuesta en caché para: {messages[0]['content'][:50]}...")
                        return json.load(f)
            except Exception as cache_error:
                print(f"Error al leer caché: {str(cache_error)}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 1000
    }
    
    # Suprimir advertencias SSL
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Extraer el hostname del URL para logs
    import urllib.parse
    parsed_url = urllib.parse.urlparse(api_url)
    hostname = parsed_url.netloc.split(':')[0]
    
    # Lista de errores para registro
    all_errors = []
    
    # Método 1: Configuración básica con SSL permisivo
    try:
        # Crear sesión simple
        session = create_session()
        
        # Realizar la petición
        response = session.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30.0
        )
        
        # Verificar respuesta
        response.raise_for_status()
        
        # Guardar en caché si está habilitado
        result = response.json()
        if use_cache:
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            except Exception as cache_write_error:
                print(f"Error al escribir caché: {str(cache_write_error)}")
        
        # Devolver JSON
        return result
    
    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
        all_errors.append(f"Error de SSL/Conexión (método 1): {str(e)}")
        # Continuar con método alternativo
    except Exception as e:
        all_errors.append(f"Error general (método 1): {str(e)}")
        # Si es un error HTTP, manejarlo específicamente
        if isinstance(e, requests.exceptions.HTTPError):
            if hasattr(e.response, 'status_code'):
                if e.response.status_code == 429:
                    raise Exception("Se ha excedido el límite de uso de la API. Verifica tu saldo o plan.")
                elif e.response.status_code == 401:
                    raise Exception("API key inválida o expirada. Verifica tus credenciales.")
                else:
                    raise Exception(f"Error HTTP {e.response.status_code}: {str(e)}")
            else:
                raise Exception(f"Error HTTP no especificado: {str(e)}")
    
    # Método 2: Usar urllib3 directamente
    try:
        # Configurar urllib3 con SSL permisivo
        http = urllib3.PoolManager(
            cert_reqs='CERT_NONE',
            assert_hostname=False
        )
        
        # Realizar la petición
        response = http.request(
            'POST', 
            api_url,
            body=json.dumps(payload).encode('utf-8'),
            headers=headers,
            timeout=30.0
        )
        
        # Verificar respuesta
        if response.status == 200:
            result = json.loads(response.data.decode('utf-8'))
            
            # Guardar en caché
            if use_cache:
                try:
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                except Exception as cache_write_error:
                    print(f"Error al escribir caché: {str(cache_write_error)}")
            
            return result
        else:
            all_errors.append(f"Error HTTP (método 2): {response.status}")
            
    except Exception as urllib3_error:
        all_errors.append(f"Error usando urllib3 (método 2): {str(urllib3_error)}")
    
    # Si todos los métodos fallaron, mostrar errores acumulados
    error_message = "Todos los métodos de conexión fallaron:\n" + "\n".join(all_errors)
    
    # Sugerencias basadas en errores
    if any("TLSV1_UNRECOGNIZED_NAME" in err for err in all_errors):
        error_message += "\n\nRecomendación: Este error sugiere un problema con la verificación del nombre del host SSL. " \
                        "Prueba acceder desde otra red o usando una VPN."
    elif any("CERTIFICATE_VERIFY_FAILED" in err for err in all_errors):
        error_message += "\n\nRecomendación: Verifica que tu sistema tenga certificados SSL actualizados."
    
    raise Exception(error_message)
