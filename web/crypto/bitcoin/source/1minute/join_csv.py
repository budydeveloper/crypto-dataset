#!/usr/bin/env python3
import csv
import sys

def join_csv_three(input_file1, input_file2, input_file3, output_file):
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile, \
         open(input_file1, 'r', encoding='utf-8', newline='') as in1, \
         open(input_file2, 'r', encoding='utf-8', newline='') as in2, \
         open(input_file3, 'r', encoding='utf-8', newline='') as in3:

        writer = csv.writer(outfile)
        reader1 = csv.reader(in1)
        reader2 = csv.reader(in2)
        reader3 = csv.reader(in3)

        # Leer encabezado de cada archivo
        header1 = next(reader1)
        header2 = next(reader2)
        header3 = next(reader3)

        # Comprobar que todos los encabezados son iguales
        if header1 != header2 or header1 != header3:
            print("Los encabezados de los archivos no coinciden.")
            sys.exit(1)

        # Escribir el encabezado una sola vez
        writer.writerow(header1)

        # Escribir las filas de cada archivo
        for row in reader1:
            writer.writerow(row)
        for row in reader2:
            writer.writerow(row)
        for row in reader3:
            writer.writerow(row)

    print(f"Los archivos '{input_file1}', '{input_file2}' y '{input_file3}' se han unido en '{output_file}'.")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python join_csv_three.py <archivo_entrada1.csv> <archivo_entrada2.csv> <archivo_entrada3.csv> <archivo_salida.csv>")
        sys.exit(1)

    input_file1 = sys.argv[1]
    input_file2 = sys.argv[2]
    input_file3 = sys.argv[3]
    output_file = sys.argv[4]
    join_csv_three(input_file1, input_file2, input_file3, output_file)


# python join_csv_three.py BTC-USD_1m_part1.csv BTC-USD_1m_part2.csv BTC-USD_1m_part3.csv BTC-USD_1m_joined.csv
