import os
import json
import yfinance as yf
import pandas as pd

class HistoricDataDownloader:
    """
    Clase para descargar datos históricos (no intradía) usando yfinance.
    """

    def __init__(self, ticker, output_dir):
        """
        :param ticker: Símbolo del activo, por ejemplo "BTC-USD"
        :param output_dir: Directorio donde se guardarán los archivos CSV.
        """
        self.ticker = ticker
        self.output_dir = output_dir
        # Crear el directorio si no existe
        os.makedirs(self.output_dir, exist_ok=True)

    def download(self, intervals, save_csv=True):
        """
        Descarga datos históricos (no intradía) para los intervalos especificados
        utilizando period="max".

        :param intervals: Lista de intervalos, ej. ["1d", "1wk", "1mo"]
        :param save_csv: Si True, guarda cada DataFrame en un archivo CSV.
        :return: Diccionario con los intervalos como llaves y los DataFrames como valores.
        """
        data_dict = {}
        for interval in intervals:
            print(f"\nDescargando datos históricos para {self.ticker} con intervalo: {interval}")
            try:
                df = yf.download(self.ticker, period="max", interval=interval, progress=False)
                if not df.empty:
                    # Si el DataFrame tiene columnas con MultiIndex, se extrae el nivel 0 para aplanarlo
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    # Reiniciamos el índice para que la fecha quede como columna
                    df.reset_index(inplace=True)

                    data_dict[interval] = df
                    if save_csv:
                        filename = os.path.join(self.output_dir, f"{self.ticker}_{interval}.csv")
                        df.to_csv(filename, index=False, lineterminator='\n')
                        print(f"  Datos guardados en: {filename}")
                    else:
                        print(f"  Datos descargados para el intervalo {interval}.")
                else:
                    print(f"  No se han obtenido datos para el intervalo {interval}.")
            except Exception as e:
                print(f"  Error al descargar datos para el intervalo {interval}: {e}")
        return data_dict

if __name__ == "__main__":
    # 1. Leer el archivo cryptos.txt, que ahora contiene únicamente una lista de tickers.
    # Ejemplo de formato de cryptos.txt:
    # [
    #     "BTC-USD",
    #     "ETH-USD",
    #     "XRP-USD",
    #     ...
    # ]
    with open("cryptos.txt", "r", encoding="utf-8") as f:
        tickers = json.load(f)

    # 2. Definir los intervalos históricos deseados
    historic_intervals = ["1d", "1wk", "1mo"]

    # 3. Procesar cada ticker de la lista
    for ticker in tickers:
        # Generamos un nombre de carpeta a partir del ticker.
        # Por ejemplo, "BTC-USD" se transformará en "btc"
        folder_name = ticker.split("-")[0].lower()
        output_directory = folder_name
        print(f"\nDescargando datos para {ticker} en carpeta: {output_directory}")
        downloader = HistoricDataDownloader(ticker, output_directory)
        downloader.download(historic_intervals, save_csv=True)
