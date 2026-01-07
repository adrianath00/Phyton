import os
import sys
import importlib.util

def cargar_modulo_manual(nombre_archivo):
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_archivo = os.path.join(ruta_actual, nombre_archivo)
    if os.path.exists(ruta_archivo):
        spec = importlib.util.spec_from_file_location("modulo", ruta_archivo)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        return modulo
    return None

def main():
    print("--- INICIANDO PIPELINE ETL ---")
    
    # 1. EJECUTAR LIMPIEZA
    etl = cargar_modulo_manual("etl_logic.py")
    if etl:
        etl.limpiar_datos()
    
    # 2. EJECUTAR CARGA A SQL
    db = cargar_modulo_manual("db_handler.py")
    if db:
        db.cargar_a_db()
    
    print("--- PIPELINE COMPLETADO ---")

if __name__ == "__main__":
    main()