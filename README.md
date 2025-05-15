# Plataforma Inteligente de Gestión de Empleados con IA 🤖📊

Esta herramienta te permite importar, cruzar, normalizar, visualizar, editar y exportar bases de datos de empleados, utilizando IA (OpenAI GPT-4) y dashboards interactivos.

---

## 🚀 Funcionalidades principales

- 🔄 **Cruce inteligente de datos** con detección de duplicados (fuzzy matching)
- 🧠 **Mapeo de columnas sugerido por IA**
- 🧹 **Normalización automática de columnas**
- 📈 **Dashboard de visualización con filtros y métricas**
- ✏️ **Editor manual de datos**
- 📤 **Exportación en CSV, Excel y JSON**
- 🔐 **Control de accesos (simulado)**
- 💬 **Enriquecimiento de datos caóticos vía interfaz conversacional con IA**

---

## 📁 Estructura del proyecto

```bash
📦 gestion-empleados-ia-streamlit/
├── main.py                    # Cruce y deduplicación inteligente
├── dashboard.py               # Visualización de métricas
├── editor.py                  # Edición directa de datos
├── exportador.py              # Exportación flexible por filtro
├── colaboracion.py            # Seguridad y permisos
├── ia_enriquecimiento.py      # IA para estructurar datos sucios
├── requirements.txt           # Dependencias
├── .streamlit/
│   ├── config.toml            # Configuración UI
│   └── secrets.toml           # Clave API de OpenAI
```

---

## 🧑‍💻 Cómo desplegar en Streamlit Cloud

1. Subí el proyecto a un repositorio en GitHub.
2. Iniciá sesión en https://streamlit.io/cloud
3. Seleccioná “New App” → Conectá el repo → Elegí `main.py` como entry point.
4. Agregá tu `OPENAI_API_KEY` en el panel de configuración (`secrets`).
5. ¡Listo! El sistema estará desplegado y disponible vía web.

---

## 🖼️ Vista previa esperada

(Podés capturar y subir imágenes del sistema funcionando para agregarlas aquí)

---

## 🛠️ Requisitos

- Cuenta de OpenAI con acceso a GPT-4
- Cuenta en [Streamlit Cloud](https://streamlit.io/cloud)
- Cuenta en GitHub (para versionado y despliegue)

---

## 📬 Contacto

Proyecto desarrollado con propósito educativo y empresarial. Para asistencia técnica o personalización, contactanos.