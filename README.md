# 📊 Proyecto de Generación de Datasets Financieros 🚀

## 📌 Descripción
Este proyecto está enfocado en la **generación de datasets financieros**. Para ello, contamos con dos opciones principales:

1️⃣ **Generación de datos en tiempo real** utilizando `yfinance` para descargar datos de criptomonedas, divisas (forex) y acciones.

2️⃣ **Recopilación de datasets históricos** obtenidos de diversas fuentes como Kaggle, disponibles para su descarga en un repositorio de Google Drive.

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

## 📂 Opciones para Generar Datasets

### 1️⃣ Generación de Datos con `yfinance`
Esta opción permite descargar datos en tiempo real desde Yahoo Finance. Los scripts organizan los datos en archivos CSV para su análisis.

#### 📌 Archivos y Funcionalidad

#### 🏦 `cryptos/`
- **📄 `cryptos.txt`**: Lista en formato JSON de criptomonedas a descargar.
- **🐍 `update_1d_1mo_1wk.py`**: Descarga datos históricos con intervalos `1d`, `1wk`, y `1mo`.
- **🐍 `update_intraday_short-term.py`**: Descarga datos intradía de corto plazo.

#### 💱 `forex/`
- **📄 `forex.txt`**: Lista de pares de divisas a descargar.
- **🐍 `update_forex_datasets.py`**: Descarga datos con intervalos desde `1m` hasta `3mo`.

#### 📈 `stocks/`
- **📄 `stocks.txt`**: Lista de acciones a descargar.
- **🐍 `update_stocks_datasets.py`**: Descarga datos de acciones con intervalos variados.

### 2️⃣ Recopilación de Datasets de Kaggle y otras Fuentes
Para complementar la generación de datos en tiempo real, puedes acceder a una recopilación de datasets financieros obtenidos de internet. Estos incluyen datos históricos extensos que pueden ser útiles para análisis más profundos.

🔗 **[Recopilación de Datasets en Google Drive](https://drive.google.com/drive/u/1/folders/1Igp4jpMJwswReW1ZRWB9F7lcTIj9Oftd)**

## 🚀 Uso

### ▶️ Descargar datos históricos de criptomonedas con `yfinance`
```sh
python cryptos/update_1d_1mo_1wk.py
```

### ▶️ Descargar datos históricos de divisas (Forex) con `yfinance`
```sh
python forex/update_forex_datasets.py
```

### ▶️ Descargar datos históricos de acciones con `yfinance`
```sh
python stocks/update_stocks_datasets.py
```

Cada script generará archivos CSV en carpetas correspondientes a cada activo.

## 📝 Notas
- 📂 Los archivos de datos se guardan en directorios con el nombre del activo o par de divisas.
- ⏳ Se recomienda ejecutar estos scripts de forma periódica para mantener actualizados los datos.

## 🏆 Licencia
Este proyecto es de uso libre. Puedes modificarlo y adaptarlo según tus necesidades. 🎉
