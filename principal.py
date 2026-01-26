import base_datos
import funciones_datos

# CONFIGURACION
USER, PASS, DSN = "SYSTEM", "SYSTEM", "localhost/xe"
RUTA_BIN = r"C:\oraclexe\app\oracle\product\11.2.0\server\bin"

def inicio():
    print("=== INICIANDO PIPELINE ETL ===\n")
    
    # 1. Activar Oracle Thick
    print("[1/5] Activando Oracle Thick...")
    base_datos.activar_modo_thick(RUTA_BIN)
    
    # 2. Limpieza y validación de datos
    print("[2/5] Limpiando y validando datos...")
    datos = funciones_datos.limpieza_completa("Clientes-2026-01-05.csv", "Tarjetas-2026-01-05.csv")
    total_registros = len(datos)
    print(f"    ✓ {total_registros} registros leídos\n")
    
    # 3. Registrar rechazados
    print("[3/5] Procesando registros con errores...")
    rechazados = funciones_datos.crear_log_errores(datos)
    validos = [d for d in datos if d['DNI_OK'] == 'Y']
    print(f"    ✓ {rechazados} registros rechazados\n")
    
    # 4. Guardar procesados
    print("[4/5] Guardando registros válidos...")
    procesados = funciones_datos.crear_log_procesados(validos)
    print(f"    ✓ {procesados} registros válidos guardados\n")
    
    # 5. Carga a BD
    print("[5/5] Cargando a base de datos Oracle...")
    db = base_datos.conectar_oracle(USER, PASS, DSN)
    if db:
        base_datos.crear_tablas_si_no_existen(db)
        resultado = base_datos.insertar_datos(db, datos)
        print(f"    ✓ {resultado['insertados']} insertados")
        print(f"    ⚠ {resultado['duplicados']} duplicados (no insertados)")
        if resultado['errores'] > 0:
            print(f"    ✗ {resultado['errores']} errores en inserción")
        db.close()
        
        # Resumen final
        print("\n")
        funciones_datos.crear_log_resumen(total_registros, len(validos), rechazados, 
                                          resultado['insertados'], resultado['duplicados'], 
                                          resultado['errores'])
        print("[✓] PIPELINE COMPLETADO\n")
    else:
        print("[✗] No se pudo conectar a Oracle")

if __name__ == "__main__":
    inicio()