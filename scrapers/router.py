# scrapers/router.py

from urllib.parse import urlparse
import requests

from exceptions import UnsupportedStoreError
from database import obtener_comercio_por_dominio
from scrapers.generic import obtener_producto


def resolver_url(url):

    respuesta = requests.get(
        url,
        allow_redirects=True,
        timeout=20
    )

    return respuesta.url


def get_scraper(url):

    dominio = urlparse(url).netloc.lower()

    # Resolver enlaces cortos de Amazon
    if dominio.endswith("amzn.eu"):

        url = resolver_url(url)

        dominio = urlparse(url).netloc.lower()

    comercio = obtener_comercio_por_dominio(dominio)

    if comercio is None:

        raise UnsupportedStoreError(
            f"Comercio no soportado: {dominio}"
        )


    return {
        "funcion": obtener_producto,
        "comercio_id": comercio[0],
        "url": url
    }
