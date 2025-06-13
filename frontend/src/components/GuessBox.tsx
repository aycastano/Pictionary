import React, { useState } from "react";
import { useGame } from "../context/GameContext";

export default function GuessBox() {
  const [guess, setGuess] = useState("");
  const { sendGuess } = useGame();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (guess.trim()) {
      sendGuess(guess.trim());
      setGuess("");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md">
      <div className="flex gap-2">
        <input
          type="text"
          value={guess}
          onChange={(e) => setGuess(e.target.value)}
          placeholder="Escribe tu adivinanza..."
          className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Adivinar
        </button>
      </div>
    </form>
  );
}
