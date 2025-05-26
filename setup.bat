@echo off
echo ===================================================
echo  Instalación de la Plataforma Inteligente de Datos
echo ===================================================
echo.

echo Creando entorno virtual...
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo Configuración de claves API...
echo.
echo Ingresa tu clave API de OpenAI (deja en blanco si no tienes):
set /p openai_key="> "

echo Ingresa tu clave API de Redpill.io (deja en blanco si no tienes):
set /p redpill_key="> "

echo.
echo Creando directorio de configuración...
mkdir .streamlit 2>nul

echo.
echo Creando archivo de secretos...
(
echo [openai]
echo api_key = "%openai_key%"
echo.
echo [redpill]
echo api_key = "%redpill_key%"
echo api_url = "https://api.redpill.ai/v1/chat/completions"
) > .streamlit\secrets.toml

echo.
echo Configuración completada. Para iniciar la aplicación, ejecuta:
echo streamlit run main.py
echo.
echo Presiona cualquier tecla para salir...
pause > nul
