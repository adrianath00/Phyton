# etl_logic.py
import os
import re
import hashlib
from datetime import datetime
import pandas as pd
import logging
from src.utils.logger import get_logger
from dotenv import load_dotenv
import unicodedata

# =====================
# INIT
# =====================
load_dotenv()
logger = get_logger("etl")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "data", "source")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")
ERROR_DIR = os.path.join(BASE_DIR, "data", "errors")

SALT = os.getenv("SALT", "default_salt_change_in_production")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ERROR_DIR, exist_ok=True)

# =====================
# REGEX
# =====================
CLIENTES_PATTERN = re.compile(r"^Clientes-\d{4}-\d{2}-\d{2}\.csv$")
TARJETAS_PATTERN = re.compile(r"^Tarjetas-\d{4}-\d{2}-\d{2}\.csv$")
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# =====================
# HELPERS
# =====================
def remove_accents(s):
    if pd.isna(s):
        return s
    s = str(s)
    return "".join(
        c for c in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(c)
    )

def normalize_name(name):
    if pd.isna(name):
        return ""
    name = remove_accents(name.strip().lower())
    parts = re.split(r"(\-|\s)", name)
    return "".join(p.capitalize() if p not in ["-", " "] else p for p in parts)

def validate_dni(dni):
    if pd.isna(dni):
        return False
    dni = re.sub(r"[^0-9A-Za-z]", "", str(dni)).upper()
    if len(dni) != 9 or not dni[:-1].isdigit():
        return False
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    return letras[int(dni[:-1]) % 23] == dni[-1]

def validate_phone(phone):
    if pd.isna(phone):
        return False
    digits = re.sub(r"\D", "", str(phone))
    return (
        len(digits) == 9 or
        (digits.startswith("34") and len(digits) == 11) or
        (digits.startswith("0034") and len(digits) == 13)
    )

def validate_email(email):
    if pd.isna(email):
        return False
    return EMAIL_REGEX.match(str(email).strip().lower()) is not None

def mask_card(number):
    if pd.isna(number):
        return ""
    digits = re.sub(r"\D", "", str(number))
    if len(digits) < 4:
        return ""
    return "XXXX-XXXX-XXXX-" + digits[-4:]

def hash_value(value):
    if pd.isna(value):
        return ""
    raw = (SALT + str(value)).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

# =====================
# CLIENTES
# =====================
def process_client_file(path):
    logger.info(f"Procesando clientes: {path}")

    try:
        df = pd.read_csv(
            path, sep=";", dtype=str,
            encoding="utf-8",
            on_bad_lines="skip",
            engine="python"
        )
    except Exception:
        df = pd.read_csv(
            path, sep=";", dtype=str,
            encoding="latin1",
            on_bad_lines="skip",
            engine="python"
        )

    df.columns = [remove_accents(c.strip()).lower() for c in df.columns]

    rename_map = {
        "cod cliente": "cod_cliente",
        "cod_cliente": "cod_cliente",
        "nombre": "nombre",
        "apellido1": "apellido1",
        "apellido2": "apellido2",
        "dni": "dni",
        "correo": "correo",
        "telefono": "telefono",
    }
    df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})

    for col in rename_map.values():
        if col not in df.columns:
            df[col] = ""

    df["nombre"] = df["nombre"].apply(normalize_name)
    df["apellido1"] = df["apellido1"].apply(normalize_name)
    df["apellido2"] = df["apellido2"].apply(normalize_name)
    df["dni"] = df["dni"].astype(str).str.replace(r"\s|-", "", regex=True).str.upper()
    df["correo"] = df["correo"].astype(str).str.strip().str.lower()
    df["telefono"] = df["telefono"].astype(str).str.replace(r"\D", "", regex=True)

    df["DNI_OK"] = df["dni"].apply(lambda x: "Y" if validate_dni(x) else "N")
    df["Telefono_OK"] = df["telefono"].apply(lambda x: "Y" if validate_phone(x) else "N")
    df["Correo_OK"] = df["correo"].apply(lambda x: "Y" if validate_email(x) else "N")

    rejects = df[df["cod_cliente"].astype(str).str.strip() == ""]
    if not rejects.empty:
        reject_path = os.path.join(
            ERROR_DIR,
            f"rows_rejected_clients_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
        )
        rejects.to_csv(reject_path, sep=";", index=False, encoding="utf-8")
        logger.warning(f"{len(rejects)} filas rechazadas guardadas en {reject_path}")
        df = df[df["cod_cliente"].astype(str).str.strip() != ""]

    out_path = os.path.join(
        OUTPUT_DIR,
        os.path.basename(path).replace(".csv", ".cleaned.csv")
    )
    df.to_csv(out_path, sep=";", index=False, encoding="utf-8")
    logger.info(f"Clientes limpios guardados en: {out_path}")

# =====================
# TARJETAS
# =====================
def process_card_file(path):
    logger.info(f"Procesando tarjetas: {path}")

    try:
        df = pd.read_csv(
            path, sep=";", dtype=str,
            encoding="utf-8",
            on_bad_lines="skip",
            engine="python"
        )
    except Exception:
        df = pd.read_csv(
            path, sep=";", dtype=str,
            encoding="latin1",
            on_bad_lines="skip",
            engine="python"
        )

    df.columns = [remove_accents(c.strip()).lower() for c in df.columns]

    rename_map = {
        "cod cliente": "cod_cliente",
        "cod_cliente": "cod_cliente",
        "numero tarjeta": "numero_tarjeta",
        "numero_tarjeta": "numero_tarjeta",
        "fecha_exp": "fecha_exp",
        "cvv": "cvv",
    }
    df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})

    for col in ["cod_cliente", "numero_tarjeta", "fecha_exp", "cvv"]:
        if col not in df.columns:
            df[col] = ""

    df["numero_tarjeta_raw"] = df["numero_tarjeta"].astype(str).str.replace(r"\D", "", regex=True)
    df["numero_tarjeta_masked"] = df["numero_tarjeta_raw"].apply(mask_card)
    df["numero_tarjeta_hash"] = df["numero_tarjeta_raw"].apply(hash_value)
    df["cvv_hash"] = df["cvv"].apply(hash_value)

    df.drop(columns=["numero_tarjeta", "numero_tarjeta_raw", "cvv"], inplace=True)

    out_path = os.path.join(
        OUTPUT_DIR,
        os.path.basename(path).replace(".csv", ".cleaned.csv")
    )
    df.to_csv(out_path, sep=";", index=False, encoding="utf-8")
    logger.info(f"Tarjetas limpias guardadas en: {out_path}")

# =====================
# RUN
# =====================
def run_etl():
    logger.info("===== INICIO PIPELINE ETL =====")
    logger.info("Buscando ficheros en: %s", INPUT_DIR)

    if not os.path.exists(INPUT_DIR):
        logger.error("Directorio input no existe")
        return

    archivos = [f for f in os.listdir(INPUT_DIR) if f.endswith(".csv")]
    logger.info("Archivos encontrados: %s", archivos)

    for f in archivos:
        full_path = os.path.join(INPUT_DIR, f)
        if CLIENTES_PATTERN.match(f):
            process_client_file(full_path)
        elif TARJETAS_PATTERN.match(f):
            process_card_file(full_path)
        else:
            logger.info("Archivo ignorado (patrón no válido): %s", f)

    logger.info("===== FIN PIPELINE ETL =====")
