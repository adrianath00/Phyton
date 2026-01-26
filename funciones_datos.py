import csv
import re
import hashlib
import os
from datetime import datetime

def validar_dni(dni):
    dni = str(dni).strip().upper().replace('"', '')
    return bool(re.match(r'^[0-9]{8}[A-Z]$', dni))

def validar_email(email):
    email = str(email).strip().replace('"', '')
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def validar_tlf(tlf):
    tlf = str(tlf).strip().replace('"', '').split('.')[0]
    return bool(re.match(r'^[679][0-9]{8}$', tlf))

def enmascarar(num):
    n = str(num).strip().replace('"', '')
    return f"XXXX-XXXX-XXXX-{n[-4:]}"

def hash_cvv(valor):
    salt = "GANG_FUENLA_2025"
    return hashlib.sha256((salt + str(valor)).encode()).hexdigest()

def limpieza_completa(file_c, file_t):
    if not os.path.exists("output"): os.makedirs("output")
    clientes = []
    with open(file_c, 'r', encoding='latin-1') as f:
        lineas = [l.strip().strip('"') for l in f if l.strip()]
        reader = csv.DictReader(lineas, delimiter=';')
        for row in reader:
            d, e, t = validar_dni(row['dni']), validar_email(row['correo']), validar_tlf(row['telefono'])
            row.update({'DNI_OK': 'Y' if d else 'N', 'DNI_KO': 'N' if d else 'Y',
                        'Correo_OK': 'Y' if e else 'N', 'Correo_KO': 'N' if e else 'Y',
                        'Telefono_OK': 'Y' if t else 'N', 'Telefono_KO': 'N' if t else 'Y'})
            clientes.append(row)
    
    # Guardar cleaned
    with open(f"output/Clientes_limpios.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=clientes[0].keys(), delimiter=';')
        writer.writeheader()
        writer.writerows(clientes)
    return clientes

def crear_log_errores(datos):
    if not os.path.exists("logs"): os.makedirs("logs")
    malos = [c for c in datos if 'N' in [c['DNI_OK'], c['Correo_OK'], c['Telefono_OK']]]
    if malos:
        with open("logs/rows_rejected.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=malos[0].keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(malos)
        return len(malos)
    return 0

def crear_log_procesados(datos_validos):
    """Guarda registro de clientes procesados correctamente"""
    if not os.path.exists("logs"): os.makedirs("logs")
    if datos_validos:
        with open("logs/rows_processed.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=datos_validos[0].keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(datos_validos)
        return len(datos_validos)
    return 0

def crear_log_resumen(total, validos, errores, insertados, duplicados, errores_bd):
    """Crea resumen final del pipeline"""
    if not os.path.exists("logs"): os.makedirs("logs")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    resumen = f"""
=== RESUMEN PIPELINE {timestamp} ===
Total registros leídos: {total}
Registros válidos: {validos}
Registros rechazados: {errores}
Registros insertados en BD: {insertados}
Registros duplicados (no insertados): {duplicados}
Errores en inserción: {errores_bd}
===============================
"""
    with open("logs/resumen.txt", 'w', encoding='utf-8') as f:
        f.write(resumen)
    print(resumen)