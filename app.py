import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import require_authentication, logout
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(
    page_title="Dashboard Sondage",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# -------------------------
# AUTH
# -------------------------
require_authentication()
logout()

# -------------------------
# LOAD DATA
# -------------------------
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "data", "sondage.csv")

    df = pd.read_csv(file_path, encoding="utf-8")
    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        "Si l’élection avait lieu aujourd’hui, pour qui voteriez-vous ?": "candidat",
        "Tranche d’âge": "age",
        "Sexe": "sexe",
        "Quartier": "quartier",
        "Lieu de vote": "lieu",
        "Quel est le principal problème à Yoff selon vous ?": "probleme",
        "Qu’attendez-vous en priorité d’un candidat ?": "priorite",
        "Votre choix est-il :": "choix_statut"
    })

    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    return df

df = load_data()

# -------------------------
# SIDEBAR NAVIGATION
# -------------------------
st.sidebar.title("📊 Navigation")

page = st.sidebar.radio(
    "Aller vers",
    [
        "📊 Dashboard Général",
        "👥 Analyse par Profil",
        "🧾 Priorités",
        "📍 Analyse Bureau de Vote",
        "🗳️ Analyse des Indécis",
        "📊 Simulation",
        "📍 Carte Géographique",
        "📈 Score Stratégique",
        "🤖 Analyse IA",
        "🧠 Profils Électeurs",
        "⚠️ Indice de Risque",
        "🔥 Zone Prioritaire d’Action",
        "📊 Résumé Exécutif",
        "📍 Carte Stratégique"


    ]
)

# -------------------------
# FILTRES DYNAMIQUES
# -------------------------
st.sidebar.markdown("## 🎯 Filtres")

quartiers = st.sidebar.multiselect(
    "Quartier",
    options=df["quartier"].dropna().unique()
)

lieux = st.sidebar.multiselect(
    "Lieu de vote",
    options=df["lieu"].dropna().unique()
)

sexes = st.sidebar.multiselect(
    "Sexe",
    options=df["sexe"].dropna().unique()
)

df_filtered = df.copy()

if quartiers:
    df_filtered = df_filtered[df_filtered["quartier"].isin(quartiers)]

if lieux:
    df_filtered = df_filtered[df_filtered["lieu"].isin(lieux)]

if sexes:
    df_filtered = df_filtered[df_filtered["sexe"].isin(sexes)]

# -------------------------
# DASHBOARD GÉNÉRAL
# -------------------------
if page == "📊 Dashboard Général":

    st.title("📊 Résultats Globaux")

    total = len(df_filtered)

    resultats = df_filtered["candidat"].value_counts(normalize=True) * 100
    resultats = resultats.reset_index()
    resultats.columns = ["Candidat", "Pourcentage"]
    resultats["Pourcentage"] = resultats["Pourcentage"].round(2)

    # --- Indécis ---
    indecis = df_filtered[
        df_filtered["choix_statut"].str.contains("Peut", na=False)
    ].shape[0] / total * 100

    # --- Leader & Écart ---
    leader = resultats.iloc[0]["Candidat"]
    leader_score = resultats.iloc[0]["Pourcentage"]
    second_score = resultats.iloc[1]["Pourcentage"] if len(resultats) > 1 else 0
    ecart = leader_score - second_score

    # -------------------------
    # MÉTRIQUES PRINCIPALES (Mobile Friendly)
    # -------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Répondants", total)
    col2.metric("Leader", leader)
    col3.metric("Score Leader", f"{leader_score} %")
    col4.metric("Indécis", f"{indecis:.1f} %")

    st.markdown("---")

    # Diagnostic rapide
    if leader_score > 50:
        st.success("Position dominante")
    elif ecart < 5:
        st.warning("Course très serrée")
    else:
        st.info("Avantage modéré")

    # -------------------------
    # CLASSEMENT
    # -------------------------
    st.subheader("🏆 Classement des candidats")
    st.dataframe(resultats, use_container_width=True)

    # -------------------------
    # GRAPHIQUE
    # -------------------------
    fig = px.pie(
        resultats,
        values="Pourcentage",
        names="Candidat",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # EXPORT PDF AMÉLIORÉ
    # -------------------------
    if st.button("📥 Télécharger Rapport PDF"):

        file_path = "rapport_sondage.pdf"
        doc = SimpleDocTemplate(file_path)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("RAPPORT STRATÉGIQUE - SONDAGE", styles["Title"]))
        elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph(f"Total répondants : {total}", styles["Normal"]))
        elements.append(Paragraph(f"Leader : {leader}", styles["Normal"]))
        elements.append(Paragraph(f"Score leader : {leader_score} %", styles["Normal"]))
        elements.append(Paragraph(f"Indécis : {indecis:.1f} %", styles["Normal"]))
        elements.append(Paragraph(f"Ecart avec second : {ecart:.1f} %", styles["Normal"]))

        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph("Classement détaillé :", styles["Heading2"]))

        for index, row in resultats.iterrows():
            elements.append(
                Paragraph(f"{row['Candidat']} : {row['Pourcentage']} %", styles["Normal"])
            )

        doc.build(elements)

        with open(file_path, "rb") as f:
            st.download_button(
                "Télécharger le PDF",
                f,
                file_name="rapport_sondage.pdf"
            )


# -------------------------
# ANALYSE PAR PROFIL
# -------------------------
elif page == "👥 Analyse par Profil":

    st.title("👥 Analyse par Tranche d'Âge")

    fig = px.histogram(
        df_filtered,
        x="age",
        color="candidat",
        barmode="group"
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# PRIORITÉS
# -------------------------
elif page == "🧾 Priorités":

    st.title("🧾 Priorités des répondants")

    priorites = (
        df_filtered["priorite"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
        .reset_index()
    )

    priorites.columns = ["Priorité", "Nombre"]

    fig = px.bar(priorites, x="Priorité", y="Nombre")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# ANALYSE PAR BUREAU
# -------------------------
elif page == "📍 Analyse Bureau de Vote":

    st.title("📍 Résultats par Bureau de Vote")

    bureau = (
        df_filtered
        .groupby(["lieu", "candidat"])
        .size()
        .reset_index(name="Votes")
    )

    fig = px.bar(bureau, x="lieu", y="Votes", color="candidat", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# ANALYSE DES INDÉCIS
# -------------------------
elif page == "🗳️ Analyse des Indécis":

    st.title("🗳️ Analyse des Indécis")

    indecis = df_filtered[
        df_filtered["choix_statut"].str.contains("Peut", na=False)
    ]

    st.metric("Nombre d'indécis", len(indecis))

    fig = px.histogram(indecis, x="age", color="sexe")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# SIMULATION
# -------------------------
elif page == "📊 Simulation":

    st.title("📊 Simulation de Report des Indécis")

    base = df_filtered["candidat"].value_counts()

    indecis_count = df_filtered[
        df_filtered["choix_statut"].str.contains("Peut", na=False)
    ].shape[0]

    candidat_select = st.selectbox("Attribuer les indécis à :", base.index)

    simulation = base.copy()
    simulation[candidat_select] += indecis_count

    simulation_percent = (simulation / simulation.sum()) * 100

    fig = px.pie(
        values=simulation_percent.values,
        names=simulation_percent.index,
        title="Simulation après report des indécis"
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Carte Géographique
# -------------------------

elif page == "📍 Carte Géographique":

    st.title("📍 Carte Interactive par Quartier")

    quartier_votes = (
        df_filtered
        .groupby(["quartier", "candidat"])
        .size()
        .reset_index(name="Votes")
    )

    # Candidat dominant par quartier
    dominant = (
        quartier_votes
        .sort_values("Votes", ascending=False)
        .drop_duplicates("quartier")
    )

    fig = px.scatter_mapbox(
        dominant,
        lat=[14.75]*len(dominant),  # Coord approximative Yoff
        lon=[-17.49]*len(dominant),
        hover_name="quartier",
        hover_data=["candidat", "Votes"],
        zoom=11,
        height=600
    )

    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Score Stratégique
# -------------------------

elif page == "📈 Score Stratégique":

    st.title("📈 Score Stratégique par Quartier")

    score = (
        df_filtered
        .groupby(["quartier", "candidat"])
        .size()
        .reset_index(name="Votes")
    )

    total_par_quartier = (
        df_filtered
        .groupby("quartier")
        .size()
        .reset_index(name="Total")
    )

    score = score.merge(total_par_quartier, on="quartier")
    score["Score (%)"] = (score["Votes"] / score["Total"]) * 100
    score["Score (%)"] = score["Score (%)"].round(2)

    st.dataframe(score.sort_values("Score (%)", ascending=False), use_container_width=True)

# -------------------------
# Analyse IA
# -------------------------

elif page == "🤖 Analyse IA":

    st.title("🤖 Analyse Automatique des Tendances")

    total = len(df_filtered)

    leader = df_filtered["candidat"].value_counts().idxmax()
    leader_score = (
        df_filtered["candidat"]
        .value_counts(normalize=True)
        .max() * 100
    )

    indecis = df_filtered[
        df_filtered["choix_statut"].str.contains("Peut", na=False)
    ].shape[0]

    st.markdown("### 📊 Diagnostic Automatique")

    if leader_score > 50:
        st.success(f"{leader} est en position dominante ({leader_score:.1f}%).")
    elif leader_score > 35:
        st.warning(f"{leader} est en tête mais fragile ({leader_score:.1f}%).")
    else:
        st.error("Course très ouverte, aucun candidat dominant.")

    st.write(f"Nombre d'indécis : {indecis}")

    if indecis > total * 0.2:
        st.warning("Fort potentiel de bascule stratégique.")

# -------------------------
# Profils Électeurs
# -------------------------
elif page == "🧠 Profils Électeurs":

    st.title("🧠 Profils Électeurs")

    profil = (
        df_filtered
        .groupby(["age", "sexe", "candidat"])
        .size()
        .reset_index(name="Votes")
        .sort_values("Votes", ascending=False)
    )

    st.subheader("Profils dominants détectés")
    st.dataframe(profil.head(10), use_container_width=True)

    fig = px.bar(
        profil.head(10),
        x="Votes",
        y="age",
        color="candidat",
        orientation="h"
    )

    st.plotly_chart(fig, use_container_width=True)



# -------------------------
# Indice de Risque
# -------------------------
elif page == "⚠️ Indice de Risque":

    st.title("⚠️ Indice de Risque Électoral")

    total = len(df_filtered)

    resultats = df_filtered["candidat"].value_counts(normalize=True) * 100
    leader_score = resultats.iloc[0]
    second_score = resultats.iloc[1] if len(resultats) > 1 else 0

    indecis = df_filtered[
        df_filtered["choix_statut"].str.contains("Peut", na=False)
    ].shape[0] / total * 100

    ecart = leader_score - second_score

    risque = (indecis * 0.5) + ((10 - ecart) * 3)

    risque = max(0, min(risque, 100))

    st.metric("Indice de risque (%)", round(risque, 1))

    if risque < 30:
        st.success("Situation stable")
    elif risque < 60:
        st.warning("Situation compétitive")
    else:
        st.error("Situation instable - risque élevé")


# -------------------------
# Zone Prioritaire d’Action
# -------------------------
elif page == "🔥 Zone Prioritaire d’Action":

    st.title("🔥 Zones Prioritaires d’Action")

    zones = []

    for quartier in df_filtered["quartier"].dropna().unique():

        df_q = df_filtered[df_filtered["quartier"] == quartier]
        total = len(df_q)

        if total < 5:
            continue

        resultats = df_q["candidat"].value_counts(normalize=True) * 100

        if len(resultats) < 2:
            continue

        leader = resultats.iloc[0]
        second = resultats.iloc[1]
        ecart = leader - second

        indecis = df_q[
            df_q["choix_statut"].str.contains("Peut", na=False)
        ].shape[0] / total * 100

        # Score stratégique
        score_priorite = (indecis * 0.5) + ((10 - ecart) * 3)

        # Classification couleur
        if score_priorite >= 60:
            niveau = "🟥 ROUGE"
        elif score_priorite >= 35:
            niveau = "🟡 ORANGE"
        else:
            niveau = "🟢 VERT"

        zones.append({
            "Quartier": quartier,
            "Total répondants": total,
            "% Indécis": round(indecis, 1),
            "Écart (%)": round(ecart, 1),
            "Score Priorité": round(score_priorite, 1),
            "Niveau": niveau
        })

    zones_df = pd.DataFrame(zones).sort_values("Score Priorité", ascending=False)

    st.dataframe(zones_df, use_container_width=True)

    # Graphique
    fig = px.bar(
        zones_df,
        x="Score Priorité",
        y="Quartier",
        color="Niveau",
        orientation="h",
        title="Classement stratégique des quartiers"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Recommandation automatique
    if not zones_df.empty:

        top = zones_df.iloc[0]

        st.markdown("## 🎯 Recommandation Stratégique")

        if "ROUGE" in top["Niveau"]:
            st.error(f"Action urgente recommandée dans : {top['Quartier']}")
        elif "ORANGE" in top["Niveau"]:
            st.warning(f"Zone à surveiller de près : {top['Quartier']}")
        else:
            st.success(f"Zone stable : {top['Quartier']}")

# -------------------------
# Résumé Exécutif
# -------------------------
elif page == "📊 Résumé Exécutif":

    st.title("📊 Résumé Exécutif")

    total = len(df_filtered)

    resultats = df_filtered["candidat"].value_counts(normalize=True) * 100
    leader = resultats.index[0]
    leader_score = resultats.iloc[0]
    second_score = resultats.iloc[1] if len(resultats) > 1 else 0
    ecart = leader_score - second_score

    indecis = df_filtered[
        df_filtered["choix_statut"].str.contains("Peut", na=False)
    ].shape[0] / total * 100

    col1, col2, col3 = st.columns(3)

    col1.metric("Leader actuel", leader)
    col2.metric("Score", f"{leader_score:.1f} %")
    col3.metric("Indécis", f"{indecis:.1f} %")

    st.markdown("---")

    if leader_score > 50:
        st.success("Position dominante")
    elif ecart < 5:
        st.warning("Course serrée")
    else:
        st.info("Avantage modéré")

    if indecis > 20:
        st.warning("Fort potentiel de bascule")


# -------------------------
# Carte Stratégique
# -------------------------
elif page == "📍 Carte Stratégique":

    st.title("📍 Carte Stratégique des Quartiers")

    zones = []

    for quartier in df_filtered["quartier"].dropna().unique():

        df_q = df_filtered[df_filtered["quartier"] == quartier]
        total = len(df_q)

        if total < 5:
            continue

        resultats = df_q["candidat"].value_counts(normalize=True) * 100

        if len(resultats) < 2:
            continue

        leader = resultats.iloc[0]
        second = resultats.iloc[1]
        ecart = leader - second

        indecis = df_q[
            df_q["choix_statut"].str.contains("Peut", na=False)
        ].shape[0] / total * 100

        score = (indecis * 0.5) + ((10 - ecart) * 3)

        if score >= 60:
            niveau = "ROUGE"
        elif score >= 35:
            niveau = "ORANGE"
        else:
            niveau = "VERT"

        zones.append({
            "quartier": quartier,
            "Score": score,
            "Niveau": niveau
        })

    zones_df = pd.DataFrame(zones)

    color_map = {
        "ROUGE": "red",
        "ORANGE": "orange",
        "VERT": "green"
    }

    fig = px.bar(
        zones_df,
        x="quartier",
        y="Score",
        color="Niveau",
        color_discrete_map=color_map,
        title="Niveau stratégique par quartier"
    )

    st.plotly_chart(fig, use_container_width=True)


