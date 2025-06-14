# 🎨 Pictionary Multiplayer

A real-time Pictionary game with web and desktop versions, built using modern technologies and a clean architecture.

## 📝 Description

Description
Pictionary Multiplayer is a real-time drawing and guessing game where players take turns drawing and guessing words. The game supports two types of clients:
-- Web Client: Interface built with React and TailwindCSS
-- Desktop Client: Native application built with Tauri v2
Currently, only one player can draw and another can guess at a time. Due to time constraints, I wasn't able to implement a ping/pong system to robustly support multiple concurrent participants.


### Main Features

🎮 Real-time gameplay with WebSockets
🖌️ Interactive drawing canvas
👥 Automatic turn-based system
📊 Real-time scoring
🎯 Random words to draw
💻 Cross-platform support (Web and Desktop)

## 🛠️ Technologies

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
- Clean/Hexagonal Architecture

## 📋 Requirements

### system
- Node.js v18 o superior
- Python 3.10 o superior
- Rust (para Tauri)
- Cargo (gestor de paquetes de Rust)

### Tools
- Tauri CLI (`cargo install tauri-cli`)
- npm o yarn
- pip (gestor de paquetes de Python)

## 🚀 Installation and Execution

### 1. Clone the repository
```bash
git clone [<url-del-repositorio>](https://github.com/aycastano/Pictionary.git)
cd pictionary
```

### 2. Configure the Backend

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# En Windows:
./venv\Scripts\activate
# En Unix/MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Configure the Web Frontend

```bash
# Navigate to the frontend directory
cd frontend

# Install dependenciess
npm install

# Start the development server
npm run dev
```

### 4. Configure the Desktop Client

```bash
# Navigate to the desktop client directory
cd desktop

# Install dependenciess
python -m venv venv
# En Windows:
./venv\Scripts\activate
# En Unix/MacOS:
source venv/bin/activate
pip install -r requirements.txt

# Install dependenciess
npm install


# Start in development mode
python.py
```

## 🏗️ Project Structure

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

### 🎮 How to Play
Start the backend server
Open the web or desktop client
The game will automatically assign the roles of drawer and guesser
The drawer will see the word to draw
The guesser must type their attempt in the text field
Points are awarded for correct guesses
Roles are alternated automatically

### 📝 License
This project is licensed under the MIT License - see the LICENSE file for more details.

### 👥 Authors
Yamid Castaño - Initial Work - https://github.com/aycastano/Pictionary

🙏 Acknowledgments
FastAPI for the excellent framework
Tauri for making desktop applications possible with web technologies
React and TailwindCSS for the UI tools

## Descripción
Juego de Pictionary multijugador que permite a los usuarios dibujar y adivinar palabras en tiempo real.

## Estructura del Proyecto
```
pictionary/
├── backend/
│   ├── api/
│   │   └── v1/
│   │       ├── game_state.py    # Lógica principal del juego
│   │       └── websocket.py     # Endpoints WebSocket
│   ├── models/
│   │   └── game.py             # Modelos de datos del juego
│   └── services/
│       └── game_service.py     # Servicios de conexión
└── frontend/
    ├── src/
    │   ├── components/         # Componentes React
    │   ├── context/           # Contexto del juego
    │   └── App.tsx           # Componente principal
    └── .env                  # Variables de entorno frontend
```

## Variables de Entorno

### Backend (.env)
```env
# Configuración del servidor
HOST=0.0.0.0
PORT=8000

# Configuración de CORS
CORS_ORIGINS=["http://localhost:5173"]

# Configuración de WebSocket
WS_PING_INTERVAL=30
WS_PING_TIMEOUT=30
```

### Frontend (.env)
```env
# URL del servidor WebSocket
VITE_WS_URL=ws://localhost:8000/api/v1/ws
```

## Modelos de Datos (game.py)

El archivo `game.py` es fundamental para la comunicación entre el frontend y el backend:

1. **Definición de Estructura**:
   - `Player`: Define la estructura de un jugador (nombre)
   - `GameState`: Define el estado del juego (jugadores, palabra actual, puntuaciones)

2. **Validación de Datos**:
   - Asegura que los datos que vienen del frontend tengan el formato correcto
   - Valida los mensajes WebSocket antes de procesarlos

3. **Serialización/Deserialización**:
   - Convierte los datos del juego a JSON para enviarlos al frontend
   - Convierte los mensajes JSON del frontend a objetos Python

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/pictionary.git
cd pictionary
```

2. Configurar el backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configurar el frontend:
```bash
cd frontend
npm install
```

## Ejecución

1. Iniciar el backend:
```bash
cd backend
uvicorn main:app --reload
```

2. Iniciar el frontend:
```bash
cd frontend
npm run dev
```

## Tecnologías Utilizadas

- **Backend**:
  - FastAPI
  - WebSockets
  - Pydantic

- **Frontend**:
  - React
  - TypeScript
  - Vite
  - Canvas API

## Características

- Dibujo en tiempo real
- Sistema de puntuación
- Chat en tiempo real
- Soporte para múltiples jugadores
- Interfaz responsiva

## Correcciones y Mejoras

### Manejo de Variables de Entorno
Se implementaron dos archivos `.env` separados para mejorar la configuración:

1. **Backend (.env)**:
   - Permite configurar el servidor sin modificar el código
   - Controla los timeouts de WebSocket
   - Gestiona los orígenes CORS permitidos

2. **Frontend (.env)**:
   - Configura la URL del WebSocket
   - Permite cambiar el servidor sin recompilar

### Modelo game.py
El archivo `game.py` se mantiene en su versión original por las siguientes razones:

1. **Compatibilidad**:
   - Es usado por `game_service.py` para la validación de datos
   - Proporciona los modelos Pydantic necesarios para la comunicación WebSocket

2. **Estructura Original**:
```python
class Player(BaseModel):
    name: str

class GameState(BaseModel):
    players: List[Player] = []
    word: str = "house"
    scores: Dict[str, int] = {}
```

3. **Razones para mantenerlo**:
   - Es una dependencia directa de `game_service.py`
   - Proporciona la estructura base para la validación de datos
   - Facilita la comunicación entre frontend y backend

4. **Beneficios**:
   - Validación automática de datos
   - Estructura clara y consistente
   - Facilita la comunicación entre frontend y backend
