# db_handler.py
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger("db")

# Por defecto sqlite local para reproducibilidad en clase. Puedes configurar DATABASE_URL en .env
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proyecto_final.db')}")

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "output")

def conectar():
    logger.info("Conectando a BD: %s", DATABASE_URL)
    engine = create_engine(DATABASE_URL, echo=False, future=True)
    return engine

def cargar_a_db():
    engine = conectar()
    archivos = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.cleaned.csv')]
    if not archivos:
        logger.info("No hay archivos cleaned.csv en %s", OUTPUT_DIR)
        return

    with engine.begin() as conn:
        for fname in archivos:
            path = os.path.join(OUTPUT_DIR, fname)
            df = pd.read_csv(path, sep=';', dtype=str, encoding='utf-8')
            # Decidir tabla: si contiene "Clientes" en nombre -> tabla_clientes, else tabla_tarjetas
            if "Clientes" in fname or "clientes" in fname.lower():
                table_name = "tabla_clientes"
            else:
                table_name = "tabla_tarjetas"

            logger.info("Insertando %s filas en tabla %s", len(df), table_name)
            # if_exists = 'append' para no perder datos; crea tabla si no existe
            df.to_sql(table_name, con=conn, if_exists='append', index=False)

    logger.info("Carga a BD completada.")

if __name__ == "__main__":
    cargar_a_db()
