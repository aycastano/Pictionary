import React, { useEffect, useRef } from "react";
import { useGame } from "../context/GameContext";

interface DrawingCanvasProps {
  isDrawer: boolean;
}

const DrawingCanvas: React.FC<DrawingCanvasProps> = ({ isDrawer }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const isDrawingRef = useRef(false);
  const lastPosRef = useRef({ x: 0, y: 0 });
  const { socket, gameState } = useGame();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Configurar canvas
    canvas.width = 600;
    canvas.height = 400;
    ctx.strokeStyle = "black";
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    // Limpiar canvas cuando cambia el drawer
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }, [gameState.current_drawer]);

  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawer || !gameState.game_started || gameState.game_paused) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    isDrawingRef.current = true;
    lastPosRef.current = { x, y };

    // Enviar inicio de línea
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(
        JSON.stringify({
          type: "draw",
          x,
          y,
          isStart: true,
        })
      );
    }
  };

  const draw = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (
      !isDrawingRef.current ||
      !isDrawer ||
      !gameState.game_started ||
      gameState.game_paused
    )
      return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Dibujar línea
    ctx.beginPath();
    ctx.moveTo(lastPosRef.current.x, lastPosRef.current.y);
    ctx.lineTo(x, y);
    ctx.stroke();

    // Enviar coordenadas
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(
        JSON.stringify({
          type: "draw",
          x,
          y,
          isStart: false,
        })
      );
    }

    lastPosRef.current = { x, y };
  };

  const stopDrawing = () => {
    isDrawingRef.current = false;
  };

  return (
    <div className="relative">
      <canvas
        ref={canvasRef}
        className={`border border-gray-300 rounded-lg ${
          isDrawer && gameState.game_started && !gameState.game_paused
            ? "cursor-crosshair"
            : "cursor-not-allowed"
        }`}
        onMouseDown={startDrawing}
        onMouseMove={draw}
        onMouseUp={stopDrawing}
        onMouseLeave={stopDrawing}
      />
      {!isDrawer && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 text-white rounded-lg">
          Esperando tu turno para dibujar
        </div>
      )}
      {isDrawer && gameState.game_paused && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 text-white rounded-lg">
          Juego pausado
        </div>
      )}
    </div>
  );
};

export default DrawingCanvas;
