#!/usr/bin/env python3
# run_pipeline.py
import os
from src.utils.logger import get_logger
import logging
from dotenv import load_dotenv

# Cargar .env si existe
load_dotenv()

logger = get_logger()

def main():
    logger.info("===== INICIO PIPELINE ETL =====")
    try:
        # 1) Limpieza y transformación
        import etl_logic
        etl_logic.run_etl()

        # 2) Carga a la base de datos
        import db_handler
        db_handler.cargar_a_db()

        logger.info("Pipeline ejecutado correctamente")
    except Exception as e:
        logger.exception("Error en el pipeline: %s", e)
    finally:
        logger.info("===== FIN PIPELINE ETL =====")

if __name__ == "__main__":
    main()
