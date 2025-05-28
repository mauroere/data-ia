@echo off
echo ========================================================
echo    PLATAFORMA IA DE DATOS - INICIANDO APLICACION
echo ========================================================
echo.
echo [INFO] Verificando dependencias...

pip install -r requirements.txt > nul 2>&1

echo [INFO] Dependencias instaladas correctamente
echo.
echo [NUEVO] Modo Agente activado!
echo El asistente de datos ahora ofrece:
echo  - Analisis estructurados
echo  - Hallazgos especificos sobre tus datos
echo  - Recomendaciones accionables
echo.
echo [INFO] Iniciando aplicacion...
echo.
echo Para acceder a la documentacion del Modo Agente:
echo  - docs_modo_agente.md (Guia de usuario)
echo  - docs_tecnica_agente.md (Documentacion tecnica)
echo.
echo Presiona Ctrl+C para detener la aplicacion
echo ========================================================
echo.

streamlit run main.py
