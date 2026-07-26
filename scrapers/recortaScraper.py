import requests


def resolver(url):

    respuesta = requests.get(
        url,
        allow_redirects=True,
        timeout=20
    )

    return respuesta.url
