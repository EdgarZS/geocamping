
# 🎕 GeoCamping

**GeoCamping** es una plataforma de reservas de zonas de campamento georreferenciadas, impulsada por mapas interactivos, pagos online y herramientas administrativas avanzadas.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey)
![Azure](https://img.shields.io/badge/Deployed%20on-Microsoft%20Azure-blue)

---

## 🏽 Funcionalidades

### 👥 Para usuarios (clientes)
- Mapa interactivo con zonas marcadas (Azure Maps)
- Consulta de información, imágenes y reglas por zona
- Selección de fechas con validación de disponibilidad
- Pronóstico del clima a 7 días al seleccionar una fecha
- Reservas online con integración Stripe
- Recepción de QR por correo tras el pago exitoso
- Vista de historial y estado de sus reservas

### 🛠️ Para administradores
- Autenticación separada y segura
- Registro gráfico de nuevas zonas con dibujo en el mapa
- Edición y eliminación de zonas existentes
- Gestión de otros administradores
- Validación de QR en campo para activar reservas
- Panel completo de gestión de reservas

---

## ⚙️ Tecnologías utilizadas

| Herramienta/Servicio           | Propósito                                        |
|-------------------------------|--------------------------------------------------|
| **Flask**                     | Backend, rutas y lógica de negocio               |
| **SQL Server (Azure)**        | Base de datos principal                          |
| **Azure Maps**                | Mapa satelital y polígonos                       |
| **Azure Blob Storage**        | Almacenamiento de imágenes y códigos QR         |
| **Azure Communication Services** | Envío de correos electrónicos               |
| **Stripe**                    | Pagos seguros                                    |
| **Open-Meteo API**            | Clima extendido por coordenadas                 |
| **Bootstrap 4**               | Diseño responsivo                                |
| **Pillow, qrcode**            | Generación y redimensionado de imágenes         |

---

## 📦 Requisitos

- Python 3.10 o superior
- Microsoft ODBC Driver for SQL Server (si ejecutas localmente)
- Claves/API Keys para:
  - Azure Maps
  - Azure Blob Storage
  - Azure Communication Services (Email)
  - Stripe
  - Open-Meteo (no requiere key)

---

## 🔧 Instalación local

1. Clona el repositorio:

```bash
git clone https://github.com/tu_usuario/geocamping.git
cd geocamping
```

2. Instala los paquetes necesarios:

```bash
pip install -r requirements.txt
```

3. Crea un archivo `.env` o configura tus variables de entorno:

```env
STRIPE_SECRET_KEY=...
STRIPE_PUBLISHABLE_KEY=...
ACS_CONNECTION_STRING=...
ACS_EMAIL_SENDER=...
AZURE_BLOB_CONNECTION_STRING=...
AZURE_BLOB_CONTAINER=...
SQL_SERVER=...
SQL_DB=...
SQL_USERNAME=...
SQL_PASSWORD=...
MAP_SUBSCRIPTION_KEY=...
SECRET_KEY=una_clave_secreta_segura
```

4. Ejecuta la app:

```bash
python app.py
```

Visita `http://localhost:5000` en tu navegador.

---

## 🚀 Despliegue en Azure App Service

1. Crea una instancia de App Service en Azure.
2. Usa el [Deployment Center](https://learn.microsoft.com/en-us/azure/app-service/deploy-continuous-deployment) para conectar tu repositorio GitHub.
3. Configura variables de entorno en **Configuration → Application settings**.
4. Asegúrate de usar un `startup command` apropiado si usas Linux:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## 📄 Estructura del proyecto

```
geocamping/
├── static/
│   └── ...         # Estilos, JS, imágenes
├── templates/
│   └── ...         # Archivos HTML Jinja2
├── app.py          # Lógica principal de Flask
├── requirements.txt
└── README.md
```

---

## 🛡️ Licencia

MIT License © [TuNombre](https://github.com/tu_usuario)

---

## 🤝 Agradecimientos

- Microsoft Azure for Students
- Open-Meteo for free and open weather data
- Stripe for friendly dev tools
- Flask for being awesome

---
