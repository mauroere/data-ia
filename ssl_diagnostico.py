import streamlit as st
import ssl
import socket
import requests
import urllib3
from urllib.parse import urlparse

def get_ssl_info():
    """Obtiene información sobre la configuración SSL del sistema"""
    ssl_info = {
        "OpenSSL Version": ssl.OPENSSL_VERSION,
        "Default SSL Protocol": ssl._DEFAULT_CIPHERS,
        "SSL Protocols Available": {
            "TLS": hasattr(ssl, "PROTOCOL_TLS"),
            "TLS 1.0": hasattr(ssl, "PROTOCOL_TLSv1"),
            "TLS 1.1": hasattr(ssl, "PROTOCOL_TLSv1_1"),
            "TLS 1.2": hasattr(ssl, "PROTOCOL_TLSv1_2"),
            "TLS 1.3": hasattr(ssl, "PROTOCOL_TLSv1_3"),
        }
    }
    return ssl_info

def test_ip_resolution(hostname):
    """Prueba la resolución de DNS para un nombre de host"""
    try:
        ip = socket.gethostbyname(hostname)
        return {"success": True, "ip": ip}
    except socket.gaierror as e:
        return {"success": False, "error": str(e)}

def test_socket_connection(hostname, port=443):
    """Prueba una conexión TCP directa al servidor"""
    try:
        sock = socket.create_connection((hostname, port), timeout=10)
        sock.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_ssl_connection(hostname, port=443):
    """Prueba una conexión SSL directa al servidor"""
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert(binary_form=True)
                return {"success": True, "has_cert": cert is not None}
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_requests_connection(url):
    """Prueba una conexión HTTP básica usando requests"""
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        # Intento 1: Normal con verificación desactivada
        response = requests.get(url, verify=False, timeout=10)
        return {
            "success": True, 
            "status_code": response.status_code,
            "elapsed_ms": response.elapsed.total_seconds() * 1000
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def run_ssl_diagnostics(url):
    """Ejecuta una serie de diagnósticos para problemas SSL"""
    parsed = urlparse(url)
    hostname = parsed.netloc.split(':')[0]
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    
    results = {
        "ssl_info": get_ssl_info(),
        "dns_resolution": test_ip_resolution(hostname),
        "tcp_connection": test_socket_connection(hostname, port),
        "ssl_connection": test_ssl_connection(hostname, port),
        "http_request": test_requests_connection(url)
    }
    
    return results

def display_ssl_diagnostics():
    """Muestra la interfaz de diagnóstico SSL"""
    st.title("🔒 Diagnóstico Avanzado SSL/TLS")
    
    url = st.text_input(
        "URL para diagnóstico", 
        value="https://api.redpill.ai/v1/models",
        help="URL completa incluyendo https://"
    )
    
    if st.button("Ejecutar diagnóstico SSL"):
        if not url:
            st.error("Por favor ingresa una URL válida")
            return
            
        with st.spinner("Ejecutando diagnósticos..."):
            results = run_ssl_diagnostics(url)
            
            # Mostrar información general SSL
            st.subheader("Información SSL del sistema")
            st.json(results["ssl_info"])
            
            # Mostrar resultados de DNS
            st.subheader("Resolución DNS")
            if results["dns_resolution"]["success"]:
                st.success(f"✅ Resolución exitosa: {results['dns_resolution']['ip']}")
            else:
                st.error(f"❌ Error de resolución DNS: {results['dns_resolution']['error']}")
            
            # Mostrar resultados de conexión TCP
            st.subheader("Conexión TCP")
            if results["tcp_connection"]["success"]:
                st.success("✅ Conexión TCP exitosa")
            else:
                st.error(f"❌ Error de conexión TCP: {results['tcp_connection']['error']}")
            
            # Mostrar resultados de conexión SSL
            st.subheader("Conexión SSL")
            if results["ssl_connection"]["success"]:
                st.success("✅ Conexión SSL exitosa")
            else:
                st.error(f"❌ Error de conexión SSL: {results['ssl_connection']['error']}")
                
                # Recomendaciones específicas para errores SSL
                error_msg = results["ssl_connection"]["error"]
                if "TLSV1_UNRECOGNIZED_NAME" in error_msg:
                    st.info("""
                    **Solución recomendada**: El error TLSV1_UNRECOGNIZED_NAME indica que el servidor no reconoce el nombre de host.
                    
                    1. Verifica que el nombre de host sea correcto
                    2. Prueba conectándote directamente a la IP: usa la dirección IP en lugar del nombre de dominio
                    3. Verifica que tu sistema tenga los certificados SSL actualizados
                    4. Intenta usar un proxy o VPN
                    """)
            
            # Mostrar resultados de la solicitud HTTP
            st.subheader("Solicitud HTTP")
            if results["http_request"]["success"]:
                st.success(f"✅ Solicitud HTTP exitosa - Código: {results['http_request']['status_code']}")
                st.write(f"Tiempo de respuesta: {results['http_request']['elapsed_ms']:.2f} ms")
            else:
                st.error(f"❌ Error en solicitud HTTP: {results['http_request']['error']}")
        
        # Mostrar soluciones generales
        st.subheader("Soluciones generales para problemas SSL/TLS")
        st.markdown("""
        1. **Actualizar certificados del sistema**: Asegúrate de tener los certificados SSL del sistema actualizados
        2. **Verificar fecha y hora**: La fecha y hora incorrectas pueden causar problemas con la validación de certificados
        3. **Probar con otra red**: Algunas redes corporativas o públicas pueden bloquear o interferir con conexiones SSL
        4. **Usar un proxy o VPN**: Puede ayudar a eludir problemas de red intermedios
        5. **Actualizar bibliotecas SSL**: Asegúrate de tener versiones actualizadas de OpenSSL y otras bibliotecas SSL
        6. **Verificar firewall**: Asegúrate de que no hay un firewall bloqueando la conexión
        """)
        
        # Ofrecer conectarse con la IP directamente
        if results["dns_resolution"]["success"]:
            ip = results["dns_resolution"]["ip"]
            parsed = urlparse(url)
            ip_url = url.replace(parsed.netloc.split(':')[0], ip)
            
            st.subheader("Probar con la dirección IP directamente")
            st.write(f"URL con IP: `{ip_url}`")
            if st.button("Probar conexión con IP directa"):
                with st.spinner("Probando conexión directa con IP..."):
                    direct_result = test_requests_connection(ip_url)
                    if direct_result["success"]:
                        st.success(f"✅ Conexión exitosa usando IP directa - Código: {direct_result['status_code']}")
                    else:
                        st.error(f"❌ Error usando IP directa: {direct_result['error']}")

if __name__ == "__main__":
    st.set_page_config(page_title="Diagnóstico SSL/TLS", layout="wide")
    display_ssl_diagnostics()
