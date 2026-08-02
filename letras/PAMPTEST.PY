"""
ByMA Open Data usa OAuth pero tiene un flujo de "usuario anónimo" 
que el browser completa automáticamente al entrar al sitio.
Este script replica ese flujo para obtener un token sin registro.
"""
import requests
import pandas as pd

BASE     = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free"
AUTH_URL = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/authenticate"

TICKER = "S31L6"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://open.bymadata.com.ar",
    "Referer": "https://open.bymadata.com.ar/",
})

# ── Paso 1: obtener token anónimo ─────────────────────────────────────────────
print("Intentando autenticación anónima...")
r = session.post(AUTH_URL, json={"username": "anonymous", "password": "anonymous"}, timeout=10)
print(f"Status auth: {r.status_code}")
print(f"Respuesta  : {r.text[:400]}")
print()

token = None
if r.ok:
    try:
        token = r.json().get("token") or r.json().get("access_token") or r.json().get("id_token")
        print(f"Token obtenido: {token[:40] if token else 'No encontrado'}...")
    except Exception:
        print("No se pudo parsear token del JSON")

if token:
    session.headers["Authorization"] = f"Bearer {token}"

# ── Paso 2: consultar intradiario ────────────────────────────────────────────
print(f"\n=== Intradiario: {TICKER} ===")
url = f"{BASE}/bnown/chartdata/security/intraday?symbol={TICKER}&settlement=0003"
r2 = session.get(url, timeout=10)
print(f"Status: {r2.status_code}")
print(r2.text[:600])

# ── Paso 3: histórico diario ─────────────────────────────────────────────────
print(f"\n=== Histórico: {TICKER} (últimos 30 días) ===")
url2 = f"{BASE}/bnown/chartdata/security/history?symbol={TICKER}&dateFrom=2026-06-01&dateTo=2026-07-31&settlement=0003"
r3 = session.get(url2, timeout=10)
print(f"Status: {r3.status_code}")
print(r3.text[:600])