from .logger import Logger
import pandas as pd

class LoadData:
    def __init__(self, logger=None):
        self.logger = logger or Logger()
        self.df = pd.DataFrame(columns=['Fecha Operación', 'Concepto', 'Fecha Valor', 'Importe', 'Saldo', 'Codigo'])

    def load(self, file_path):
        self.logger.info(f"Cargando archivo: {file_path}")
        if file_path.endswith('.csv') or file_path.endswith('.txt'):
            data = pd.read_csv(file_path, sep='|')
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            data = pd.read_excel(file_path)
        else:
            self.logger.error(f"Formato de archivo no soportado: {file_path}")
            raise ValueError(f"Formato de archivo no soportado: {file_path}")
        self.logger.info(f"Archivo cargado correctamente: {file_path}")
        return data

    def view_data(self, data):
        self.logger.info(data.head(10))

    def agregar_datos_al_dataframe(self, df, data):
        # Une los datos al DataFrame original
        self.df = pd.concat([self.df, data], ignore_index=True)
        return self.df


# Ejemplo de uso
if __name__ == "__main__":
    loader = LoadData()
    logger = loader.logger
    movimientos = loader.df

    logger.info(f"Estado actual de la tabla de movimientos: {movimientos.head(10)}")
    logger.info("Cargando datos de mayo")

    data_mayo_txt = loader.load("data/gastos_mayo.csv")

    loader.agregar_datos_al_dataframe(movimientos, data_mayo_txt)
    logger.info(f"Estado actual de la tabla de movimientos: {movimientos.head(100)}")
    

