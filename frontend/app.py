import streamlit as st

st.set_page_config(page_title="LunarLander Agent", page_icon="🚀", layout="centered")

st.title("🚀 LunarLander Agent")
st.markdown("---")

st.markdown(
    """
## Bienvenue!

Vous êtes ici pour regarder l'agent RL optimisé jouer au jeu LunarLander.

### 🎮 Navigation
Utilisez le menu de gauche pour:
- **Play** - Regarder l'agent jouer!

### 📊 Modèle
- **Architecture:** DQN (Deep Q-Network)
- **Hyperparamètres optimisés:** `learning_starts=5000`
- **Score moyen:** 241.33 ± 36.91
- **Statut:** ✅ Déployé et prêt!

### 🔧 Technologie
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Framework RL:** Stable-Baselines3
- **Environnement:** Gymnasium (LunarLander-v3)

---
Cliquez sur **Play** pour commencer! 🎯
"""
)
