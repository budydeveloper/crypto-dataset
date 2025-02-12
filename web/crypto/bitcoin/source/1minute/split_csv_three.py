#!/usr/bin/env python3
import csv
import sys

def split_csv_three(input_file, output_file1, output_file2, output_file3):
    # Contar la cantidad total de filas de datos (excluyendo el encabezado)
    with open(input_file, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f) - 1  # restamos 1 por el encabezado
    if total_lines <= 0:
        print("El archivo no contiene filas de datos.")
        sys.exit(1)

    # Calcular cuántas filas irán en cada parte
    base = total_lines // 3
    remainder = total_lines % 3

    # Distribuir el resto entre las primeras partes si es necesario
    if remainder == 0:
        p1 = p2 = p3 = base
    elif remainder == 1:
        p1 = base + 1
        p2 = base
        p3 = base
    elif remainder == 2:
        p1 = base + 1
        p2 = base + 1
        p3 = base

    # Abrir el archivo de entrada y los tres archivos de salida
    with open(input_file, 'r', encoding='utf-8', newline='') as infile, \
         open(output_file1, 'w', encoding='utf-8', newline='') as out1, \
         open(output_file2, 'w', encoding='utf-8', newline='') as out2, \
         open(output_file3, 'w', encoding='utf-8', newline='') as out3:

        reader = csv.reader(infile)
        writer1 = csv.writer(out1)
        writer2 = csv.writer(out2)
        writer3 = csv.writer(out3)

        # Leer y escribir el encabezado en cada archivo de salida
        header = next(reader)
        writer1.writerow(header)
        writer2.writerow(header)
        writer3.writerow(header)

        # Escribir las filas en el archivo correspondiente
        count = 0
        for row in reader:
            if count < p1:
                writer1.writerow(row)
            elif count < p1 + p2:
                writer2.writerow(row)
            else:
                writer3.writerow(row)
            count += 1

    print(f"El archivo '{input_file}' se ha dividido en:")
    print(f"  - {output_file1} (primeras {p1} filas)")
    print(f"  - {output_file2} (siguientes {p2} filas)")
    print(f"  - {output_file3} (restantes {p3} filas)")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python split_csv_three.py <archivo_entrada.csv> <archivo_salida1.csv> <archivo_salida2.csv> <archivo_salida3.csv>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file1 = sys.argv[2]
    output_file2 = sys.argv[3]
    output_file3 = sys.argv[4]
    split_csv_three(input_file, output_file1, output_file2, output_file3)
