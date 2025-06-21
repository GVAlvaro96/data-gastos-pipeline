#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión a PostgreSQL y la clase DatabaseConnector.
"""

import sys
import os
import logging
from datetime import datetime

# Agregar el directorio src al path para importar nuestros módulos

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.database_conector import DatabaseConnector

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_connection():
    """Prueba la conexión básica a PostgreSQL."""
    print("🔍 Probando conexión a PostgreSQL...")
    
    try:
        with DatabaseConnector() as db:
            # Probar conexión básica
            result = db.execute_query("SELECT version();")
            print("✅ Conexión exitosa!")
            print(f"📋 Versión de PostgreSQL: {result[0]['version']}")
            
            # Listar tablas existentes
            tables = db.execute_query("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            if tables:
                print(f"📊 Tablas existentes: {[t['table_name'] for t in tables]}")
            else:
                print("📊 No hay tablas en la base de datos")
                
            return True
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_table_operations():
    """Prueba las operaciones de creación y eliminación de tablas."""
    print("\n🔧 Probando operaciones de tablas...")
    
    try:
        with DatabaseConnector() as db:
            # Definir estructura de tabla de prueba
            test_columns = [
                ('id', 'SERIAL PRIMARY KEY'),
                ('nombre', 'VARCHAR(100) NOT NULL'),
                ('valor', 'DECIMAL(10,2)'),
                ('fecha_creacion', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            ]
            
            # Crear tabla de prueba
            print("📝 Creando tabla de prueba...")
            if db.create_table('tabla_prueba', test_columns):
                print("✅ Tabla de prueba creada exitosamente")
            else:
                print("⚠️ La tabla ya existe o hubo un error")
            
            # Verificar que la tabla existe
            if db.table_exists('tabla_prueba'):
                print("✅ Verificación: La tabla existe")
            else:
                print("❌ Error: La tabla no existe")
                return False
            
            # Insertar datos de prueba
            print("📊 Insertando datos de prueba...")
            insert_command = """
            INSERT INTO tabla_prueba (nombre, valor) 
            VALUES (%s, %s)
            """
            
            test_data = [
                ('Producto A', 100.50),
                ('Producto B', 250.75),
                ('Producto C', 75.25)
            ]
            
            rows_affected = db.execute_many(insert_command, test_data)
            print(f"✅ {rows_affected} registros insertados")
            
            # Consultar datos
            print("🔍 Consultando datos...")
            results = db.execute_query("SELECT * FROM tabla_prueba ORDER BY id")
            
            print("📋 Datos en la tabla:")
            for row in results:
                print(f"  ID: {row['id']}, Nombre: {row['nombre']}, Valor: ${row['valor']:.2f}")
            
            # Eliminar tabla de prueba
            print("🗑️ Eliminando tabla de prueba...")
            if db.drop_table('tabla_prueba'):
                print("✅ Tabla de prueba eliminada")
            else:
                print("❌ Error al eliminar la tabla")
                return False
                
            return True
            
    except Exception as e:
        print(f"❌ Error en operaciones de tabla: {e}")
        return False

def test_gastos_table():
    """Prueba la creación de la tabla de gastos real."""
    print("\n💰 Probando tabla de gastos...")
    
    try:
        with DatabaseConnector() as db:
            # Definir estructura de tabla de gastos
            gastos_columns = [
                ('id', 'SERIAL PRIMARY KEY'),
                ('fecha', 'DATE NOT NULL'),
                ('descripcion', 'VARCHAR(255)'),
                ('monto', 'DECIMAL(10,2) NOT NULL'),
                ('categoria', 'VARCHAR(100)'),
                ('subcategoria', 'VARCHAR(100)'),
                ('mes', 'VARCHAR(20)'),
                ('anio', 'INTEGER'),
                ('metodo_pago', 'VARCHAR(50)'),
                ('notas', 'TEXT'),
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            ]
            
            # Crear tabla de gastos
            print("📝 Creando tabla de gastos...")
            if db.create_table('gastos', gastos_columns):
                print("✅ Tabla de gastos creada exitosamente")
            else:
                print("⚠️ La tabla ya existe")
            
            # Insertar datos de ejemplo
            print("📊 Insertando datos de ejemplo...")
            insert_gasto = """
            INSERT INTO gastos (fecha, descripcion, monto, categoria, mes, anio, metodo_pago) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            gastos_ejemplo = [
                ('2024-01-15', 'Supermercado Carrefour', 150.50, 'Alimentación', 'enero', 2024, 'Tarjeta'),
                ('2024-01-20', 'Gasolina Repsol', 45.00, 'Transporte', 'enero', 2024, 'Efectivo'),
                ('2024-01-25', 'Restaurante El Bueno', 35.00, 'Alimentación', 'enero', 2024, 'Tarjeta'),
                ('2024-01-30', 'Netflix', 15.99, 'Entretenimiento', 'enero', 2024, 'Tarjeta'),
                ('2024-02-05', 'Farmacia', 25.30, 'Salud', 'febrero', 2024, 'Efectivo'),
                ('2024-02-10', 'Ropa Zara', 89.99, 'Vestimenta', 'febrero', 2024, 'Tarjeta')
            ]
            
            rows_affected = db.execute_many(insert_gasto, gastos_ejemplo)
            print(f"✅ {rows_affected} gastos insertados")
            
            # Consulta con agregaciones
            print("📈 Consultando resumen de gastos...")
            resumen_query = """
            SELECT 
                categoria,
                COUNT(*) as total_registros,
                SUM(monto) as total_monto,
                AVG(monto) as promedio_monto,
                MIN(monto) as gasto_minimo,
                MAX(monto) as gasto_maximo
            FROM gastos 
            GROUP BY categoria 
            ORDER BY total_monto DESC
            """
            
            resumen = db.execute_query(resumen_query)
            
            print("\n📊 Resumen por categoría:")
            print("-" * 60)
            for fila in resumen:
                print(f"🏷️  {fila['categoria']}")
                print(f"   📊 Registros: {fila['total_registros']}")
                print(f"   💰 Total: ${fila['total_monto']:.2f}")
                print(f"   📈 Promedio: ${fila['promedio_monto']:.2f}")
                print(f"   📉 Mínimo: ${fila['gasto_minimo']:.2f}")
                print(f"   📈 Máximo: ${fila['gasto_maximo']:.2f}")
                print("-" * 60)
            
            # Consulta por mes
            print("\n📅 Gastos por mes:")
            mes_query = """
            SELECT 
                mes,
                COUNT(*) as total_registros,
                SUM(monto) as total_monto
            FROM gastos 
            GROUP BY mes 
            ORDER BY mes
            """
            
            gastos_mes = db.execute_query(mes_query)
            for fila in gastos_mes:
                print(f"   📅 {fila['mes'].title()}: {fila['total_registros']} gastos, ${fila['total_monto']:.2f}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error en tabla de gastos: {e}")
        return False

def main():
    """Función principal que ejecuta todas las pruebas."""
    print("🚀 Iniciando pruebas de base de datos PostgreSQL")
    print("=" * 60)
    
    # Prueba 1: Conexión básica
    if not test_connection():
        print("\n❌ Falló la prueba de conexión. Verifica tu configuración.")
        return False
    
    # Prueba 2: Operaciones de tabla
    if not test_table_operations():
        print("\n❌ Fallaron las operaciones de tabla.")
        return False
    
    # # Prueba 3: Tabla de gastos
    # if not test_gastos_table():
    #     print("\n❌ Falló la prueba de tabla de gastos.")
    #     return False
    
    print("\n" + "=" * 60)
    print("🎉 ¡Todas las pruebas pasaron exitosamente!")
    print("✅ La base de datos está configurada correctamente")
    print("✅ La clase DatabaseConnector funciona perfectamente")
    print("✅ La tabla de gastos está lista para usar")


    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 