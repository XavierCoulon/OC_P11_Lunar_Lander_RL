from fastapi import APIRouter, HTTPException, Request
from .schemas import PredictRequest, PredictResponse
import numpy as np

router = APIRouter()

@router.get("/health")
async def health(http_request: Request):
    """Health check"""
    return {
        "status": "ok",
        "model_loaded": http_request.app.state.agent is not None
    }

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
