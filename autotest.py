"""
Script de autotest para verificar todas las funcionalidades de la aplicación.
Ejecuta pruebas automáticas para comprobar que todos los componentes funcionan correctamente.
"""

import os
import sys
import importlib
import traceback
import json
import pandas as pd
from pathlib import Path
import streamlit as st
from contextlib import redirect_stdout, redirect_stderr
import io
import time
import datetime

# Constantes
CRITICAL_MODULES = [
    "utils", "api_context", "api_proxy", "api_fix", 
    "ui_components", "ui_styles", "asistente_datos_mejorado"
]

# Configuración de colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")

def print_subheader(message):
    print(f"{Colors.OKBLUE}{Colors.BOLD}{message}{Colors.ENDC}")

def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message):
    print(f"  {message}")

# Funciones de test
def test_importacion_modulos():
    """Prueba la importación de todos los módulos críticos."""
    print_subheader("Probando importación de módulos críticos...")
    resultados = []
    
    for modulo in CRITICAL_MODULES:
        try:
            importlib.import_module(modulo)
            print_success(f"Módulo '{modulo}' importado correctamente")
            resultados.append({"modulo": modulo, "status": "ok", "mensaje": "Importado correctamente"})
        except Exception as e:
            error_msg = str(e)
            print_error(f"Error al importar '{modulo}': {error_msg}")
            resultados.append({"modulo": modulo, "status": "error", "mensaje": error_msg})
    
    return resultados

def test_api_key():
    """Prueba la obtención de la API key."""
    print_subheader("Probando obtención de API key...")
    resultados = []
    
    # Método 1: Desde el módulo utils
    try:
        from utils import get_api_key
        api_key = get_api_key()
        if api_key and len(api_key) > 10:
            print_success("API key obtenida correctamente desde utils.get_api_key()")
            resultados.append({"metodo": "utils.get_api_key", "status": "ok"})
        else:
            print_warning(f"API key desde utils.get_api_key() parece inválida: {api_key[:4]}...")
            resultados.append({"metodo": "utils.get_api_key", "status": "warning", "mensaje": "API key parece inválida"})
    except Exception as e:
        print_error(f"Error al obtener API key desde utils.get_api_key(): {str(e)}")
        resultados.append({"metodo": "utils.get_api_key", "status": "error", "mensaje": str(e)})
    
    # Método 2: Desde api_fix
    try:
        from api_fix import ensure_api_key_exists
        # Crear un objeto de sesión falso para la prueba
        if 'session_state' not in st.__dict__:
            st.session_state = {}
        
        # Ejecutar la función
        ensure_api_key_exists()
        
        if "redpill_api_key" in st.session_state and st.session_state["redpill_api_key"]:
            print_success("API key asegurada correctamente con api_fix.ensure_api_key_exists()")
            resultados.append({"metodo": "api_fix.ensure_api_key_exists", "status": "ok"})
        else:
            print_error("api_fix.ensure_api_key_exists() no guardó la API key en session_state")
            resultados.append({"metodo": "api_fix.ensure_api_key_exists", "status": "error", "mensaje": "No se guardó la API key"})
    except Exception as e:
        print_error(f"Error al ejecutar api_fix.ensure_api_key_exists(): {str(e)}")
        resultados.append({"metodo": "api_fix.ensure_api_key_exists", "status": "error", "mensaje": str(e)})
    
    # Método 3: Desde secrets.toml
    try:
        secrets_path = Path('.streamlit') / 'secrets.toml'
        if secrets_path.exists():
            import toml
            secrets = toml.load(secrets_path)
            if "redpill" in secrets and "api_key" in secrets["redpill"]:
                api_key = secrets["redpill"]["api_key"]
                if api_key and len(api_key) > 10:
                    print_success("API key encontrada en secrets.toml")
                    resultados.append({"metodo": "secrets.toml", "status": "ok"})
                else:
                    print_warning(f"API key en secrets.toml parece inválida: {api_key[:4]}...")
                    resultados.append({"metodo": "secrets.toml", "status": "warning", "mensaje": "API key parece inválida"})
            else:
                print_warning("No se encontró sección redpill.api_key en secrets.toml")
                resultados.append({"metodo": "secrets.toml", "status": "warning", "mensaje": "Sección redpill.api_key no encontrada"})
        else:
            print_warning("Archivo secrets.toml no encontrado")
            resultados.append({"metodo": "secrets.toml", "status": "warning", "mensaje": "Archivo no encontrado"})
    except Exception as e:
        print_error(f"Error al leer secrets.toml: {str(e)}")
        resultados.append({"metodo": "secrets.toml", "status": "error", "mensaje": str(e)})
    
    return resultados

def test_ui_components():
    """Prueba los componentes de UI."""
    print_subheader("Probando componentes de UI...")
    resultados = []
    
    try:
        from ui_components import stat_card, data_card, chat_message, loading_animation
        
        # Probar stat_card
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                stat_card("Prueba", 100, 5)
            print_success("Componente stat_card funciona correctamente")
            resultados.append({"componente": "stat_card", "status": "ok"})
        except Exception as e:
            print_error(f"Error en componente stat_card: {str(e)}")
            resultados.append({"componente": "stat_card", "status": "error", "mensaje": str(e)})
        
        # Probar data_card
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                data_card("Título de prueba", "Contenido de prueba")
            print_success("Componente data_card funciona correctamente")
            resultados.append({"componente": "data_card", "status": "ok"})
        except Exception as e:
            print_error(f"Error en componente data_card: {str(e)}")
            resultados.append({"componente": "data_card", "status": "error", "mensaje": str(e)})
        
        # Probar chat_message
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                chat_message("Mensaje de prueba", "user")
            print_success("Componente chat_message funciona correctamente")
            resultados.append({"componente": "chat_message", "status": "ok"})
        except Exception as e:
            print_error(f"Error en componente chat_message: {str(e)}")
            resultados.append({"componente": "chat_message", "status": "error", "mensaje": str(e)})
        
        # Probar loading_animation
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                loading_animation()
            print_success("Componente loading_animation funciona correctamente")
            resultados.append({"componente": "loading_animation", "status": "ok"})
        except Exception as e:
            print_error(f"Error en componente loading_animation: {str(e)}")
            resultados.append({"componente": "loading_animation", "status": "error", "mensaje": str(e)})
            
    except Exception as e:
        print_error(f"Error al importar ui_components: {str(e)}")
        resultados.append({"componente": "ui_components", "status": "error", "mensaje": str(e)})
    
    return resultados

def test_ui_styles():
    """Prueba los estilos de UI."""
    print_subheader("Probando estilos de UI...")
    resultados = []
    
    try:
        from ui_styles import apply_styles
        
        # Probar apply_styles
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                apply_styles()
            print_success("Función apply_styles funciona correctamente")
            resultados.append({"funcion": "apply_styles", "status": "ok"})
        except Exception as e:
            print_error(f"Error en función apply_styles: {str(e)}")
            resultados.append({"funcion": "apply_styles", "status": "error", "mensaje": str(e)})
            
    except Exception as e:
        print_error(f"Error al importar ui_styles: {str(e)}")
        resultados.append({"modulo": "ui_styles", "status": "error", "mensaje": str(e)})
    
    return resultados

def test_api_context():
    """Prueba las funciones de api_context."""
    print_subheader("Probando funciones de api_context...")
    resultados = []
    
    try:
        from api_context import generar_contexto_datos
        
        # Crear un DataFrame de prueba
        df_test = pd.DataFrame({
            'id': [1, 2, 3],
            'nombre': ['Juan', 'María', 'Pedro'],
            'edad': [30, 25, 40]
        })
        
        # Probar generar_contexto_datos
        try:
            contexto = generar_contexto_datos(df_test)
            if contexto and isinstance(contexto, str) and len(contexto) > 0:
                print_success("Función generar_contexto_datos funciona correctamente")
                resultados.append({"funcion": "generar_contexto_datos", "status": "ok"})
            else:
                print_warning("generar_contexto_datos devolvió un resultado vacío o inválido")
                resultados.append({"funcion": "generar_contexto_datos", "status": "warning", "mensaje": "Resultado vacío o inválido"})
        except Exception as e:
            print_error(f"Error en función generar_contexto_datos: {str(e)}")
            resultados.append({"funcion": "generar_contexto_datos", "status": "error", "mensaje": str(e)})
            
    except Exception as e:
        print_error(f"Error al importar api_context: {str(e)}")
        resultados.append({"modulo": "api_context", "status": "error", "mensaje": str(e)})
    
    return resultados

def test_utils():
    """Prueba las funciones de utils."""
    print_subheader("Probando funciones de utils...")
    resultados = []
    
    try:
        from utils import normalize_column_names, are_similar
        
        # Probar normalize_column_names
        try:
            df_test = pd.DataFrame({
                'ID Usuario': [1, 2, 3],
                'Nombre Completo': ['Juan', 'María', 'Pedro'],
                'Edad (años)': [30, 25, 40]
            })
            
            df_norm = normalize_column_names(df_test)
            expected_columns = ['id_usuario', 'nombre_completo', 'edad_anos']
            
            if list(df_norm.columns) == expected_columns:
                print_success("Función normalize_column_names funciona correctamente")
                resultados.append({"funcion": "normalize_column_names", "status": "ok"})
            else:
                print_warning(f"normalize_column_names no normalizó correctamente. Esperado: {expected_columns}, Obtenido: {list(df_norm.columns)}")
                resultados.append({"funcion": "normalize_column_names", "status": "warning", "mensaje": "Normalización incorrecta"})
        except Exception as e:
            print_error(f"Error en función normalize_column_names: {str(e)}")
            resultados.append({"funcion": "normalize_column_names", "status": "error", "mensaje": str(e)})
        
        # Probar are_similar
        try:
            similar = are_similar("Juan Pérez", "Juan Perez")
            not_similar = are_similar("Juan Pérez", "María González")
            
            if similar and not not_similar:
                print_success("Función are_similar funciona correctamente")
                resultados.append({"funcion": "are_similar", "status": "ok"})
            else:
                print_warning(f"are_similar no funcionó como se esperaba. Similar: {similar}, No similar: {not_similar}")
                resultados.append({"funcion": "are_similar", "status": "warning", "mensaje": "Comparación incorrecta"})
        except Exception as e:
            print_error(f"Error en función are_similar: {str(e)}")
            resultados.append({"funcion": "are_similar", "status": "error", "mensaje": str(e)})
            
    except Exception as e:
        print_error(f"Error al importar utils: {str(e)}")
        resultados.append({"modulo": "utils", "status": "error", "mensaje": str(e)})
    
    return resultados

def test_api_fix():
    """Prueba las funciones de api_fix."""
    print_subheader("Probando funciones de api_fix...")
    resultados = []
    
    try:
        from api_fix import ensure_api_key_exists
        
        # Limpiar session_state para la prueba
        if 'redpill_api_key' in st.session_state:
            del st.session_state['redpill_api_key']
        
        # Probar ensure_api_key_exists
        try:
            ensure_api_key_exists()
            
            if 'redpill_api_key' in st.session_state and st.session_state['redpill_api_key']:
                print_success("Función ensure_api_key_exists funciona correctamente")
                resultados.append({"funcion": "ensure_api_key_exists", "status": "ok"})
            else:
                print_error("ensure_api_key_exists no configuró la API key en session_state")
                resultados.append({"funcion": "ensure_api_key_exists", "status": "error", "mensaje": "No se configuró la API key"})
        except Exception as e:
            print_error(f"Error en función ensure_api_key_exists: {str(e)}")
            resultados.append({"funcion": "ensure_api_key_exists", "status": "error", "mensaje": str(e)})
            
    except Exception as e:
        print_error(f"Error al importar api_fix: {str(e)}")
        resultados.append({"modulo": "api_fix", "status": "error", "mensaje": str(e)})
    
    return resultados

def test_asistente_datos_mejorado():
    """Prueba las funciones del asistente de datos mejorado."""
    print_subheader("Probando funciones del asistente de datos mejorado...")
    resultados = []
    
    try:
        # Solo verificamos que se pueda importar, no ejecutamos funciones ya que requieren Streamlit
        import asistente_datos_mejorado
        print_success("Módulo asistente_datos_mejorado importado correctamente")
        resultados.append({"modulo": "asistente_datos_mejorado", "status": "ok"})
        
        # Verificar presencia de funciones clave
        funciones_clave = [
            "run_data_assistant", "process_query", "display_data_analysis", 
            "format_analysis_results", "export_chat_history"
        ]
        
        for funcion in funciones_clave:
            if hasattr(asistente_datos_mejorado, funcion):
                print_success(f"Función {funcion} encontrada en asistente_datos_mejorado")
                resultados.append({"funcion": funcion, "status": "ok"})
            else:
                print_warning(f"Función {funcion} no encontrada en asistente_datos_mejorado")
                resultados.append({"funcion": funcion, "status": "warning", "mensaje": "Función no encontrada"})
            
    except Exception as e:
        print_error(f"Error al importar asistente_datos_mejorado: {str(e)}")
        resultados.append({"modulo": "asistente_datos_mejorado", "status": "error", "mensaje": str(e)})
    
    return resultados

def test_integracion_componentes():
    """Prueba la integración entre componentes."""
    print_subheader("Probando integración entre componentes...")
    resultados = []
    
    # Test 1: Verificar que main.py importa correctamente asistente_datos_mejorado
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if "asistente_datos_mejorado" in contenido:
            print_success("main.py importa asistente_datos_mejorado")
            resultados.append({"test": "main_importa_asistente", "status": "ok"})
        else:
            print_warning("main.py no parece importar asistente_datos_mejorado")
            resultados.append({"test": "main_importa_asistente", "status": "warning", "mensaje": "No se encontró la importación"})
    except Exception as e:
        print_error(f"Error al verificar importaciones en main.py: {str(e)}")
        resultados.append({"test": "main_importa_asistente", "status": "error", "mensaje": str(e)})
    
    # Test 2: Verificar que asistente_datos_mejorado usa api_fix
    try:
        with open('asistente_datos_mejorado.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if "api_fix" in contenido and "ensure_api_key_exists" in contenido:
            print_success("asistente_datos_mejorado usa api_fix.ensure_api_key_exists")
            resultados.append({"test": "asistente_usa_api_fix", "status": "ok"})
        else:
            print_warning("asistente_datos_mejorado no parece usar api_fix.ensure_api_key_exists")
            resultados.append({"test": "asistente_usa_api_fix", "status": "warning", "mensaje": "No se encontró la importación"})
    except Exception as e:
        print_error(f"Error al verificar importaciones en asistente_datos_mejorado.py: {str(e)}")
        resultados.append({"test": "asistente_usa_api_fix", "status": "error", "mensaje": str(e)})
    
    # Test 3: Verificar que asistente_datos_mejorado usa ui_components
    try:
        with open('asistente_datos_mejorado.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if "ui_components" in contenido:
            print_success("asistente_datos_mejorado usa ui_components")
            resultados.append({"test": "asistente_usa_ui_components", "status": "ok"})
        else:
            print_warning("asistente_datos_mejorado no parece usar ui_components")
            resultados.append({"test": "asistente_usa_ui_components", "status": "warning", "mensaje": "No se encontró la importación"})
    except Exception as e:
        print_error(f"Error al verificar importaciones en asistente_datos_mejorado.py: {str(e)}")
        resultados.append({"test": "asistente_usa_ui_components", "status": "error", "mensaje": str(e)})
    
    return resultados

def ejecutar_tests():
    """Ejecuta todas las pruebas y genera un informe."""
    print_header("Autotest de la Plataforma de Análisis de Datos")
    print(f"Fecha y hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Directorio de trabajo: {os.getcwd()}")
    print()
    
    resultados = {}
    
    # Ejecutar todas las pruebas
    resultados["importacion_modulos"] = test_importacion_modulos()
    resultados["api_key"] = test_api_key()
    resultados["ui_components"] = test_ui_components()
    resultados["ui_styles"] = test_ui_styles()
    resultados["api_context"] = test_api_context()
    resultados["utils"] = test_utils()
    resultados["api_fix"] = test_api_fix()
    resultados["asistente_datos_mejorado"] = test_asistente_datos_mejorado()
    resultados["integracion_componentes"] = test_integracion_componentes()
    
    # Generar resumen
    print_header("Resumen de Resultados")
    
    total_tests = 0
    exitosos = 0
    advertencias = 0
    errores = 0
    
    for categoria, tests in resultados.items():
        for test in tests:
            total_tests += 1
            if test.get("status") == "ok":
                exitosos += 1
            elif test.get("status") == "warning":
                advertencias += 1
            else:
                errores += 1
    
    print_subheader(f"Total de pruebas: {total_tests}")
    print_success(f"Exitosas: {exitosos}")
    print_warning(f"Advertencias: {advertencias}")
    print_error(f"Errores: {errores}")
    
    # Calcular porcentaje de éxito
    porcentaje_exito = (exitosos / total_tests) * 100 if total_tests > 0 else 0
    print(f"\nPorcentaje de éxito: {porcentaje_exito:.2f}%")
    
    # Guardar resultados en un archivo JSON
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"autotest_resultados_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump({
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "resultados": resultados,
            "resumen": {
                "total": total_tests,
                "exitosos": exitosos,
                "advertencias": advertencias,
                "errores": errores,
                "porcentaje_exito": porcentaje_exito
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultados guardados en: autotest_resultados_{timestamp}.json")
    
    # Devolver el código de salida según los resultados
    if errores > 0:
        return 1  # Error
    elif advertencias > 0:
        return 2  # Advertencia
    else:
        return 0  # Éxito

if __name__ == "__main__":
    sys.exit(ejecutar_tests())
