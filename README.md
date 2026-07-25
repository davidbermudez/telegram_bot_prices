# BOT TELEGRAM PARA AVISAR DE CAMBIOS DE PRECIO

Bot de Telegram para monitorizar precios de productos y recibir notificaciones cuando cambien.

El proyecto permite que varios usuarios añadan productos mediante Telegram y reciban automáticamente avisos cuando el precio del producto se modifique.

Aunque inicialmente está orientado a productos de Lidl, la arquitectura está preparada para incorporar otros comercios mediante nuevos módulos de extracción de precios (*scrapers*).

---

## Características

- 🤖 Bot de Telegram interactivo.
- 👥 Soporte para múltiples usuarios.
- 🛒 Cada usuario puede definir sus propios productos.
- 🔎 Extracción automática del nombre y precio del producto.
- 💾 Persistencia mediante SQLite.
- 📉 Detección de cambios de precio.
- 🔔 Notificaciones automáticas por Telegram.
- ⏱️ Monitorización periódica mediante cron.
- 🐍 Entorno virtual Python independiente.

---

# Arquitectura

El proyecto está dividido en varios componentes:

```
telegram_bot_prices/
│
├── bot.py # Bot Telegram e interacción con usuarios
├── monitor.py # Proceso de comprobación de precios
├── scraper.py # Extracción de datos de productos
├── database.py # Gestión de base de datos SQLite
├── config.py # Configuración del bot
│
├── precios.db # Base de datos SQLite
├── requirements.txt # Dependencias Python
│
└── .venv/ # Entorno virtual Python
```
---


---

# Funcionamiento general

El sistema funciona mediante dos procesos independientes:

## Bot Telegram (`bot.py`)

Proceso permanente encargado de:

- Registrar usuarios.
- Recibir comandos.
- Añadir productos.
- Mostrar seguimientos.
- Eliminar seguimientos.

Debe permanecer siempre activo.

Se recomienda ejecutarlo como servicio `systemd`.

---

## Monitor de precios (`monitor.py`)

Proceso periódico encargado de:

1. Obtener los productos registrados.
2. Consultar el precio actual.
3. Compararlo con el último precio almacenado.
4. Notificar a los usuarios si existe un cambio.
5. Actualizar el precio guardado.

Se ejecuta mediante `cron`.

---

# Requisitos

- Python 3.10 o superior.
- Cuenta de Telegram.
- Bot creado mediante BotFather.
- Sistema Linux recomendado.

---

# Instalación

Clonar o copiar el proyecto:

```bash
git clone https://github.com/davidbermudez/telegram_bot_prices.git
cd telegram_bot_prices
```

Crear un entorno virtual

```
python3 -m venv .venv
```

Activarlo:
```
source .venv/bin/activate
```

Instalar dependencias

```
pip install -r requirements.txt
```

En Telegram, crear un bot en @BotFather

Configura el bot en config.py con el token obtenido en Telegram

```
BOT_TOKEN = "TOKEN_DEL_BOT"
```

## Inicialización de la base de datos

```
python bot.py
```
Con ello se genera un archivo precios.db (SQLite) con las tablas:

### usuarios

Guarda los usuarios registrados.

Campos principales:

- id
- chat_id
- fecha_alta

### productos

Guarda los productos monitorizados.

Campos principales:

- id
- url
- nombre
- precio

### seguimientos

Relaciona usuarios y productos.

Permite que:

- varios usuarios sigan un mismo producto;
- un usuario siga múltiples productos.

## Uso del  bot

### Inicio

El usuario inicia una conversación:

    /start

El bot registra automáticamente al usuario.

### Añadir un producto

Ejecutar:

    /add

El bot solicitará la URL:

    🔗 Envíame la URL del producto que quieres vigilar.

Ejemplo:

    https://www.lidl.es/p/parkside-set-de-llaves-de-vaso-216-piezas/p100401392

El bot analizará el producto y creará el seguimiento.

### Consultar productos

Comando:

    /list

Ejemplo:
```
📋 Tus seguimientos:

#1
🛒 Set de llaves Parkside 216 piezas
💶 59.99€
```

### Eliminar seguimiento

Comando:

    /remove ID

Ejemplo:

    /remove 1

Elimina únicamente el seguimiento del usuario actual.

El producto seguirá disponible para otros usuarios.

### Ayuda

Comando:

    /help

Muestra los comandos disponibles.

## Monitorización automática

El monitor se puede ejecutar manualmente:

    python monitor.py

Ejemplo de salida:

Sin cambios: Set de llaves Parkside 216 piezas

## Programación con cron

Editar:

    crontab -e

Añadir:

    0 * * * * flock -n /tmp/pricelidl-monitor.lock /home/usuario/scripts/telegram_bot_prices/.venv/bin/python /home/usuario/scripts/telegram_bot_prices/monitor.py >> /home/usuario/scripts/telegram_bot_prices/monitor.log 2>&1

Esto ejecuta el monitor cada hora evitando ejecuciones simultáneas.

## Convertir el script en un servicio

### Crear un archivo con el formato adecuado

    sudo nano /etc/systemd/system/alertpricebot.service

```
[Unit]
Description=Price Telegram Bot
After=network.target

[Service]
User=david
WorkingDirectory=/home/david/scripts/telegram_bot_prices
ExecStart=/home/david/scripts/telegram_bot_prices/.venv/bin/python /home/david/scripts/telegram_bot_prices/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Activar el servicio

```
sudo systemctl daemon-reload
sudo systemctl enable alertpricebot
sudo systemctl start alertpricebot
```

### Verificar

```
systemctl status alertpricebot
```

### Ver los logs

```
journalctl -u alertpricebot -f
```

## Script monitor.py

Script que envía los mensajes con los cambios de precios de los productos suscritos por los usuarios


## Añadir nuevos comercios

La arquitectura está preparada para añadir nuevos scrapers.

Ejemplo futuro:

```
scrapers/
│
├── lidl.py
├── amazon.py
└── decathlon.py
```

Cada scraper deberá devolver:

```
{
    "nombre": "Nombre producto",
    "precio": "59.99€"
}
```

El monitor podrá seleccionar automáticamente el scraper adecuado según la URL.

## Mejoras futuras

Posibles evoluciones:

- Confirmación antes de crear seguimiento.
- Precio objetivo ("avísame cuando baje de X").
- Historial de precios.
- Gráficas de evolución.
- Soporte para más tiendas.
- Panel web de administración.
- Gestión de usuarios.
- Límites de productos por usuario.
- Dockerización completa.

## Licencia

Proyecto personal para uso privado.
