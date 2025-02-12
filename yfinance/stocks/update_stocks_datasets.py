#!/usr/bin/env python3
import os
import pandas as pd
import yfinance as yf

def main():
    # Lista de intervalos a descargar.
    intervals = [
        "1m", "2m", "5m", "15m", "30m",
        "60m", "90m", "1h", "1d", "5d",
        "1wk", "1mo", "3mo"
    ]

    # Definir el período adecuado para cada intervalo
    periodos_por_intervalo = {
        "1m": "7d",    # Solo se permiten 7-8 días de datos para este intervalo.
        "2m": "60d",
        "5m": "60d",
        "15m": "60d",
        "30m": "60d",
        "60m": "730d", # Ejemplo: 2 años de datos.
        "90m": "60d",  # Máximo permitido para este intervalo.
        "1h": "730d",
        "1d": "max",
        "5d": "max",
        "1wk": "max",
        "1mo": "max",
        "3mo": "max"
    }

    # Leer el fichero stocks.txt y obtener los tickers (ignorando líneas vacías o comentarios)
    try:
        with open("stocks.txt", "r") as f:
            tickers = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    except FileNotFoundError:
        print("El fichero 'stocks.txt' no se ha encontrado.")
        return

    # Procesar cada ticker
    for ticker in tickers:
        print(f"\nProcesando {ticker} ...")
        # Crear carpeta para el ticker en el directorio actual
        folder = os.path.join(os.getcwd(), ticker)
        os.makedirs(folder, exist_ok=True)

        # Para stocks no se añade sufijo; se usa el ticker tal cual
        ticker_yf = ticker

        # Descargar y guardar datos para cada intervalo
        for interval in intervals:
            periodo = periodos_por_intervalo.get(interval, "max")
            print(f"  Descargando datos en intervalo '{interval}' (period='{periodo}') para {ticker_yf}...")
            try:
                data = yf.Ticker(ticker_yf).history(interval=interval, period=periodo)
            except Exception as e:
                print(f"    Error al descargar {ticker_yf} para intervalo {interval}: {e}")
                continue

            if data.empty:
                print(f"    No se han obtenido datos para {ticker_yf} en el intervalo {interval}.")
                continue

            # Convertir el índice en una columna y renombrarla si es necesario
            data.reset_index(inplace=True)
            if "Datetime" in data.columns:
                data.rename(columns={"Datetime": "Date"}, inplace=True)
            # Asegurarse de que la columna "Date" sea de tipo datetime
            if "Date" in data.columns:
                data["Date"] = pd.to_datetime(data["Date"])

            # Definir el archivo CSV de salida
            output_file = os.path.join(folder, f"{ticker}_{interval}.csv")

            # Si el archivo CSV ya existe, cargarlo y concatenar los nuevos datos
            if os.path.exists(output_file):
                try:
                    data_existente = pd.read_csv(output_file, parse_dates=["Date"])
                except Exception as e:
                    print(f"    Error al leer {output_file}: {e}")
                    data_existente = pd.DataFrame()
                # Concatenar los datos existentes con los nuevos
                datos_combinados = pd.concat([data_existente, data])
                # Eliminar duplicados basándose en la columna "Date"
                datos_combinados.drop_duplicates(subset="Date", keep="last", inplace=True)
                # Ordenar los datos por fecha
                datos_combinados.sort_values("Date", inplace=True)
            else:
                datos_combinados = data

            # Guardar los datos (combinados o nuevos) en el archivo CSV
            try:
                datos_combinados.to_csv(output_file, index=False)
                print(f"    Datos guardados en {output_file}")
            except Exception as e:
                print(f"    Error al guardar los datos en {output_file}: {e}")

if __name__ == "__main__":
    main()
