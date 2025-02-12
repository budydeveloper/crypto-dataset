#!/usr/bin/env python3
import csv
import glob
import datetime
import sys
import os

# Encabezado base esperado para la mayoría de los archivos
HEADER_BASE = ['datetime', 'open', 'high', 'low', 'close', 'volume']

# Lista de formatos permitidos para la columna datetime
FORMATOS_DATETIME = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']

def validar_fecha(fecha_str):
    """
    Intenta convertir la cadena 'fecha_str' usando distintos formatos.
    Devuelve True si alguno de los formatos es correcto, o False en caso contrario.
    """
    for fmt in FORMATOS_DATETIME:
        try:
            datetime.datetime.strptime(fecha_str, fmt)
            return True
        except ValueError:
            continue
    return False

def validar_archivo(ruta_archivo):
    """
    Valida el archivo CSV especificado y devuelve una lista de errores encontrados.
    Si la lista está vacía, el archivo es correcto.
    Se adapta la validación del encabezado y el número de columnas según si el archivo es de 1 minuto.
    """
    errores = []
    
    # Determinar la cantidad de columnas esperadas y cómo validar el encabezado según el nombre del archivo
    basename = os.path.basename(ruta_archivo)
    if basename == "BTC-USD_1m.csv":
        expected_columns = 7
        # Se espera que las primeras 6 columnas sean iguales a HEADER_BASE;
        # la columna extra se ignora en la validación del encabezado.
        def header_check(header):
            return (len(header) == 7 and header[:6] == HEADER_BASE)
    else:
        expected_columns = 6
        def header_check(header):
            return (header == HEADER_BASE)
    
    try:
        with open(ruta_archivo, newline='', encoding='utf-8') as csvfile:
            lector = csv.reader(csvfile)
            try:
                encabezado = next(lector)
            except StopIteration:
                errores.append("Archivo vacío.")
                return errores

            if not header_check(encabezado):
                if expected_columns == 7:
                    errores.append(
                        f"Encabezado incorrecto. Se esperaba que las primeras 6 columnas fueran {HEADER_BASE} y un total de 7 columnas, pero se encontró: {encabezado}"
                    )
                else:
                    errores.append(
                        f"Encabezado incorrecto. Se esperaba: {HEADER_BASE} pero se encontró: {encabezado}"
                    )

            num_linea = 1
            for fila in lector:
                num_linea += 1
                # Verificar que la fila tenga el número correcto de columnas
                if len(fila) != expected_columns:
                    errores.append(
                        f"Línea {num_linea}: Número incorrecto de columnas. Se esperaban {expected_columns} pero se encontraron {len(fila)}."
                    )
                    continue

                # Validar el formato de la fecha usando los formatos permitidos
                fecha_str = fila[0]
                if not validar_fecha(fecha_str):
                    errores.append(
                        f"Línea {num_linea}: Formato de fecha inválido ('{fecha_str}'). Se esperaba alguno de los formatos: {FORMATOS_DATETIME}"
                    )

                # Convertir los valores numéricos de las columnas 1 a 5 (open, high, low, close, volume)
                try:
                    open_val  = float(fila[1])
                    high_val  = float(fila[2])
                    low_val   = float(fila[3])
                    close_val = float(fila[4])
                    volume_val = float(fila[5])
                except ValueError as e:
                    errores.append(f"Línea {num_linea}: Error al convertir a número: {e}")
                    continue

                # Validar coherencia de precios: low <= open <= high y low <= close <= high
                if not (low_val <= open_val <= high_val):
                    errores.append(
                        f"Línea {num_linea}: El precio de apertura ({open_val}) no está entre el mínimo ({low_val}) y el máximo ({high_val})."
                    )
                if not (low_val <= close_val <= high_val):
                    errores.append(
                        f"Línea {num_linea}: El precio de cierre ({close_val}) no está entre el mínimo ({low_val}) y el máximo ({high_val})."
                    )
    except Exception as e:
        errores.append(f"Error al leer el archivo: {e}")
    return errores

def main():
    """
    Función principal:
      - Si se pasan archivos como argumentos, se validan esos.
      - De lo contrario, se buscan archivos CSV que comiencen con 'BTC-USD_' en el directorio actual.
    """
    if len(sys.argv) > 1:
        archivos = sys.argv[1:]
    else:
        archivos = glob.glob("BTC-USD_*.csv")

    if not archivos:
        print("No se encontraron archivos CSV para validar.")
        return

    hubo_errores = False
    for archivo in archivos:
        print(f"Validando archivo: {archivo}")
        errores = validar_archivo(archivo)
        if errores:
            hubo_errores = True
            for error in errores:
                print("  ERROR:", error)
        else:
            print("  OK")

    # Devuelve un código de salida distinto de cero si hubo algún error
    if hubo_errores:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
