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

### Improvements

  ### Environment Variable Management
  Two separate .env files were implemented to improve configuration:
  
  ### Backend (.env):
  Allows server configuration without modifying the code
  Controls WebSocket timeouts
  Manages allowed CORS origins
  
  ### Frontend (.env):
  Configures the WebSocket URL
  Allows switching servers without recompiling
  
  ### Model game.py
  The game.py file is kept in its original version for the following reasons:
  
  ### Compatibility:
  It is used by game_service.py for data validation
  It provides the necessary Pydantic models for WebSocket communication
  It is a direct dependency of game_service.py
  It provides the base structure for data validation
  It facilitates communication between frontend and backend
  
  ### Benefits:
  Automatic data validation
  Clear and consistent structure
  Eases communication between frontend and backend

