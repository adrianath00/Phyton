import base_datos
import funciones_datos

# CONFIGURACION
USER, PASS, DSN = "SYSTEM", "SYSTEM", "localhost/xe"
RUTA_BIN = r"C:\oraclexe\app\oracle\product\11.2.0\server\bin"

def inicio():
    print("--- INICIANDO PROYECTO FINAL ---")
    
    # 1. Oracle Thick
    base_datos.activar_modo_thick(RUTA_BIN)
    
    # 2. ETL
    datos = funciones_datos.limpieza_completa("Clientes-2026-01-05.csv", "Tarjetas-2026-01-05.csv")
    
    # 3. Errores
    err = funciones_datos.crear_log_errores(datos)
    print(f"[*] Registros con errores: {err}")
    
    # 4. Carga
    db = base_datos.conectar_oracle(USER, PASS, DSN)
    if db:
        base_datos.crear_tablas_si_no_existen(db)
        subidos = base_datos.insertar_datos(db, datos)
        print(f"[!] EXITO: {subidos} registros subidos a Oracle.")
        db.close()

if __name__ == "__main__":
    inicio()