from datetime import timedelta, date
import pandas as pd
import sys
from pathlib import Path
import requests

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.append(str(RAIZ))

from utils.auth import obtener_credenciales_hb
from pyhomebroker import HomeBroker
import pyhomebroker.history.history as hist_mod

# ── PARÁMETROS ───────────────────────────────────────────────────────────────
TICKER         = "PAMP"
DIAS           = 100
TIMEOUT_SEG    = 8
MAX_VACIOS_SEG = 10
# ─────────────────────────────────────────────────────────────────────────────


def _get_intraday_dia(hb, ticker, dia, timeout):
    """
    Pide velas de 1 minuto para un único día.
    Pasa from=dia, to=dia+1 (igual que el ejemplo oficial del repo).
    Inyecta timeout porque pyhomebroker no lo expone.
    """
    original = hist_mod.rq.get

    def get_con_timeout(url, **kwargs):
        kwargs.setdefault('timeout', timeout)
        return original(url, **kwargs)

    hist_mod.rq.get = get_con_timeout
    try:
        # from_date=dia, to_date=dia+1  ← ventana de 1 día completo
        df = hb.history.get_intraday_history(ticker, dia, dia + timedelta(days=1))
    finally:
        hist_mod.rq.get = original

    return df


def data_intradiaria(ticker: str = TICKER, dias: int = DIAS):
    creds = obtener_credenciales_hb()

    hb = HomeBroker(creds["broker"])
    try:
        hb.auth.login(
            dni=creds["dni"],
            user=creds["user"],
            password=creds["password"],
            raise_exception=True,
        )
        print("✅ Login exitoso en HomeBroker")
    except Exception as e:
        print(f"❌ Error de login: {e}")
        return

    hoy        = date.today()
    desde      = hoy - timedelta(days=dias)
    all_data   = []
    dias_ok    = 0
    dias_sin   = 0
    vacios_seg = 0

    cursor = hoy
    while cursor >= desde:
        if cursor.weekday() >= 5:
            cursor -= timedelta(days=1)
            continue

        try:
            df = _get_intraday_dia(hb, ticker, cursor, TIMEOUT_SEG)

            if df is not None and not df.empty:
                df["symbol"] = ticker
                all_data.append(df)
                dias_ok    += 1
                vacios_seg  = 0
                print(f"  ✅ {cursor}  → {len(df)} velas")
            else:
                dias_sin   += 1
                vacios_seg += 1
                print(f"  ⚠️  {cursor}  → sin datos ({vacios_seg} consecutivos)")

        except requests.exceptions.Timeout:
            dias_sin   += 1
            vacios_seg += 1
            print(f"  ⏱️  {cursor}  → timeout ({vacios_seg} consecutivos)")

        except Exception as e:
            dias_sin   += 1
            vacios_seg += 1
            print(f"  ❌ {cursor}  → {e} ({vacios_seg} consecutivos)")

        if vacios_seg >= MAX_VACIOS_SEG:
            print(f"\n🛑 {MAX_VACIOS_SEG} días hábiles seguidos sin datos — cortando.")
            break

        cursor -= timedelta(days=1)

    print(f"\nResumen: {dias_ok} días con datos / {dias_sin} sin datos")

    if not all_data:
        print(f"\n❌ Sin datos intradiarios para '{ticker}' en HomeBroker (TM).")
        return

    combined = (
        pd.concat(all_data, ignore_index=True)
        .sort_values("date", ascending=False)
        .reset_index(drop=True)
    )

    print(f"\n📊 Total de velas: {len(combined)}")
    print(combined.head(10).to_string())

    archivo = f"{ticker.lower()}_intradiario.xlsx"
    combined.to_excel(archivo, index=False, engine="openpyxl")
    print(f"\n💾 Guardado como '{archivo}'")
    return combined


if __name__ == "__main__":
    data_intradiaria()