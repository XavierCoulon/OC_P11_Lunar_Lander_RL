from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config import API_HOST, API_PORT, MODEL_PATH
from . import agent_service
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    print("\n" + "=" * 70)
    print("🚀 DÉMARRAGE API LunarLander")
    print("=" * 70)

    app.state.agent = agent_service.get_agent(MODEL_PATH)

    print("=" * 70)
    print("✅ API PRÊTE!")
    print(f"📍 Accès: http://{API_HOST}:{API_PORT}")
    print(f"📖 Docs: http://{API_HOST}:{API_PORT}/docs")
    print("=" * 70 + "\n")

    yield

    # Shutdown (si nécessaire)
    print("🛑 Arrêt de l'API...")


app = FastAPI(
    title="LunarLander Agent API",
    version="1.0",
    description="API pour l'agent RL optimisé - Prédictions uniquement",
    lifespan=lifespan,
)

# CORS middleware (pour Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host=API_HOST, port=API_PORT, reload=True)
