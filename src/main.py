#!/usr/bin/env python3
"""
Script principal para el pipeline de procesamiento de datos de gastos.
Este script implementa un pipeline ETL (Extract, Transform, Load) para procesar
archivos de gastos en diferentes formatos.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path para importaciones
sys.path.append(str(Path(__file__).parent))

from etl.load_data import LoadData
from etl.transform_data import TransformData
from etl.logger import Logger
from etl.DB_Gastos import cargar_gastos_desde_dataframe
from config.database_conector import DatabaseConnector


def main():
    """
    Función principal que ejecuta el pipeline ETL completo.
    """
    # Configuración inicial
    logger = Logger()
    logger.info("Iniciando pipeline de procesamiento de datos de gastos")
    
    # Definir columnas esperadas en los datos
    columns = [
        'Fecha Operación', 
        'Concepto', 
        'Fecha Valor', 
        'Importe', 
        'Saldo', 
        'Referencia 1',
        'Referencia 2'
    ]
    
    try:
        # 1. EXTRACT - Cargar datos
        logger.info("=== FASE 1: EXTRACT ===")
        loader = LoadData(columns, logger)
        
        # Directorio de datos
        data_dir = Path("D:\WORKSPACE\data-gastos-pipeline\data")
        
        # Procesar todos los archivos en el directorio data
        for file_path in data_dir.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.csv', '.txt', '.xls', '.xlsx']:
                logger.info(f"Procesando archivo: {file_path}")
                
                # Cargar datos del archivo
                gastos_2025 = loader.load(str(file_path))
                
                
                # Agregar al DataFrame acumulado
                loader.agregar_datos_al_dataframe(gastos_2025)
        
        # Mostrar vista previa de todos los datos cargados
        # loader.view_data()
        
        # 2. TRANSFORM - Transformar datos
        logger.info("=== FASE 2: TRANSFORM ===")
        transformer = TransformData(loader.df, logger)
        
        # Aplicar transformaciones básicas
        df_clean = transformer.eliminar_duplicados(loader.df)
        df_clean = transformer.transformar_campos(df_clean, 'Importe', 'float')
        df_clean = transformer.transformar_campos(df_clean, 'Saldo', 'float')
        df_clean = transformer.transformar_campos(df_clean, 'Fecha Operación', 'datetime')
        df_clean = transformer.transformar_campos(df_clean, 'Fecha Valor', 'datetime')
        df_clean = transformer.transformar_campos(df_clean, 'Referencia 1', 'str')
        df_clean = transformer.transformar_campos(df_clean, 'Referencia 2', 'str')
        df_clean = transformer.eliminar_duplicados(df_clean)

        # logger.info(f"Datos transformados: \n{df_clean.to_string()}")
        # loader.view_data()
        
        # Ejemplo de filtros (comentados para uso opcional)
        df_abril = transformer.filtrar_por_fecha(df_clean, '2025-04-01', '2025-04-30')
        df_abril = transformer.ordenar_por_fecha(df_abril)

        transformer.resumen(df_abril)
        transformer.resumen(df_clean)
  
        
    except Exception as e:
        logger.error(f"Error en el pipeline: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
