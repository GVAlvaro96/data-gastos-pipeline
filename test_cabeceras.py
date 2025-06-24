#!/usr/bin/env python3
"""
Script de prueba para verificar la detección de cabeceras en DataFrames.
"""

import pandas as pd
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

from etl.transform_data import TransformData
from etl.logger import Logger

def test_deteccion_cabeceras():
    """Prueba la detección de cabeceras con diferentes formatos."""
    
    logger = Logger()
    transformer = TransformData(logger=logger)
    
    print("🧪 Probando detección de cabeceras...")
    print("=" * 60)
    
    # Test 1: DataFrame con cabeceras en español
    print("\n📋 Test 1: Cabeceras en español")
    df1 = pd.DataFrame({
        'Fecha Operación': ['Fecha Operación', '2025-01-20', '2025-01-21'],
        'Concepto': ['Concepto', 'Netflix', 'Spotify'],
        'Importe': ['Importe', 15.99, 9.99],
        'Saldo': ['Saldo', 1500.00, 1490.01]
    })
    print("DataFrame original:")
    print(df1.head())
    
    df1_limpio = transformer.limpiar_dataframe_para_carga(df1)
    print("\nDataFrame después de limpieza:")
    print(df1_limpio.head())
    
    # Test 2: DataFrame con cabeceras en inglés
    print("\n📋 Test 2: Cabeceras en inglés")
    df2 = pd.DataFrame({
        'Fecha Operación': ['Date', '2025-01-20', '2025-01-21'],
        'Concepto': ['Description', 'Netflix', 'Spotify'],
        'Importe': ['Amount', 15.99, 9.99],
        'Saldo': ['Balance', 1500.00, 1490.01]
    })
    print("DataFrame original:")
    print(df2.head())
    
    df2_limpio = transformer.limpiar_dataframe_para_carga(df2)
    print("\nDataFrame después de limpieza:")
    print(df2_limpio.head())
    
    # Test 3: DataFrame sin cabeceras (datos limpios)
    print("\n📋 Test 3: Sin cabeceras")
    df3 = pd.DataFrame({
        'Fecha Operación': ['2025-01-20', '2025-01-21'],
        'Concepto': ['Netflix', 'Spotify'],
        'Importe': [15.99, 9.99],
        'Saldo': [1500.00, 1490.01]
    })
    print("DataFrame original:")
    print(df3.head())
    
    df3_limpio = transformer.limpiar_dataframe_para_carga(df3)
    print("\nDataFrame después de limpieza:")
    print(df3_limpio.head())
    
    # Test 4: DataFrame con datos mixtos (cabeceras + datos inválidos)
    print("\n📋 Test 4: Datos mixtos")
    df4 = pd.DataFrame({
        'Fecha Operación': ['Fecha Operación', '2025-01-20', '2025-01-21', ''],
        'Concepto': ['Concepto', 'Netflix', 'Spotify', ''],
        'Importe': ['Importe', 15.99, 'texto_invalido', 0],
        'Saldo': ['Saldo', 1500.00, 1490.01, '']
    })
    print("DataFrame original:")
    print(df4.head())
    
    df4_limpio = transformer.limpiar_dataframe_para_carga(df4)
    print("\nDataFrame después de limpieza:")
    print(df4_limpio.head())
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")

def test_con_datos_reales():
    """Prueba con datos reales de tu directorio data."""
    print("\n🔍 Probando con datos reales...")
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("⚠️ Directorio 'data' no encontrado")
        return
    
    logger = Logger()
    transformer = TransformData(logger=logger)
    
    for file_path in data_dir.glob("*.csv"):
        print(f"\n📁 Procesando: {file_path.name}")
        
        try:
            # Cargar CSV
            df = pd.read_csv(file_path, sep=',', header=None, skiprows=9)
            df.columns = ['Fecha Operación', 'Concepto', 'Fecha Valor', 'Importe', 'Saldo', 'Referencia 1', 'Referencia 2']
            
            print(f"   Filas originales: {len(df)}")
            print("   Primera fila:")
            print(f"   {df.iloc[0].to_dict()}")
            
            # Aplicar limpieza
            df_limpio = transformer.limpiar_dataframe_para_carga(df)
            
            print(f"   Filas después de limpieza: {len(df_limpio)}")
            if len(df_limpio) > 0:
                print("   Primera fila después de limpieza:")
                print(f"   {df_limpio.iloc[0].to_dict()}")
            
        except Exception as e:
            print(f"   ❌ Error procesando {file_path.name}: {e}")

if __name__ == "__main__":
    test_deteccion_cabeceras()
    test_con_datos_reales() 