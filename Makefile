.PHONY: api frontend dev stop help

help:
	@echo "📚 Commandes disponibles:"
	@echo ""
	@echo "  make api        - Démarrer l'API FastAPI (port 8000)"
	@echo "  make frontend   - Démarrer l'interface Streamlit (port 8501)"
	@echo "  make dev        - Démarrer l'API et le frontend en parallèle"
	@echo "  make stop       - Arrêter tous les processus (API + Streamlit)"
	@echo ""

api:
	@echo "🚀 Démarrage API..."
	uv run python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	@echo "🎮 Démarrage Interface..."
	uv run streamlit run frontend/app.py

dev:
	@echo "🚀 Démarrage API et Interface..."
	@echo "📍 API: http://127.0.0.1:8000"
	@echo "📍 Interface: http://localhost:8501"
	@echo ""
	@(uv run python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000 &) && \
	(sleep 2 && uv run streamlit run frontend/app.py &) && \
	wait

stop:
	@echo "🛑 Arrêt des processus..."
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@pkill -f "streamlit" 2>/dev/null || true
	@echo "✅ Arrêt completed"
