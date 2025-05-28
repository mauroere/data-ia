@echo off
REM Script mejorado para iniciar la aplicación con diagnóstico previo
REM Creado: Mayo 2025

echo ==========================================
echo    INICIANDO PLATAFORMA DE ANALISIS DE DATOS
echo ==========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python no está instalado o no está en el PATH.
    echo Por favor, instale Python 3.8 o superior.
    echo.
    pause
    exit /b 1
)

REM Verificar si pip está instalado
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pip no está instalado o no está en el PATH.
    echo Por favor, reinstale Python con pip incluido.
    echo.
    pause
    exit /b 1
)

echo [INFO] Verificando dependencias...
pip install -r requirements.txt --quiet

REM Verificar la estructura del proyecto
if not exist main.py (
    echo [ERROR] No se encuentra el archivo main.py
    echo Por favor, asegúrese de ejecutar este script desde el directorio raíz del proyecto.
    echo.
    pause
    exit /b 1
)

REM Verificar y crear directorio .streamlit si no existe
if not exist .streamlit (
    echo [INFO] Creando directorio .streamlit...
    mkdir .streamlit
)

REM Verificar secrets.toml
if not exist .streamlit\secrets.toml (
    echo [AVISO] No se encontró el archivo secrets.toml
    echo [INFO] Creando un archivo secrets.toml con una API key predeterminada...
    
    echo [redpill] > .streamlit\secrets.toml
    echo api_key = "sk-xYBWXr1epqP3Uq1A05qUql9tAyBsJE5F8PL5L66gBaE328VG" >> .streamlit\secrets.toml
    echo api_url = "https://redpill.io/api/v1" >> .streamlit\secrets.toml
    
    echo [INFO] Archivo secrets.toml creado correctamente.
) else (
    echo [INFO] Archivo secrets.toml encontrado.
)

REM Ejecutar diagnóstico rápido
echo.
echo [INFO] Ejecutando diagnóstico rápido...
python autotest.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [AVISO] El diagnóstico detectó algunos problemas.
    echo Se recomienda ejecutar el diagnóstico completo: python diagnostico_sistema.py
    echo.
    
    choice /C SN /M "¿Desea continuar de todos modos? (S/N)"
    if %ERRORLEVEL% EQU 2 (
        echo.
        echo [INFO] Iniciando herramienta de diagnóstico...
        start cmd /k python diagnostico_sistema.py
        exit /b 0
    )
)

echo.
echo [INFO] Limpiando caché antigua...
if exist cache (
    del /q cache\*.json 2>nul
)

echo.
echo [INFO] Iniciando la aplicación...
echo [INFO] Presione Ctrl+C para detener la aplicación.
echo.

streamlit run main.py

echo.
echo [INFO] Aplicación finalizada.
echo.
pause
