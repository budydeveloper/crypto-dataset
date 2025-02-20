#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import pandas as pd
from datetime import timedelta
from binance.client import Client
from tqdm.autonotebook import tqdm

class UnifiedDataDownloader:
    """
    Clase unificada para descargar datos históricos e intradiarios desde Binance.
    Para los intervalos intradiarios se descarga en bloques (chunks) para sortear el límite de 1000 velas.
    Ahora se conserva la información completa devuelta por Binance.
    """

    def __init__(self, ticker, output_dir):
        """
        :param ticker: Símbolo del par en formato Binance, por ejemplo "BTCUSDT".
        :param output_dir: Directorio donde se guardarán los archivos CSV.
        """
        self.ticker = ticker
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # Instanciar el cliente de Binance (puedes pasar API key y secret si lo requieres)
        self.client = Client()
        
        # Mapeo de intervalos que Binance acepta
        self.binance_interval_map = {
            "1m": Client.KLINE_INTERVAL_1MINUTE,
            "5m": Client.KLINE_INTERVAL_5MINUTE,
            "15m": Client.KLINE_INTERVAL_15MINUTE,
            "30m": Client.KLINE_INTERVAL_30MINUTE,
            "60m": Client.KLINE_INTERVAL_1HOUR,
            "1h": Client.KLINE_INTERVAL_1HOUR,
            "1d": Client.KLINE_INTERVAL_1DAY,
            "1wk": Client.KLINE_INTERVAL_1WEEK,
            "1mo": Client.KLINE_INTERVAL_1MONTH
        }
        
        # Definir intervalos intradiarios y históricos según Binance
        self.intraday_intervals = {"1m", "5m", "15m", "30m", "60m", "1h"}
        self.historical_intervals = {"1d", "1wk", "1mo"}

    def process_klines(self, df):
        """
        Procesa el DataFrame con la información de las velas, 
        asignando nombres de columnas y creando la columna 'datetime'
        (basada en 'open_time') y conservando las columnas adicionales.
        """
        # Asignar nombres a las columnas según la documentación de Binance
        df.columns = [
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'num_trades',
            'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
        ]
        # Convertir open_time y close_time a datetime
        df['datetime'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        
        # Definir las columnas a conservar; ajusta esta lista si deseas filtrar o reordenar
        all_columns = [
            'datetime', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'num_trades',
            'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
        ]
        df = df[all_columns]
        
        # Convertir las columnas numéricas a float, excepto las de tiempo
        cols_to_float = ['open', 'high', 'low', 'close', 'volume',
                         'quote_asset_volume', 'taker_buy_base_vol', 'taker_buy_quote_vol']
        df.loc[:, cols_to_float] = df.loc[:, cols_to_float].astype(float)
        return df

    def download_interval(self, interval, save_csv=True, historical_days=None, chunk_days=None):
        """
        Descarga datos para un intervalo específico.
        
        :param interval: Intervalo de datos en formato unificado (ej.: "1d", "15m", etc.).
        :param save_csv: Si True, guarda los datos en un archivo CSV.
        :param historical_days: (Para datos intradiarios) Número total de días a descargar.
        :param chunk_days: (Para datos intradiarios) Número de días por bloque de descarga.
        :return: DataFrame con los datos descargados.
        """
        # Verificar que el intervalo esté en el mapeo de Binance
        if interval not in self.binance_interval_map:
            raise Exception(f"Intervalo {interval} no es soportado por Binance.")

        mapped_interval = self.binance_interval_map[interval]

        if interval in self.intraday_intervals:
            # Valores por defecto para días históricos según el intervalo
            if historical_days is None:
                if interval in ['1m', '5m', '15m', '30m']:
                    historical_days = 30
                elif interval in ['60m', '1h']:
                    historical_days = 90
                else:
                    historical_days = 30
            if chunk_days is None:
                chunk_days = 8 if interval == '1m' else 15

            now = pd.Timestamp.now()
            end_date = now
            start_date = now - pd.Timedelta(days=historical_days) + pd.Timedelta(days=1)
            chunk_timedelta = pd.Timedelta(days=chunk_days)

            data_frames = []
            current_start = start_date
            while current_start < end_date:
                current_end = min(current_start + chunk_timedelta, end_date)
                print(f"Descargando datos intradiarios de {current_start.date()} a {current_end.date()} para {self.ticker} | intervalo {interval}")
                try:
                    start_str = current_start.strftime("%d %b %Y")
                    end_str = current_end.strftime("%d %b %Y")
                    klines = self.client.get_historical_klines(self.ticker, mapped_interval, start_str, end_str)
                    if klines:
                        df = pd.DataFrame(klines)
                        if not df.empty:
                            df = self.process_klines(df)
                            data_frames.append(df)
                    else:
                        print("  No se obtuvieron datos en este periodo.")
                except Exception as e:
                    print(f"  Error descargando datos de {current_start.date()} a {current_end.date()}: {e}")
                current_start = current_end

            if data_frames:
                result = pd.concat(data_frames, ignore_index=True)
                result.drop_duplicates(subset=["datetime"], keep='first', inplace=True)
                result.sort_values(by="datetime", inplace=True)
            else:
                print("No se han descargado datos intradiarios.")
                result = pd.DataFrame()

            if save_csv:
                filename = os.path.join(self.output_dir, f"{self.ticker}_{interval}.csv")
                if os.path.isfile(filename):
                    print(f"El archivo {filename} ya existe. Leyendo datos previos para concatenar...")
                    try:
                        existing_data = pd.read_csv(filename)
                        existing_data['datetime'] = pd.to_datetime(existing_data['datetime'])
                        result = pd.concat([existing_data, result], ignore_index=True)
                        result.drop_duplicates(subset=["datetime"], keep='first', inplace=True)
                        result.sort_values(by="datetime", inplace=True)
                    except Exception as e:
                        print(f"  Error al leer el archivo existente: {e}")
                result.to_csv(filename, index=False)
                print(f"Datos guardados/acumulados en: {filename}")

            return result

        elif interval in self.historical_intervals:
            print(f"Descargando datos históricos para {self.ticker} | intervalo {interval}")
            try:
                now = pd.Timestamp.now()
                start_str = "1 Jan 2018"
                end_str = now.strftime("%d %b %Y")
                klines = self.client.get_historical_klines(self.ticker, mapped_interval, start_str, end_str)
                if klines:
                    df = pd.DataFrame(klines)
                    if not df.empty:
                        df = self.process_klines(df)
                        if save_csv:
                            filename = os.path.join(self.output_dir, f"{self.ticker}_{interval}.csv")
                            df.to_csv(filename, index=False)
                            print(f"Datos guardados en: {filename}")
                        return df
                else:
                    print(f"  No se han obtenido datos para el intervalo {interval}.")
                    return pd.DataFrame()
            except Exception as e:
                print(f"  Error al descargar datos históricos para el intervalo {interval}: {e}")
                return pd.DataFrame()
        else:
            raise Exception(f"Intervalo {interval} no reconocido.")

    def download(self, intervals, save_csv=True, intraday_params=None):
        """
        Descarga datos para una lista de intervalos.
        
        :param intervals: Lista de intervalos deseados (ej.: ["1d", "1wk", "1mo", "1m", "15m", ...]).
        :param save_csv: Si True, guarda los datos en archivos CSV.
        :param intraday_params: Diccionario opcional con parámetros para intervalos intradiarios.
        :return: Diccionario con intervalos como llaves y DataFrames como valores.
        """
        results = {}
        for interval in intervals:
            params = {}
            if intraday_params and interval in intraday_params:
                params = intraday_params[interval]
            results[interval] = self.download_interval(interval, save_csv=save_csv, **params)
        return results

def convert_yfinance_to_binance(ticker):
    """
    Convierte tickers en formato yfinance (ej.: "BTC-USD") a formato Binance (ej.: "BTCUSDT").
    Se asume que el par es contra USD.
    """
    if '-' in ticker:
        base, quote = ticker.split('-')
        if quote.upper() == 'USD':
            return base.upper() + 'USDT'
    return ticker.upper()

# ----------------------------------------------------------
# Ejecución principal
# ----------------------------------------------------------
if __name__ == "__main__":
    with open("cryptos.txt", "r", encoding="utf-8") as f:
        tickers_yfinance = json.load(f)
    
    tickers = [convert_yfinance_to_binance(ticker) for ticker in tickers_yfinance]

    historical_intervals = ["1d", "1wk", "1mo"]
    intraday_intervals = ["1m", "5m", "15m", "30m", "60m", "1h"]
    intervals = historical_intervals + intraday_intervals

    intraday_params = {
        "1m": {"historical_days": 30, "chunk_days": 8},
        "5m": {"historical_days": 30, "chunk_days": 15},
        "15m": {"historical_days": 30, "chunk_days": 15},
        "30m": {"historical_days": 30, "chunk_days": 15},
        "60m": {"historical_days": 90, "chunk_days": 15},
        "1h": {"historical_days": 90, "chunk_days": 15},
    }

    for ticker in tqdm(tickers, desc="Tickers"):
        folder_name = ticker.replace("USDT", "").lower()
        output_directory = os.path.join(folder_name)
        print(f"\nDescargando datos para {ticker} en carpeta: {output_directory}")
        downloader = UnifiedDataDownloader(ticker, output_directory)
        downloader.download(intervals, save_csv=True, intraday_params=intraday_params)
