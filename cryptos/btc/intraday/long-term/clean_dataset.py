import pandas as pd

def clean_dataset(input_file, output_file=None):
    """
    Lee un archivo CSV con columnas originales:
    Date, Symbol, Open, High, Low, Close, Volume, CloseTime, QuoteVol, Trades, TakerBuyBase, TakerBuyQuote
    y lo transforma a un nuevo CSV con las columnas:
    Date, Close, High, Low, Open, Volume
    
    La columna Date se convierte a datetime con zona horaria UTC.
    
    Parámetros:
      - input_file: ruta del archivo CSV de entrada.
      - output_file: ruta del archivo CSV de salida. Si no se indica, la función retorna el DataFrame resultante.
    
    Retorna:
      - DataFrame con los datos limpios.
    """
    # Lee el CSV original
    df = pd.read_csv(input_file)
    
    # Convierte la columna Date a datetime y añade la zona horaria UTC
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize('UTC')
    
    # Selecciona y reordena las columnas deseadas:
    # En el CSV original las columnas son: Open, High, Low, Close, Volume (además de otras)
    # Queremos: Date, Close, High, Low, Open, Volume
    columnas_deseadas = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
    df_clean = df[columnas_deseadas]
    
    # Si se especifica ruta de salida, guarda el DataFrame en un nuevo CSV
    if output_file:
        df_clean.to_csv(output_file, index=False)
        print(f"Archivo procesado y guardado en: {output_file}")
    
    return df_clean

if __name__ == '__main__':
    # Lista de archivos CSV a procesar
    archivos = [
        'BTC-USD_1h.csv',
        'BTC-USD_4h.csv',
        'BTC-USD_15m.csv'
    ]
    
    for archivo in archivos:
        # Define el nombre del archivo de salida (por ejemplo, agregando el prefijo "clean_")
        salida = f"clean_{archivo}"
        # Procesa el archivo
        clean_dataset(archivo, salida)
