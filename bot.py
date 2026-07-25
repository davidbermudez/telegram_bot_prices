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
from scraper import obtener_datos_producto

import database

ESPERANDO_URL = 1


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


# command add
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🔗 Envíame la URL del producto que quieres vigilar."
    )

    return ESPERANDO_URL


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

    await update.message.reply_text(
        "🔗 Envíame la URL del producto que quieres vigilar."
    )

    return ESPERANDO_URL


async def recibir_url(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    chat_id = update.effective_chat.id

    url = update.message.text.strip()

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

        datos = obtener_datos_producto(url)

        usuario_id = database.obtener_usuario(
            chat_id
        )

        producto_id = database.crear_producto(
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

    except Exception as e:

        await update.message.reply_text(
            f"❌ No he podido analizar el producto.\n\n"
            f"{str(e)}"
        )

    return ConversationHandler.END


# 
async def list_products(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    chat_id = update.effective_chat.id

    productos = database.listar_productos_usuario(
        chat_id
    )

    if not productos:

        await update.message.reply_text(
            "📋 No tienes productos en seguimiento."
        )

        return


    mensaje = "📋 Tus seguimientos:\n\n"


    for producto in productos:

        mensaje += (
            f"#{producto[0]}\n"
            f"🛒 {producto[1]}\n"
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

        producto_id = int(
            context.args[0]
        )

    except ValueError:

        await update.message.reply_text(
            "❌ El ID debe ser un número"
        )

        return

    eliminado = database.eliminar_seguimiento(
        chat_id,
        producto_id
    )


    if eliminado:

        await update.message.reply_text(
            "✅ Seguimiento eliminado"
        )

    else:

        await update.message.reply_text(
            "⚠️ No existe ese seguimiento"
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

    database.inicializar()

    app = Application.builder()\
        .token(BOT_TOKEN)\
        .post_init(post_init)\
        .build()

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
