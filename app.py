
import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd

# ============================================================
# CONFIGURATION
# CONFIGURATION
# ============================================================

API_BASE = "https://api.football-data.org/v4"

# ============================================================
# GOOGLE ADSENSE
# ============================================================

ADSENSE_CLIENT = "ca-pub-9405850065557656"

ADSENSE_SCRIPT = f"""
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}"
     crossorigin="anonymous"></script>
"""

ADSENSE_SLOT = f"""
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="{ADSENSE_CLIENT}"
     data-ad-slot="4489613144"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({{}});
</script>
"""


def show_ad(height=280):
    """Affiche un bloc publicitaire AdSense. Ne fonctionne qu'une fois l'app
    déployée sur un vrai domaine public et le compte AdSense approuvé."""
    components.html(ADSENSE_SCRIPT + ADSENSE_SLOT, height=height)

# ============================================================
# TOKEN API
# ============================================================
# Le token N'EST PLUS écrit en dur dans le code.
# Crée un fichier .streamlit/secrets.toml (à côté de ce script) avec :
#
#   FOOTBALL_DATA_API_TOKEN = "ton_token_ici"
#
# Ce fichier est à ajouter à .gitignore pour ne jamais le pousser sur GitHub.
# En local tu peux aussi définir la variable d'environnement du même nom.

import os

API_TOKEN ="d9c602b3dbdc426eaaf99a1e389cd54c"

# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="Football Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
h1 { font-weight: 800; }
[data-testid="stMetric"] {
    border: 1px solid rgba(128,128,128,.25);
    border-radius: 12px;
    padding: 12px;
}
.match-card {
    padding: 18px;
    border-radius: 14px;
    border: 1px solid rgba(128,128,128,.25);
    text-align: center;
    margin-bottom: 10px;
}
.small-text { opacity: 0.7; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# VERIFICATION TOKEN
# VERIFICATION TOKEN
# ============================================================

if not API_TOKEN:
    st.error(
        "❌ Token football-data.org non configuré.\n\n"
        "Ajoute-le dans `.streamlit/secrets.toml` sous la clé "
        "`FOOTBALL_DATA_API_TOKEN`, ou définis la variable d'environnement "
        "du même nom."
    )
    st.stop()


# ============================================================
# COMPETITIONS
# ============================================================

COMPETITIONS = {
    "Premier League": "PL",
    "La Liga": "PD",
    "Bundesliga": "BL1",
    "Serie A": "SA",
    "Ligue 1": "FL1",
    "Champions League": "CL",
    "Eredivisie": "DED",
    "Primeira Liga": "PPL"
}

# ============================================================
# API CLIENT
# ============================================================

API_ERROR_MESSAGES = {
    "BAD_REQUEST": "❌ Requête incorrecte.",
    "UNAUTHORIZED": "❌ Token API invalide.",
    "FORBIDDEN": "❌ Accès refusé. Cet endpoint peut nécessiter un abonnement supérieur.",
    "NOT_FOUND": "❌ Ressource introuvable.",
    "RATE_LIMIT": "⏳ Limite de requêtes atteinte (10/min en offre gratuite). Réessaie dans un instant.",
    "TIMEOUT": "⏱️ Timeout de connexion.",
    "CONNECTION": "🌐 Impossible de contacter football-data.org.",
    "REQUEST_ERROR": "❌ Erreur réseau."
}


@st.cache_data(ttl=300, show_spinner=False)
def api_request(endpoint, params=None):
    url = API_BASE + endpoint
    headers = {"X-Auth-Token": API_TOKEN, "Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
    except requests.exceptions.Timeout:
        return None, "TIMEOUT"
    except requests.exceptions.ConnectionError:
        return None, "CONNECTION"
    except requests.exceptions.RequestException:
        return None, "REQUEST_ERROR"

    if response.status_code == 200:
        return response.json(), None

    error_map = {400: "BAD_REQUEST", 401: "UNAUTHORIZED", 403: "FORBIDDEN",
                 404: "NOT_FOUND", 429: "RATE_LIMIT"}
    return None, error_map.get(response.status_code, f"HTTP_{response.status_code}")


def show_api_error(error):
    st.error(API_ERROR_MESSAGES.get(error, f"❌ Erreur API : {error}"))


def fetch(endpoint, params=None, note_on_error=None):
    """Fetch data and show an error inline if it fails. Returns None on failure."""
    data, error = api_request(endpoint, params)
    if error:
        show_api_error(error)
        if note_on_error:
            st.info(note_on_error)
        return None
    return data


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.title("⚽ Football Analytics")
    st.divider()

    competition_name = st.selectbox("🏟️ Compétition", list(COMPETITIONS.keys()))
    competition_code = COMPETITIONS[competition_name]

    season = st.number_input("📅 Saison", min_value=2020, max_value=2030, value=2026, step=1)

    st.divider()
    st.subheader("🔌 API")

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("Tester", use_container_width=True):
            with st.spinner("Connexion..."):
                data = fetch(f"/competitions/{competition_code}")
            if data:
                st.success("🟢 Connecté")
                st.caption(f"Compétition : {data.get('name', '-')}")

    with col_b:
        if st.button("🔄 Vider cache", use_container_width=True):
            st.cache_data.clear()
            st.success("Cache vidé")

    st.divider()
    st.caption("API : football-data.org")

    st.divider()
    show_ad(height=280)

# ============================================================
# HEADER
# ============================================================

st.title("⚽ Football Analytics")
st.caption(f"{competition_name} • Saison {season}")

# ============================================================
# NAVIGATION
# ============================================================

pages = [
    "📊 Dashboard", "🏆 Classement", "📅 Matchs", "⚽ Équipes",
    "🥅 Buteurs", "📈 Analyse", "⚔️ Comparaison", "🔎 Match"
]

page = st.radio("Navigation", pages, horizontal=True, label_visibility="collapsed")

st.divider()

# ============================================================
# DASHBOARD
# ============================================================

if page == "📊 Dashboard":
    st.header("📊 Dashboard")

    if st.button("🚀 Actualiser", type="primary"):
        with st.spinner("Chargement des données..."):
            competition = fetch(f"/competitions/{competition_code}")
            standings = fetch(f"/competitions/{competition_code}/standings", {"season": season})
            matches = fetch(f"/competitions/{competition_code}/matches", {"season": season})

        if competition is None:
            st.stop()

        match_list = matches.get("matches", []) if matches else []
        finished = [m for m in match_list if m.get("status") == "FINISHED"]
        upcoming = [m for m in match_list if m.get("status") in ["SCHEDULED", "TIMED"]]
        current_season = competition.get("currentSeason", {})

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏟️ Compétition", competition_name)
        col2.metric("📅 Matchs", len(match_list))
        col3.metric("✅ Terminés", len(finished))
        col4.metric("⏳ À venir", len(upcoming))

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📅 Saison")
            st.write(f"Début : {current_season.get('startDate', '-')}")
            st.write(f"Fin : {current_season.get('endDate', '-')}")
            st.write(f"Journée actuelle : {current_season.get('currentMatchday', '-')}")

        with col2:
            if standings:
                tables = standings.get("standings", [])
                if tables and tables[0].get("table"):
                    leader = tables[0]["table"][0]
                    st.subheader("🥇 Leader")
                    st.metric("Équipe", leader.get("team", {}).get("name", "-"))
                    st.write(f"Points : **{leader.get('points', 0)}**")
                    st.write(f"Différence : **{leader.get('goalDifference', 0)}**")

        st.divider()

        # TOP 10
        if standings:
            tables = standings.get("standings", [])
            if tables and tables[0].get("table"):
                rows = [{
                    "Pos": t.get("position"),
                    "Équipe": t.get("team", {}).get("name"),
                    "MJ": t.get("playedGames"),
                    "V": t.get("won"),
                    "N": t.get("draw"),
                    "D": t.get("lost"),
                    "Diff": t.get("goalDifference"),
                    "Pts": t.get("points"),
                } for t in tables[0]["table"][:10]]

                st.subheader("🏆 Classement")
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # PROCHAINS MATCHS
        st.subheader("📅 Prochains matchs")

        if not upcoming:
            st.info("Aucun prochain match trouvé.")

        for match in upcoming[:6]:
            home = match.get("homeTeam", {})
            away = match.get("awayTeam", {})
            date = match.get("utcDate", "-")

            st.markdown(f"""
                <div class="match-card">
                <b>{home.get('name', '-')}</b>
                &nbsp;&nbsp; VS &nbsp;&nbsp;
                <b>{away.get('name', '-')}</b>
                <br><br>
                <span class="small-text">{date}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Clique sur **🚀 Actualiser** pour charger le dashboard.")

# ============================================================
# CLASSEMENT
# ============================================================

elif page == "🏆 Classement":
    st.header("🏆 Classement")

    data = fetch(f"/competitions/{competition_code}/standings", {"season": season})

    if data:
        standings = data.get("standings", [])

        if not standings or not standings[0].get("table"):
            st.info("Aucun classement disponible.")
        else:
            table = standings[0]["table"]

            rows = [{
                "Position": t.get("position"),
                "Équipe": t.get("team", {}).get("name"),
                "MJ": t.get("playedGames"),
                "V": t.get("won"),
                "N": t.get("draw"),
                "D": t.get("lost"),
                "BP": t.get("goalsFor"),
                "BC": t.get("goalsAgainst"),
                "Diff": t.get("goalDifference"),
                "Pts": t.get("points"),
            } for t in table]

            df = pd.DataFrame(rows)
            leader = df.iloc[0]

            c1, c2, c3 = st.columns(3)
            c1.metric("🥇 Leader", leader["Équipe"])
            c2.metric("⭐ Points", leader["Pts"])
            c3.metric("⚽ Différence", leader["Diff"])

            st.dataframe(df, use_container_width=True, hide_index=True)

            st.download_button(
                "📥 Télécharger CSV",
                df.to_csv(index=False).encode("utf-8"),
                "classement.csv",
                "text/csv"
            )

# ============================================================
# MATCHS
# ============================================================

elif page == "📅 Matchs":
    st.header("📅 Matchs")

    col1, col2 = st.columns(2)

    with col1:
        status = st.selectbox(
            "Statut",
            ["ALL", "SCHEDULED", "TIMED", "IN_PLAY", "PAUSED", "FINISHED", "POSTPONED", "CANCELED"]
        )

    with col2:
        limit = st.slider("Nombre de matchs", 10, 100, 30)

    params = {"season": season}
    if status != "ALL":
        params["status"] = status

    data = fetch(f"/competitions/{competition_code}/matches", params)

    if data:
        matches = data.get("matches", [])

        rows = []
        for match in matches[:limit]:
            full_time = match.get("score", {}).get("fullTime", {})
            rows.append({
                "Date": match.get("utcDate"),
                "Journée": match.get("matchday"),
                "Domicile": match.get("homeTeam", {}).get("name"),
                "Extérieur": match.get("awayTeam", {}).get("name"),
                "Score": f"{full_time.get('home', '-')} - {full_time.get('away', '-')}",
                "Statut": match.get("status"),
                "ID": match.get("id"),
            })

        df = pd.DataFrame(rows)
        st.metric("Matchs", len(df))

        if df.empty:
            st.info("Aucun match trouvé.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "📥 Exporter CSV",
                df.to_csv(index=False).encode("utf-8"),
                "matches.csv",
                "text/csv"
            )
            st.caption("💡 Note l'ID d'un match pour le retrouver dans l'onglet 🔎 Match.")

# ============================================================
# EQUIPES
# ============================================================

elif page == "⚽ Équipes":
    st.header("⚽ Équipes")

    data = fetch(f"/competitions/{competition_code}/teams", {"season": season})

    if data:
        teams = data.get("teams", [])
        st.metric("Nombre d'équipes", len(teams))

        search = st.text_input("🔎 Rechercher une équipe")

        if search:
            teams = [t for t in teams if search.lower() in t.get("name", "").lower()]

        if not teams:
            st.info("Aucune équipe ne correspond à la recherche.")

        cols = st.columns(4)

        for i, team in enumerate(teams):
            with cols[i % 4]:
                crest = team.get("crest")
                if crest:
                    try:
                        st.image(crest, width=80)
                    except Exception:
                        pass

                st.subheader(team.get("shortName") or team.get("name", "-"))
                st.caption(team.get("name", "-"))
                st.write(f"🏟️ {team.get('venue', '-')}")
                st.write(f"TLA : {team.get('tla', '-')}")
                st.divider()

# ============================================================
# BUTEURS
# ============================================================

elif page == "🥅 Buteurs":
    st.header("🥅 Meilleurs buteurs")

    limit = st.slider("Nombre de joueurs", 5, 50, 20)

    data = fetch(
        f"/competitions/{competition_code}/scorers",
        {"season": season, "limit": limit},
        note_on_error="Selon ton abonnement football-data.org, cet endpoint peut être limité."
    )

    if data:
        scorers = data.get("scorers", [])

        rows = [{
            "Pos": i,
            "Joueur": s.get("player", {}).get("name"),
            "Équipe": s.get("team", {}).get("name"),
            "Buts": s.get("goals", 0),
            "Passes": s.get("assists", 0),
            "Matchs": s.get("playedMatches", 0),
        } for i, s in enumerate(scorers, 1)]

        df = pd.DataFrame(rows)

        if df.empty:
            st.info("Aucun buteur disponible.")
        else:
            leader = df.iloc[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("🥇 Leader", leader["Joueur"])
            c2.metric("⚽ Buts", leader["Buts"])
            c3.metric("🎯 Passes", leader["Passes"])

            st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================================
# ANALYSE
# ============================================================

elif page == "📈 Analyse":
    st.header("📈 Analyse statistique")

    data = fetch(f"/competitions/{competition_code}/matches", {"season": season})

    if data:
        matches = data.get("matches", [])

        rows = []
        for match in matches:
            full_time = match.get("score", {}).get("fullTime", {})
            home, away = full_time.get("home"), full_time.get("away")

            if home is not None and away is not None:
                rows.append({
                    "Domicile": match.get("homeTeam", {}).get("name"),
                    "Extérieur": match.get("awayTeam", {}).get("name"),
                    "HomeGoals": home,
                    "AwayGoals": away,
                })

        df = pd.DataFrame(rows)

        if df.empty:
            st.info("Pas encore assez de matchs terminés.")
        else:
            df["TotalGoals"] = df["HomeGoals"] + df["AwayGoals"]

            total_matches = len(df)
            total_goals = int(df["TotalGoals"].sum())
            avg_goals = df["TotalGoals"].mean()
            home_wins = int((df["HomeGoals"] > df["AwayGoals"]).sum())
            draws = int((df["HomeGoals"] == df["AwayGoals"]).sum())
            away_wins = int((df["HomeGoals"] < df["AwayGoals"]).sum())

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Matchs analysés", total_matches)
            c2.metric("⚽ Buts", total_goals)
            c3.metric("📊 Moyenne buts", f"{avg_goals:.2f}")
            c4.metric("🏠 Victoires domicile", home_wins)

            st.divider()

            c1, c2, c3 = st.columns(3)
            c1.metric("🏠 Domicile", home_wins)
            c2.metric("🤝 Nuls", draws)
            c3.metric("✈️ Extérieur", away_wins)

            st.subheader("⚽ Distribution des buts")
            st.bar_chart(df["TotalGoals"].value_counts().sort_index())

            st.subheader("📊 Résultats")
            result_data = pd.DataFrame({
                "Résultat": ["Domicile", "Nul", "Extérieur"],
                "Nombre": [home_wins, draws, away_wins],
            })
            st.bar_chart(result_data.set_index("Résultat"))

# ============================================================
# COMPARAISON
# ============================================================

elif page == "⚔️ Comparaison":
    st.header("⚔️ Comparaison de deux équipes")

    standings_data = fetch(f"/competitions/{competition_code}/standings", {"season": season})

    if standings_data:
        tables = standings_data.get("standings", [])
        table = tables[0].get("table", []) if tables else []
        team_names = [t.get("team", {}).get("name") for t in table]

        if len(team_names) < 2:
            st.warning("Pas assez d'équipes disponibles.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                team_a = st.selectbox("Équipe A", team_names, index=0)
            with col2:
                team_b = st.selectbox("Équipe B", team_names, index=1)

            if team_a == team_b:
                st.warning("Choisis deux équipes différentes.")
            else:
                team_a_data = next((x for x in table if x.get("team", {}).get("name") == team_a), None)
                team_b_data = next((x for x in table if x.get("team", {}).get("name") == team_b), None)

                if team_a_data and team_b_data:
                    fields = [
                        ("Position", "position"), ("Matchs", "playedGames"),
                        ("Victoires", "won"), ("Nuls", "draw"), ("Défaites", "lost"),
                        ("Buts marqués", "goalsFor"), ("Buts encaissés", "goalsAgainst"),
                        ("Différence", "goalDifference"), ("Points", "points"),
                    ]

                    comparison = pd.DataFrame({
                        team_a: [team_a_data.get(key) for _, key in fields],
                        team_b: [team_b_data.get(key) for _, key in fields],
                    }, index=[label for label, _ in fields])

                    st.dataframe(comparison, use_container_width=True)

                    # Petit résumé visuel
                    diff_pts = (team_a_data.get("points", 0) or 0) - (team_b_data.get("points", 0) or 0)
                    if diff_pts > 0:
                        st.success(f"🏆 {team_a} devance {team_b} de {diff_pts} points.")
                    elif diff_pts < 0:
                        st.success(f"🏆 {team_b} devance {team_a} de {abs(diff_pts)} points.")
                    else:
                        st.info(f"🤝 {team_a} et {team_b} sont à égalité de points.")

# ============================================================
# MATCH DETAILS
# ============================================================

elif page == "🔎 Match":
    st.header("🔎 Recherche d'un match")

    search_mode = st.radio(
        "Rechercher par",
        ["ID du match", "Équipe"],
        horizontal=True
    )

    match_data = None

    if search_mode == "ID du match":
        match_id = st.number_input("ID du match", min_value=1, value=1, step=1)

        if st.button("🔍 Rechercher", type="primary"):
            with st.spinner("Recherche du match..."):
                match_data = fetch(f"/matches/{int(match_id)}")

    else:
        teams_data = fetch(f"/competitions/{competition_code}/teams", {"season": season})

        if teams_data:
            teams = teams_data.get("teams", [])
            team_names = [t.get("name") for t in teams]
            chosen_team = st.selectbox("Équipe", team_names)

            if st.button("🔍 Voir les matchs récents", type="primary"):
                team_id = next((t.get("id") for t in teams if t.get("name") == chosen_team), None)

                if team_id:
                    with st.spinner("Recherche des matchs..."):
                        team_matches = fetch(f"/teams/{team_id}/matches", {"season": season, "limit": 15})

                    if team_matches:
                        options = {
                            f"{m.get('utcDate', '-')[:10]} — "
                            f"{m.get('homeTeam', {}).get('name', '-')} vs "
                            f"{m.get('awayTeam', {}).get('name', '-')} "
                            f"({m.get('status', '-')})": m.get("id")
                            for m in team_matches.get("matches", [])
                        }

                        if options:
                            st.session_state["match_options"] = options
                        else:
                            st.info("Aucun match trouvé pour cette équipe.")

            if "match_options" in st.session_state:
                chosen_label = st.selectbox("Choisir un match", list(st.session_state["match_options"].keys()))
                if st.button("Afficher ce match"):
                    match_id = st.session_state["match_options"][chosen_label]
                    with st.spinner("Chargement..."):
                        match_data = fetch(f"/matches/{int(match_id)}")

    if match_data:
        home = match_data.get("homeTeam", {})
        away = match_data.get("awayTeam", {})
        full_time = match_data.get("score", {}).get("fullTime", {})

        c1, c2, c3 = st.columns([2, 1, 2])

        with c1:
            if home.get("crest"):
                try:
                    st.image(home["crest"], width=100)
                except Exception:
                    pass
            st.subheader(home.get("name", "-"))

        with c2:
            st.markdown("<h1 style='text-align:center'>VS</h1>", unsafe_allow_html=True)
            st.markdown(
                f"<h2 style='text-align:center'>{full_time.get('home', '-')} - {full_time.get('away', '-')}</h2>",
                unsafe_allow_html=True
            )

        with c3:
            if away.get("crest"):
                try:
                    st.image(away["crest"], width=100)
                except Exception:
                    pass
            st.subheader(away.get("name", "-"))

        st.divider()

        c1, c2, c3 = st.columns(3)
        c1.metric("Statut", match_data.get("status", "-"))
        c2.metric("Journée", match_data.get("matchday", "-"))
        c3.metric("Compétition", match_data.get("competition", {}).get("name", "-"))

        st.divider()

        with st.expander("📦 Données API complètes"):
            st.json(match_data)

# ============================================================
# FOOTER
# ============================================================

st.divider()
show_ad(height=100)
st.caption("⚽ Football Analytics | Python + Streamlit + football-data.org")