import sqlite3


DB = "precios.db"


def conectar():
    return sqlite3.connect(DB)


def inicializar():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY,
        chat_id INTEGER UNIQUE,
        fecha_alta DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY,
        url TEXT UNIQUE,
        nombre TEXT,
        precio TEXT,
        fecha_alta DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seguimientos (
        usuario_id INTEGER,
        producto_id INTEGER,
        UNIQUE(usuario_id, producto_id)
    )
    """)

    conn.commit()
    conn.close()


def crear_usuario(chat_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO usuarios(chat_id)
        VALUES (?)
        """,
        (chat_id,)
    )

    conn.commit()
    conn.close()


def obtener_usuario(chat_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id FROM usuarios
        WHERE chat_id=?
        """,
        (chat_id,)
    )

    resultado = cursor.fetchone()

    conn.close()

    return resultado[0] if resultado else None


def crear_producto(url, nombre, precio):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO productos(
            url,
            nombre,
            precio
        )
        VALUES (?, ?, ?)
        """,
        (
            url,
            nombre,
            precio
        )
    )

    conn.commit()

    cursor.execute(
        """
        SELECT id FROM productos
        WHERE url=?
        """,
        (url,)
    )

    producto_id = cursor.fetchone()[0]

    conn.close()

    return producto_id



def crear_seguimiento(usuario_id, producto_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO seguimientos
        VALUES (?,?)
        """,
        (
            usuario_id,
            producto_id
        )
    )

    conn.commit()
    conn.close()


def listar_productos_usuario(chat_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            p.id,
            p.nombre,
            p.precio
        FROM productos p
        INNER JOIN seguimientos s
            ON p.id = s.producto_id
        INNER JOIN usuarios u
            ON s.usuario_id = u.id
        WHERE u.chat_id = ?
        ORDER BY p.id
        """,
        (chat_id,)
    )

    productos = cursor.fetchall()

    conn.close()

    return productos


def eliminar_seguimiento(chat_id, producto_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM seguimientos
        WHERE usuario_id = (
            SELECT id
            FROM usuarios
            WHERE chat_id = ?
        )
        AND producto_id = ?
        """,
        (
            chat_id,
            producto_id
        )
    )

    eliminado = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return eliminado


def obtener_productos():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, url, nombre, precio
        FROM productos
        """
    )

    productos = cursor.fetchall()

    conn.close()

    return productos


def actualizar_precio(producto_id, precio):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE productos
        SET precio = ?
        WHERE id = ?
        """,
        (
            precio,
            producto_id
        )
    )

    conn.commit()
    conn.close()


def usuarios_producto(producto_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT u.chat_id
        FROM usuarios u
        INNER JOIN seguimientos s
            ON u.id = s.usuario_id
        WHERE s.producto_id = ?
        """,
        (producto_id,)
    )

    usuarios = cursor.fetchall()

    conn.close()

    return [
        usuario[0]
        for usuario in usuarios
    ]
