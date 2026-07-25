# AlertPriceBot

Bot de Telegram para monitorizar precios de productos en comercios online y recibir notificaciones cuando cambien.

El objetivo del proyecto es disponer de un sistema sencillo y extensible que permita a cualquier usuario añadir productos mediante una URL, realizar un seguimiento automático y recibir avisos cuando el precio detectado por el scraper cambie.

Actualmente soporta productos de Lidl y está preparado para incorporar nuevos comercios mediante una arquitectura basada en scrapers independientes.

---

## Características

* 🤖 Integración con Telegram.
* 🛒 Seguimiento personalizado de productos por usuario.
* 🔎 Extracción automática de información desde páginas web.
* 💶 Control del precio actual de cada producto.
* 🔔 Avisos cuando el precio cambia.
* 🏪 Arquitectura preparada para múltiples comercios.
* ⚙️ Configuración de selectores HTML almacenada en base de datos.
* 🗄️ Persistencia mediante SQLite.
* 👥 Múltiples usuarios utilizando el mismo bot.

---

## Funcionamiento

El flujo básico es:

```
Usuario
   |
   | /add URL
   |
   v
Telegram Bot
   |
   v
Router de comercios
   |
   v
Scraper específico
   |
   v
Base de datos
   |
   v
Monitor periódico
   |
   v
Notificación Telegram
```

---

# Comandos disponibles

## `/start`

Registra al usuario e inicia la interacción con el bot.

---

## `/add`

Añade un producto al sistema de seguimiento.

Ejemplo:

```
/add https://www.lidl.es/p/...
```

El bot:

1. Identifica el comercio.
2. Ejecuta el scraper correspondiente.
3. Obtiene nombre y precio.
4. Guarda el producto.
5. Crea el seguimiento para el usuario.

---

## `/list`

Muestra los productos actualmente vigilados.

Ejemplo:

```
📋 Tus seguimientos:

1️⃣ Parkside Set de llaves de vaso
💶 59.99€

2️⃣ Taladro inalámbrico
💶 89.99€
```

Los números mostrados al usuario no corresponden al ID interno de la base de datos.

El sistema utiliza posiciones virtuales para evitar mostrar identificadores internos.

---

## `/remove`

Elimina un seguimiento.

Ejemplo:

```
/remove 2
```

El usuario elimina el segundo producto mostrado en `/list`.

Internamente el bot resuelve la posición visible con el producto real asociado.

---

## `/help`

Muestra la ayuda del bot.

---

# Arquitectura del proyecto

Actualmente:

```
alert-prices-bot/

├── bot.py
├── monitor.py
├── database.py
├── config.py
├── exceptions.py
│
├── scrapers/
│   ├── router.py
│   └── lidl.py
│
├── precios.db
├── requirements.txt
└── README.md
```

---

# Componentes principales

## bot.py

Responsable de la comunicación con Telegram.

Gestiona:

* comandos;
* conversaciones;
* altas de productos;
* consultas de usuario;
* eliminación de seguimientos.

No contiene lógica de scraping.

---

## monitor.py

Proceso encargado de revisar periódicamente los precios almacenados.

Normalmente se ejecuta mediante cron.

Ejemplo:

```
0 * * * * /ruta/al/proyecto/.venv/bin/python /ruta/al/proyecto/monitor.py
```

Realiza:

1. Consulta de productos activos.
2. Ejecución del scraper correspondiente.
3. Comparación con el precio almacenado.
4. Envío de avisos si detecta cambios.

---

## scrapers/

Contiene los módulos encargados de obtener información de cada comercio.

Ejemplo:

```
scrapers/

├── router.py
└── lidl.py
```

El router determina qué scraper debe utilizarse según la URL.

Ejemplo:

```
https://www.lidl.es/p/...
        |
        v
     LidlScraper
```

---

## database.py

Capa de acceso a SQLite.

Gestiona:

* usuarios;
* comercios;
* configuración de scrapers;
* productos;
* seguimientos.

---

# Base de datos

Tablas principales:

## usuarios

Usuarios registrados en Telegram.

Campos principales:

* id interno.
* chat_id.
* fecha de alta.

---

## comercios

Catálogo de comercios soportados.

Ejemplo:

```
1 | Lidl | lidl.es
```

---

## scraper_config

Configuración dinámica del scraper.

Permite modificar selectores HTML sin cambiar código.

Ejemplo:

```
nombre:
meta[property='og:title']

precio:
div.ods-price__value
```

---

## productos

Productos monitorizados.

Incluye:

* URL.
* nombre.
* precio actual.
* comercio asociado.
* estado de última comprobación.

---

## seguimientos

Relación entre usuarios y productos.

Permite que varios usuarios puedan seguir el mismo producto.

---

# Instalación

## Requisitos

* Python 3.10+
* SQLite
* Cuenta de Telegram
* Bot creado mediante BotFather

---

## Crear entorno virtual

```
python3 -m venv .venv
```

Activar:

Linux:

```
source .venv/bin/activate
```

Windows:

```
.venv\Scripts\activate
```

---

## Instalar dependencias

```
pip install -r requirements.txt
```

---

## Configuración

Crear el archivo de configuración con el token del bot:

```
BOT_TOKEN=xxxxxxxx
```

---

# Ejecución

## Bot Telegram

```
python3 bot.py
```

Debe mostrar:

```
Bot iniciado
```

---

## Monitor

Ejecutar manualmente:

```
python3 monitor.py
```

o mediante cron.

---

# Añadir nuevos comercios

Para incorporar un nuevo comercio:

1. Crear un scraper dentro de `scrapers/`.
2. Añadir la identificación del comercio en `router.py`.
3. Crear el registro correspondiente en la tabla `comercios`.
4. Añadir sus selectores HTML en `scraper_config`.

Ejemplo futuro:

```
scrapers/

├── lidl.py
├── amazon.py
├── mediamarkt.py
└── decathlon.py
```

---

# Gestión de errores

El proyecto utiliza excepciones específicas:

* Producto no encontrado.
* Precio no localizado.
* Nombre no localizado.
* Comercio no soportado.
* Error de conexión.

Esto permite distinguir entre:

* un producto eliminado;
* un cambio en la web;
* un fallo temporal de red.

---

# Estado actual

Proyecto en fase de evolución.

Versión actual:

```
1.x
```

Próximos objetivos:

* Sistema de migraciones de base de datos.
* Historial de precios.
* Más comercios.
* Mejor gestión de errores.
* Panel de administración.
* Configuración avanzada por usuario.

---

# Licencia

Pendiente de definir.

---

Desarrollado con Python, SQLite y Telegram Bot API.
