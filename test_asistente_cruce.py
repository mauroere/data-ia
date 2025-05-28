"""
Script para probar el asistente de cruce inteligente.

Ejecutar con: python test_asistente_cruce.py
"""

import pandas as pd
import sys
import os

# Añadir directorio actual al path para importar módulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from api_context import make_api_request_agente
    from api_fix import ensure_api_key_exists