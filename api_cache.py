import os
import json
import hashlib
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_cache.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("api_cache")

class APICache:
    """
    Sistema de caché para respuestas de API que permite reducir el número de peticiones
    """
    
    def __init__(self, cache_dir=None, ttl_hours=24):
        """
        Inicializa el sistema de caché
        
        Args:
            cache_dir: Directorio donde se almacenarán los archivos de caché
            ttl_hours: Tiempo de vida de las entradas en caché (horas)
        """
        # Determinar el directorio de caché
        if cache_dir is None:
            # Usar directorio por defecto
            self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
        else:
            self.cache_dir = cache_dir
            
        # Crear directorio si no existe
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.ttl = timedelta(hours=ttl_hours)
        logger.info(f"Caché inicializada en {self.cache_dir} con TTL de {ttl_hours} horas")
    
    def get_cache_key(self, data):
        """
        Genera una clave única para los datos
        
        Args:
            data: Datos para los que generar la clave
            
        Returns:
            str: Clave única para los datos
        """
        # Convertir a JSON ordenado y calcular hash MD5
        hash_input = json.dumps(data, sort_keys=True)
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def get_cache_path(self, cache_key):
        """
        Obtiene la ruta al archivo de caché
        
        Args:
            cache_key: Clave de caché
            
        Returns:
            str: Ruta absoluta al archivo de caché
        """
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, query_data):
        """
        Obtiene un resultado de la caché si existe y es válido
        
        Args:
            query_data: Datos de la consulta
            
        Returns:
            dict: Datos almacenados en caché o None si no existen o han expirado
        """
        cache_key = self.get_cache_key(query_data)
        cache_path = self.get_cache_path(cache_key)
        
        # Verificar si existe el archivo de caché
        if not os.path.exists(cache_path):
            logger.debug(f"No existe caché para {cache_key}")
            return None
        
        try:
            # Verificar si ha expirado
            file_modified_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
            if datetime.now() - file_modified_time > self.ttl:
                logger.debug(f"Caché expirada para {cache_key}")
                return None
            
            # Leer datos de caché
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                
            logger.info(f"Usando datos en caché para {cache_key}")
            return cached_data
        
        except Exception as e:
            logger.error(f"Error al leer caché: {str(e)}")
            return None
    
    def set(self, query_data, result_data):
        """
        Almacena un resultado en la caché
        
        Args:
            query_data: Datos de la consulta
            result_data: Datos de respuesta a almacenar
            
        Returns:
            bool: True si se almacenó correctamente, False en caso contrario
        """
        cache_key = self.get_cache_key(query_data)
        cache_path = self.get_cache_path(cache_key)
        
        try:
            # Guardar datos en caché
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Datos almacenados en caché para {cache_key}")
            return True
        
        except Exception as e:
            logger.error(f"Error al escribir caché: {str(e)}")
            return False
    
    def clear_expired(self):
        """
        Elimina todas las entradas expiradas de la caché
        
        Returns:
            int: Número de archivos eliminados
        """
        now = datetime.now()
        files_removed = 0
        
        try:
            # Recorrer todos los archivos de caché
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.cache_dir, filename)
                    
                    # Verificar tiempo de modificación
                    modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if now - modified_time > self.ttl:
                        # Eliminar archivo expirado
                        os.remove(filepath)
                        files_removed += 1
            
            logger.info(f"Se eliminaron {files_removed} archivos de caché expirados")
            return files_removed
            
        except Exception as e:
            logger.error(f"Error al limpiar caché: {str(e)}")
            return 0
    
    def clear_all(self):
        """
        Elimina todas las entradas de la caché
        
        Returns:
            int: Número de archivos eliminados
        """
        files_removed = 0
        
        try:
            # Recorrer todos los archivos de caché
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.cache_dir, filename)
                    
                    # Eliminar archivo
                    os.remove(filepath)
                    files_removed += 1
            
            logger.info(f"Se eliminaron todos los {files_removed} archivos de caché")
            return files_removed
            
        except Exception as e:
            logger.error(f"Error al limpiar caché: {str(e)}")
            return 0
    
    def get_stats(self):
        """
        Obtiene estadísticas de uso de la caché
        
        Returns:
            dict: Estadísticas de uso de la caché
        """
        try:
            # Contar archivos y espacio usado
            file_count = 0
            total_size = 0
            oldest_file = None
            newest_file = None
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.cache_dir, filename)
                    file_count += 1
                    
                    # Tamaño
                    file_size = os.path.getsize(filepath)
                    total_size += file_size
                    
                    # Tiempo de modificación
                    modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    # Actualizar archivos más antiguo y más reciente
                    if oldest_file is None or modified_time < oldest_file[1]:
                        oldest_file = (filename, modified_time)
                    
                    if newest_file is None or modified_time > newest_file[1]:
                        newest_file = (filename, modified_time)
            
            return {
                "file_count": file_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "oldest_file": oldest_file[0] if oldest_file else None,
                "oldest_file_date": oldest_file[1].isoformat() if oldest_file else None,
                "newest_file": newest_file[0] if newest_file else None,
                "newest_file_date": newest_file[1].isoformat() if newest_file else None,
                "cache_dir": self.cache_dir,
                "ttl_hours": self.ttl.total_seconds() / 3600
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {str(e)}")
            return {
                "error": str(e)
            }


# Función auxiliar para usar en otros módulos
def get_api_cache(ttl_hours=24):
    """
    Obtiene una instancia del sistema de caché
    
    Args:
        ttl_hours: Tiempo de vida de las entradas en caché (horas)
        
    Returns:
        APICache: Instancia del sistema de caché
    """
    return APICache(ttl_hours=ttl_hours)
