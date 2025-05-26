@echo off
echo Limpiando archivos de cache para la aplicacion de Datos IA...

set CACHE_DIR=%~dp0cache
if not exist "%CACHE_DIR%" (
    echo No se encontro directorio de cache.
    echo Se creara al ejecutar la aplicacion por primera vez.
    goto :EOF
)

echo Borrando archivos de cache de la API...
del /q "%CACHE_DIR%\*.json" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Los archivos de cache fueron eliminados correctamente.
) else (
    echo No se encontraron archivos de cache para eliminar.
)

echo.
echo Operacion completada.
pause
