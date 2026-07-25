from urllib.parse import urlparse

from exceptions import UnsupportedStoreError
from scrapers.lidl import obtener_producto


def get_scraper(url):

    dominio = urlparse(url).netloc.lower()

    if dominio.endswith("lidl.es"):

        return {
            "funcion": obtener_producto,
            "comercio_id": 1
        }

    raise UnsupportedStoreError(
        f"Comercio no soportado: {dominio}"
    )
