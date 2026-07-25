import sqlite3

from database import DB_PATH


def crear_tablas(conn):

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        nombre TEXT
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comercios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        dominio TEXT NOT NULL UNIQUE,
        url_base TEXT,
        clase_scraper TEXT NOT NULL,
        activo INTEGER DEFAULT 1
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scraper_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        comercio_id INTEGER NOT NULL,
        campo TEXT NOT NULL,
        selector TEXT NOT NULL,

        FOREIGN KEY(comercio_id)
            REFERENCES comercios(id)
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        comercio_id INTEGER NOT NULL,
        url TEXT NOT NULL UNIQUE,
        nombre TEXT,
        precio_actual TEXT,
        ultimo_ok DATETIME,
        ultimo_error TEXT,
        fecha_error DATETIME,

        FOREIGN KEY(comercio_id)
            REFERENCES comercios(id)
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seguimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        fecha_alta DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(usuario_id)
            REFERENCES usuarios(id),

        FOREIGN KEY(producto_id)
            REFERENCES productos(id)
    )
    """)


    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS
    idx_scraper_config_campo
    ON scraper_config(comercio_id, campo)
    """)


    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS
    idx_usuario_producto
    ON seguimientos(usuario_id, producto_id)
    """)


    conn.commit()



def cargar_comercios(conn):

    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO comercios
    (
        nombre,
        dominio,
        url_base,
        clase_scraper
    )
    VALUES
    (
        'Lidl',
        'lidl.es',
        'https://www.lidl.es',
        'LidlScraper'
    )
    """)

    conn.commit()



def cargar_config_scrapers(conn):

    cursor = conn.cursor()

    cursor.execute("""
    SELECT id
    FROM comercios
    WHERE dominio = 'lidl.es'
    """)

    comercio = cursor.fetchone()

    if comercio is None:
        raise Exception(
            "No existe el comercio Lidl"
        )

    comercio_id = comercio[0]


    configuraciones = [
        (
            comercio_id,
            "nombre",
            "meta[property='og:title']"
        ),
        (
            comercio_id,
            "precio",
            "div.ods-price__value"
        )
    ]


    cursor.executemany(
        """
        INSERT OR IGNORE INTO scraper_config
        (
            comercio_id,
            campo,
            selector
        )
        VALUES (?, ?, ?)
        """,
        configuraciones
    )


    conn.commit()



def main():

    conn = sqlite3.connect(DB_PATH)

    crear_tablas(conn)

    cargar_comercios(conn)

    cargar_config_scrapers(conn)

    conn.close()


    print(
        "Base de datos inicializada correctamente"
    )



if __name__ == "__main__":
    main()
