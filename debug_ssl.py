import streamlit as st
import requests
import ssl
import socket
import OpenSSL.crypto
import certifi
import urllib3
import os
import platform
import sys
import subprocess
import json
from datetime import datetime

# Desactivar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_ssl_info():
    """Obtiene información sobre la configuración SSL/TLS del sistema"""
    info = {
        "openssl_version": ssl.OPENSSL_VERSION,
        "default_ciphers": ssl.get_default_verify_paths(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "certifi_version": certifi.__version__,
        "certifi_path": certifi.where()
    }
    return info

def check_host_ssl(hostname, port=443):
    """Verifica la conexión SSL con un host específico"""
    try:
        # Crear contexto SSL
        context = ssl.create_default_context()
        
        # Intentar conexión
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Extraer información del certificado
                issuer = dict(x[0] for x in cert['issuer'])
                subject = dict(x[0] for x in cert['subject'])
                
                return {
                    "success": True,
                    "cipher": ssock.cipher(),
                    "version": ssock.version(),
                    "issuer": issuer,
                    "subject": subject,
                    "expiry": cert['notAfter'],
                    "raw_cert": cert
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

def test_api_endpoint(url, api_key=None):
    """Prueba un endpoint de API con diferentes niveles de verificación SSL"""
    results = []
    
    # Opción 1: Verificación SSL estándar
    try:
        headers = {"User-Agent": "SSL-Test/1.0"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            
        response = requests.get(
            url,
            headers=headers,
            timeout=10.0
        )
        
        results.append({
            "method": "Verificación SSL estándar",
            "success": response.status_code < 400,
            "status_code": response.status_code,
            "elapsed_ms": response.elapsed.total_seconds() * 1000
        })
    except Exception as e:
        results.append({
            "method": "Verificación SSL estándar",
            "success": False,
            "error": str(e)
        })
    
    # Opción 2: Desactivar verificación SSL
    try:
        response = requests.get(
            url,
            headers=headers,
            verify=False,
            timeout=10.0
        )
        
        results.append({
            "method": "Verificación SSL desactivada",
            "success": response.status_code < 400,
            "status_code": response.status_code,
            "elapsed_ms": response.elapsed.total_seconds() * 1000
        })
    except Exception as e:
        results.append({
            "method": "Verificación SSL desactivada",
            "success": False,
            "error": str(e)
        })
    
    # Opción 3: Usar certificados de certifi
    try:
        response = requests.get(
            url,
            headers=headers,
            verify=certifi.where(),
            timeout=10.0
        )
        
        results.append({
            "method": "Certificados de certifi",
            "success": response.status_code < 400,
            "status_code": response.status_code,
            "elapsed_ms": response.elapsed.total_seconds() * 1000
        })
    except Exception as e:
        results.append({
            "method": "Certificados de certifi",
            "success": False,
            "error": str(e)
        })
        
    return results

def debug_ssl():
    st.title("Diagnóstico SSL/TLS")
    
    # Información general del sistema
    st.subheader("Información del sistema")
    ssl_info = get_ssl_info()
    for key, value in ssl_info.items():
        st.write(f"**{key}:** {value}")
    
    # Probar conexión a hosts específicos
    st.subheader("Probar conexión SSL")
    
    col1, col2 = st.columns(2)
    with col1:
        hostname = st.text_input("Hostname a probar:", value="api.redpill.ai")
    with col2:
        port = st.number_input("Puerto:", value=443, min_value=1, max_value=65535)
    
    if st.button("Probar conexión SSL"):
        with st.spinner(f"Probando conexión SSL a {hostname}:{port}..."):
            result = check_host_ssl(hostname, port)
            
            if result["success"]:
                st.success(f"✓ Conexión SSL exitosa a {hostname}:{port}")
                st.write(f"**Cifrado:** {result['cipher']}")
                st.write(f"**Versión TLS:** {result['version']}")
                st.write(f"**Expedido por:** {result['issuer'].get('organizationName', result['issuer'])}")
                st.write(f"**Expedido para:** {result['subject'].get('commonName', result['subject'])}")
                st.write(f"**Expira:** {result['expiry']}")
            else:
                st.error(f"✗ Error de conexión SSL a {hostname}:{port}")
                st.write(f"**Error:** {result['error']}")
                st.write(f"**Tipo de error:** {result['error_type']}")
    
    # Probar endpoints de API
    st.subheader("Probar endpoints API")
    
    api_url = st.text_input("URL del endpoint:", value="https://api.redpill.ai/v1/models")
    api_key = st.text_input("API Key (opcional):", type="password")
    
    if st.button("Probar endpoint API"):
        with st.spinner(f"Probando endpoint {api_url}..."):
            results = test_api_endpoint(api_url, api_key)
            
            for result in results:
                if result["success"]:
                    st.success(f"✓ {result['method']}: Exitoso (Status: {result['status_code']}, Tiempo: {result['elapsed_ms']:.2f}ms)")
                else:
                    st.error(f"✗ {result['method']}: Fallido ({result.get('error', 'Error desconocido')})")
    
    # Prueba específica para la API de Redpill
    st.subheader("Prueba específica para Redpill.ai")
    
    redpill_api_key = st.text_input("API Key de Redpill:", type="password", key="redpill_key")
    
    endpoints = [
        "https://api.redpill.ai/v1/models",
        "https://api.redpill.ai/v1/chat/completions",
        "https://api.redpill.ai/v1/completions",
        "https://api.redpill.ai/api/v1/chat/completions"
    ]
    
    selected_endpoint = st.selectbox("Endpoint a probar:", endpoints)
    
    if st.button("Probar Redpill API"):
        with st.spinner(f"Probando {selected_endpoint}..."):
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {redpill_api_key}"
            }
            
            if "chat/completions" in selected_endpoint:
                payload = {
                    "model": "mistralai/ministral-8b",
                    "messages": [{"role": "user", "content": "Hola, ¿cómo estás?"}],
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            else:
                payload = {
                    "model": "mistralai/ministral-8b",
                    "prompt": "Hola, ¿cómo estás?",
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            
            try:
                response = requests.post(
                    selected_endpoint,
                    headers=headers,
                    json=payload,
                    verify=False,
                    timeout=15.0
                )
                
                st.write(f"**Status code:** {response.status_code}")
                
                if response.status_code == 200:
                    st.success(f"✓ Solicitud exitosa")
                    st.json(response.json())
                else:
                    st.error(f"✗ Error: {response.status_code}")
                    st.code(response.text)
                    
            except Exception as e:
                st.error(f"✗ Excepción: {str(e)}")

if __name__ == "__main__":
    debug_ssl()
