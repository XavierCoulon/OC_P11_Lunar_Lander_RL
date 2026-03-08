from stable_baselines3 import DQN
from pathlib import Path
import numpy as np


class AgentService:
    """Service pour gérer le modèle RL"""

    def __init__(self, model_path: Path):
        """Charger le modèle"""
        print(f"📦 Chargement du modèle depuis: {model_path}")
        self.model = DQN.load(str(model_path))
        print("✅ Modèle chargé!")

    def predict(self, observation: np.ndarray) -> int:
        """
        Prédire l'action pour une observation

        Args:
            observation: array de 8 floats [x, y, vx, vy, angle, angularv, left_contact, right_contact]

        Returns:
            action: int (0-3)
        """
        action, _ = self.model.predict(observation, deterministic=True)
        return int(action)


# Instance globale singleton
_agent = None


def get_agent(model_path: Path) -> AgentService:
    """Retourner instance singleton du service"""
    global _agent
    if _agent is None:
        _agent = AgentService(model_path)
    return _agent
