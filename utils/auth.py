import os
from pathlib import Path
import requests
from dotenv import load_dotenv

# Carga automática del .env que vive en esta misma carpeta (utils/)
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def obtener_token():
    usuario = os.getenv("IOL_USERNAME")
    password = os.getenv("IOL_PASSWORD")

    if not usuario or not password:
        print("❌ Error: No se encontraron las credenciales en utils/.env")
        return None

    url = "https://api.invertironline.com/token"
    data = {
        "username": usuario,
        "password": password,
        "grant_type": "password",
    }
    try:
        res = requests.post(url, data=data)
        res.raise_for_status()
        return res.json().get("access_token")
    except Exception as e:
        print(f"❌ Error al autenticar: {e}")
        return None