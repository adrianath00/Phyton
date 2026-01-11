import pandas as pd
import os
from sqlalchemy import create_engine

# CONFIGURACIÓN: Cambia esto por tus datos de PostgreSQL o MySQL
# 'tipo_db://usuario:password@localhost:puerto/nombre_bd'
DATABASE_URL = "postgresql://postgres:admin@localhost:5432/ejercicio_final"

def cargar_a_db():
    engine = create_engine(DATABASE_URL)
    ruta_output = "data/output"
    
    archivos = [f for f in os.listdir(ruta_output) if f.endswith('.cleaned.csv')]
    
    for f in archivos:
        df = pd.read_csv(f"{ruta_output}/{f}", sep=';')
        nombre_tabla = "clientes" if "Clientes" in f else "tarjetas"
        
        # Insertar datos. Si la tabla no existe, la crea sola.
        df.to_sql(nombre_tabla, engine, if_exists='append', index=False)
        print(f"Datos de {f} subidos a la tabla {nombre_tabla}.")

if __name__ == "__main__":
    cargar_a_db()