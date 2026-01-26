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
    cursor = conn.cursor()
    cursor.execute("DELETE FROM CLIENTES")
    final = 0
    for c in lista:
        if c['DNI_OK'] == 'Y':
            cursor.execute("""
                INSERT INTO CLIENTES (cod_cliente, nombre, apellido1, apellido2, dni, correo, telefono)
                VALUES (:1, :2, :3, :4, :5, :6, :7)
            """, (c['cod_cliente'], c['nombre'], c['apellido1'], c['apellido2'], 
                  c['dni'], c['correo'], c['telefono']))
            final += 1
    conn.commit()
    cursor.close()
    return final