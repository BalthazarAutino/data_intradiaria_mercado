import os
from datetime import datetime, timedelta
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

IOL_USERNAME = os.getenv("IOL_USERNAME")
IOL_PASSWORD = os.getenv("IOL_PASSWORD")

ticker = "AE38D"
ticker_bonito = ticker.lower()

def obtener_token():
    url = "https://api.invertironline.com/token"
    data = {
        "username": IOL_USERNAME,
        "password": IOL_PASSWORD,
        "grant_type": "password",
    }
    res = requests.post(url, data=data)
    res.raise_for_status()
    return res.json().get("access_token")

# funcion que trae la data del mercado del ticker
def data(dias=1000):
    token = obtener_token()
    if not token:
        print("❌ Error de autenticación.")
        return

    fecha_hasta = datetime.now().strftime("%Y-%m-%d")
    fecha_desde = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")

    url = f"https://api.invertironline.com/api/v2/bCBA/Titulos/{ticker}/Cotizacion/seriehistorica/{fecha_desde}/{fecha_hasta}/sinAjustar"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"⏳ Descargando data pura de mercado de {ticker} ({dias} días)...")
    res = requests.get(url, headers=headers)

    if res.status_code != 200 or not res.json():
        print(f"❌ Error al consultar la API: {res.status_code}")
        return

    data = res.json()
    print(f"✅ Se obtuvieron {len(data)} registros puros de mercado.")

    # Convertimos la respuesta cruda directamente a un DataFrame
    df_raw = pd.DataFrame(data)

    # Ordenamos de más reciente a más antiguo por la marca de tiempo exacta
    if "fechaHora" in df_raw.columns:
        df_raw["fechaHora"] = pd.to_datetime(df_raw["fechaHora"], format="mixed")
        df_raw = df_raw.sort_values(
            by="fechaHora", ascending=False
        ).reset_index(drop=True)

    # Exportación 1:1 a Excel sin agrupaciones ni filtros
    archivo_excel = f"{ticker_bonito}_data.xlsx"
    print(f"💾 Guardando '{archivo_excel}'...")
    
    df_raw.to_excel(archivo_excel, index=False, engine="openpyxl")

    print(
        f"🎉 ¡Listo! Archivo '{archivo_excel}' generado con las {len(df_raw)} filas de data cruda."
    )

#4693
if __name__ == "__main__":
    data(dias=1000)