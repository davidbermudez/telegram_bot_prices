import requests

import database
from scraper import obtener_datos_producto
from config import BOT_TOKEN


def enviar_telegram(chat_id, mensaje):

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": mensaje
        },
        timeout=20
    )


def comprobar_productos():

    productos = database.obtener_productos()

    for producto in productos:

        producto_id, url, nombre, precio_anterior = producto

        try:

            datos = obtener_datos_producto(url)

            precio_actual = datos["precio"]


            if precio_actual != precio_anterior:

                mensaje = (
                    "📉 Cambio de precio detectado\n\n"
                    f"🛒 {nombre}\n\n"
                    f"Antes: {precio_anterior}\n"
                    f"Ahora: {precio_actual}\n\n"
                    f"{url}"
                )


                usuarios = database.usuarios_producto(
                    producto_id
                )


                for chat_id in usuarios:

                    enviar_telegram(
                        chat_id,
                        mensaje
                    )


                database.actualizar_precio(
                    producto_id,
                    precio_actual
                )


                print(
                    f"Cambio {nombre}: "
                    f"{precio_anterior} -> {precio_actual}"
                )


            else:

                print(
                    f"Sin cambios: {nombre}"
                )


        except Exception as e:

            print(
                f"Error con {url}: {e}"
            )


if __name__ == "__main__":

    database.inicializar()

    comprobar_productos()
