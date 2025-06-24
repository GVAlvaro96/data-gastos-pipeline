##limpieza, categorías, agrupaciones, etc.

from .load_data import LoadData
from .logger import Logger
import pandas as pd


class TransformData:
    def __init__(self, df=None, logger=None):
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

    def limpiar_dataframe_para_carga(self, df) -> pd.DataFrame:
        """
        Limpia el DataFrame eliminando cabeceras y filas problemáticas.
        
        Args:
            df: DataFrame original
            
        Returns:
            pd.DataFrame: DataFrame limpio listo para cargar
        """
        try:
            df_limpio = df.copy()
            self.logger.info(f"🧹 Iniciando limpieza de DataFrame con {len(df_limpio)} filas")
            
            # 1. Verificar si la primera fila contiene cabeceras
            if len(df_limpio) > 0:
                primera_fila = df_limpio.iloc[0]
                tiene_cabeceras = False
                
                # Detectar si la primera fila contiene nombres de columnas
                # Buscar coincidencias exactas o parciales con nombres de columnas esperados
                nombres_cabeceras = [
                    'fecha operación', 'fecha_operacion', 'fecha operacion',
                    'concepto', 'descripción', 'descripcion',
                    'fecha valor', 'fecha_valor', 'fecha valor',
                    'importe', 'monto', 'cantidad',
                    'saldo', 'balance',
                    'referencia 1', 'referencia_1', 'ref1',
                    'referencia 2', 'referencia_2', 'ref2'
                ]
                
                # Verificar cada valor en la primera fila
                for col in df_limpio.columns:
                    valor_primera_fila = str(primera_fila[col]).lower().strip()
                    self.logger.info(f"   Verificando columna '{col}': '{valor_primera_fila}'")
                    
                    if valor_primera_fila in nombres_cabeceras:
                        tiene_cabeceras = True
                        self.logger.info(f"   ✅ Detectada cabecera en columna '{col}': '{valor_primera_fila}'")
                        break
                
                # 2. Eliminar primera fila si contiene cabeceras
                if tiene_cabeceras:
                    self.logger.info("🧹 Detectadas cabeceras en primera fila, eliminando...")
                    df_limpio = df_limpio.iloc[1:].reset_index(drop=True)
                    self.logger.info(f"   Filas restantes después de eliminar cabeceras: {len(df_limpio)}")
                else:
                    self.logger.info("✅ No se detectaron cabeceras en la primera fila")
            
            # 3. Filtrar filas con datos válidos
            if len(df_limpio) > 0:
                # Eliminar filas donde Importe no sea numérico
                filas_antes = len(df_limpio)
                df_limpio = df_limpio[pd.to_numeric(df_limpio['Importe'], errors='coerce').notna()]
                filas_despues = len(df_limpio)
                
                if filas_antes != filas_despues:
                    self.logger.info(f"   🗑️ Eliminadas {filas_antes - filas_despues} filas con Importe inválido")
                
                # 4. Eliminar filas completamente vacías
                filas_antes = len(df_limpio)
                df_limpio = df_limpio.dropna(how='all')
                filas_despues = len(df_limpio)
                
                if filas_antes != filas_despues:
                    self.logger.info(f"   🗑️ Eliminadas {filas_antes - filas_despues} filas completamente vacías")
            
            self.logger.info(f"✅ DataFrame limpio: {len(df_limpio)} filas válidas de {len(df)} originales")
            return df_limpio
            
        except Exception as e:
            self.logger.error(f"❌ Error al limpiar DataFrame: {e}")
            return df
        