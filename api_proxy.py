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
    """Adaptador HTTP que fuerza TLS 1.2"""
    def init_poolmanager(self, connections, maxsize, block=False):
        """Inicializa un PoolManager con TLS 1.2"""
        ctx = ssl_.create_urllib3_context(ssl.PROTOCOL_TLSv1_2)
        # Desactivar la verificación del nombre del host
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=ctx
        )

def create_session():
    """Crea una sesión de requests con configuración SSL personalizada"""
    session = requests.Session()
    # Usar el adaptador TLS personalizado para todas las conexiones HTTPS
    adapter = TLSAdapter()
    session.mount("https://", adapter)
    # Desactivar verificación SSL
    session.verify = False
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }
    
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
    
    except requests.RequestException as e:
        error_message = str(e)
        raise Exception(f"Error en la petición: {error_message}")
