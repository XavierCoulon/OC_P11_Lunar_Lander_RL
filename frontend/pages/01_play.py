import streamlit as st
import requests
import numpy as np
import gymnasium as gym
from gymnasium.wrappers import RecordVideo
import time
from typing import Any
from pathlib import Path

st.set_page_config(page_title="Play - LunarLander Agent", page_icon="🎮", layout="wide")

st.title("🎮 Play")

# Configuration API
API_URL = "http://127.0.0.1:8000"

# État Streamlit
if "game_active" not in st.session_state:
    st.session_state.game_active = False
if "env_local" not in st.session_state:
    st.session_state.env_local = None  # type: ignore
if "current_obs" not in st.session_state:
    st.session_state.current_obs = None  # type: ignore
if "score" not in st.session_state:
    st.session_state.score = 0
if "steps" not in st.session_state:
    st.session_state.steps = 0
if "game_done" not in st.session_state:
    st.session_state.game_done = False
if "actions_taken" not in st.session_state:
    st.session_state.actions_taken = []  # type: ignore
if "record_video" not in st.session_state:
    st.session_state.record_video = False


# Vérifier connexion API
@st.cache_resource
def check_api() -> bool:
    try:
        resp = requests.get(f"{API_URL}/health", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False


if not check_api():
    st.error(
        "❌ API non accessible! Lancez d'abord: `uv run python -m uvicorn api.main:app --reload`"
    )
    st.stop()

st.success("✅ Connecté à l'API")

# Options d'enregistrement
col_options = st.columns([1, 2])
with col_options[0]:
    st.session_state.record_video = st.checkbox("📹 Enregistrer vidéo", value=False)
with col_options[1]:
    if st.session_state.record_video:
        st.info("La vidéo sera sauvegardée dans `data/videos/`")

# Boutons de contrôle
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("▶️ Commencer", key="start_btn"):
        # Créer nouvel environnement
        env = gym.make("LunarLander-v3", render_mode="rgb_array")

        # Wrapper RecordVideo si demandé
        if st.session_state.record_video:
            video_folder = Path("data/videos")
            video_folder.mkdir(parents=True, exist_ok=True)
            video_id = f"lunar_lander_{int(time.time())}"
            env = RecordVideo(env, video_folder=str(video_folder), name_prefix=video_id)

        st.session_state.env_local = env
        st.session_state.current_obs, _ = st.session_state.env_local.reset()

        st.session_state.score = 0
        st.session_state.steps = 0
        st.session_state.actions_taken = []
        st.session_state.game_active = True
        st.session_state.game_done = False

with col2:
    if st.button("⏹️ Arrêter", key="stop_btn"):
        st.session_state.game_active = False
        if st.session_state.env_local is not None:
            st.session_state.env_local.close()
            st.session_state.env_local = None

st.markdown("---")

# Layout du jeu
col_env, col_info = st.columns([2, 1])

# Colonne gauche: rendu du jeu
with col_env:
    placeholder_frame = st.empty()
    placeholder_status = st.empty()

# Colonne droite: infos
with col_info:
    score_placeholder = st.empty()
    steps_placeholder = st.empty()
    status_placeholder = st.empty()

# Boucle de jeu
if st.session_state.game_active and st.session_state.env_local is not None:
    if st.session_state.current_obs is None:
        st.error("❌ Observation initiale non disponible")
        st.stop()

    obs: np.ndarray = st.session_state.current_obs.copy()

    # Boucle jusqu'à done
    while st.session_state.game_active and not st.session_state.game_done:
        time.sleep(0.05)  # ~20 FPS

        try:
            # Appel API pour prédire l'action
            response = requests.post(
                f"{API_URL}/predict", json={"observation": obs.tolist()}, timeout=5
            )

            if response.status_code != 200:
                st.error(f"❌ Erreur API: {response.status_code}")
                break

            data: dict[str, Any] = response.json()
            action: int = int(data["action"])

            # Faire le step LOCALEMENT dans l'env
            if st.session_state.env_local is None:
                st.error("❌ Environnement perdu")
                break

            # Tracker l'action
            st.session_state.actions_taken.append(action)

            obs, reward, terminated, truncated, info = st.session_state.env_local.step(
                action
            )
            done: bool = bool(terminated or truncated)

            # Mettre à jour métriques
            st.session_state.score += float(reward)
            st.session_state.steps += 1
            st.session_state.current_obs = obs

            # Rendu image
            frame = st.session_state.env_local.render()
            if frame is not None:
                placeholder_frame.image(frame, width=800)

            # Mettre à jour infos
            with score_placeholder.container():
                st.metric("Score", f"{st.session_state.score:.1f}")
            with steps_placeholder.container():
                st.metric("Steps", st.session_state.steps)
            with status_placeholder.container():
                action_names = ["🔴 Aucun", "⬅️ Gauche", "➡️ Droite", "🔵 Moteur"]
                action_str = (
                    action_names[action]
                    if 0 <= action < len(action_names)
                    else f"Action {action}"
                )
                st.info(f"{action_str} | Reward: {reward:+.2f}")

            if done:
                st.session_state.game_done = True
                st.session_state.game_active = False
                if st.session_state.env_local is not None:
                    st.session_state.env_local.close()
                    st.session_state.env_local = None

                # Déterminer le succès (atterrissage réussi: score > 0)
                success = st.session_state.score > 0

                # Logger la session
                try:
                    log_response = requests.post(
                        f"{API_URL}/log-game",
                        json={
                            "score": st.session_state.score,
                            "steps": st.session_state.steps,
                            "actions": st.session_state.actions_taken,
                            "success": success,
                        },
                        timeout=5,
                    )
                    if log_response.status_code == 200:
                        placeholder_status.success(
                            f"🎯 Jeu terminé! Score final: {st.session_state.score:.1f}\n✅ Session loggée"
                        )
                    else:
                        placeholder_status.success(
                            f"🎯 Jeu terminé! Score final: {st.session_state.score:.1f}"
                        )
                except Exception as e:
                    placeholder_status.success(
                        f"🎯 Jeu terminé! Score final: {st.session_state.score:.1f}"
                    )

        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            if st.session_state.env_local is not None:
                st.session_state.env_local.close()
                st.session_state.env_local = None
            break

elif st.session_state.game_done:
    st.success(f"✅ Partie terminée! Score: {st.session_state.score:.1f}")
