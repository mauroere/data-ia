# 📚 Guía de Usuario - Plataforma de Análisis de Datos con IA

Esta guía proporciona instrucciones paso a paso para utilizar la Plataforma de Análisis de Datos con IA, destacando las nuevas funcionalidades y mejoras.

## 📋 Índice

1. [Primeros pasos](#primeros-pasos)
2. [Carga y análisis de datos](#carga-y-análisis-de-datos)
3. [Uso del Asistente de Datos Mejorado](#uso-del-asistente-de-datos-mejorado)
4. [Solución de problemas comunes](#solución-de-problemas-comunes)
5. [Preguntas frecuentes](#preguntas-frecuentes)

---

## 🚀 Primeros pasos

### Configuración inicial

1. Asegúrate de tener Python 3.8 o superior instalado.
2. Instala todas las dependencias con: `pip install -r requirements.txt`
3. Configura tu API key de Redpill.io:
   - Crea un archivo `.streamlit/secrets.toml` con el siguiente contenido:
     ```toml
     [redpill]
     api_key = "tu_api_key_aquí"
     api_url = "https://redpill.io/api/v1"
     ```
   - Alternativamente, la aplicación ahora permite funcionar con una API key predeterminada en entornos de solo lectura.

### Ejecución de la aplicación

Para iniciar la aplicación, ejecuta:

```bash
streamlit run main.py
```

También puedes usar el script incluido:

- En Windows: `run_app.bat`
- En Linux/Mac: `sh setup.sh`

---

## 📊 Carga y análisis de datos

### Cargar archivos

1. Navega a la sección "Cargar Archivos" en la barra lateral.
2. Selecciona uno o dos archivos (CSV, Excel, JSON) para cargar.
3. La aplicación detectará automáticamente el formato y codificación.

### Edición y exportación

1. Usa la sección "Editor" para modificar datos cargados.
2. Los cambios se guardan automáticamente en la sesión.
3. Exporta los datos en varios formatos desde la sección "Exportador".

### Dashboard interactivo

1. Accede a "Dashboard" para visualizar tus datos.
2. Selecciona columnas para filtrar y crear gráficos.
3. Las visualizaciones son interactivas y pueden personalizarse.

---

## 🤖 Uso del Asistente de Datos Mejorado

El nuevo asistente de datos incluye mejoras significativas en la interfaz de usuario y funcionalidad.

### Características principales

1. **Interfaz moderna**: Diseño mejorado con componentes visuales avanzados.
2. **Análisis contextual**: El asistente ahora entiende mejor tus datos.
3. **Exportación de resultados**: Guarda análisis y chats para referencia futura.

### Cómo usar el asistente

1. Carga tus datos en la aplicación.
2. Navega a la sección "Asistente de Datos".
3. Escribe tu pregunta o selecciona una de las sugerencias.
4. El asistente analizará tus datos y proporcionará respuestas visuales e interactivas.

### Ejemplos de preguntas

- "Muéstrame un resumen de los datos cargados"
- "¿Cuáles son las principales tendencias en estas ventas?"
- "Genera un análisis de correlación entre estas variables"
- "Limpia estos datos y elimina duplicados"

---

## 🔧 Solución de problemas comunes

### Herramienta de diagnóstico

La aplicación ahora incluye una herramienta de diagnóstico unificada para resolver problemas comunes:

1. Ejecuta `streamlit run diagnostico_sistema.py`
2. Selecciona la opción de diagnóstico apropiada.
3. Sigue las instrucciones para resolver cualquier problema.

### Problemas con la API key

Si encuentras problemas con la API key:

1. Verifica que el archivo `.streamlit/secrets.toml` existe y tiene el formato correcto.
2. La aplicación ahora tiene un sistema de respaldo que funciona incluso en entornos de solo lectura.
3. Usa la herramienta de diagnóstico para verificar y solucionar problemas de conexión.

### Errores de SSL

Si encuentras errores relacionados con SSL:

1. Ejecuta el diagnóstico de SSL en la herramienta de diagnóstico.
2. Consulta el archivo `docs_ssl_solutions.md` para soluciones específicas.

---

## ❓ Preguntas frecuentes

### ¿La aplicación funciona sin conexión a internet?

No, se requiere conexión a internet para comunicarse con la API de Redpill.io. Sin embargo, la aplicación incluye un sistema de caché que reduce la necesidad de conexiones frecuentes.

### ¿Puedo usar la aplicación en un entorno de solo lectura?

Sí, la nueva versión está diseñada para funcionar en entornos de solo lectura, utilizando un sistema de respaldo para la API key y configuraciones.

### ¿Cómo exporto los resultados de un análisis?

En la sección del asistente de datos, hay un botón "Exportar" que permite guardar tanto el historial de chat como los resultados del análisis en formatos CSV, Excel o JSON.

### ¿Qué hago si la aplicación muestra errores al cargar?

Ejecuta la herramienta de diagnóstico (`diagnostico_sistema.py`) para identificar y resolver problemas. También puedes verificar los archivos de registro en la carpeta donde se ejecuta la aplicación.

---

## 📞 Soporte técnico

Si necesitas ayuda adicional:

1. Consulta la documentación técnica en la carpeta del proyecto.
2. Verifica los archivos de diagnóstico y soluciones SSL.
3. Ejecuta las herramientas de prueba incluidas en el proyecto.

---

_Última actualización: Mayo 2025_
