import os
from pathlib import Path
import requests
from dotenv import load_dotenv

# Carga automática del .env que vive en esta misma carpeta (utils/)
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)


# ── IOL ──────────────────────────────────────────────────────────────────────

def obtener_token():
    usuario = os.getenv("IOL_USERNAME")
    password = os.getenv("IOL_PASSWORD")

    if not usuario or not password:
        print("❌ Error: No se encontraron las credenciales IOL en utils/.env")
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
        print(f"❌ Error al autenticar con IOL: {e}")
        return None


# ── HOMEBROKER — TOMAR INVERSIONES (broker 81) ───────────────────────────────

def obtener_credenciales_hb() -> dict:
    """
    Credenciales para HomeBroker vía Tomar Inversiones (broker 81).
    Variables en utils/.env: HB_BROKER, HB_DNI, HB_USER, HB_PASSWORD
    """
    broker   = os.getenv("HB_BROKER")
    dni      = os.getenv("HB_DNI")
    user     = os.getenv("HB_USER")
    password = os.getenv("HB_PASSWORD")

    faltantes = [k for k, v in {
        "HB_BROKER": broker, "HB_DNI": dni,
        "HB_USER": user, "HB_PASSWORD": password,
    }.items() if not v]

    if faltantes:
        raise ValueError(f"❌ Faltan variables en utils/.env: {', '.join(faltantes)}")

    return {"broker": int(broker), "dni": dni, "user": user, "password": password}


# ── HOMEBROKER — COCOS CAPITAL (broker 265) ──────────────────────────────────

def obtener_credenciales_cocos() -> dict:
    """
    Credenciales para HomeBroker vía Cocos Capital (broker 265).
    Cocos no usa DNI separado — el campo dni recibe el mismo valor que user.
    Variables en utils/.env: COCOS_BROKER, COCOS_USER, COCOS_PASSWORD
    """
    broker   = os.getenv("COCOS_BROKER", "265")
    user     = os.getenv("COCOS_USER")
    password = os.getenv("COCOS_PASSWORD")

    faltantes = [k for k, v in {
        "COCOS_USER": user, "COCOS_PASSWORD": password,
    }.items() if not v]

    if faltantes:
        raise ValueError(f"❌ Faltan variables en utils/.env: {', '.join(faltantes)}")

    return {"broker": int(broker), "user": user, "password": password}