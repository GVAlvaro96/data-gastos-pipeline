import pandas as pd
from .logger import Logger

class LoadData:
    def __init__(self,columns=None,logger=None):
        self.logger = logger or Logger()
        self.columns = columns
        self.df = pd.DataFrame([],columns=self.columns)

    def load(self, file_path):
        self.logger.info(f"Cargando archivo: {file_path}")
        if file_path.endswith(('.csv', '.txt')):
            data = pd.read_csv(file_path, sep=',', header=None, skiprows=9)
            if self.columns:
                data.columns = self.columns
         
        elif file_path.endswith(('.xlsx', '.xls')):
            data = pd.read_excel(file_path, header=None)
            if self.columns:
                data.columns = self.columns
        else:
            self.logger.error(f"Formato de archivo no soportado: {file_path}")
            raise ValueError(f"Formato de archivo no soportado: {file_path}")
        self.logger.info(f"Archivo cargado correctamente: {file_path}")
        return data
    
 
    def agregar_datos_al_dataframe(self, data):
        self.logger.info(f"Agregando nuevos datos al DataFrame")
        self.df = pd.concat([self.df, data], ignore_index=True)
        return self.df

    def view_data(self):
        self.logger.info(f"Vista previa del DataFrame acumulado:\n{self.df.head(100)}")



