import requests
import urllib3
import ssl
import streamlit as st
from api_proxy import create_session

def test_api_connection(api_url, api_key):
    """
    Prueba la conexión a la API y devuelve información de diagnóstico
    
    Args:
        api_url: URL de la API a probar
        api_key: API key para autenticación
        
    Returns:
        dict: Resultados del diagnóstico
    """
    # Suprimir advertencias SSL
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Información sobre SSL/TLS disponible
    ssl_info = {
        "openssl_version": ssl.OPENSSL_VERSION,
        "ssl_protocol_versions": {
            "TLS 1.0": ssl.PROTOCOL_TLSv1,
            "TLS 1.2": ssl.PROTOCOL_TLSv1_2,
            "TLS": ssl.PROTOCOL_TLS,
        }
    }
    
    # Probar conexión básica
    ping_result = None
    try:
        # Crear sesión con configuración personalizada
        session = create_session()
        
        # Intentar una petición simple
        response = session.get(
            api_url.split("/v1")[0] + "/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0
        )
        
        ping_result = {
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "elapsed_ms": response.elapsed.total_seconds() * 1000,
            "content_preview": str(response.content)[:100] if response.content else None
        }
    except Exception as e:
        ping_result = {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
    
    return {
        "ssl_info": ssl_info,
        "ping_result": ping_result
    }

def display_connection_test():
    """Muestra una interfaz para probar la conexión API"""
    st.title("🔍 Diagnóstico de Conexión API")
    
    # Obtener valores de API
    api_url = st.text_input(        "URL de API", 
        value="https://api.redpill.ai/v1/chat/completions",
        help="URL completa del endpoint de la API"
    )
    
    api_key = st.text_input(
        "API Key",
        value="",
        type="password",
        help="Clave de API para autenticación"
    )
    
    if st.button("Probar Conexión"):
        if not api_url or not api_key:
            st.error("Por favor ingresa la URL y API Key")
            return
            
        with st.spinner("Probando conexión..."):
            result = test_api_connection(api_url, api_key)
            
            # Mostrar resultados
            st.subheader("Información de SSL/TLS")
            st.json(result["ssl_info"])
            
            st.subheader("Resultado de Ping")
            if result["ping_result"]["success"]:
                st.success(f"✅ Conexión exitosa - Código: {result['ping_result']['status_code']}")
                st.write(f"Tiempo de respuesta: {result['ping_result']['elapsed_ms']:.2f} ms")
                if result["ping_result"].get("content_preview"):
                    st.text("Vista previa de respuesta:")
                    st.code(result["ping_result"]["content_preview"])
            else:
                st.error(f"❌ Error de conexión: {result['ping_result']['error']}")
                st.info("Recomendaciones:")
                
                error_msg = result["ping_result"]["error"]
                if "TLSV1_UNRECOGNIZED_NAME" in error_msg:
                    st.write("""
                    1. Verifica que la URL sea correcta
                    2. Prueba con otro navegador o conexión de red
                    3. Verifica si hay restricciones de firewall o proxy
                    """)
                elif "CERTIFICATE_VERIFY_FAILED" in error_msg:
                    st.write("""
                    1. Verifica que tu sistema tenga certificados SSL actualizados
                    2. Verifica la fecha y hora de tu sistema
                    3. Considera usar una VPN si estás en una red con restricciones
                    """)
                elif "SSLError" in error_msg:
                    st.write("""
                    1. Prueba con una versión más reciente de Python y OpenSSL
                    2. Verifica que tu red permita conexiones SSL/TLS seguras
                    3. Prueba conectándote a través de otra red
                    """)
                elif "ConnectionError" in error_msg:
                    st.write("""
                    1. Verifica tu conexión a Internet
                    2. Prueba con otra red (WiFi, datos móviles, etc.)
                    3. Verifica si el servidor está en mantenimiento
                    """)
                else:
                    st.write("""
                    1. Verifica que la API Key sea correcta
                    2. Revisa si el servicio está disponible
                    3. Contacta al soporte técnico con el mensaje de error
                    """)
    
    # Mostrar consejos
    with st.expander("Consejos de depuración"):
        st.markdown("""
        ### Soluciones comunes para problemas de SSL/TLS:
        
        1. **Error de nombre no reconocido (TLSV1_UNRECOGNIZED_NAME)**
           - Asegúrate de que la URL sea correcta y esté bien escrita
           - Prueba acceder al sitio web desde un navegador para verificar si es accesible
           - Considera usar un proxy o VPN
        
        2. **Error de verificación de certificado**
           - Verifica que tu sistema operativo tenga certificados SSL actualizados
           - Actualiza las bibliotecas de SSL/Python en tu sistema
        
        3. **Errores de conexión**
           - Verifica tu firewall o proxy
           - Prueba con otra conexión de red
           - Verifica si el servicio está en funcionamiento
        """)

if __name__ == "__main__":
    st.set_page_config(page_title="Diagnóstico de API", layout="wide")
    display_connection_test()
