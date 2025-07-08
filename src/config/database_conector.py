import psycopg2
import psycopg2.extras
from psycopg2 import pool
import logging
from typing import Optional, List, Dict, Any, Tuple
import os
from contextlib import contextmanager
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class DatabaseConnector:
    """
    Clase para manejar conexiones a base de datos PostgreSQL.
    Incluye funcionalidades para pool de conexiones, transacciones y logging.
    """
    
    def __init__(self, 
                 host: str = None,
                 port: int = 5432,
                 database: str = None,
                 user: str = None,
                 password: str = None,
                 min_connections: int = 1,
                 max_connections: int = 10):
        """
        Inicializa el conector de base de datos.
        
        Args:
            host: Host de la base de datos
            port: Puerto de la base de datos (default: 5432)
            database: Nombre de la base de datos
            user: Usuario de la base de datos
            password: Contraseña de la base de datos
            min_connections: Número mínimo de conexiones en el pool
            max_connections: Número máximo de conexiones en el pool
        """
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or int(os.getenv('DB_PORT', 5432))
        self.database = database or os.getenv('DB_NAME', 'postgres')
        self.user = user or os.getenv('DB_USER', 'postgres')
        self.password = password or os.getenv('DB_PASSWORD', '')
        
        self.min_connections = min_connections
        self.max_connections = max_connections
        
        self.connection_pool = None
        self.logger = logging.getLogger(__name__)
        
    def create_connection_pool(self) -> bool:
        """
        Crea un pool de conexiones a la base de datos.
        
        Returns:
            bool: True si el pool se creó exitosamente, False en caso contrario
        """
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=self.min_connections,
                maxconn=self.max_connections,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.logger.info(f"Pool de conexiones creado exitosamente para {self.database}")
            return True
        except Exception as e:
            self.logger.error(f"Error al crear el pool de conexiones: {str(e)}")
            return False
    
    def get_connection(self):
        """
        Obtiene una conexión del pool.
        
        Returns:
            Connection: Conexión de PostgreSQL
        """
        if not self.connection_pool:
            if not self.create_connection_pool():
                raise Exception("No se pudo crear el pool de conexiones")
        
        try:
            connection = self.connection_pool.getconn()
            if connection:
                self.logger.debug("Conexión obtenida del pool")
                return connection
            else:
                raise Exception("No se pudo obtener una conexión del pool")
        except Exception as e:
            self.logger.error(f"Error al obtener conexión del pool: {str(e)}")
            raise
    
    def return_connection(self, connection):
        """
        Devuelve una conexión al pool.
        
        Args:
            connection: Conexión a devolver
        """
        if self.connection_pool and connection:
            self.connection_pool.putconn(connection)
            self.logger.debug("Conexión devuelta al pool")
    
    @contextmanager
    def get_db_connection(self):
        """
        Context manager para manejar conexiones de forma segura.
        
        Yields:
            Connection: Conexión de PostgreSQL
        """
        connection = None
        try:
            connection = self.get_connection()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            self.logger.error(f"Error en la conexión: {str(e)}")
            raise
        finally:
            if connection:
                self.return_connection(connection)
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SELECT y retorna los resultados.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)
            
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con los resultados
        """
        with self.get_db_connection() as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
    
    def execute_command(self, command: str, params: tuple = None) -> int:
        """
        Ejecuta un comando INSERT, UPDATE, DELETE y retorna el número de filas afectadas.
        
        Args:
            command: Comando SQL a ejecutar
            params: Parámetros para el comando (opcional)
            
        Returns:
            int: Número de filas afectadas
        """
        with self.get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(command, params)
                connection.commit()
                return cursor.rowcount
    
    def execute_many(self, command: str, params_list: List[tuple]) -> int:
        """
        Ejecuta un comando múltiples veces con diferentes parámetros.
        
        Args:
            command: Comando SQL a ejecutar
            params_list: Lista de tuplas de parámetros
            
        Returns:
            int: Número total de filas afectadas
        """
        with self.get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(command, params_list)
                connection.commit()
                return cursor.rowcount
    
    def table_exists(self, table_name: str) -> bool:
        """
        Verifica si una tabla existe en la base de datos.
        
        Args:
            table_name: Nombre de la tabla a verificar
            
        Returns:
            bool: True si la tabla existe, False en caso contrario
        """
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
        """
        result = self.execute_query(query, (table_name,))
        return result[0]['exists'] if result else False
    
    def create_table(self, table_name: str, columns: List[Tuple[str, str]]) -> bool:
        """
        Crea una tabla en la base de datos.
        
        Args:
            table_name: Nombre de la tabla
            columns: Lista de tuplas (nombre_columna, tipo_dato)
            
        Returns:
            bool: True si la tabla se creó exitosamente
        """
        if self.table_exists(table_name):
            self.logger.warning(f"La tabla {table_name} ya existe")
            return True
        
        columns_def = ", ".join([f"{col[0]} {col[1]}" for col in columns])
        command = f"CREATE TABLE {table_name} ({columns_def})"
        
        try:
            self.execute_command(command)
            self.logger.info(f"Tabla {table_name} creada exitosamente")
            return True
        except Exception as e:
            self.logger.error(f"Error al crear la tabla {table_name}: {str(e)}")
            return False
    
    def drop_table(self, table_name: str) -> bool:
        """
        Elimina una tabla de la base de datos.
        
        Args:
            table_name: Nombre de la tabla a eliminar
            
        Returns:
            bool: True si la tabla se eliminó exitosamente
        """
        if not self.table_exists(table_name):
            self.logger.warning(f"La tabla {table_name} no existe")
            return True
        
        command = f"DROP TABLE IF EXISTS {table_name}"
        
        try:
            self.execute_command(command)
            self.logger.info(f"Tabla {table_name} eliminada exitosamente")
            return True
        except Exception as e:
            self.logger.error(f"Error al eliminar la tabla {table_name}: {str(e)}")
            return False
    
    def close_pool(self):
        """
        Cierra el pool de conexiones.
        """
        if self.connection_pool:
            self.connection_pool.closeall()
            self.logger.info("Pool de conexiones cerrado")
    
    def __enter__(self):
        """
        Context manager entry.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        """
        self.close_pool()
