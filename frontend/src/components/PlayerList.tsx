import React from "react";
import { useGame } from "../context/GameContext";

export default function PlayerList() {
  const { gameState } = useGame();
  const players = Object.entries(gameState.players || {}).map(
    ([playerName, player]) => ({
      ...player,
      name: playerName,
    })
  );

  return (
    <div className="w-full max-w-md bg-white rounded-lg shadow p-4">
      <h2 className="text-xl font-bold mb-4">Jugadores</h2>
      <div className="space-y-2">
        {players.map((player) => (
          <div
            key={player.name}
            className={`flex justify-between items-center p-2 rounded ${
              player.is_drawer ? "bg-green-100" : "bg-gray-50"
            }`}
          >
            <span className="font-medium">
              {player.name}
              {player.is_drawer && " 🎨"}
            </span>
            <span className="text-gray-600">{player.score} puntos</span>
          </div>
        ))}
      </div>
    </div>
  );
}
