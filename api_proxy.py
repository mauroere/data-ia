import requests
import json
import os
import streamlit as st
import urllib3
import ssl
from urllib3.poolmanager import PoolManager
from urllib3.util import ssl_
from requests.adapters import HTTPAdapter

# Suprimir advertencias SSL para evitar mensajes molestos en la consola
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TLSAdapter(HTTPAdapter):
    """Adaptador HTTP que fuerza TLS 1.2 y maneja errores comunes de SSL"""
    def init_poolmanager(self, connections, maxsize, block=False):
        """Inicializa un PoolManager con TLS 1.2 y configuración segura"""
        # Crear contexto SSL que ignora problemas de verificación de nombre de host
        ctx = ssl_.create_urllib3_context(ssl.PROTOCOL_TLS)
        # Desactivar la verificación del nombre del host
        ctx.check_hostname = False
        # No verificar certificados
        ctx.verify_mode = ssl.CERT_NONE
        # Configurar para ignorar errores específicos de SSL
        ctx.options |= ssl.OP_NO_SSLv2
        ctx.options |= ssl.OP_NO_SSLv3
        ctx.options |= ssl.OP_NO_TLSv1
        ctx.options |= ssl.OP_NO_TLSv1_1
        
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=ctx,
            server_hostname='api.redpill.io'  # Forzar el nombre del servidor
        )

def create_session():
    """Crea una sesión de requests con configuración SSL personalizada"""
    session = requests.Session()
    # Usar el adaptador TLS personalizado para todas las conexiones HTTPS
    adapter = TLSAdapter()
    session.mount("https://", adapter)
    # Desactivar verificación SSL
    session.verify = False
    # Configurar el User-Agent
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    })
    return session

def make_api_request_proxy(api_key, api_url, messages, model="redpill-1", temperature=0.3):
    """
    Realiza una petición a la API usando una configuración SSL personalizada
    
    Args:
        api_key: Clave API
        api_url: URL del endpoint de la API
        messages: Lista de mensajes para la API
        model: Modelo a usar
        temperature: Temperatura para la generación
        
    Returns:
        dict: Respuesta JSON de la API
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 1000
    }
    
    # Suprimir advertencias SSL
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    try:
        # Crear sesión con configuración personalizada
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
        
        # Devolver JSON
        return response.json()
    
    except requests.exceptions.SSLError as e:
        # Manejar específicamente errores SSL
        error_ssl = str(e)
        if "TLSV1_UNRECOGNIZED_NAME" in error_ssl:
            raise Exception(f"Error de SSL con nombre de host no reconocido. Detalles: {error_ssl}")
        elif "CERTIFICATE_VERIFY_FAILED" in error_ssl:
            raise Exception(f"Error de verificación de certificado SSL. Detalles: {error_ssl}")
        else:
            raise Exception(f"Error de SSL no especificado: {error_ssl}")
    except requests.exceptions.ConnectionError as e:
        # Manejar errores de conexión
        raise Exception(f"Error de conexión a {api_url}: {str(e)}")
    except requests.exceptions.Timeout as e:
        # Manejar errores de timeout
        raise Exception(f"Tiempo de espera agotado para {api_url}: {str(e)}")
    except requests.exceptions.HTTPError as e:
        # Manejar errores HTTP
        if hasattr(e.response, 'status_code'):
            if e.response.status_code == 429:
                raise Exception("Se ha excedido el límite de uso de la API. Verifica tu saldo o plan.")
            elif e.response.status_code == 401:
                raise Exception("API key inválida o expirada. Verifica tus credenciales.")
            else:
                raise Exception(f"Error HTTP {e.response.status_code}: {str(e)}")
        else:
            raise Exception(f"Error HTTP no especificado: {str(e)}")
    except Exception as e:
        # Cualquier otro error
        raise Exception(f"Error en la petición: {str(e)}")
