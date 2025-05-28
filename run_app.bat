@echo off
echo ===== PLATAFORMA IA DE DATOS =====
cd /d %~dp0
set PYTHONPATH=%CD%

echo.
echo 1. Iniciar la aplicacion
echo 2. Configurar la aplicacion (solucionar problemas)
echo 3. Probar conexion con Redpill API
echo.

choice /c 123 /n /m "Selecciona una opcion (1-3): "

if errorlevel 3 goto test_api
if errorlevel 2 goto setup
if errorlevel 1 goto run_app

:run_app
echo.
echo Iniciando la aplicacion...
python -m streamlit run main.py
goto end

:setup
echo.
echo Configurando la aplicacion...
python setup_redpill.py
echo.
pause
goto start

:test_api
echo.
echo Probando conexion con Redpill API...
python test_conexion_redpill_basic.py
echo.
pause
goto start

:start
cls
%0

:end
pause
