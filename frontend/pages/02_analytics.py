import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import json

st.set_page_config(
    page_title="Analytics - LunarLander Agent", page_icon="📊", layout="wide"
)

st.title("📊 Analytics")

# Chemin du fichier de logs
LOGS_FILE = Path("data/game_sessions.jsonl")


def load_sessions() -> list[dict]:
    """Charger toutes les sessions loggées"""
    if not LOGS_FILE.exists():
        return []

    sessions = []
    with open(LOGS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    sessions.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return sessions


# Charger les données
sessions = load_sessions()

if not sessions:
    st.warning("❌ Aucune session loggée pour le moment. Jouez une partie d'abord !")
    st.stop()

# Convertir en DataFrame
df = pd.DataFrame(sessions)

# Parser la timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")

# Ajouter un numéro de partie
df["partie"] = range(1, len(df) + 1)

# Métriques principales
st.markdown("### 📈 Statistiques globales")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Parties jouées", len(df))

with col2:
    st.metric("Score moyen", f"{df['score'].mean():.1f}")

with col3:
    success_rate = df["success"].sum() / len(df) * 100
    st.metric("Taux de succès", f"{success_rate:.1f}%")

with col4:
    avg_steps = df["steps"].mean()
    st.metric("Steps moyens", f"{avg_steps:.0f}")

st.markdown("---")

# Tableau détaillé des sessions avec vidéos
st.markdown("### 📋 Historique des sessions")

# Récupérer les fichiers vidéo disponibles
videos_folder = Path("data/videos")
video_files_dict = {}
if videos_folder.exists():
    for vf in videos_folder.glob("*.mp4"):
        # Associer la vidéo à la session par timestamp approximatif
        video_files_dict[vf.name] = vf

# Afficher chaque session
cols = st.columns([1, 2, 1, 1, 1, 1.2])
cols[0].write("**Partie**")
cols[1].write("**Date/Heure**")
cols[2].write("**Score**")
cols[3].write("**Steps**")
cols[4].write("**Succès**")
cols[5].write("**Vidéo**")

for idx, row in df.iterrows():
    cols = st.columns([1, 2, 1, 1, 1, 1.2])

    with cols[0]:
        st.write(f"#{int(row['partie'])}")

    with cols[1]:
        st.write(row["timestamp"].strftime("%Y-%m-%d %H:%M:%S"))

    with cols[2]:
        st.write(f"{row['score']:.1f}")

    with cols[3]:
        st.write(f"{int(row['steps'])}")

    with cols[4]:
        st.write("✅ Succès" if row["success"] else "❌ Crash")

    with cols[5]:
        # Chercher une vidéo pour cette session
        video_found = False
        for video_file in video_files_dict.values():
            # Vérifier si le timestamp de la vidéo est proche
            video_time = datetime.fromtimestamp(video_file.stat().st_mtime)
            if (
                abs((video_time - row["timestamp"]).total_seconds()) < 60
            ):  # Moins d'1 min d'écart
                with open(video_file, "rb") as f:
                    st.download_button(
                        label="📹 Télécharger",
                        data=f.read(),
                        file_name=video_file.name,
                        mime="video/mp4",
                        key=f"download_{idx}_{video_file.name}",
                    )
                video_found = True
                break

        if not video_found:
            st.write("-")

st.markdown("---")
fig_score = px.line(
    df,
    x="partie",
    y="score",
    markers=True,
    title="Évolution du score",
    labels={"partie": "Numéro de partie", "score": "Score"},
)
fig_score.add_hline(
    y=df["score"].mean(),
    line_dash="dash",
    line_color="red",
    annotation_text=f"Moyenne: {df['score'].mean():.1f}",
)
st.plotly_chart(fig_score, width="stretch")

# Deux colonnes pour les graphiques
col1, col2 = st.columns(2)

with col1:
    # Distribution des scores
    st.markdown("### 📊 Distribution des scores")
    fig_hist = px.histogram(
        df,
        x="score",
        nbins=20,
        title="Histogramme des scores",
        labels={"score": "Score", "count": "Nombre de parties"},
    )
    st.plotly_chart(fig_hist, width="stretch")

with col2:
    # Réussite vs Échec
    st.markdown("### 🎯 Réussite vs Échec")
    success_counts = df["success"].value_counts()
    fig_success = px.pie(
        values=success_counts.values,
        names=["Atterrissage réussi" if i else "Crash" for i in success_counts.index],
        title="Répartition réussite/crash",
        color_discrete_map={"Atterrissage réussi": "#00ff00", "Crash": "#ff0000"},
    )
    st.plotly_chart(fig_success, width="stretch")

st.markdown("---")

# Actions les plus fréquentes
st.markdown("### 🎮 Distribution des actions")
all_actions = []
for actions in df["actions"]:
    all_actions.extend(actions)

action_names = {0: "Aucun", 1: "Gauche", 2: "Droite", 3: "Moteur"}
action_counts = {}
for action in all_actions:
    action_counts[action_names.get(action, f"Inconnu ({action})")] = (
        action_counts.get(action_names.get(action, f"Inconnu ({action})"), 0) + 1
    )

if action_counts:
    fig_actions = px.bar(
        x=list(action_counts.keys()),
        y=list(action_counts.values()),
        title="Fréquence des actions",
        labels={"x": "Action", "y": "Nombre d'appels"},
    )
    st.plotly_chart(fig_actions, width="stretch")
