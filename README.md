# 🧠 Plataforma Inteligente de Gestión de Empleados con IA

Este proyecto es una aplicación de escritorio web desarrollada en Python + Streamlit que permite importar, auditar, cruzar, editar y enriquecer bases de datos de empleados con ayuda de inteligencia artificial (Redpill.io LLM).

---

## ✅ Funcionalidades principales

- **📁 Cargar y cruzar archivos**: permite cargar dos archivos (base actual y nuevo), detectar duplicados o coincidencias similares usando fuzzy matching.
- **📊 Dashboard**: visualización interactiva con filtros por columnas y gráficos dinámicos.
- **✏️ Editor de datos**: tabla editable directamente desde la interfaz y exportación del resultado.
- **📤 Exportador**: exportación filtrada de la base por columna y valor en CSV, Excel o JSON.
- **🤖 Enriquecimiento IA**: permite pegar datos no estructurados para que la IA los limpie y estructure automáticamente.
- **🧠 Asistente en Modo Agente**: interfaz avanzada que proporciona análisis estructurados con hallazgos y recomendaciones sobre los datos cargados.
- **🕓 Historial de análisis exportable**: el historial de interacciones con la IA se guarda en sesión y puede descargarse como CSV.
- **🔄 Reinicio rápido**: botón que permite reiniciar la sesión y limpiar todos los datos cargados.
- **🔍 Diagnóstico de API/SSL**: herramientas avanzadas para diagnosticar y resolver problemas de conexión SSL.
- **📝 Sistema de caché**: reduce la necesidad de conectarse a la API y mejora el rendimiento.

---

## 🛠️ Requisitos técnicos

- Python 3.8 o superior
- Cuenta en Redpill.io con clave de API
- Librerías (ya incluidas en `requirements.txt`):

```txt
streamlit
pandas
sqlalchemy
psycopg2-binary
requests
fuzzywuzzy
python-Levenshtein
altair
xlsxwriter
chardet
openpyxl
urllib3
```

---

## 🚀 Cómo desplegar en Streamlit Cloud

1. Subí el contenido del repositorio a GitHub.
2. Ingresá a [https://streamlit.io/cloud](https://streamlit.io/cloud).
3. Hacé clic en “New app” y seleccioná el repositorio.
4. Indicá `main.py` como archivo principal.
5. Agregá la API key en `Secrets` con el siguiente formato:

```toml
[redpill]
api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
api_url = "https://redpill.io/api/v1"
```

6. ¡Listo! La app estará online.

---

## 🚀 Inicio rápido

Para iniciar la aplicación en tu entorno local:

1. Clona este repositorio
2. Instala las dependencias: `pip install -r requirements.txt`
3. Ejecuta el script de inicio mejorado:
   - En Windows: `iniciar_app_mejorada.bat`
   - En Linux/Mac: `sh setup.sh`

Si encuentras algún problema, ejecuta la herramienta de diagnóstico:

```
streamlit run diagnostico_sistema.py
```

---

## 📦 Estructura del proyecto

```
plataforma-ia-datos/
│
├── main.py                    # Interfaz principal unificada
├── asistente_datos.py         # Asistente de datos original
├── asistente_datos_mejorado.py # Asistente con UX/UI mejorada
├── api_fix.py                 # Solución para API keys en entornos de solo lectura
├── ui_components.py           # Componentes UI reutilizables
├── ui_styles.py               # Estilos CSS globales
├── diagnostico_sistema.py     # Herramienta de diagnóstico unificada
├── autotest.py                # Tests automáticos del sistema
├── GUIA_USUARIO.md            # Guía completa para usuarios
├── requirements.txt           # Dependencias
├── README.md                  # Documentación
├── .streamlit/
│   ├── config.toml            # Configuración visual y de servidor
│   └── secrets.toml           # (solo local, usar Secrets en Streamlit Cloud)
```

---

## 🔧 Nuevas funcionalidades (Mayo 2025)

- **🛡️ Modo de funcionamiento en solo lectura**: Ahora la aplicación puede funcionar en entornos donde el sistema de archivos es de solo lectura.
- **🎨 Interfaz de usuario mejorada**: Rediseño completo de la UI con componentes modernos y experiencia de usuario optimizada.
- **🧪 Sistema de diagnóstico unificado**: Nueva herramienta para detectar y solucionar problemas comunes.
- **📋 Documentación mejorada**: Guía de usuario detallada y actualizada.
- **🔄 Sistema de pruebas automáticas**: Herramienta para verificar la integridad del sistema.
- **🚀 Script de inicio mejorado**: Verifica dependencias y realiza diagnóstico antes de iniciar.

---

## 💡 Ideas futuras

- Integración con Supabase para historial persistente.
- Autenticación de usuarios.
- Dashboard personalizado por rol.
- Entrenamiento incremental del asistente IA.
- Expansión de las capacidades del Modo Agente con análisis estadísticos avanzados.
- Generación automática de visualizaciones basadas en los hallazgos del Modo Agente.
- Exportación de informes completos a partir de los análisis del agente.

---

## 📬 Contacto

Este proyecto fue desarrollado por y para profesionales que gestionan grandes volúmenes de datos laborales y necesitan agilidad, trazabilidad y asistencia IA.

Para soporte técnico, mejoras o nuevas funciones, podés abrir un issue o contactarme directamente.
