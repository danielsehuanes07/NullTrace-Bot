# NullTrace OSINT Bot

Sistema de automatización OSINT desarrollado con FastAPI, Docker, n8n y Telegram para la recolección y análisis de información pública.

---

## 🚀 Características

* Automatización de consultas OSINT mediante Telegram
* Integración con múltiples fuentes públicas
* Scraping de información con Playwright y BeautifulSoup
* Backend desarrollado en FastAPI
* Orquestación de flujos con n8n
* Despliegue local mediante Docker

---

## 🌎 Alcance

Este proyecto está enfocado principalmente en fuentes públicas de Colombia (SIMIT, RUES, entre otras).

Toda la información utilizada proviene de fuentes abiertas (OSINT).

---

## 🧱 Arquitectura

* **n8n** → Orquestación de flujos
* **FastAPI** → Microservicio backend
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
* Bot de Telegram (BotFather)
* Dominio público o túnel (ngrok, Cloudflare Tunnel, etc.)

---

## 📥 Clonar repositorio

```
git clone https://github.com/danielsehuanes07/NullTrace-Bot.git
cd NullTrace-Bot
```

---

## ▶️ Ejecutar proyecto

```
docker compose up --build
```

---

## 🌐 Servicios

* n8n → http://localhost:5679
* API → http://localhost:5000

---

## 🔄 Importar workflow en n8n

1. Abre n8n en:

   ```
   http://localhost:5679
   ```

2. En la interfaz:

   * Click en **Import**
   * Selecciona:

   ```
   n8n/workflow.json
   ```

3. Verifica los nodos importados

4. Configura las credenciales necesarias (Telegram, APIs, etc.)

5. Ejecuta el workflow manualmente para validar funcionamiento

---

## 🤖 Configuración de Telegram

1. Crear bot en Telegram con **@BotFather**
2. Copiar el token generado
3. En n8n:

   * Crear credenciales de Telegram
   * Asignarlas a los nodos correspondientes

---

## 🌍 Configuración de dominio (IMPORTANTE)

Para que Telegram funcione correctamente, necesitas exponer n8n a internet.

Ejemplo con ngrok:

```
ngrok http 5679
```

Esto generará una URL pública:

```
https://xxxx.ngrok-free.app
```

---

## ⚠️ Configuración en docker-compose.yml

Debes editar:

```
docker-compose.yml
```

Y reemplazar:

```
WEBHOOK_URL=https://your-domain.com
N8N_HOST=your-domain.com
```

Por tu dominio real:

```
WEBHOOK_URL=https://tu-dominio-publico
N8N_HOST=tu-dominio-publico
```

Puedes usar:

* ngrok
* Cloudflare Tunnel
* VPS con dominio propio
* cualquier dominio accesible públicamente

---

## 🧪 Pruebas

Ejemplo de prueba del microservicio:

```
curl http://localhost:5000/consultar/spam/3001234567
```

---

## 🔐 API externas (opcional)

El proyecto incluye integraciones con APIs externas.

Ejemplo:

```
YOUR_API_KEY
```

Debes reemplazarlo por tu propia clave si deseas usar esa funcionalidad.

---

## ⚠️ Nota importante

Este proyecto NO incluye:

* tokens reales
* API keys reales
* credenciales
* configuraciones personales

---

## 🧠 Funcionamiento sin APIs externas

El sistema puede seguir funcionando parcialmente gracias a:

* scraping web
* fuentes OSINT públicas
* lógica propia del backend

---

## 🛠️ Personalización

El proyecto es modular y puede ampliarse fácilmente con nuevas fuentes OSINT, APIs y flujos en n8n.:

* agregar nuevas fuentes OSINT
* integrar nuevas APIs
* crear nuevos flujos en n8n
* mejorar el backend en FastAPI

Esto lo convierte en una base flexible para proyectos de automatización en ciberseguridad y OSINT.

---

## 👨‍💻 Autor

Daniel Sehuanes

