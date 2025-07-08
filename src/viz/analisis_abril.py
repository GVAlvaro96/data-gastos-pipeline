import matplotlib.pyplot as plt
import pandas as pd
import sys
from pathlib import Path
from ..config.database_conector import DatabaseConnector

try:
    with DatabaseConnector() as db:
        # Probar conexión básica
        result = db.execute_query("SELECT version();")

        print("✅ Conexión exitosa!")
        print(f"📋 Versión de PostgreSQL: {result[0]['version']}")
 
except Exception as e:
    print(f"❌ Error al conectar a la base de datos: {e}")

db = DatabaseConnector()

gastos_abril = pd.DataFrame()
gastos_abril = pd.read_sql("""
SELECT * FROM vw_gastos2025_abril ORDER BY fecha_operacion asc;""", db.get_connection())
print(f"📊 Datos de abril cargados: {len(gastos_abril)} filas")
print(gastos_abril.head())

print("🔍 Analizando gastos de abril...")
print(gastos_abril.describe())
nuemero_gatos = gastos_abril.describe()['fecha_operacion']['count']
print(f"📈 Número total de gastos en abril: {nuemero_gatos}")
gasto_total = gastos_abril['importe'].sum()
print(f"💰 Gasto total en abril: {gastos_abril['importe'].sum()}")
dia_mas_gastos = gastos_abril['fecha_operacion'].dt.day.value_counts().idxmax() 
gasto_dia_mas_gastos = gastos_abril[gastos_abril['fecha_operacion'].dt.day == dia_mas_gastos]['importe'].sum()
print(f"📅 Día con más gastos: {dia_mas_gastos} de abril, se gasto:{gasto_dia_mas_gastos} ")

#Graficos

# ##Mostraremos un grafico con los gastos por dia
# gastos_por_dia = gastos_abril.groupby(gastos_abril['fecha_operacion'].dt.day)['importe'].sum().reset_index() # agrupo por día y sumo los importes
# gastos_por_dia.columns = ['dia', 'importe'] # renombro las columnas para mayor claridad
# plt.figure(figsize=(12, 6)) # tamaño del gráfico
# plt.bar(gastos_por_dia['dia'], gastos_por_dia['importe'], color='skyblue') # color de las barras
# plt.title('Gastos por día en abril 2025')   # título del gráfico
# plt.xlabel('Día del mes') # etiqueta del eje X
# plt.ylabel('Importe total (€)') # etiqueta del eje Y
# plt.xticks(gastos_por_dia['dia']) # muestro todos los días del mes
# plt.grid(axis='y', linestyle='--', alpha=0.3) # líneas de la cuadrícula en el eje Y
# plt.tight_layout() # ajusta el diseño para que no se solapen los elementos
# print("📊 Gráfico de gastos por día generado.")
# plt.savefig(Path(__file__).parent / 'gastos_por_dia_abril.png')# Guardar el gráfico
# plt.show()# Mostrar el gráfico

# ##rafico de gasto por condepto
# gato_concepto = gastos_abril.groupby('concepto')['importe'].sum().reset_index() # agrupo por concepto y sumo los importes
# gato_concepto.columns = ['concepto', 'importe'] # renombro las columnas para mayor claridad
# plt.figure(figsize=(12, 6)) # tamaño del gráfico    
# plt.bar(gato_concepto['concepto'], gato_concepto['importe'], color='lightgreen') # color de las barras
# plt.title('Gastos por concepto en abril 2025')   # título del gráfico   
# plt.xlabel('Concepto') # etiqueta del eje X
# plt.ylabel('Importe total (€)') # etiqueta del eje Y
# plt.xticks(rotation=45, ha='right') # rotación de las etiquetas del eje X para mejor legibilidad
# plt.grid(axis='y', linestyle='--', alpha=0.3) # líneas de la cuadrícula en el eje Y
# plt.tight_layout() # ajusta el diseño para que no se solapen los elementos
# print("📊 Gráfico de gastos por concepto generado.")    
# plt.savefig(Path(__file__).parent / 'gastos_por_concepto_abril.png')# Guardar el gráfico
# plt.show()# Mostrar el gráfico

'''
Un histograma o boxplot para ver:

    Si haces muchos pequeños pagos o algunos grandes.

    Detectar valores atípicos (por ejemplo, una transferencia grande o una compra puntual).
'''

# Histograma de los importes de los gastos
plt.figure(figsize=(12, 6)) # tamaño del gráfico
plt.hist(gastos_abril['importe'], bins=150, color='purple', alpha=0.7) # color y transparencia de las barras
plt.title('Histograma de importes de gastos en abril 2025') # título del gráfico
plt.xlabel('Importe (€)') # etiqueta del eje X          
plt.ylabel('Frecuencia') # etiqueta del eje Y
plt.grid(axis='y', linestyle='--', alpha=0.3) # líneas de la cuadrícula en el eje Y
plt.tight_layout() # ajusta el diseño para que no se solapen los elementos
print("📊 Histograma de importes de gastos generado.")
plt.savefig(Path(__file__).parent / 'histograma_importes_abril.png')# Guardar el gráfico
plt.show()# Mostrar el gráfico