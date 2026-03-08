from pydantic import BaseModel, Field
from typing import Annotated

# Constantes
OBSERVATION_SIZE = 8
ACTIONS = [0, 1, 2, 3]  # LunarLander: 0=Aucun, 1=Gauche, 2=Droite, 3=Moteur
ACTION_NAMES = {0: "Aucun", 1: "Gauche", 2: "Droite", 3: "Moteur"}

# Types avec validation
ObservationList = Annotated[
    list[float],
    Field(
        min_length=OBSERVATION_SIZE,
        max_length=OBSERVATION_SIZE,
        description=f"Observation avec exactement {OBSERVATION_SIZE} floats: [x, y, vx, vy, angle, angularv, left_contact, right_contact]",
    ),
]

ActionInt = Annotated[
    int, Field(ge=0, le=3, description="Action: 0=Aucun, 1=Gauche, 2=Droite, 3=Moteur")
]


class PredictRequest(BaseModel):
    """Request pour prédire une action"""

    observation: ObservationList

    class Config:
        json_schema_extra = {
            "example": {"observation": [0.0, 1.4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}
        }


class PredictResponse(BaseModel):
    """Response avec l'action prédite"""

    action: ActionInt

    class Config:
        json_schema_extra = {"example": {"action": 3}}


class GameSessionRequest(BaseModel):
    """Request pour logger une session de jeu"""

    score: float = Field(description="Score final de la session")
    steps: int = Field(ge=0, description="Nombre de steps joués")
    actions: list[int] = Field(description="Liste des actions prises")
    success: bool = Field(description="Succès (atterrissage réussi)")

    class Config:
        json_schema_extra = {
            "example": {
                "score": 150.5,
                "steps": 500,
                "actions": [0, 3, 3, 2, 1],
                "success": True,
            }
        }


class GameSessionResponse(BaseModel):
    """Response après logging d'une session"""

    status: str = Field(description="Statut du logging")
    session_id: str = Field(description="ID unique de la session")

    class Config:
        json_schema_extra = {"example": {"status": "logged", "session_id": "game_1234.5"}}
