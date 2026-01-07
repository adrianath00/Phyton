import pandas as pd
import os
from sqlalchemy import create_engine, text

def cargar_a_db():
    # --- PASO 1: UBICACIÓN Y CONEXIÓN ---
    # Calculamos la ruta de los archivos limpios (data/output)
    base_path = os.path.dirname(os.path.abspath(__file__))
    ruta_output = os.path.join(base_path, "data", "output")
    
    # Creamos el motor de la base de datos (se genera el archivo proyecto_final.db)
    engine = create_engine('sqlite:///proyecto_final.db')
    
    print("\n[SQL] Iniciando fase de carga...")

    # --- PASO 2: SELECCIÓN DE ARCHIVOS ---
    # Buscamos solo los archivos que ya hemos limpiado
    archivos = [f for f in os.listdir(ruta_output) if f.endswith('.cleaned.csv')]
    
    if not archivos:
        print("[SQL] Error: No se encontraron archivos limpios para cargar.")
        return

    for nombre_archivo in archivos:
        try:
            # --- PASO 3: LECTURA Y CARGA ---
            df = pd.read_csv(os.path.join(ruta_output, nombre_archivo), sep=';')
            
            # Decidimos el nombre de la tabla según el archivo
            nombre_tabla = "tabla_clientes" if "Clientes" in nombre_archivo else "tabla_tarjetas"
            
            # El comando 'to_sql' hace todo el trabajo:
            # 'if_exists=replace' borra la tabla vieja y crea la nueva para no duplicar datos
            df.to_sql(nombre_tabla, con=engine, if_exists='replace', index=False)
            print(f"Registros de '{nombre_archivo}' cargados en la tabla '{nombre_tabla}'.")
            
        except Exception as e:
            print(f"Error al cargar {nombre_archivo}: {e}")

    # --- PASO 4: PRUEBA DE FUNCIONAMIENTO ---
    print("\n[SQL] Verificando tablas creadas...")
    with engine.connect() as conexion:
        # Consultamos a la base de datos qué tablas tiene dentro
        res = conexion.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        for fila in res:
            print(f"   -> Tabla detectada: {fila[0]}")