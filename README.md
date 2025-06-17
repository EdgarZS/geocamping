
# 🎕 GeoCamping

**GeoCamping** es una plataforma de reservas de zonas de campamento georreferenciadas, impulsada por mapas interactivos, pagos online y herramientas administrativas avanzadas.

![Python](https://img.shields.io/badge/Python-3.13+-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey)
![Azure](https://img.shields.io/badge/Deployed%20on-Microsoft%20Azure-blue)

---
## Esquipo de Desarrollo

Este proyecto fue desarrollado como parte del Proyecto Final para la materia de "Programacion de Bases de Datos - 5701" en el "Tecnologico de Estudios Superiores de Ecatepec"

| Nombre          | Rol                     |
| --------------- | ----------------------- |
| Alcántara Pérez Alan Eduardo    | Administrador del Servidor SQL       |
| Arana López Estefany Michelle    | Administradora del Servicio de Comunicaciones   |
| Castro Soriano Víctor Adrián   | Administrador del gestor de archivos BLOB |
| Estrada Tapia Fernanda Graciela   | Administradora del servicio de Azure Maps     |
| Huerta Torres Miguel Ángel | Experto en Bases de Datos        |
| Zaragoza San Juan Edgar Noe | Lider del Proyecto, Programador FullStack        |

---

## Funcionalidades

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

- Python 3.13 o superior
- Microsoft ODBC Driver for SQL Server
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

Visita `http://127.0.0.1:5000` en tu navegador.

---

## 🚀 Despliegue en Azure App Service

1. Crea una instancia de App Service en Azure.
2. Usa el [Deployment Center](https://learn.microsoft.com/en-us/azure/app-service/deploy-continuous-deployment) para conectar tu repositorio GitHub.
3. Configura variables de entorno en **Configuration → Application settings**.

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
## 🎥 Video Demo

[![Ver demo](assets/demo-preview.png)](https://youtu.be/_DtFGIQaS0k)

## 🖼️ Capturas

### Vista de Reservas
![Reservas](assets/reservas-screenshot.png)

### Mapa de Zonas Disponibles
![Mapa](assets/mapa-preview.png)