"""
Script para verificar la sintaxis del archivo main.py sin ejecutarlo.
No requiere dependencias externas.
"""

import ast
import sys

def verificar_archivo_python(ruta_archivo):
    """Verifica la sintaxis de un archivo Python sin ejecutarlo."""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            contenido = file.read()
            
        # Intentar parsear el archivo como código Python
        ast.parse(contenido)
        print(f"✅ El archivo {ruta_archivo} tiene una sintaxis Python válida.")
        return True
    except SyntaxError as e:
        linea = e.lineno
        columna = e.offset
        mensaje = e.msg
        print(f"❌ Error de sintaxis en {ruta_archivo} línea {linea}, columna {columna}: {mensaje}")
        
        # Mostrar la línea problemática
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as file:
                lineas = file.readlines()
                if linea <= len(lineas):
                    print(f"Línea {linea}: {lineas[linea-1].rstrip()}")
                    print(" " * (columna + 8) + "^")
        except Exception:
            pass
        
        return False
    except Exception as e:
        print(f"❌ Error al leer o analizar {ruta_archivo}: {str(e)}")
        return False

if __name__ == "__main__":
    archivo = "c:\\Users\\rementeriama\\Downloads\\Code\\data-ia\\main.py"
    verificar_archivo_python(archivo)
