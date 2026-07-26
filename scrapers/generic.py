from bs4 import BeautifulSoup
import requests

import database

from exceptions import (
    PriceNotFoundError,
    ProductNameNotFoundError,
    ProductNotFoundError,
    NetworkError,
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 Chrome/137.0 Safari/537.36"
    )
}


def obtener_producto(url, comercio_id):

    try:

        respuesta = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

    except requests.RequestException as e:

        raise NetworkError(str(e))


    if respuesta.status_code == 404:

        raise ProductNotFoundError(
            "Producto no encontrado"
        )


    respuesta.raise_for_status()


    soup = BeautifulSoup(
        respuesta.text,
        "html.parser"
    )


    selector_nombre = database.obtener_config_scraper(
        comercio_id,
        "nombre"
    )

    selector_precio = database.obtener_config_scraper(
        comercio_id,
        "precio"
    )


    nombre_elemento = soup.select_one(
        selector_nombre
    )

    if nombre_elemento is None:

        raise ProductNameNotFoundError(
            "No se encontró el nombre"
        )


    precio_elemento = soup.select_one(
        selector_precio
    )

    if precio_elemento is None:

        raise PriceNotFoundError(
            "No se encontró el precio"
        )


    nombre = (
        nombre_elemento["content"]
        if nombre_elemento.name == "meta"
        else nombre_elemento.text.strip()
    )


    return {
        "nombre": nombre,
        "precio": precio_elemento.text.strip()
    }
