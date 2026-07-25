import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 Chrome/137.0 Safari/537.36"
    )
}


def obtener_datos_producto(url):

    respuesta = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    respuesta.raise_for_status()

    soup = BeautifulSoup(
        respuesta.text,
        "html.parser"
    )

    titulo = soup.select_one(
        "meta[property='og:title']"
    )

    precio = soup.select_one(
        # for Lidl 
        "div.ods-price__value"
    )

    if precio is None:
        raise Exception(
            "No se ha podido localizar el precio"
        )

    nombre = (
        titulo["content"]
        if titulo
        else "Producto sin nombre"
    )

    return {
        "nombre": nombre,
        "precio": precio.text.strip()
    }
