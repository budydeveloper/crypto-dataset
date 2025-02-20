#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pip install --upgrade yfinance

import os
import json
import yfinance as yf
import pandas as pd
from datetime import timedelta

class UnifiedDataDownloader:
    """
    Clase unificada para descargar datos tanto históricos (no intradiarios) como intradiarios usando yfinance.

    Dependiendo del intervalo solicitado, se aplica:
      - Para intervalos históricos (ej: "1d", "1wk", "1mo"): descarga con period="max".
      - Para intervalos intradiarios (ej: "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"):
        descarga en bloques (chunks) debido a las limitaciones de yfinance.
    """

    def __init__(self, ticker, output_dir):
        """
        :param ticker: Símbolo del activo, por ejemplo "BTC-USD".
        :param output_dir: Directorio donde se guardarán los archivos CSV.
        """
        self.ticker = ticker
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # Definir los intervalos intradiarios reconocidos
        self.intraday_intervals = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}

    def flatten_columns(self, df):
        """
        Aplana las columnas del DataFrame en caso de MultiIndex o columnas que sean tuplas.
        """
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        else:
            # En caso de que alguna columna sea una tupla
            new_columns = []
            for col in df.columns:
                if isinstance(col, tuple):
                    new_columns.append(col[0])
                else:
                    new_columns.append(col)
            df.columns = new_columns
        return df

    def unify_columns(self, df):
        """
        Renombra y unifica las columnas a:
          datetime, open, high, low, close, volume
        y elimina la columna 'Adj Close' si existe.
        """
        rename_map = {}
        # Renombrar posibles nombres de columnas
        if "Date" in df.columns:
            rename_map["Date"] = "datetime"
        if "Datetime" in df.columns:
            rename_map["Datetime"] = "datetime"
        if "Open" in df.columns:
            rename_map["Open"] = "open"
        if "High" in df.columns:
            rename_map["High"] = "high"
        if "Low" in df.columns:
            rename_map["Low"] = "low"
        if "Close" in df.columns:
            rename_map["Close"] = "close"
        if "Volume" in df.columns:
            rename_map["Volume"] = "volume"

        df.rename(columns=rename_map, inplace=True)

        # Eliminar 'Adj Close' si existe
        if "Adj Close" in df.columns:
            df.drop(columns=["Adj Close"], inplace=True)

        # Convertir la columna 'datetime' a tipo datetime y eliminar posibles zonas horarias
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"], errors='coerce').dt.tz_localize(None)

        # Reordenar columnas (solo las que existan)
        final_cols = ["datetime", "open", "high", "low", "close", "volume"]
        final_cols = [col for col in final_cols if col in df.columns]
        df = df[final_cols]

        return df

    def download_interval(self, interval, save_csv=True, historical_days=None, chunk_days=None):
        """
        Descarga datos para un intervalo específico.

        :param interval: Intervalo de datos, ej: "1d", "1m", etc.
        :param save_csv: Si True, guarda los datos en un archivo CSV.
        :param historical_days: (Para datos intradiarios) Número total de días históricos a descargar.
        :param chunk_days: (Para datos intradiarios) Número de días por bloque de descarga.
        :return: DataFrame con los datos descargados.
        """
        if interval in self.intraday_intervals:
            # ----- Datos intradiarios -----
            # Definir valores por defecto si no se especifican
            if historical_days is None:
                if interval in ['1m', '2m', '5m', '15m', '30m']:
                    historical_days = 30
                elif interval in ['60m', '1h']:
                    historical_days = 90
                elif interval == '90m':
                    historical_days = 60
                else:
                    historical_days = 30
            if chunk_days is None:
                chunk_days = 8 if interval == '1m' else 15

            now = pd.Timestamp.now()
            end_date = now
            start_date = now - timedelta(days=historical_days) + timedelta(days=1)
            max_chunk = timedelta(days=chunk_days)

            data_frames = []
            current_start = start_date
            while current_start < end_date:
                current_end = min(current_start + max_chunk, end_date)
                print(f"Descargando datos intradiarios de {current_start.date()} a {current_end.date()} para {self.ticker} | intervalo {interval}")
                try:
                    df = yf.download(
                        self.ticker,
                        start=current_start.strftime("%Y-%m-%d"),
                        end=current_end.strftime("%Y-%m-%d"),
                        interval=interval,
                        progress=False
                    )
                    if not df.empty:
                        df.reset_index(inplace=True)
                        df = self.flatten_columns(df)
                        df = self.unify_columns(df)
                        data_frames.append(df)
                    else:
                        print("  No se obtuvieron datos en este periodo.")
                except Exception as e:
                    print(f"  Error descargando datos de {current_start.date()} a {current_end.date()}: {e}")
                current_start = current_end

            if not data_frames:
                print("No se han descargado datos intradiarios.")
                result = pd.DataFrame()
            else:
                result = pd.concat(data_frames, ignore_index=True)
                if "datetime" in result.columns:
                    result.drop_duplicates(subset=["datetime"], keep='first', inplace=True)
                    result.sort_values(by="datetime", inplace=True)

            if save_csv:
                filename = os.path.join(self.output_dir, f"{self.ticker}_{interval}.csv")
                if os.path.isfile(filename):
                    print(f"El archivo {filename} ya existe. Leyendo datos previos para concatenar...")
                    try:
                        existing_data = pd.read_csv(filename)
                        existing_data = self.unify_columns(existing_data)
                        result = pd.concat([existing_data, result], ignore_index=True)
                        if "datetime" in result.columns:
                            result.drop_duplicates(subset=["datetime"], keep='first', inplace=True)
                            result.sort_values(by="datetime", inplace=True)
                    except Exception as e:
                        print(f"  Error al leer el archivo existente: {e}")
                result.to_csv(filename, index=False, lineterminator='\n')
                print(f"Datos guardados/acumulados en: {filename}")

            return result

        else:
            # ----- Datos históricos (no intradiarios) -----
            print(f"Descargando datos históricos para {self.ticker} | intervalo {interval}")
            try:
                df = yf.download(self.ticker, period="max", interval=interval, progress=False)
                if not df.empty:
                    df = self.flatten_columns(df)
                    df.reset_index(inplace=True)
                    # Renombrar columnas para unificar
                    df.rename(columns={
                        "Date": "datetime",
                        "Open": "open",
                        "High": "high",
                        "Low": "low",
                        "Close": "close",
                        "Volume": "volume"
                    }, inplace=True)
                    if "Adj Close" in df.columns:
                        df.drop(columns=["Adj Close"], inplace=True)
                    df["datetime"] = pd.to_datetime(df["datetime"])
                    df = df[["datetime", "open", "high", "low", "close", "volume"]]

                    if save_csv:
                        filename = os.path.join(self.output_dir, f"{self.ticker}_{interval}.csv")
                        df.to_csv(filename, index=False, lineterminator='\n')
                        print(f"  Datos guardados en: {filename}")

                    return df
                else:
                    print(f"  No se han obtenido datos para el intervalo {interval}.")
                    return pd.DataFrame()
            except Exception as e:
                print(f"  Error al descargar datos históricos para el intervalo {interval}: {e}")
                return pd.DataFrame()

    def download(self, intervals, save_csv=True, intraday_params=None):
        """
        Descarga datos para una lista de intervalos.

        :param intervals: Lista de intervalos deseados, por ejemplo: ["1d", "1wk", "1mo", "1m", "15m", ...]
        :param save_csv: Si True, guarda los datos en archivos CSV.
        :param intraday_params: Diccionario opcional para parámetros intradiarios por intervalo,
                                ej: {"1m": {"historical_days": 30, "chunk_days": 8}, ...}
        :return: Diccionario con los intervalos como llaves y los DataFrames resultantes como valores.
        """
        results = {}
        for interval in intervals:
            params = {}
            if intraday_params and interval in intraday_params:
                params = intraday_params[interval]
            results[interval] = self.download_interval(interval, save_csv=save_csv, **params)
        return results

# ---------------------------------------------------------------------
# Ejecución principal
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Cargar el fichero cryptos.txt (archivo JSON con lista de tickers)
    with open("cryptos.txt", "r", encoding="utf-8") as f:
        tickers = json.load(f)

    # 2. Definir intervalos a descargar:
    #    - Intervalos históricos (no intradiarios)
    historical_intervals = ["1d", "1wk", "1mo"]
    #    - Intervalos intradiarios
    intraday_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]
    # Combinar intervalos (ajusta según lo que necesites)
    intervals = historical_intervals + intraday_intervals

    # 3. Opcional: parámetros específicos para datos intradiarios por intervalo
    intraday_params = {
        "1m": {"historical_days": 30, "chunk_days": 8},
        "2m": {"historical_days": 30, "chunk_days": 15},
        "5m": {"historical_days": 30, "chunk_days": 15},
        "15m": {"historical_days": 30, "chunk_days": 15},
        "30m": {"historical_days": 30, "chunk_days": 15},
        "60m": {"historical_days": 90, "chunk_days": 15},
        "90m": {"historical_days": 60, "chunk_days": 15},
        "1h": {"historical_days": 90, "chunk_days": 15},
    }

    # 4. Procesar cada ticker
    for ticker in tickers:
        # Generar directorio de salida basado en el ticker (por ejemplo, "BTC-USD" -> carpeta "btc")
        folder_name = ticker.split("-")[0].lower()
        output_directory = os.path.join(folder_name)
        print(f"\nDescargando datos para {ticker} en carpeta: {output_directory}")
        downloader = UnifiedDataDownloader(ticker, output_directory)
        downloader.download(intervals, save_csv=True, intraday_params=intraday_params)
