import pandas as pd
import os

def limpiar_datos():
    # Usamos rutas absolutas para estar 100% seguros
    base_path = os.path.dirname(os.path.abspath(__file__))
    # Si tus archivos están en C:\PROYECTO_ETL_GANG_FUENLA\data...
    entrada = os.path.join(base_path, "data", "source")
    salida = os.path.join(base_path, "data", "output")
    
    print(f"DEBUG: Buscando archivos en: {entrada}")
    
    if not os.path.exists(entrada):
        print(f"ERROR: La carpeta {entrada} no existe.")
        return

    archivos = [f for f in os.listdir(entrada) if f.endswith('.csv')]
    print(f"DEBUG: Archivos encontrados: {archivos}")

    for f in archivos:
        try:
            ruta_input = os.path.join(entrada, f)
            # Intentamos leer el archivo
            df = pd.read_csv(ruta_input, sep=';', encoding='latin1') 
            
            print(f"DEBUG: Procesando {f}... Filas leídas: {len(df)}")
            
            # --- AQUÍ VA TU LÓGICA DE LIMPIEZA ---
            # Ejemplo rápido: nombres a mayúsculas
            if 'nombre' in df.columns:
                df['nombre'] = df['nombre'].str.upper()

            # Guardar
            if not os.path.exists(salida):
                os.makedirs(salida)
                
            ruta_output = os.path.join(salida, f.replace(".csv", ".cleaned.csv"))
            df.to_csv(ruta_output, index=False, sep=';', encoding='utf-8')
            
            if os.path.exists(ruta_output):
                print(f"ARCHIVO CREADO EN: {ruta_output}")
            else:
                print(f"ERROR: El archivo no se creó en {ruta_output}")

        except Exception as e:
            print(f"Error fatal con el archivo {f}: {e}")