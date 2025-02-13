# 📊 Proyecto de Descarga de Datos con Yahoo Finance 🚀

## 📌 Descripción
Este proyecto permite la descarga automática de datos históricos y de intervalos específicos de **criptomonedas**, **divisas (forex)** y **acciones** utilizando la biblioteca `yfinance`. Los datos descargados se guardan en archivos CSV organizados en carpetas por tipo de activo.

## 📁 Estructura del Proyecto

```plaintext
📂 yfinance/
│── 📂 cryptos/
│   │── 📄 cryptos.txt
│   │── 🐍 update_1d_1mo_1wk.py
│   │── 🐍 update_intraday_short-term.py
│
│── 📂 forex/
│   │── 📄 forex.txt
│   │── 🐍 update_forex_datasets.py
│
│── 📂 stocks/
│   │── 📄 stocks.txt
│   │── 🐍 update_stocks_datasets.py
│
│── ⚙️ .gitattributes
│── ⚙️ .gitignore
│── 📜 README.md
```

## 🔧 Requisitos

- 🐍 Python 3.x
- 📦 `yfinance`
- 📦 `pandas`

Puedes instalar las dependencias ejecutando:
```sh
pip install yfinance pandas
```

## 📂 Archivos y Funcionalidad

### 1️⃣ `cryptos/`
- **📄 `cryptos.txt`**: Contiene una lista en formato JSON de criptomonedas a descargar.
- **🐍 `update_1d_1mo_1wk.py`**: Descarga datos históricos con intervalos `1d`, `1wk`, y `1mo`.
- **🐍 `update_intraday_short-term.py`**: Descarga datos intradía de corto plazo.

### 2️⃣ `forex/`
- **📄 `forex.txt`**: Lista de pares de divisas a descargar.
- **🐍 `update_forex_datasets.py`**: Descarga datos con intervalos desde `1m` hasta `3mo`.

### 3️⃣ `stocks/`
- **📄 `stocks.txt`**: Lista de acciones a descargar.
- **🐍 `update_stocks_datasets.py`**: Descarga datos de acciones con intervalos variados.

## 🚀 Uso

### ▶️ Descargar datos históricos de criptomonedas
```sh
python cryptos/update_1d_1mo_1wk.py
```

### ▶️ Descargar datos históricos de divisas (Forex)
```sh
python forex/update_forex_datasets.py
```

### ▶️ Descargar datos históricos de acciones
```sh
python stocks/update_stocks_datasets.py
```

Cada script generará archivos CSV en carpetas correspondientes a cada activo.

## 📥 Descarga de Datasets Adicionales
También puedes acceder a una recopilación de datasets de internet provenientes de Kaggle a través del siguiente enlace de Google Drive:

🔗 [Recopilación de Datasets en Google Drive](https://drive.google.com/drive/u/1/folders/1Igp4jpMJwswReW1ZRWB9F7lcTIj9Oftd)

## 📝 Notas
- 📂 Los archivos de datos se guardan en directorios con el nombre del activo o par de divisas.
- ⏳ Se recomienda ejecutar estos scripts de forma periódica para mantener actualizados los datos.

## 🏆 Licencia
Este proyecto es de uso libre. Puedes modificarlo y adaptarlo según tus necesidades. 🎉
