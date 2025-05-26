import requests
import json
import os
import streamlit as st
import urllib3
import ssl
import socket
from urllib3.poolmanager import PoolManager
from urllib3.util import ssl_
from requests.adapters import HTTPAdapter
from urllib3.connection import HTTPSConnection
from urllib3.connectionpool import HTTPSConnectionPool

# Suprimir advertencias SSL para evitar mensajes molestos en la consola
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HostNameIgnoringHTTPSConnection(HTTPSConnection):
    """Conexión HTTPS que ignora la verificación del nombre de host"""
    def _new_conn(self):
        sock = socket.create_connection(
            address=(self.host, self.port),
            timeout=self.timeout,
            source_address=self.source_address,
        )
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_NONE
        context.check_hostname = False
        return context.wrap_socket(sock, server_hostname=None)

class HostNameIgnoringHTTPSConnectionPool(HTTPSConnectionPool):
    """Pool de conexiones HTTPS que usa la conexión personalizada"""
    ConnectionCls = HostNameIgnoringHTTPSConnection

class AdvancedTLSAdapter(HTTPAdapter):
    """Adaptador HTTP avanzado que maneja problemas comunes de SSL"""
    def __init__(self, *args, **kwargs):
        self.target_host = kwargs.pop('target_host', None)
        super(AdvancedTLSAdapter, self).__init__(*args, **kwargs)
    
    def init_poolmanager(self, connections, maxsize, block=False):
        """Inicializa un PoolManager con SSL avanzado"""
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
        
        # Usar la conexión personalizada para hosts problemáticos
        if self.target_host:
            pool_kwargs = {
                'num_pools': connections,
                'maxsize': maxsize,
                'block': block,
                'strict': True,
                'ssl_context': ctx,
            }
            self.poolmanager = urllib3.PoolManager(
                **pool_kwargs,
                # Use our custom connection class for specific hosts
                connection_pool_kw={'pool_classes': {
                    'https': HostNameIgnoringHTTPSConnectionPool
                }}
            )
        else:
            self.poolmanager = PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                ssl_context=ctx
            )

def resolve_ip(hostname):
    """Resuelve la IP de un nombre de host"""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        # Si no se puede resolver, devolver el hostname original
        return hostname

def create_session(target_host=None):
    """
    Crea una sesión de requests con configuración SSL personalizada
    
    Args:
        target_host: Nombre de host específico para usar conexión personalizada
    """
    session = requests.Session()
    
    # Usar el adaptador TLS avanzado para todas las conexiones HTTPS
    adapter = AdvancedTLSAdapter(target_host=target_host)
    session.mount("https://", adapter)
    
    # Desactivar verificación SSL
    session.verify = False
    
    # Configurar el User-Agent
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    })
    
    return session
from urllib3.connectionpool import HTTPSConnectionPool

# Suprimir advertencias SSL para evitar mensajes molestos en la consola
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HostNameIgnoringHTTPSConnection(HTTPSConnection):
    """Conexión HTTPS que ignora la verificación del nombre de host"""
    def _new_conn(self):
        sock = socket.create_connection(
            address=(self.host, self.port),
            timeout=self.timeout,
            source_address=self.source_address,
        )
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_NONE
        context.check_hostname = False
        return context.wrap_socket(sock, server_hostname=None)

class HostNameIgnoringHTTPSConnectionPool(HTTPSConnectionPool):
    """Pool de conexiones HTTPS que usa la conexión personalizada"""
    ConnectionCls = HostNameIgnoringHTTPSConnection

class AdvancedTLSAdapter(HTTPAdapter):
    """Adaptador HTTP avanzado que maneja problemas comunes de SSL"""
    def __init__(self, *args, **kwargs):
        self.target_host = kwargs.pop('target_host', None)
        super(AdvancedTLSAdapter, self).__init__(*args, **kwargs)
    
    def init_poolmanager(self, connections, maxsize, block=False):
        """Inicializa un PoolManager con SSL avanzado"""
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
        
        # Usar la conexión personalizada para hosts problemáticos
        if self.target_host:
            pool_kwargs = {
                'num_pools': connections,
                'maxsize': maxsize,
                'block': block,
                'strict': True,
                'ssl_context': ctx,
            }
            self.poolmanager = urllib3.PoolManager(
                **pool_kwargs,
                # Use our custom connection class for specific hosts
                connection_pool_kw={'pool_classes': {
                    'https': HostNameIgnoringHTTPSConnectionPool
                }}
            )
        else:
            self.poolmanager = PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                ssl_context=ctx
            )

def resolve_ip(hostname):
    """Resuelve la IP de un nombre de host"""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        # Si no se puede resolver, devolver el hostname original
        return hostname

def create_session(target_host=None):
    """
    Crea una sesión de requests con configuración SSL personalizada
    
    Args:
        target_host: Nombre de host específico para usar conexión personalizada
    """
    session = requests.Session()
    
    # Usar el adaptador TLS avanzado para todas las conexiones HTTPS
    adapter = AdvancedTLSAdapter(target_host=target_host)
    session.mount("https://", adapter)
    
    # Desactivar verificación SSL
    session.verify = False
    
    # Configurar el User-Agent
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    })
    
    return session

def make_api_request_proxy(api_key, api_url, messages, model="redpill-llama-3-8b-chat", temperature=0.3, use_cache=True):
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
    import json
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
    
    # Extraer el hostname del URL
    import urllib.parse
    parsed_url = urllib.parse.urlparse(api_url)
    hostname = parsed_url.netloc.split(':')[0]  # Obtener solo el nombre del host sin el puerto
    
    # Lista de errores para registro
    all_errors = []
    
    # Método 1: Intentar con la sesión avanzada personalizada
    try:
        # Crear sesión con manejo avanzado de SSL
        session = create_session(target_host=hostname)
        
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
    
    # Método 2: Usar IP directamente con encabezado Host
    try:
        # Resolver la IP del servidor
        ip = resolve_ip(hostname)
        if ip != hostname:  # Solo si se pudo resolver
            # Crear una nueva URL usando la IP en lugar del nombre de host
            # pero mantener el nombre de host en el encabezado Host
            ip_url = api_url.replace(hostname, ip)
            
            # Crear una nueva sesión
            direct_session = requests.Session()
            direct_session.verify = False
            direct_session.headers.update(headers)
            direct_session.headers.update({"Host": hostname})  # Importante: mantener el Host original
            
            # Realizar la petición directamente a la IP
            response = direct_session.post(
                ip_url,
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
        else:
            all_errors.append("No se pudo resolver la IP del servidor")
    except Exception as direct_error:
        all_errors.append(f"Error usando IP directa (método 2): {str(direct_error)}")
    
    # Método 3: SNI nulo con conexión de socket personalizada
    try:
        import socket
        import json
        
        # Crear contexto SSL personalizado que no usa SNI
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_NONE
        context.check_hostname = False
        
        # Resolver la IP
        ip = resolve_ip(hostname)
        
        # Crear conexión
        sock = socket.create_connection((ip, 443), timeout=10)
        ssock = context.wrap_socket(sock, server_hostname="")  # SNI vacío
        
        # Formar request HTTP
        request_body = json.dumps(payload)
        request = (
            f"POST {parsed_url.path} HTTP/1.1\r\n"
            f"Host: {hostname}\r\n"
            f"Authorization: Bearer {api_key}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(request_body)}\r\n"
            f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n"
            f"Connection: close\r\n"
            f"\r\n"
            f"{request_body}"
        )
        
        # Enviar request
        ssock.sendall(request.encode())
        
        # Recibir respuesta
        response_data = b""
        while True:
            chunk = ssock.recv(4096)
            if not chunk:
                break
            response_data += chunk
        
        # Cerrar socket
        ssock.close()
        
        # Procesar respuesta HTTP
        try:
            # Separar cabeceras y cuerpo
            headers_end = response_data.find(b"\r\n\r\n") + 4
            headers = response_data[:headers_end].decode("utf-8", errors="ignore")
            body = response_data[headers_end:]
            
            # Verificar si es respuesta chunked
            if "Transfer-Encoding: chunked" in headers:
                # Proceso simple para manejar chunked encoding
                # (Una implementación completa sería más compleja)
                body = body.split(b"\r\n")[1::2]  # Ignorar tamaños de chunk
                body = b"".join(body)
            
            # Analizar respuesta JSON
            result = json.loads(body)
            
            # Guardar en caché si está habilitado
            if use_cache:
                try:
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                except Exception as cache_write_error:
                    print(f"Error al escribir caché: {str(cache_write_error)}")
            
            # Devolver resultado
            return result
              except json.JSONDecodeError:
            all_errors.append(f"Error al decodificar JSON en respuesta de socket")
            if b"200 OK" in response_data:
                all_errors.append(f"Respuesta del servidor: {response_data[:200]}")
    except Exception as socket_error:
        all_errors.append(f"Error en conexión de socket (método 3): {str(socket_error)}")
    
    # Si todos los métodos fallaron, mostrar errores acumulados
    error_message = "Todos los métodos de conexión fallaron:\n" + "\n".join(all_errors)
    
    # Verificar si hay un patrón en los errores
    if any("TLSV1_UNRECOGNIZED_NAME" in err for err in all_errors):
        error_message += "\n\nRecomendación: Este error sugiere un problema con la verificación del nombre del host SSL. " \
                        "Prueba acceder desde otra red o usando una VPN."
    elif any("CERTIFICATE_VERIFY_FAILED" in err for err in all_errors):
        error_message += "\n\nRecomendación: Verifica que tu sistema tenga certificados SSL actualizados."
    
    raise Exception(error_message)
