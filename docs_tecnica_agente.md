# Documentación Técnica: Implementación del Modo Agente

## Introducción

Este documento técnico describe la implementación del Modo Agente en la aplicación de análisis de datos, específicamente en el módulo de Cruce Inteligente. El Modo Agente proporciona un análisis más estructurado y proactivo que el modo de chat conversacional tradicional.

## Arquitectura

El Modo Agente se implementa a través de la función `make_api_request_agente()` en el módulo `api_context.py`. Esta función:

1. Utiliza el mismo backend de API (Redpill.io) que el modo chat
2. Incorpora instrucciones específicas que definen el comportamiento del agente
3. Proporciona un formato estructurado de respuesta (Análisis, Hallazgos, Recomendaciones)
4. Usa parámetros optimizados para respuestas más precisas y detalladas

## Diferencias clave con el modo chat

| Característica       | Modo Chat | Modo Agente                   |
| -------------------- | --------- | ----------------------------- |
| Temperatura          | 0.7       | 0.3 (más determinístico)      |
| Tokens máximos       | 1000      | 1500                          |
| Instrucciones        | Generales | Específicas y estructuradas   |
| Formato de respuesta | Libre     | Estructurado en secciones     |
| Comportamiento       | Reactivo  | Proactivo con recomendaciones |
| Response Format      | No especificado | `{"type": "text"}`      |

## Instrucciones Especializadas

Las instrucciones enviadas al modelo son críticas para obtener respuestas estructuradas:

```python
instrucciones_agente = """
Actúa como un agente de análisis de datos especializado que puede:
1. Interpretar datos y realizar análisis básicos
2. Buscar patrones, correlaciones y tendencias en los datos
3. Sugerir acciones específicas basadas en el análisis
4. Responder a consultas técnicas sobre los datos
5. Explicar el significado de los resultados del cruce de datos
6. Proponer nuevos análisis o cruces que podrían ser útiles

IMPORTANTE: DEBES responder SIEMPRE utilizando EXACTAMENTE el siguiente formato estructurado:

📊 ANÁLISIS:
[Breve resumen de tu interpretación de los datos]

🔍 HALLAZGOS:
1. [Primer hallazgo importante]
2. [Segundo hallazgo importante]
3. [Más hallazgos si corresponde]

📈 RECOMENDACIONES:
- [Primera recomendación concreta]
- [Segunda recomendación concreta]
- [Más recomendaciones si corresponde]
"""
```
3. La adaptación de la interfaz de usuario para reflejar el nuevo paradigma de agente
4. La actualización del formato de visualización usando markdown en lugar de texto plano

## Generación de contexto

El agente utiliza la misma función de generación de contexto que el modo chat, definida en `generar_contexto_datos()`. Esta función:

1. Examina los DataFrames almacenados en `st.session_state`
2. Genera descripciones de los datos cargados
3. Incluye ejemplos de las filas de datos
4. Incorpora información sobre campos clave y coincidencias

## Instrucciones del agente

Las instrucciones específicas que definen el comportamiento del agente son:

```python
instrucciones_agente = """
Actúa como un agente de análisis de datos que puede:
1. Interpretar datos y realizar análisis básicos
2. Buscar patrones, correlaciones y tendencias en los datos
3. Sugerir acciones específicas basadas en el análisis
4. Responder a consultas técnicas sobre los datos
5. Explicar el significado de los resultados del cruce de datos
6. Proponer nuevos análisis o cruces que podrían ser útiles

Cuando respondas, sigue este formato:
1. 📊 ANÁLISIS: Breve resumen de tu interpretación de los datos
2. 🔍 HALLAZGOS: Enumera los principales hallazgos o conclusiones
3. 📈 RECOMENDACIONES: Sugiere acciones concretas o análisis adicionales

Usa lenguaje técnico pero comprensible y responde siempre en español.
"""
```

## Manejo de errores

El Modo Agente implementa un manejo de errores mejorado que:

1. Detecta y comunica errores específicos (límite de API, problemas SSL, timeouts)
2. Proporciona mensajes de error más descriptivos
3. Sugiere acciones correctivas específicas para cada tipo de error

## Estructura de payload de la API

```python
payload = {
    "model": "mistralai/ministral-8b",
    "messages": [
        {"role": "system", "content": "Eres un agente inteligente especializado en análisis de datos..."},
        {"role": "user", "content": pregunta_enriquecida}
    ],
    "temperature": 0.5,
    "max_tokens": 1500
}
```

## Cómo extender el Modo Agente

### Agregar nuevas capacidades de análisis

Para agregar nuevas capacidades de análisis:

1. Modifica las instrucciones en `instrucciones_agente` en `api_context.py`
2. Actualiza la documentación de usuario para reflejar las nuevas capacidades
3. Considera agregar ejemplos específicos en el contexto para mejorar el rendimiento

### Personalizar el formato de respuesta

Para modificar el formato de respuesta:

1. Actualiza la sección de formato en `instrucciones_agente`
2. Ajusta la visualización en `main.py` para que coincida con el nuevo formato
3. Actualiza la lógica de almacenamiento del historial si es necesario

### Optimizar parámetros del modelo

Los parámetros actuales están optimizados para un equilibrio entre precisión y velocidad. Para ajustarlos:

1. Modifica `temperature` (valores más bajos = más determinista)
2. Ajusta `max_tokens` según la longitud de respuesta deseada
3. Considera experimentar con diferentes modelos base

## Pruebas

Para probar el Modo Agente:

1. Utiliza `test_agente_simple.py` para pruebas básicas sin dependencias
2. Usa `test_api_agente.py` para pruebas más completas con datos de ejemplo
3. Verifica que las respuestas sigan el formato estructurado esperado

## Limitaciones conocidas

1. El modo agente requiere más tokens que el modo chat, lo que puede aumentar los costos de API
2. Las respuestas más largas pueden ocasionar timeouts en conexiones lentas
3. El formato estructurado puede no ser óptimo para todas las consultas

## Recomendaciones para futuros desarrollos

1. Implementar un modo híbrido que alterne entre agente y chat según el tipo de consulta
2. Agregar capacidades de análisis estadístico más avanzadas
3. Incorporar visualización automática de datos basada en los hallazgos del agente
4. Explorar la integración con otras APIs de IA para análisis especializados
