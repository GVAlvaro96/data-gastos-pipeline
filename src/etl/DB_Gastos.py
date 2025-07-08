from src.config.database_conector import DatabaseConnector
import pandas as pd
from typing import List, Dict, Any
import sys
from pathlib import Path
from .load_data import LoadData
from .transform_data import TransformData

# Agregar el directorio src al path para importaciones
sys.path.append(str(Path(__file__).parent))

# Directorio de datos
data_dir = Path("D:\WORKSPACE\data-gastos-pipeline\data")
# Definir columnas esperadas en los datos
columns = [
    'Fecha_Operacion', 
    'Concepto', 
    'Fecha_Valor', 
    'Importe', 
    'Saldo', 
    'Referencia_1',
    'Referencia_2'
]
loader = LoadData()
transformer = TransformData()

def cargar_dataframe_a_tabla(df: pd.DataFrame, tabla: str, db: DatabaseConnector) -> bool:
    """
    Carga un DataFrame a una tabla de PostgreSQL.
    
    Args:
        df: DataFrame de pandas a cargar
        tabla: Nombre de la tabla destino
        db: Instancia de DatabaseConnector
        
    Returns:
        bool: True si se cargó exitosamente
    """
    try:
        # Preparar los datos para inserción
        columnas = columns
        placeholders = ', '.join(['%s'] * len(columnas))
        columnas_str = ', '.join(columnas)
        
        # Crear comando INSERT
        insert_command = f"""
        INSERT INTO {tabla} ({columnas_str})
        VALUES ({placeholders})
        """
        
        # Convertir DataFrame a lista de tuplas
        datos = [tuple(row) for row in df.values]
        
        # Insertar datos
        filas_insertadas = db.execute_many(insert_command, datos)
        print(f"✅ {filas_insertadas} filas insertadas en la tabla {tabla}")
        return True
        
    except Exception as e:
        print(f"❌ Error al cargar DataFrame: {e}")
        return False


try:
    with DatabaseConnector() as db:
        # Probar conexión básica
        result = db.execute_query("SELECT version();")
        print("✅ Conexión exitosa!")
        print(f"📋 Versión de PostgreSQL: {result[0]['version']}")

        # Crear tabla de gastos
        if db.table_exists('gastos_2025'):
            print("✅ Tabla gastos_2025 ya existe")
        else:
            db.execute_command("""
            CREATE TABLE IF NOT EXISTS gastos_2025 (
                id SERIAL PRIMARY KEY NOT NULL,
                Fecha_Operacion TIMESTAMP NOT NULL, 
                Concepto VARCHAR(255), 
                Fecha_Valor TIMESTAMP, 
                Importe DECIMAL(10, 2), 
                Saldo DECIMAL(10, 2), 
                Referencia_1 VARCHAR(255),
                Referencia_2 VARCHAR(255)
            );
            """)
            print("✅ Tabla gastos_2025 creada exitosamente")


        for file_path in data_dir.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.csv', '.txt', '.xls', '.xlsx']:
                print(f"📋 Procesando archivo: {file_path}")
                
                # Cargar datos del archivo
                gastos_2025 = loader.load(str(file_path))
                # Aplicar transformaciones básicas
                df_clean = transformer.eliminar_duplicados(gastos_2025)
                df_clean = transformer.transformar_campos(df_clean, 0, 'datetime')
                df_clean = transformer.transformar_campos(df_clean, 1, 'text')
                df_clean = transformer.transformar_campos(df_clean, 2, 'datetime')
                df_clean = transformer.transformar_campos(df_clean, 3, 'float')
                df_clean = transformer.transformar_campos(df_clean, 4, 'float')
                df_clean = transformer.transformar_campos(df_clean, 5 ,'text')
                df_clean = transformer.transformar_campos(df_clean, 6 ,'text')
                df_clean = transformer.eliminar_duplicados(df_clean)
                # df_clean = transformer.limpiar_dataframe_para_carga(df_clean)
                
                # Agregar al DataFrame acumulado
                # argar_dataframe_a_tabla(df_clean, 'gastos_2025', db)
    

except Exception as e:
    print(f"❌ Error de conexión: {e}")

    