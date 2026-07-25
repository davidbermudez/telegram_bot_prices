import sqlite3

DB_PATH = "precios.db"


def conectar():

    return sqlite3.connect(DB_PATH)



# -------------------------
# Usuarios
# -------------------------

def crear_usuario(telegram_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO usuarios
        (
            chat_id
        )
        VALUES (?)
        """,
        (
            telegram_id,
        )
    )

    conn.commit()
    conn.close()



def obtener_usuario(telegram_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM usuarios
        WHERE chat_id = ?
        """,
        (
            telegram_id,
        )
    )

    usuario = cursor.fetchone()

    conn.close()

    if usuario:
        return usuario[0]

    return None



# -------------------------
# Comercios
# -------------------------

def obtener_comercio_por_dominio(
        dominio
):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            nombre,
            dominio,
            clase_scraper

        FROM comercios

        WHERE dominio = ?
        AND activo = 1
        """,
        (
            dominio,
        )
    )

    comercio = cursor.fetchone()

    conn.close()

    return comercio



# -------------------------
# Configuración scraper
# -------------------------

def obtener_config_scraper(
        comercio_id,
        campo
):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT selector

        FROM scraper_config

        WHERE comercio_id = ?
        AND campo = ?
        """,
        (
            comercio_id,
            campo
        )
    )

    resultado = cursor.fetchone()

    conn.close()

    if resultado:
        return resultado[0]

    return None



# -------------------------
# Productos
# -------------------------

def crear_producto(
        comercio_id,
        url,
        nombre,
        precio
):

    conn = conectar()
    cursor = conn.cursor()


    cursor.execute(
        """
        INSERT OR IGNORE INTO productos
        (
            comercio_id,
            url,
            nombre,
            precio_actual,
            ultimo_ok
        )

        VALUES
        (
            ?,
            ?,
            ?,
            ?,
            CURRENT_TIMESTAMP
        )
        """,
        (
            comercio_id,
            url,
            nombre,
            precio
        )
    )


    conn.commit()


    cursor.execute(
        """
        SELECT id

        FROM productos

        WHERE url = ?
        """,
        (
            url,
        )
    )


    producto = cursor.fetchone()


    conn.close()


    return producto[0]



# -------------------------
# Seguimientos
# -------------------------

def crear_seguimiento(
        usuario_id,
        producto_id
):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO seguimientos
        (
            usuario_id,
            producto_id
        )

        VALUES
        (
            ?,
            ?
        )
        """,
        (
            usuario_id,
            producto_id
        )
    )

    conn.commit()
    conn.close()



def obtener_seguimientos_usuario(
        usuario_id
):

    conn = conectar()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT

            productos.id,
            productos.nombre,
            productos.precio_actual,
            seguimientos.fecha_alta


        FROM seguimientos


        JOIN productos

        ON productos.id = seguimientos.producto_id


        WHERE seguimientos.usuario_id = ?


        ORDER BY seguimientos.fecha_alta ASC
        """,
        (
            usuario_id,
        )
    )


    productos = cursor.fetchall()

    conn.close()

    return productos



def obtener_producto_por_posicion(
        usuario_id,
        posicion
):

    conn = conectar()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT productos.id


        FROM seguimientos


        JOIN productos

        ON productos.id = seguimientos.producto_id


        WHERE seguimientos.usuario_id = ?


        ORDER BY seguimientos.fecha_alta ASC


        LIMIT 1 OFFSET ?
        """,
        (
            usuario_id,
            posicion - 1
        )
    )


    producto = cursor.fetchone()

    conn.close()


    if producto:

        return producto[0]


    return None



def eliminar_seguimiento(
        usuario_id,
        producto_id
):

    conn = conectar()
    cursor = conn.cursor()


    cursor.execute(
        """
        DELETE FROM seguimientos

        WHERE usuario_id = ?
        AND producto_id = ?
        """,
        (
            usuario_id,
            producto_id
        )
    )


    eliminado = cursor.rowcount > 0

    conn.commit()
    conn.close()


    return eliminado
