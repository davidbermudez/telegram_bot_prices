from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
from config import BOT_TOKEN
from scrapers.router import get_scraper
from exceptions import (
    PriceMonitorError,
    UnsupportedStoreError,
    InvalidProductURLError,
    ProductNotFoundError,
    PriceNotFoundError,
    ProductNameNotFoundError,
    NetworkError,
)

import database

ESPERANDO_URL = 1

# errores
async def error_handler(
    update,
    context
):

    print(
        f"Error: {context.error}"
    )


# command start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    database.crear_usuario(chat_id)

    mensaje = """
👋 Bienvenido a *AlertPriceBot*

🛒 Este bot vigila productos por ti y te avisa cuando cambie su precio.

Para empezar:

1️⃣  Añade un producto:

`/add URL`

2️⃣  Consulta tus seguimientos:

`/list`

3️⃣  Elimina un seguimiento:

`/remove ID`

Escribe:

`/help`

para ver todos los comandos disponibles.
"""

    await update.message.reply_text(
        mensaje,
        parse_mode="Markdown"
    )


# command help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mensaje = """
🤖 *PriceLidl Bot - Ayuda*

Este bot permite vigilar precios de productos y recibir avisos cuando cambien.

📌 *Comandos disponibles*

/start
Registra tu usuario y muestra la bienvenida.

/add URL
Añade un producto para seguimiento.

Ejemplo:
/add https://www.lidl.es/p/...

/list
Muestra tus productos vigilados.

/remove ID
Elimina un seguimiento.

Ejemplo:
/remove 3

/help
Muestra esta ayuda.

💡 Recibirás una notificación automáticamente cuando el precio de un producto cambie.
"""

    await update.message.reply_text(
        mensaje,
        parse_mode="Markdown"
    )


# cancelar
async def cancelar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "❌ Operación cancelada."
    )

    return ConversationHandler.END


async def add_inicio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if context.args:

        url = " ".join(context.args)

        return await procesar_url(
            update,
            context,
            url
        )

    await update.message.reply_text(
        "🔗 Envíame la URL del producto que quieres vigilar."
    )

    return ESPERANDO_URL


async def procesar_url(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    url: str
):

    chat_id = update.effective_chat.id

    if not url.startswith("http"):

        await update.message.reply_text(
            "❌ Eso no parece una URL válida.\n\n"
            "Envíame un enlace completo."
        )

        return ESPERANDO_URL

    await update.message.reply_text(
        "🔎 Analizando producto..."
    )

    try:

        scraper_info = get_scraper(url)

        url_scraper = scraper_info.get(
            "url",
            url
        )

        datos = scraper_info["funcion"](
            url_scraper,
            scraper_info["comercio_id"]
        )

        usuario_id = database.obtener_usuario(chat_id)

        producto_id = database.crear_producto(
            scraper_info["comercio_id"],
            url,
            datos["nombre"],
            datos["precio"]
        )

        database.crear_seguimiento(
            usuario_id,
            producto_id
        )

        await update.message.reply_text(
            "✅ Seguimiento creado\n\n"
            f"🛒 {datos['nombre']}\n"
            f"💶 Precio actual: {datos['precio']}\n\n"
            "Te avisaré cuando cambie."
        )

    except UnsupportedStoreError:

        await update.message.reply_text(
            "❌ Este comercio todavía no está soportado."
        )

    except InvalidProductURLError:

        await update.message.reply_text(
            "❌ La URL no corresponde a un producto válido."
        )

    except ProductNotFoundError:

        await update.message.reply_text(
            "❌ El producto ya no está disponible."
        )

    except PriceNotFoundError:

        await update.message.reply_text(
            "⚠️ He encontrado el producto, pero no he podido localizar su precio."
        )

    except ProductNameNotFoundError:

        await update.message.reply_text(
            "⚠️ He encontrado la página, pero no he podido identificar el nombre del producto."
        )

    except NetworkError:

        await update.message.reply_text(
            "🌐 No he podido conectar con la tienda. Inténtalo de nuevo dentro de unos minutos."
        )

    except PriceMonitorError as e:

        await update.message.reply_text(
            f"⚠️ {e}"
        )

    except Exception as e:

        print(e)

        await update.message.reply_text(
            "❌ Se ha producido un error interno."
        )

    return ConversationHandler.END


async def recibir_url(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    url = update.message.text.strip()

    return await procesar_url(
        update,
        context,
        url
    )


async def list_products(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    chat_id = update.effective_chat.id

    usuario_id = database.obtener_usuario(chat_id)

    productos = database.obtener_seguimientos_usuario(
        usuario_id
    )

    if not productos:

        await update.message.reply_text(
            "📋 No tienes productos en seguimiento."
        )

        return


    mensaje = "📋 Tus seguimientos:\n\n"


    for numero, producto in enumerate(productos, start=1):

        mensaje += (
            f"{numero}️⃣ {producto[1]}\n"
            f"💶 {producto[2]}\n\n"
        )


    await update.message.reply_text(
        mensaje
    )


# command remove
async def remove(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    chat_id = update.effective_chat.id

    if not context.args:

        await update.message.reply_text(
            "Uso:\n/remove ID"
        )

        return

    try:

        posicion = int(
            context.args[0]
        )

    except ValueError:

        await update.message.reply_text(
            "❌ El ID debe ser un número"
        )

        return


    usuario_id = database.obtener_usuario(chat_id)


    producto_id = database.obtener_producto_por_posicion(
        usuario_id,
        posicion
    )


    if producto_id is None:

        await update.message.reply_text(
            "⚠️ No existe ese seguimiento."
        )

        return


    eliminado = database.eliminar_seguimiento(
        usuario_id,
        producto_id
    )


    if eliminado:

        await update.message.reply_text(
            "✅ Seguimiento eliminado"
        )

    else:

        await update.message.reply_text(
            "⚠️ No se pudo eliminar el seguimiento"
        )


async def post_init(application):

    from telegram import BotCommand

    await application.bot.set_my_commands(
        [
            BotCommand(
                "start",
                "Registrarse y comenzar"
            ),
            BotCommand(
                "add",
                "Añadir producto"
            ),
            BotCommand(
                "list",
                "Ver productos seguidos"
            ),
            BotCommand(
                "remove",
                "Eliminar seguimiento"
            ),
            BotCommand(
                "help",
                "Mostrar ayuda"
            ),
        ]
    )


def main():

    app = Application.builder()\
        .token(BOT_TOKEN)\
        .post_init(post_init)\
        .build()

    app.add_error_handler(error_handler)

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("help", help)
    )

    app.add_handler(
        CommandHandler("list", list_products)
    )

    app.add_handler(
        CommandHandler("remove", remove)
    )

    conv_add = ConversationHandler(

        entry_points=[
            CommandHandler(
                "add",
                add_inicio
            )
        ],

        states={

            ESPERANDO_URL: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    recibir_url
                )
            ]

        },

        fallbacks=[
            CommandHandler(
                "cancel",
                cancelar
            )
        ]
    )

    app.add_handler(conv_add)

    print("Bot iniciado")

    app.run_polling()


if __name__ == "__main__":
    main()
