import requests
from bs4 import BeautifulSoup

from database import obtener_config_scraper

from exceptions import (
    PriceNotFoundError,
    ProductNameNotFoundError,
    ProductNotFoundError,
    NetworkError,
)


COMERCIO_ID = 1


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 Chrome/137.0 Safari/537.36"
    )
}



def obtener_producto(url):

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

    try:
        respuesta.raise_for_status()

    except requests.HTTPError as e:
        raise NetworkError(str(e))


    soup = BeautifulSoup(
        respuesta.text,
        "html.parser"
    )


    selector_nombre = obtener_config_scraper(
        COMERCIO_ID,
        "nombre"
    )


    selector_precio = obtener_config_scraper(
        COMERCIO_ID,
        "precio"
    )


    if not selector_nombre:

        raise ProductNameNotFoundError(
            "No existe configuración para nombre"
        )


    if not selector_precio:

        raise PriceNotFoundError(
            "No existe configuración para precio"
        )


    titulo = soup.select_one(
        selector_nombre
    )


    precio = soup.select_one(
        selector_precio
    )


    if titulo is None:

        raise ProductNameNotFoundError(
            "No se ha encontrado el nombre"
        )


    if precio is None:

        raise PriceNotFoundError(
            "No se ha encontrado el precio"
        )


    return {
        "nombre": titulo["content"],
        "precio": precio.text.strip()
    }
