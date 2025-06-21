# Configuración de Base de Datos PostgreSQL

Este documento explica cómo configurar y usar la base de datos PostgreSQL en el proyecto de pipeline de gastos.

## 📋 Requisitos Previos

1. **PostgreSQL instalado** en tu sistema
2. **Python 3.8+** con pip
3. **Dependencias del proyecto** instaladas

## 🔧 Configuración Inicial

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

1. **Copiar el archivo de ejemplo:**
   ```bash
   cp env.example .env
   ```

2. **Editar el archivo `.env`** con tus credenciales:
   ```bash
   # Configuración de Base de Datos PostgreSQL
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=data_gastos
   DB_USER=postgres
   DB_PASSWORD=tu_contraseña_real
   
   # Configuración del Pool de Conexiones
   DB_MIN_CONNECTIONS=1
   DB_MAX_CONNECTIONS=10
   
   # Configuración de Logging
   LOG_LEVEL=INFO
   LOG_FILE=logs/pipeline.log
   
   # Configuración de la Aplicación
   APP_ENV=development
   DEBUG=True
   ```

### 3. Crear la Base de Datos

```sql
-- Conectar a PostgreSQL como superusuario
psql -U postgres

-- Crear la base de datos
CREATE DATABASE data_gastos;

-- Crear usuario (opcional)
CREATE USER gastos_user WITH PASSWORD 'tu_contraseña';

-- Dar permisos al usuario
GRANT ALL PRIVILEGES ON DATABASE data_gastos TO gastos_user;

-- Salir de psql
\q
```

## 🚀 Uso de la Clase DatabaseConnector

### Ejemplo Básico

```python
from src.config.database_conector import DatabaseConnector

# Crear instancia del conector
db = DatabaseConnector()

# Verificar conexión
try:
    db.create_connection_pool()
    print("✅ Conexión exitosa a PostgreSQL")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
```

### Ejemplos de Uso

#### 1. Crear Tabla de Gastos

```python
# Definir estructura de la tabla
columnas_gastos = [
    ('id', 'SERIAL PRIMARY KEY'),
    ('fecha', 'DATE NOT NULL'),
    ('descripcion', 'VARCHAR(255)'),
    ('monto', 'DECIMAL(10,2) NOT NULL'),
    ('categoria', 'VARCHAR(100)'),
    ('mes', 'VARCHAR(20)'),
    ('anio', 'INTEGER'),
    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
]

# Crear tabla
db.create_table('gastos', columnas_gastos)
```

#### 2. Insertar Datos

```python
# Insertar un registro
comando = """
INSERT INTO gastos (fecha, descripcion, monto, categoria, mes, anio) 
VALUES (%s, %s, %s, %s, %s, %s)
"""
db.execute_command(comando, ('2024-01-15', 'Supermercado', 150.50, 'Alimentación', 'enero', 2024))

# Insertar múltiples registros
datos = [
    ('2024-01-20', 'Gasolina', 45.00, 'Transporte', 'enero', 2024),
    ('2024-01-25', 'Restaurante', 35.00, 'Alimentación', 'enero', 2024),
    ('2024-01-30', 'Netflix', 15.99, 'Entretenimiento', 'enero', 2024)
]
db.execute_many(comando, datos)
```

#### 3. Consultar Datos

```python
# Consulta simple
resultados = db.execute_query("SELECT * FROM gastos WHERE mes = %s", ('enero',))

# Consulta con agregaciones
query_agregada = """
SELECT 
    categoria,
    COUNT(*) as total_registros,
    SUM(monto) as total_monto,
    AVG(monto) as promedio_monto
FROM gastos 
WHERE anio = %s 
GROUP BY categoria 
ORDER BY total_monto DESC
"""
resumen = db.execute_query(query_agregada, (2024,))

for fila in resumen:
    print(f"Categoría: {fila['categoria']}")
    print(f"Total: ${fila['total_monto']:.2f}")
    print(f"Promedio: ${fila['promedio_monto']:.2f}")
    print("---")
```

#### 4. Uso con Context Manager

```python
# Manejo seguro de conexiones
with DatabaseConnector() as db:
    # Verificar si la tabla existe
    if not db.table_exists('gastos'):
        print("Creando tabla gastos...")
        db.create_table('gastos', columnas_gastos)
    
    # Ejecutar operaciones
    db.execute_command("INSERT INTO gastos (fecha, monto) VALUES (%s, %s)", 
                      ('2024-01-01', 100.00))
    
    # Las conexiones se cierran automáticamente
```

## 🔍 Verificación de Conexión

### Script de Prueba

```python
# test_connection.py
from src.config.database_conector import DatabaseConnector
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

def test_connection():
    try:
        with DatabaseConnector() as db:
            # Probar conexión
            result = db.execute_query("SELECT version();")
            print("✅ Conexión exitosa!")
            print(f"Versión de PostgreSQL: {result[0]['version']}")
            
            # Listar tablas existentes
            tables = db.execute_query("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            print(f"📋 Tablas existentes: {[t['table_name'] for t in tables]}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_connection()
```

## 🛠️ Solución de Problemas

### Error: "connection to server failed"

1. **Verificar que PostgreSQL esté ejecutándose:**
   ```bash
   # Windows
   net start postgresql-x64-15
   
   # Linux/Mac
   sudo systemctl status postgresql
   ```

2. **Verificar credenciales en `.env`**
3. **Verificar que la base de datos existe**

### Error: "authentication failed"

1. **Verificar usuario y contraseña**
2. **Verificar permisos del usuario**
3. **Verificar configuración de `pg_hba.conf`**

### Error: "database does not exist"

```sql
-- Crear la base de datos
CREATE DATABASE data_gastos;
```

## 📊 Estructura Recomendada de Tablas

### Tabla Principal: `gastos`

```sql
CREATE TABLE gastos (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    descripcion VARCHAR(255),
    monto DECIMAL(10,2) NOT NULL,
    categoria VARCHAR(100),
    subcategoria VARCHAR(100),
    mes VARCHAR(20),
    anio INTEGER,
    metodo_pago VARCHAR(50),
    notas TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabla de Categorías: `categorias`

```sql
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    color VARCHAR(7),
    icono VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔐 Seguridad

- ✅ El archivo `.env` está en `.gitignore`
- ✅ Las credenciales no se suben al repositorio
- ✅ Uso de parámetros preparados para prevenir SQL injection
- ✅ Pool de conexiones para mejor rendimiento

## 📝 Notas Importantes

1. **Siempre usa parámetros preparados** para evitar SQL injection
2. **Cierra las conexiones** usando context managers
3. **Maneja las excepciones** apropiadamente
4. **Usa transacciones** para operaciones críticas
5. **Monitorea el pool de conexiones** en producción 