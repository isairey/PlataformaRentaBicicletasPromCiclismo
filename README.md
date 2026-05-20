<div align="center">

<img width="220" src="https://cdn-icons-png.flaticon.com/512/2972/2972185.png" />

# 🚴 Bike Network System

### Plataforma moderna de renta de bicicletas y promoción de ciclismo ⚡

<p align="center">
  <b>Bike Network System</b> es una plataforma enfocada en la gestión de bicicletas, reservas, eventos ciclistas y rutas interactivas utilizando mapas dinámicos y arquitectura moderna.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Bike_Rental-System-00C853?style=for-the-badge&logo=googlemaps&logoColor=white">
  <img src="https://img.shields.io/badge/Leaflet-Interactive_Map-199900?style=for-the-badge&logo=leaflet&logoColor=white">
  <img src="https://img.shields.io/badge/JWT-Security-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white">
  <img src="https://img.shields.io/badge/REST_API-Backend-FF6F00?style=for-the-badge&logo=fastapi&logoColor=white">
</p>

<p align="center">
  <a href="#-acerca-del-proyecto">Acerca</a> •
  <a href="#-características">Características</a> •
  <a href="#-tecnologías-utilizadas">Tecnologías</a> •
  <a href="#-instalación">Instalación</a> •
  <a href="#-vista-previa">Vista previa</a>
</p>

</div>

---

# 🌌 Acerca del proyecto

**Bike Network System** es una plataforma diseñada para la administración de bicicletas, reservas y promoción de actividades ciclistas mediante herramientas modernas de gestión y visualización.

El sistema permite:

- 🚴 Gestionar bicicletas
- 📅 Programar eventos ciclistas
- 🗺️ Mostrar rutas en mapas interactivos
- 🔐 Autenticación JWT
- 📦 Controlar inventario
- 📋 Gestionar reservas
- 🏁 Administrar competencias

La plataforma fue desarrollada con enfoque en:

- ⚡ Arquitectura moderna
- 📡 APIs REST
- 🔄 Escalabilidad
- 🔐 Seguridad
- 🛠️ Mantenibilidad
- 🌐 Compatibilidad multiplataforma

---

# ✨ Características

## 🚴 Gestión de bicicletas

- ➕ Registro de bicicletas
- 📋 Información detallada
- 🎨 Gestión de color y tipo
- ⚡ Estado de disponibilidad
- 🛠️ CRUD completo

---

## 📅 Sistema de renta

- 🛒 Reserva de bicicletas
- 📆 Gestión de disponibilidad
- 🔄 Retorno de bicicletas
- ⚡ Actualización automática
- 📋 Historial de rentas

---

## 🗺️ Mapa interactivo

- 📍 Integración Leaflet
- 🚴 Visualización de bicicletas
- 🛣️ Rutas ciclistas
- ⚡ Carga dinámica de mapas
- 🌍 Navegación interactiva

---

## 🎉 Eventos y competencias

- 📅 Eventos programados
- 🏁 Competencias ciclistas
- 🛣️ Rutas disponibles
- 📋 Calendario de actividades

---

## 🔐 Seguridad

- 🔑 JWT Authentication
- 🔒 Hashing con bcrypt
- 🛡️ Protección de endpoints
- 👥 Gestión de usuarios

---

# 👨‍💻 Módulos del sistema

## 🔐 Authentication Module

Módulo de autenticación y usuarios.

### Funcionalidades:

- 👤 Registro de usuarios
- 🔑 Login seguro
- 🚪 Logout
- 🛡️ Gestión JWT
- 🔒 Seguridad bcrypt

---

## 🚴 Bike CRUD Module

Módulo de bicicletas.

### Funcionalidades:

- ➕ Registrar bicicletas
- 📋 Listar bicicletas
- ✏️ Editar información
- ❌ Eliminar bicicletas
- ⚡ Gestión de estados

---

## 📅 Rental Module

Sistema de renta.

### Funcionalidades:

- 🚴 Reservar bicicletas
- 🔄 Retornar bicicletas
- 📋 Control de disponibilidad
- ⚡ Actualización automática

---

## 🗺️ Map Module

Módulo de mapas.

### Funcionalidades:

- 🌍 Leaflet Maps
- 📍 Visualización dinámica
- 🚴 Ubicación de bicicletas
- 🛣️ Gestión de rutas

---

## 🎉 Events Module

Módulo de eventos.

### Funcionalidades:

- 📅 Eventos ciclistas
- 🏁 Competencias
- 🛣️ Rutas disponibles
- 📋 Agenda de actividades

---

# 🛠️ Tecnologías utilizadas

## ⚙️ Frontend

<p>
  <img src="https://skillicons.dev/icons?i=html,css,js" />
</p>

- HTML5
- CSS3
- JavaScript
- Responsive Design
- Leaflet.js

---

## ⚙️ Backend

<p>
  <img src="https://skillicons.dev/icons?i=nodejs,express" />
</p>

- Node.js
- Express.js
- REST APIs
- JWT Authentication
- Arquitectura modular

---

## 🗄️ Base de datos

<p>
  <img src="https://skillicons.dev/icons?i=mysql" />
</p>

- MySQL
- Persistencia relacional
- Gestión de inventario
- Transacciones

---

## 🧰 Herramientas

<p>
  <img src="https://skillicons.dev/icons?i=git,github,vscode" />
</p>

- Git
- GitHub
- VS Code
- Postman
- npm

---

# 📂 Estructura del proyecto

```bash
Bike-Network-System/
│
├── authentication/
├── bike-crud/
├── rental/
├── map/
├── events/
├── docs/
├── frontend/
├── backend/
├── database/
├── README.md
└── LICENSE
```

---

# 🏗️ Arquitectura del sistema

## ⚡ Arquitectura general

```text
Cliente → Frontend → REST API → Database
                     ↓
                Leaflet Maps
```

---

## 🔄 Flujo del sistema

```text
Usuario → Login → Reservar bicicleta → Mapa interactivo → Eventos
```

---

# 📊 Requerimientos funcionales

## 🚴 Funcionalidades principales

- Registro de usuarios
- Login JWT
- CRUD de bicicletas
- Reservación de bicicletas
- Gestión de disponibilidad
- Eventos y competencias
- Rutas ciclistas
- Mapa interactivo

---

# 🔐 Requerimientos no funcionales

## ⚡ Calidad del sistema

- ⏱️ Respuesta menor a 2 segundos
- 🌐 Disponibilidad del 95%
- 🔒 Seguridad con bcrypt
- 📈 Escalabilidad concurrente
- 🛠️ Código mantenible
- 📱 Compatibilidad multiplataforma

---

# ⚡ Instalación

## 📋 Requisitos

- Node.js
- npm
- MySQL
- Navegador moderno
- Git

---

# 🚀 Configuración del proyecto

## 1️⃣ Clonar repositorio

```bash
git clone https://github.com/camazog1/Bike-Network-System.git
```

---

## 2️⃣ Entrar al proyecto

```bash
cd Bike-Network-System
```

---

## 3️⃣ Instalar dependencias

```bash
npm install
```

---

## 4️⃣ Configurar base de datos

Crear base de datos MySQL y configurar credenciales.

---

## 5️⃣ Ejecutar servidor

```bash
npm start
```

---

## 6️⃣ Abrir aplicación

```bash
http://localhost:3000
```

---

# 📸 Vista previa

## 🖥️ Arquitectura y diagramas

<div align="center">

### 🏗️ Diagrama de contexto
<img src="https://github.com/user-attachments/assets/4c0c877c-65e2-4cd4-8ee4-f1a253c0163d" width="100%"/>

### ⚙️ Diagrama de componentes
<img src="https://raw.githubusercontent.com/camazog1/Bike-Network-System/refs/heads/main/docs/DiagramComponent.png" width="100%"/>

### 🔄 Secuencia de usuarios
<img src="https://raw.githubusercontent.com/camazog1/Bike-Network-System/refs/heads/main/docs/sequence_diagrams_user.png" width="100%"/>

### 🚴 Secuencia de renta
<img src="https://raw.githubusercontent.com/camazog1/Bike-Network-System/refs/heads/main/docs/sequence_diagrams_rent.png" width="100%"/>

### 🗺️ Secuencia de mapas
<img src="https://raw.githubusercontent.com/camazog1/Bike-Network-System/refs/heads/main/docs/sequence_diagrams_Map_bikes.png" width="100%"/>

### ☁️ Diagrama de despliegue
<img src="https://github.com/user-attachments/assets/35c0a090-4014-45ec-b37f-bc731c54868c" width="100%"/>

</div>

---

# 🧠 Decisiones arquitectónicas

## ☁️ Infraestructura y despliegue

- Arquitectura cloud-ready
- Escalabilidad modular
- APIs desacopladas
- Compatibilidad multiplataforma

---

## ⚙️ Stack tecnológico

- APIs REST
- JWT Authentication
- Leaflet Integration
- Arquitectura modular
- Buenas prácticas de desarrollo

---

# 👥 Equipo de desarrollo

| Rol | Integrante |
|---|---|
| 👨‍💼 Product Owner | Carlos Alberto Mazo |
| 🧩 Scrum Master | Patricia Arango |
| 💻 Developer | Jehison David Cifuentes |
| 💻 Developer | Miguel Vasquez |
| 💻 Developer | Jhonnathan Ocampo |
| 🧪 QA | Oswaldo Alzate |

---

# 🧠 Objetivos del proyecto

## 🎯 Aprendizaje y arquitectura moderna

- Desarrollo backend
- APIs REST
- Seguridad JWT
- Gestión de inventarios
- Leaflet Maps
- Sistemas escalables
- Arquitectura modular

---

# 🚧 Roadmap

## 🔮 Próximas mejoras

- 📱 Aplicación móvil
- ☁️ Deploy cloud
- 🔔 Notificaciones push
- 📊 Dashboard analítico
- 🤖 IA para rutas recomendadas
- 🚴 GPS en tiempo real
- 🌐 Integración social

---

# 🤝 Contribuciones

Las contribuciones son bienvenidas ❤️

## Cómo contribuir

1. Fork del proyecto

```bash
git checkout -b feature/nueva-funcionalidad
```

2. Commit

```bash
git commit -m "✨ Nueva funcionalidad"
```

3. Push

```bash
git push origin feature/nueva-funcionalidad
```

4. Pull Request 🚀

---

# 👨‍💻 Desarrollador

<div align="center">

## Isai Reyes — Full Stack Developer

Desarrollador apasionado por plataformas modernas, sistemas geográficos y aplicaciones escalables 🚀

</div>

---

# 🌟 Apoya el proyecto

⭐ Dale una estrella  
🍴 Haz fork  
📢 Comparte el proyecto

---

# 📜 Licencia

Proyecto orientado al aprendizaje de arquitecturas modernas, APIs REST y sistemas interactivos de movilidad.

---

<div align="center">

### 🚴 Bike Network System — movilidad inteligente y moderna ⚡

</div>
