import oracledb

def activar_modo_thick(ruta_bin):
    try:
        oracledb.init_oracle_client(lib_dir=ruta_bin)
        print("[+] Modo Thick activado.")
    except Exception as e:
        print(f"[-] Error modo Thick: {e}")

def conectar_oracle(user, password, dsn):
    try:
        return oracledb.connect(user=user, password=password, dsn=dsn)
    except Exception as e:
        print(f"[-] Error conexion: {e}")
        return None

def crear_tablas_si_no_existen(conn):
    cursor = conn.cursor()
    # SQL para Clientes
    cursor.execute("""
        BEGIN
            EXECUTE IMMEDIATE 'CREATE TABLE CLIENTES (
                cod_cliente VARCHAR2(10) PRIMARY KEY,
                nombre VARCHAR2(50),
                apellido1 VARCHAR2(50),
                apellido2 VARCHAR2(50),
                dni VARCHAR2(12),
                correo VARCHAR2(100),
                telefono VARCHAR2(20)
            )';
        EXCEPTION WHEN OTHERS THEN IF SQLCODE != -955 THEN RAISE; END IF;
        END;
    """)
    conn.commit()
    cursor.close()

def insertar_datos(conn, lista):
    """Inserta datos evitando duplicados (clave primaria: cod_cliente)"""
    cursor = conn.cursor()
    insertados = 0
    duplicados = 0
    errores = 0
    
    for c in lista:
        if c['DNI_OK'] == 'Y':
            try:
                cursor.execute("""
                    INSERT INTO CLIENTES (cod_cliente, nombre, apellido1, apellido2, dni, correo, telefono)
                    VALUES (:1, :2, :3, :4, :5, :6, :7)
                """, (c['cod_cliente'], c['nombre'], c['apellido1'], c['apellido2'], 
                      c['dni'], c['correo'], c['telefono']))
                insertados += 1
            except oracledb.IntegrityError:
                # cod_cliente duplicado
                duplicados += 1
            except Exception as e:
                print(f"[-] Error insertando {c['cod_cliente']}: {e}")
                errores += 1
    
    conn.commit()
    cursor.close()
    return {"insertados": insertados, "duplicados": duplicados, "errores": errores}