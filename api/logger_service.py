import json
from pathlib import Path
from datetime import datetime
from typing import Any, Optional


class GameLogger:
    """Service pour logger les sessions de jeu en JSONL"""

    LOGS_FILE = Path("data/game_sessions.jsonl")

    def __init__(self):
        """Initialiser le logger"""
        # Créer le répertoire si nécessaire
        self.LOGS_FILE.parent.mkdir(parents=True, exist_ok=True)

    def log_session(
        self,
        score: float,
        steps: int,
        actions: list[int],
        success: bool,
        session_id: Optional[str] = None,
    ) -> None:
        """
        Sauvegarder une session de jeu

        Args:
            score: Score final
            steps: Nombre de steps
            actions: Liste des actions prises
            success: Succès (atterrissage réussi)
            session_id: ID de session optionnel
        """
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "score": float(score),
            "steps": int(steps),
            "actions": actions,
            "success": bool(success),
            "session_id": session_id or f"game_{datetime.now().timestamp()}",
        }

        # Ajouter à la fin du fichier JSONL
        with open(self.LOGS_FILE, "a") as f:
            f.write(json.dumps(session_data) + "\n")

        print(f"✅ Session loggée: {session_data['session_id']}")

    @staticmethod
    def read_sessions() -> list[dict[str, Any]]:
        """Lire toutes les sessions loggées"""
        if not GameLogger.LOGS_FILE.exists():
            return []

        sessions = []
        with open(GameLogger.LOGS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        sessions.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        return sessions


# Instance globale singleton
_logger: Optional[GameLogger] = None


def get_logger() -> GameLogger:
    """Retourner instance singleton du logger"""
    global _logger
    if _logger is None:
        _logger = GameLogger()
    return _logger
