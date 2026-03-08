from fastapi import APIRouter, HTTPException, Request
from .schemas import (
    PredictRequest,
    PredictResponse,
    GameSessionRequest,
    GameSessionResponse,
)
from .logger_service import get_logger
import numpy as np
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health(http_request: Request):
    """Health check"""
    return {"status": "ok", "model_loaded": http_request.app.state.agent is not None}


@router.post("/predict", response_model=PredictResponse)
async def predict(predict_request: PredictRequest, http_request: Request):
    """
    Prédire l'action pour une observation donnée

    Request body:
    {
        "observation": [x, y, vx, vy, angle, angularv, left_contact, right_contact]
    }

    Response:
    {
        "action": 0-3
    }
    """
    if http_request.app.state.agent is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")

    obs = np.array(predict_request.observation, dtype=np.float32)
    action = http_request.app.state.agent.predict(obs)
    return PredictResponse(action=action)


@router.post("/log-game", response_model=GameSessionResponse)
async def log_game(session_request: GameSessionRequest):
    """
    Logger une session de jeu

    Request body:
    {
        "score": 150.5,
        "steps": 500,
        "actions": [0, 3, 3, 2, 1],
        "success": true
    }

    Response:
    {
        "status": "logged",
        "session_id": "game_1234.5"
    }
    """
    logger = get_logger()
    session_id = f"game_{datetime.now().timestamp()}"

    logger.log_session(
        score=session_request.score,
        steps=session_request.steps,
        actions=session_request.actions,
        success=session_request.success,
        session_id=session_id,
    )

    return GameSessionResponse(status="logged", session_id=session_id)
