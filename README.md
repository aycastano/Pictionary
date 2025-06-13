# 🎨 Pictionary Multiplayer

Un juego de Pictionary en tiempo real con versiones web y de escritorio, construido con tecnologías modernas y una arquitectura limpia.

## 📝 Descripción

Pictionary Multiplayer es un juego de dibujo y adivinanza en tiempo real donde los jugadores se turnan para dibujar y adivinar palabras. El juego soporta dos tipos de clientes:

- **Cliente Web**: Interfaz construida con React y TailwindCSS
- **Cliente Desktop**: Aplicación nativa construida con Tauri v2

### Características principales

- 🎮 Juego en tiempo real con WebSockets
- 🖌️ Canvas interactivo para dibujar
- 👥 Sistema de turnos automático
- 📊 Puntuación en tiempo real
- 🎯 Palabras aleatorias para dibujar
- 💻 Soporte multiplataforma (Web y Desktop)

## 🛠️ Tecnologías

### Frontend (Web)
- TypeScript
- React
- TailwindCSS
- WebSockets

### Desktop
- Tauri v2
- Rust
- WebSockets

### Backend
- FastAPI (Python)
- WebSockets
- Arquitectura Limpia/Hexagonal

## 📋 Requisitos

### Sistema
- Node.js v18 o superior
- Python 3.10 o superior
- Rust (para Tauri)
- Cargo (gestor de paquetes de Rust)

### Herramientas
- Tauri CLI (`cargo install tauri-cli`)
- npm o yarn
- pip (gestor de paquetes de Python)

## 🚀 Instalación y Ejecución

### 1. Clonar el repositorio
```bash
git clone [<url-del-repositorio>](https://github.com/aycastano/Pictionary.git)
cd pictionary
```

### 2. Configurar el Backend

```bash
# Navegar al directorio del backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
./venv\Scripts\activate
# En Unix/MacOS:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar el servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Configurar el Frontend Web

```bash
# Navegar al directorio del frontend
cd frontend

# Instalar dependencias
npm install

# Iniciar el servidor de desarrollo
npm run dev
```

### 4. Configurar el Cliente Desktop

```bash
# Navegar al directorio del cliente desktop
cd desktop

# Instalar dependencias
npm install

# Iniciar en modo desarrollo
npm run tauri dev
```

## 🏗️ Estructura del Proyecto

```
pictionary/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── domain/
│   │   └── main.py
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   └── App.tsx
│   ├── package.json
│   └── README.md
├── desktop/
│   ├── src/
│   ├── src-tauri/
│   └── package.json
└── README.md
```

## 🎮 Cómo Jugar

1. Inicia el servidor backend
2. Abre el cliente web o desktop
3. El juego asignará automáticamente los roles de dibujante y adivinador
4. El dibujante verá la palabra a dibujar
5. El adivinador debe escribir su intento en el campo de texto
6. Los puntos se otorgan por adivinanzas correctas
7. Los roles se alternan automáticamente



## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- Yamid Castaño - *Trabajo Inicial* - https://github.com/aycastano/Pictionary

## 🙏 Agradecimientos

- FastAPI por el excelente framework
- Tauri por hacer posible las aplicaciones de escritorio con web technologies
- React y TailwindCSS por las herramientas de UI
