# Soluciones para Problemas de Conexión SSL en la Aplicación

## Introducción

Este documento describe las soluciones implementadas para resolver problemas de conexión SSL, especialmente el error `TLSV1_UNRECOGNIZED_NAME` que ocurre al conectarse a la API de Redpill.io.

## Problema

El error `TLSV1_UNRECOGNIZED_NAME` ocurre durante una conexión SSL/TLS cuando el cliente envía una extensión SNI (Server Name Indication) al servidor, pero el servidor no reconoce o no puede gestionar correctamente el nombre de host proporcionado. Esto puede ocurrir por varias razones:

1. El servidor no soporta la extensión SNI
2. El nombre de host proporcionado no coincide con ninguno de los certificados del servidor
3. Problemas de configuración en el servidor o cliente
4. Restricciones de red o firewall que modifican la conexión

## Soluciones Implementadas

### 1. Sistema Avanzado de Manejo SSL

Hemos implementado una solución multicapa para manejar problemas de SSL:

- **AdvancedTLSAdapter**: Un adaptador personalizado que configura la conexión SSL para ignorar problemas comunes de verificación.
- **HostNameIgnoringHTTPSConnection**: Una clase de conexión HTTPS que ignora completamente la verificación del nombre de host.
- **Sistema de Fallback**: Si falla la conexión normal, intentamos con métodos alternativos.

### 2. Estrategia de 3 Métodos

La función `make_api_request_proxy` intenta conectarse usando tres métodos diferentes:

1. **Método 1**: Conexión estándar con adaptador TLS personalizado
2. **Método 2**: Conexión directa a la IP del servidor (resolviendo el nombre del host) manteniendo el encabezado Host original
3. **Método 3**: Conexión de bajo nivel usando sockets con SNI vacío

Si un método falla, se prueba el siguiente, proporcionando mayor robustez a la conexión.

### 3. Sistema de Caché

Para reducir la necesidad de conexiones a la API, hemos implementado un sistema de caché de dos niveles:

- **Caché de nivel 1**: Implementado en `api_cache.py`, guarda respuestas basadas en la entrada exacta
- **Caché de nivel 2**: Integrado en `make_api_request_proxy`, proporciona una capa adicional de caché

Las entradas en caché expiran después de 24 horas por defecto, pero este tiempo es configurable.

### 4. Herramientas de Diagnóstico

Hemos añadido herramientas avanzadas de diagnóstico:

- **api_diagnostico.py**: Permite probar la conexión básica a la API
- **ssl_diagnostico.py**: Proporciona diagnósticos detallados de problemas SSL, incluyendo:
  - Pruebas de resolución DNS
  - Pruebas de conexión TCP
  - Pruebas de handshake SSL
  - Pruebas de solicitud HTTP

## Uso de las Herramientas de Diagnóstico

### Diagnóstico de API

1. Navega a la sección "🔍 Diagnóstico API" en el menú de navegación
2. Ingresa la URL de la API y tu clave API
3. Haz clic en "Probar Conexión" para ver el resultado

### Diagnóstico SSL

1. Navega a la pestaña "Diagnóstico SSL" en la sección de diagnóstico
2. Ingresa la URL para diagnosticar (por defecto es la API de Redpill)
3. Haz clic en "Ejecutar diagnóstico SSL" para ver resultados detallados

## Mantenimiento del Sistema de Caché

El sistema de caché puede gestionarse desde el panel lateral:

1. **Limpiar caché expirada**: Elimina solo las entradas que han expirado
2. **Limpiar toda la caché**: Elimina todas las entradas, útil si hay problemas con datos en caché
3. **Estadísticas de caché**: Muestra información sobre el uso actual de la caché

## Solución de Problemas Comunes

### Error "TLSV1_UNRECOGNIZED_NAME" persiste

Si el error persiste a pesar de las soluciones implementadas:

1. Verifica que estás usando una versión reciente de Python con soporte TLS actualizado
2. Prueba conectarte desde otra red (algunos firewalls corporativos pueden interferir)
3. Verifica si el servicio de API está disponible usando un navegador web
4. Considera usar una VPN para eludir restricciones de red

### Problemas de Rendimiento

Si notas que la aplicación es lenta al realizar peticiones a la API:

1. Verifica las estadísticas de caché para asegurarte de que se está utilizando correctamente
2. Ajusta el tiempo de vida de la caché según tus necesidades (valor por defecto: 24 horas)
3. Si realizas muchas peticiones similares, considera agruparlas para aprovechar mejor la caché

## Conclusión

Estas soluciones proporcionan una robustez significativa a la aplicación frente a problemas de conexión SSL, especialmente el error `TLSV1_UNRECOGNIZED_NAME`. El sistema multicapa de conexión y caché asegura que la aplicación pueda funcionar incluso en entornos de red desafiantes.
