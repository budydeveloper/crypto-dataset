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
    Para los intervalos intradiarios se descarga en bloques (chunks) para sortear el límite de 1000 velas,
    iniciando desde el primer candle histórico disponible, y se retoma la descarga en caso de existir CSV previo.
    Todos los CSV se guardan con cabecera.
    """

    def __init__(self, ticker, output_dir):
        """
        :param ticker: Símbolo del par en formato Binance, por ejemplo "BTCUSDT".
        :param output_dir: Directorio donde se guardarán los archivos CSV.
        """
        self.ticker = ticker
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # Instanciar el cliente de Binance (se pueden pasar API key y secret si se requiere)
        self.client = Client()
        
        # Mapeo de intervalos que Binance acepta (se elimina "60m", se conserva "1h")
        self.binance_interval_map = {
            "1m": Client.KLINE_INTERVAL_1MINUTE,
            "5m": Client.KLINE_INTERVAL_5MINUTE,
            "15m": Client.KLINE_INTERVAL_15MINUTE,
            "30m": Client.KLINE_INTERVAL_30MINUTE,
            "1h": Client.KLINE_INTERVAL_1HOUR,
            "1d": Client.KLINE_INTERVAL_1DAY,
            "1wk": Client.KLINE_INTERVAL_1WEEK,
            "1mo": Client.KLINE_INTERVAL_1MONTH
        }
        
        # Definir intervalos intradiarios y históricos
        self.intraday_intervals = {"1m", "5m", "15m", "30m", "1h"}
        self.historical_intervals = {"1d", "1wk", "1mo"}
        
        # Nombres de columna según el orden que devuelve Binance
        self.column_names = [
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "num_trades",
            "taker_buy_base_vol", "taker_buy_quote_vol", "ignore"
        ]

    def process_klines(self, df):
        """
        Asigna nombres de columna y convierte los timestamps (open_time y close_time)
        de Unix (milisegundos) a un formato legible ("YYYY-MM-DD HH:MM:SS").
        Se conserva el resto de la información tal cual viene.
        """
        df.columns = self.column_names
        df["open_time"] = pd.to_datetime(df["open_time"], unit='ms').dt.strftime("%Y-%m-%d %H:%M:%S")
        df["close_time"] = pd.to_datetime(df["close_time"], unit='ms').dt.strftime("%Y-%m-%d %H:%M:%S")
        return df

    def get_first_available_date(self, interval):
        """
        Determina el primer candle disponible para el activo y el intervalo dado mediante búsqueda.
        Se realiza una búsqueda aproximada con saltos de 30 días hasta encontrar datos,
        y luego se refina la fecha usando búsqueda binaria.
        
        :param interval: Intervalo en formato unificado (ej.: "15m").
        :return: Timestamp del primer candle disponible.
        """
        mapped_interval = self.binance_interval_map[interval]
        
        current_date = pd.Timestamp("2017-01-01")
        last_no_data = None
        first_with_data = None
        
        while current_date < pd.Timestamp.now():
            start_str = current_date.strftime("%d %b %Y")
            end_date = current_date + pd.Timedelta(days=1)
            end_str = end_date.strftime("%d %b %Y")
            print(f"Probando datos para: {start_str} - {end_str}")
            try:
                # Solicita un solo candle (limit=1) en el rango de un día
                klines = self.client.get_historical_klines(self.ticker, mapped_interval, start_str, end_str, limit=1)
            except Exception as e:
                print(f"Error al consultar datos para {current_date.date()}: {e}")
                klines = []
            if klines:
                first_with_data = pd.to_datetime(klines[0][0], unit='ms')
                print(f"Datos encontrados a partir de: {first_with_data}")
                break
            else:
                last_no_data = current_date
                current_date += pd.Timedelta(days=30)  # Incrementa 30 días
        
        if first_with_data is None:
            raise Exception("No se encontraron datos para este activo e intervalo.")
        
        # Búsqueda binaria para refinar la fecha
        low = last_no_data + pd.Timedelta(days=1) if last_no_data is not None else pd.Timestamp("2017-01-01")
        high = first_with_data

        while low < high:
            mid = low + (high - low) / 2
            start_str = mid.strftime("%d %b %Y")
            end_date = mid + pd.Timedelta(days=1)
            end_str = end_date.strftime("%d %b %Y")
            try:
                klines = self.client.get_historical_klines(self.ticker, mapped_interval, start_str, end_str, limit=1)
            except Exception as e:
                print(f"Error en la búsqueda binaria para {mid.date()}: {e}")
                klines = []
            if klines:
                high = mid
            else:
                low = mid + pd.Timedelta(milliseconds=1)
        print(f"Primer candle determinado: {high}")
        return high

    def download_interval(self, interval, save_csv=True, chunk_days=None):
        """
        Descarga datos para un intervalo específico.
        - Para intradiarios:
            • Si existe CSV previo, retoma desde la última vela almacenada.
            • Si no existe, se busca el primer candle disponible y se descarga desde esa fecha hasta ahora en bloques.
        - Para históricos:
            Se descarga todo el historial desde "1 Jan 2017".
        
        :param interval: Intervalo en formato unificado (ej.: "15m").
        :param save_csv: Si True, guarda los datos en un archivo CSV (con cabecera).
        :param chunk_days: Número de días por bloque de descarga para intradiarios (por defecto 15).
        :return: DataFrame con los datos descargados.
        """
        if interval not in self.binance_interval_map:
            raise Exception(f"Intervalo {interval} no es soportado por Binance.")
        
        mapped_interval = self.binance_interval_map[interval]
        filename = os.path.join(self.output_dir, f"{self.ticker}_{interval}.csv")
        
        if interval in self.intraday_intervals:
            # Intradiarios: si existe CSV previo, se retoma desde la última vela; de lo contrario, se busca el primer dato.
            if os.path.isfile(filename):
                print(f"El archivo {filename} ya existe. Leyendo datos previos para retomar descarga...")
                try:
                    existing_data = pd.read_csv(filename, header=0)
                    last_open_time = existing_data.iloc[-1]["open_time"]
                    last_open_time = pd.to_datetime(last_open_time, format="%Y-%m-%d %H:%M:%S")
                    start_date = last_open_time + pd.Timedelta(seconds=1)
                except Exception as e:
                    print(f"  Error al leer el archivo existente: {e}")
                    start_date = self.get_first_available_date(interval)
            else:
                start_date = self.get_first_available_date(interval)
                print(f"El primer candle disponible para {self.ticker} en intervalo {interval} es: {start_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            now = pd.Timestamp.now()
            if chunk_days is None:
                chunk_days = 15  # Valor por defecto para intradiarios
            
            chunk_timedelta = pd.Timedelta(days=chunk_days)
            data_frames = []
            current_start = start_date
            while current_start < now:
                current_end = min(current_start + chunk_timedelta, now)
                print(f"Descargando datos de {current_start.strftime('%Y-%m-%d')} a {current_end.strftime('%Y-%m-%d')} para {self.ticker} | intervalo {interval}")
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
                    print(f"  Error descargando datos de {current_start.strftime('%Y-%m-%d')} a {current_end.strftime('%Y-%m-%d')}: {e}")
                current_start = current_end
            
            if data_frames:
                result = pd.concat(data_frames, ignore_index=True)
                result.drop_duplicates(subset=["open_time"], keep='first', inplace=True)
                result.sort_values(by="open_time", inplace=True)
            else:
                result = pd.DataFrame(columns=self.column_names)
            
            # Si existe CSV previo, concatenar los datos anteriores (solo si ambos DataFrames no son vacíos)
            if os.path.isfile(filename):
                try:
                    existing_data = pd.read_csv(filename, header=0)
                    if not existing_data.empty and not result.empty:
                        result = pd.concat([existing_data, result], ignore_index=True)
                    elif not existing_data.empty:
                        result = existing_data
                    result.drop_duplicates(subset=["open_time"], keep='first', inplace=True)
                    result.sort_values(by="open_time", inplace=True)
                except Exception as e:
                    print(f"  Error al leer el archivo existente: {e}")
            
            if save_csv:
                result.to_csv(filename, index=False, header=True)
                print(f"Datos guardados/acumulados en: {filename}")
            
            return result
        
        elif interval in self.historical_intervals:
            # Históricos: se descarga todo el historial desde "1 Jan 2017"
            print(f"Descargando datos históricos para {self.ticker} | intervalo {interval}")
            try:
                start_str = "1 Jan 2017"
                now = pd.Timestamp.now()
                end_str = now.strftime("%d %b %Y")
                klines = self.client.get_historical_klines(self.ticker, mapped_interval, start_str, end_str)
                if klines:
                    df = pd.DataFrame(klines)
                    if not df.empty:
                        df = self.process_klines(df)
                        if save_csv:
                            df.to_csv(filename, index=False, header=True)
                            print(f"Datos guardados en: {filename}")
                        return df
                else:
                    print(f"  No se han obtenido datos para el intervalo {interval}.")
                    return pd.DataFrame(columns=self.column_names)
            except Exception as e:
                print(f"  Error al descargar datos históricos para el intervalo {interval}: {e}")
                return pd.DataFrame(columns=self.column_names)
        else:
            raise Exception(f"Intervalo {interval} no reconocido.")

    def download(self, intervals, save_csv=True, intraday_params=None):
        """
        Descarga datos para una lista de intervalos.
        
        :param intervals: Lista de intervalos deseados (ej.: ["1d", "1wk", "1mo", "1m", "15m", ...]).
        :param save_csv: Si True, guarda los datos en archivos CSV (con cabecera).
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

if __name__ == "__main__":
    with open("cryptos.txt", "r", encoding="utf-8") as f:
        tickers = json.load(f)
    
    # Se espera que el archivo 'cryptos.txt' contenga los tickers en formato Binance (ej.: "BTCUSDT")
    historical_intervals = ["1d", "1wk", "1mo"]
    intraday_intervals = ["1m", "5m", "15m", "30m", "1h"]
    intervals = historical_intervals + intraday_intervals

    for ticker in tqdm(tickers, desc="Tickers"):
        folder_name = ticker.replace("USDT", "").lower()
        output_directory = os.path.join(folder_name)
        print(f"\nDescargando datos para {ticker} en carpeta: {output_directory}")
        downloader = UnifiedDataDownloader(ticker, output_directory)
        downloader.download(intervals, save_csv=True)
