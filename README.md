# NullTrace OSINT Bot

Sistema de automatización OSINT desarrollado con FastAPI, Docker, n8n y Telegram para la recolección y análisis de información pública.

---

## 🚀 Características

* Automatización de consultas OSINT mediante Telegram
* Integración con múltiples fuentes públicas
* Scraping de información (Playwright + BeautifulSoup)
* Microservicio en FastAPI
* Orquestación con n8n
* Despliegue local con Docker

---

## 🌎 Alcance

Este proyecto está enfocado principalmente en fuentes públicas de **Colombia** (SIMIT, RUES, entre otras).

Toda la información consultada proviene de **datos públicos (OSINT)**.

---

## 🧱 Arquitectura

* **n8n** → Orquestación de flujos
* **FastAPI** → Backend (microservicio)
* **Docker Compose** → Infraestructura
* **Telegram Bot** → Interfaz de usuario

---

## 📁 Estructura del proyecto

```
.
├── docker-compose.yml
├── microservicio/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
└── n8n/
    └── workflow.json
```

---

## ⚙️ Requisitos

* Docker Desktop
* Git
* ngrok (opcional para uso en tiempo real)

---

## ▶️ Ejecución

Clonar el repositorio:

```
git clone https://github.com/danielsehuanes07/NullTrace-Bot.git
cd NullTrace-Bot
```

Levantar servicios:

```
docker compose up --build
```

---

## 🌐 Servicios

* n8n: http://localhost:5679
* API: http://localhost:5000

---

## 🔄 Importar workflow en n8n

1. Accede a: http://localhost:5679
2. Importa el archivo:

```
n8n/workflow.json
```

---

## 🤖 Configuración de Telegram (OBLIGATORIO)

Para que el bot funcione:

1. Crear un bot en Telegram usando **@BotFather**
2. Obtener el token del bot
3. En n8n:

   * Crear credenciales de Telegram
   * Asignarlas a los nodos correspondientes

---

## 🌍 Uso con ngrok (IMPORTANTE)

Para recibir mensajes desde Telegram en local:

1. Ejecutar:

```
ngrok http 5679
```

2. Copiar la URL generada, por ejemplo:

```
https://xxxx.ngrok-free.app
```

---

## ⚠️ Configuración en docker-compose.yml

Debes editar el archivo:

```
docker-compose.yml
```

Y reemplazar:

```
WEBHOOK_URL=https://your-domain.com
N8N_HOST=your-domain.com
```

Por tu URL de ngrok:

```
WEBHOOK_URL=https://tu-url-ngrok.ngrok-free.app
N8N_HOST=tu-url-ngrok.ngrok-free.app
```

---

## 🧪 Pruebas del microservicio

Puedes probar directamente:

```
curl http://localhost:5000/consultar/spam/3001234567
```

---

## 🔐 API externas (opcional)

El proyecto incluye integración con servicios externos como NumVerify:

```
YOUR_API_KEY
```

Debes reemplazarlo por tu propia clave si deseas usar esa funcionalidad.

---

## ⚠️ Nota importante

* No se incluyen credenciales reales
* No se incluyen tokens
* No se incluyen API keys
* El usuario debe configurar sus propios servicios

---

## 🧠 Funcionamiento sin API keys

El sistema puede funcionar parcialmente sin APIs externas, ya que utiliza:

* scraping web
* fuentes OSINT públicas
* lógica propia del backend

---

## 👨‍💻 Autor

Daniel Sehuanes

