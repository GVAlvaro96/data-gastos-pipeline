from src.config.database_conector import DatabaseConnector

try:
    with DatabaseConnector() as db:
        # Probar conexión básica
        result = db.execute_query("SELECT version();")
        print("✅ Conexión exitosa!")
        print(f"📋 Versión de PostgreSQL: {result[0]['version']}")

except Exception as e:
    print(f"❌ Error de conexión: {e}")
        