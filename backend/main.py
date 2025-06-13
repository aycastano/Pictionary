from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Asegurar que el directorio actual está en el path
sys.path.append(str(Path(__file__).parent))

try:
    from api.v1 import endpoints, websocket
    from api.v1.websocket import router as ws_router
except ImportError as e:
    logger.error(f"Error importando módulos: {e}")
    raise

app = FastAPI(
    title="Pictionary API",
    description="API para el juego Pictionary",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
try:
    app.include_router(endpoints.router, prefix="/api/v1")
    app.include_router(ws_router, prefix="/api/v1")
except Exception as e:
    logger.error(f"Error incluyendo routers: {e}")
    raise

@app.get("/")
async def root():
    """Endpoint raíz para verificar que la API está funcionando"""
    return {
        "message": "Pictionary API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Endpoint para verificar la salud de la API"""
    return {
        "status": "healthy",
        "websocket": True,
        "game_state": True
    }

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Error iniciando el servidor: {e}")
        raise
