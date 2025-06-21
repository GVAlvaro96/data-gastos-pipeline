##limpieza, categorías, agrupaciones, etc.

from .load_data import LoadData
from .logger import Logger
import pandas as pd


class TransformData:
    def __init__(self, df, logger=None):
        self.logger = logger or Logger()
        self.df = None

    def eliminar_duplicados(self, df):
        self.logger.info("Eliminando duplicados")
        self.df = df.drop_duplicates()
        self.logger.info(f"Duplicados eliminados: {self.df.shape[0]}")
        return self.df

    def filtrar_por_fecha(self, df, fecha_inicio, fecha_fin):
        self.logger.info(f"Filtrando por fecha: {fecha_inicio} a {fecha_fin}")
        
        # Convertir las cadenas de fecha a objetos datetime para una comparación correcta
        fecha_inicio_dt = pd.to_datetime(fecha_inicio)
        fecha_fin_dt = pd.to_datetime(fecha_fin)
        
        # Aplicar el filtro usando las fechas convertidas
        self.df = df[(df['Fecha Operación'] >= fecha_inicio_dt) & (df['Fecha Operación'] <= fecha_fin_dt)]
        
        self.logger.info(f"Filtrado por fecha: {self.df.shape[0]}")
        return self.df
    
    def filtrar_por_concepto(self, df, concepto):
        self.logger.info(f"Filtrando por concepto: {concepto}")
        self.df = df[df['Concepto'].str.contains(concepto)]
        self.logger.info(f"Filtrado por concepto: {self.df.shape[0]}")
        return self.df
    
    def filtrar_por_importe(self, df, importe_minimo, importe_maximo):
        self.logger.info(f"Filtrando por importe: {importe_minimo} a {importe_maximo}")
        self.df = df[df['Importe'] >= importe_minimo]
        self.df = df[df['Importe'] <= importe_maximo]
        self.logger.info(f"Filtrado por importe: {self.df.shape[0]}")
        return self.df
    
    def ordenar_por_fecha(self, df):
        self.logger.info("Ordenando por fecha")
        self.df = df.sort_values(by='Fecha Operación')
        self.logger.info(f"Ordenado por fecha: {self.df.shape[0]}")
        return self.df

    def transformar_campos(self, df, campo, tipo):
        self.logger.info(f"Transformando campo '{campo}' a tipo '{tipo}'")
        try:
            if tipo == 'float':
                # Reemplazar comas de miles y convertir a float
                df[campo] = df[campo].astype(str).str.replace(',', '', regex=False).astype(float)
            elif tipo == 'datetime':
                # Usar pd.to_datetime para convertir a fecha
                df[campo] = pd.to_datetime(df[campo], dayfirst=True, errors='coerce')
            else:
                # Conversión estándar para otros tipos
                df = df.astype({campo: tipo})
            
            self.logger.info(f"Campo '{campo}' transformado exitosamente a '{tipo}'")
            return df
        except Exception as e:
            self.logger.error(f"Error al transformar el campo '{campo}': {e}")
            raise TypeError(f"Error while type casting for column '{campo}'")

    
    def resumen(self, df):
        self.logger.info("Generando resumen")
        self.logger.info(f"Numero total de movimientos:\n {df.shape[0]} ")
        self.logger.info(f"Resumen: \n{df.describe().to_string()}")
        # self.logger.info(f"Resumen por concepto: \n{df.groupby('Concepto').describe().to_string()}")
        self.logger.info(f"Conteo por concepto: \n{df['Concepto'].value_counts().to_string()}")