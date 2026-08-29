import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================

API_BASE = "https://api.football-data.org/v4"

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

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

h1 {
    font-weight: 800;
}

[data-testid="stMetric"] {
    border: 1px solid rgba(128,128,128,.25);
    border-radius: 12px;
    padding: 12px;
}

.team-card {
    padding: 18px;
    border-radius: 14px;
    border: 1px solid rgba(128,128,128,.25);
    margin-bottom: 15px;
}

.match-card {
    padding: 18px;
    border-radius: 14px;
    border: 1px solid rgba(128,128,128,.25);
    text-align: center;
}

.small-text {
    opacity: 0.7;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# TOKEN
# ============================================================
# ============================================================
# TOKEN
# ============================================================

API_TOKEN = st.secrets.get(
    "FOOTBALL_API_TOKEN",
    ""
)

if not API_TOKEN:
    st.error(
        "❌ Token football-data.org non configuré."
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

@st.cache_data(
    ttl=300,
    show_spinner=False
)
def api_request(
    endpoint,
    params=None
):

    if not API_TOKEN:
        return None, "TOKEN_MISSING"

    try:

        response = requests.get(
            API_BASE + endpoint,
            headers={
                "X-Auth-Token": API_TOKEN,
                "Accept": "application/json"
            },
            params=params,
            timeout=20
        )

        if response.status_code == 200:

            return response.json(), None

        if response.status_code == 400:
            return None, "BAD_REQUEST"

        if response.status_code == 401:
            return None, "UNAUTHORIZED"

        if response.status_code == 403:
            return None, "FORBIDDEN"

        if response.status_code == 404:
            return None, "NOT_FOUND"

        if response.status_code == 429:
            return None, "RATE_LIMIT"

        return None, f"HTTP_{response.status_code}"

    except requests.exceptions.Timeout:

        return None, "TIMEOUT"

    except requests.exceptions.ConnectionError:

        return None, "CONNECTION"

    except requests.exceptions.RequestException:

        return None, "REQUEST_ERROR"


def show_api_error(error):

    messages = {

        "TOKEN_MISSING":
            "❌ Token API absent. Configure .streamlit/secrets.toml.",

        "UNAUTHORIZED":
            "❌ Token API invalide.",

        "FORBIDDEN":
            "❌ Accès refusé. Ton abonnement ne permet peut-être pas cet endpoint.",

        "NOT_FOUND":
            "❌ Ressource introuvable.",

        "RATE_LIMIT":
            "⏳ Limite de requêtes atteinte. Attends avant de recommencer.",

        "BAD_REQUEST":
            "❌ Requête incorrecte.",

        "TIMEOUT":
            "⏱️ Timeout de connexion.",

        "CONNECTION":
            "🌐 Impossible de contacter football-data.org.",

        "REQUEST_ERROR":
            "❌ Erreur réseau."
    }

    st.error(
        messages.get(
            error,
            f"Erreur API : {error}"
        )
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚽ Football Analytics")

    st.divider()

    competition_name = st.selectbox(
        "🏟️ Compétition",
        list(COMPETITIONS.keys())
    )

    competition_code = COMPETITIONS[
        competition_name
    ]

    season = st.number_input(
        "📅 Saison",
        min_value=2020,
        max_value=2030,
        value=2026,
        step=1
    )

    st.divider()

    st.subheader("🔌 API")

    if st.button(
        "Tester la connexion",
        use_container_width=True
    ):

        data, error = api_request(
            f"/competitions/{competition_code}"
        )

        if data:

            st.success("🟢 API connectée")

        else:

            show_api_error(error)

    st.divider()

    st.caption(
        "Données : football-data.org"
    )


# ============================================================
# HEADER
# ============================================================

st.title("⚽ Football Analytics")

st.caption(
    f"{competition_name} • Saison {season}"
)


# ============================================================
# NAVIGATION
# ============================================================

pages = [
    "📊 Dashboard",
    "🏆 Classement",
    "📅 Matchs",
    "⚽ Équipes",
    "🥅 Buteurs",
    "📈 Analyse",
    "⚔️ Comparaison",
    "🔎 Match"
]

page = st.radio(
    "Navigation",
    pages,
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()


# ============================================================
# DASHBOARD
# ============================================================

if page == "📊 Dashboard":

    st.header("📊 Dashboard")

    if st.button(
        "🚀 Actualiser",
        type="primary"
    ):

        with st.spinner(
            "Chargement des données..."
        ):

            competition, error1 = api_request(
                f"/competitions/{competition_code}"
            )

            standings, error2 = api_request(
                f"/competitions/{competition_code}/standings",
                {
                    "season": season
                }
            )

            matches, error3 = api_request(
                f"/competitions/{competition_code}/matches",
                {
                    "season": season
                }
            )

        if error1:

            show_api_error(error1)

        else:

            match_list = (
                matches.get("matches", [])
                if matches
                else []
            )

            finished = [
                m for m in match_list
                if m.get("status") == "FINISHED"
            ]

            upcoming = [
                m for m in match_list
                if m.get("status")
                in ["SCHEDULED", "TIMED"]
            ]

            current_season = (
                competition.get(
                    "currentSeason",
                    {}
                )
                if competition
                else {}
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "🏟️ Compétition",
                    competition_name
                )

            with col2:

                st.metric(
                    "📅 Matchs",
                    len(match_list)
                )

            with col3:

                st.metric(
                    "✅ Terminés",
                    len(finished)
                )

            with col4:

                st.metric(
                    "⏳ À venir",
                    len(upcoming)
                )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                st.subheader(
                    "📅 Saison"
                )

                st.write(
                    "Début :",
                    current_season.get(
                        "startDate",
                        "-"
                    )
                )

                st.write(
                    "Fin :",
                    current_season.get(
                        "endDate",
                        "-"
                    )
                )

                st.write(
                    "Journée actuelle :",
                    current_season.get(
                        "currentMatchday",
                        "-"
                    )
                )

            with col2:

                if standings:

                    table = standings.get(
                        "standings",
                        []
                    )

                    if table:

                        first_table = table[0].get(
                            "table",
                            []
                        )

                        if first_table:

                            leader = first_table[0]

                            st.subheader(
                                "🥇 Leader"
                            )

                            st.metric(
                                "Équipe",
                                leader.get(
                                    "team",
                                    {}
                                ).get(
                                    "name",
                                    "-"
                                )
                            )

                            st.write(
                                f"Points : "
                                f"**{leader.get('points', 0)}**"
                            )

                            st.write(
                                f"Différence : "
                                f"**{leader.get('goalDifference', 0)}**"
                            )

            st.divider()

            # TOP 10

            if standings:

                tables = standings.get(
                    "standings",
                    []
                )

                if tables:

                    table = tables[0].get(
                        "table",
                        []
                    )

                    rows = []

                    for team in table[:10]:

                        rows.append({

                            "Pos":
                                team.get(
                                    "position"
                                ),

                            "Équipe":
                                team.get(
                                    "team",
                                    {}
                                ).get(
                                    "name"
                                ),

                            "MJ":
                                team.get(
                                    "playedGames"
                                ),

                            "V":
                                team.get(
                                    "won"
                                ),

                            "N":
                                team.get(
                                    "draw"
                                ),

                            "D":
                                team.get(
                                    "lost"
                                ),

                            "Diff":
                                team.get(
                                    "goalDifference"
                                ),

                            "Pts":
                                team.get(
                                    "points"
                                )
                        })

                    st.subheader(
                        "🏆 Classement"
                    )

                    st.dataframe(
                        pd.DataFrame(rows),
                        use_container_width=True,
                        hide_index=True
                    )

            # PROCHAINS MATCHS

            st.subheader(
                "📅 Prochains matchs"
            )

            for match in upcoming[:6]:

                home = match.get(
                    "homeTeam",
                    {}
                )

                away = match.get(
                    "awayTeam",
                    {}
                )

                date = match.get(
                    "utcDate",
                    "-"
                )

                st.markdown(
                    f"""
                    <div class="match-card">

                    <b>{home.get('name', '-')}</b>

                    &nbsp;&nbsp; VS &nbsp;&nbsp;

                    <b>{away.get('name', '-')}</b>

                    <br><br>

                    <span class="small-text">
                    {date}
                    </span>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.write("")


# ============================================================
# CLASSEMENT
# ============================================================

elif page == "🏆 Classement":

    st.header("🏆 Classement")

    data, error = api_request(
        f"/competitions/{competition_code}/standings",
        {
            "season": season
        }
    )

    if error:

        show_api_error(error)

    else:

        standings = data.get(
            "standings",
            []
        )

        if not standings:

            st.info(
                "Aucun classement disponible."
            )

        else:

            table = standings[0].get(
                "table",
                []
            )

            rows = []

            for team in table:

                rows.append({

                    "Position":
                        team.get(
                            "position"
                        ),

                    "Équipe":
                        team.get(
                            "team",
                            {}
                        ).get(
                            "name"
                        ),

                    "MJ":
                        team.get(
                            "playedGames"
                        ),

                    "V":
                        team.get(
                            "won"
                        ),

                    "N":
                        team.get(
                            "draw"
                        ),

                    "D":
                        team.get(
                            "lost"
                        ),

                    "BP":
                        team.get(
                            "goalsFor"
                        ),

                    "BC":
                        team.get(
                            "goalsAgainst"
                        ),

                    "Diff":
                        team.get(
                            "goalDifference"
                        ),

                    "Pts":
                        team.get(
                            "points"
                        )
                })

            df = pd.DataFrame(rows)

            if not df.empty:

                leader = df.iloc[0]

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "🥇 Leader",
                    leader["Équipe"]
                )

                c2.metric(
                    "⭐ Points",
                    leader["Pts"]
                )

                c3.metric(
                    "⚽ Différence",
                    leader["Diff"]
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                st.download_button(
                    "📥 Télécharger CSV",
                    df.to_csv(
                        index=False
                    ).encode("utf-8"),
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
            [
                "ALL",
                "SCHEDULED",
                "TIMED",
                "IN_PLAY",
                "PAUSED",
                "FINISHED",
                "POSTPONED",
                "CANCELED"
            ]
        )

    with col2:

        limit = st.slider(
            "Nombre de matchs",
            10,
            100,
            30
        )

    params = {
        "season": season
    }

    if status != "ALL":

        params["status"] = status

    data, error = api_request(
        f"/competitions/{competition_code}/matches",
        params
    )

    if error:

        show_api_error(error)

    else:

        matches = data.get(
            "matches",
            []
        )

        rows = []

        for match in matches[:limit]:

            score = match.get(
                "score",
                {}
            )

            full_time = score.get(
                "fullTime",
                {}
            )

            rows.append({

                "Date":
                    match.get(
                        "utcDate"
                    ),

                "Journée":
                    match.get(
                        "matchday"
                    ),

                "Domicile":
                    match.get(
                        "homeTeam",
                        {}
                    ).get(
                        "name"
                    ),

                "Extérieur":
                    match.get(
                        "awayTeam",
                        {}
                    ).get(
                        "name"
                    ),

                "Score":
                    f"{full_time.get('home', '-')}"
                    f" - "
                    f"{full_time.get('away', '-')}",

                "Statut":
                    match.get(
                        "status"
                    ),

                "ID":
                    match.get(
                        "id"
                    )
            })

        df = pd.DataFrame(rows)

        st.metric(
            "Matchs",
            len(df)
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        if not df.empty:

            st.download_button(
                "📥 Exporter CSV",
                df.to_csv(
                    index=False
                ).encode("utf-8"),
                "matches.csv",
                "text/csv"
            )


# ============================================================
# EQUIPES
# ============================================================

elif page == "⚽ Équipes":

    st.header("⚽ Équipes")

    data, error = api_request(
        f"/competitions/{competition_code}/teams",
        {
            "season": season
        }
    )

    if error:

        show_api_error(error)

    else:

        teams = data.get(
            "teams",
            []
        )

        st.metric(
            "Nombre d'équipes",
            len(teams)
        )

        search = st.text_input(
            "🔎 Rechercher une équipe"
        )

        if search:

            teams = [
                t for t in teams
                if search.lower()
                in t.get(
                    "name",
                    ""
                ).lower()
            ]

        cols = st.columns(4)

        for i, team in enumerate(teams):

            with cols[i % 4]:

                crest = team.get(
                    "crest"
                )

                if crest:

                    try:

                        st.image(
                            crest,
                            width=80
                        )

                    except Exception:

                        pass

                st.subheader(
                    team.get(
                        "shortName"
                    )
                    or team.get(
                        "name",
                        "-"
                    )
                )

                st.caption(
                    team.get(
                        "name",
                        "-"
                    )
                )

                st.write(
                    f"🏟️ {team.get('venue', '-')}"
                )

                st.write(
                    f"TLA : {team.get('tla', '-')}"
                )

                st.divider()


# ============================================================
# BUTEURS
# ============================================================

elif page == "🥅 Buteurs":

    st.header("🥅 Meilleurs buteurs")

    limit = st.slider(
        "Nombre de joueurs",
        5,
        50,
        20
    )

    data, error = api_request(
        f"/competitions/{competition_code}/scorers",
        {
            "season": season,
            "limit": limit
        }
    )

    if error:

        show_api_error(error)

        st.info(
            "Cet endpoint peut nécessiter "
            "un niveau d'accès supérieur selon ton abonnement."
        )

    else:

        scorers = data.get(
            "scorers",
            []
        )

        rows = []

        for i, scorer in enumerate(
            scorers,
            1
        ):

            player = scorer.get(
                "player",
                {}
            )

            team = scorer.get(
                "team",
                {}
            )

            rows.append({

                "Pos":
                    i,

                "Joueur":
                    player.get(
                        "name"
                    ),

                "Équipe":
                    team.get(
                        "name"
                    ),

                "Buts":
                    scorer.get(
                        "goals",
                        0
                    ),

                "Passes":
                    scorer.get(
                        "assists",
                        0
                    ),

                "Matchs":
                    scorer.get(
                        "playedMatches",
                        0
                    )
            })

        df = pd.DataFrame(rows)

        if not df.empty:

            leader = df.iloc[0]

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "🥇 Leader",
                leader["Joueur"]
            )

            c2.metric(
                "⚽ Buts",
                leader["Buts"]
            )

            c3.metric(
                "🎯 Passes",
                leader["Passes"]
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# ANALYSE
# ============================================================

elif page == "📈 Analyse":

    st.header("📈 Analyse statistique")

    data, error = api_request(
        f"/competitions/{competition_code}/matches",
        {
            "season": season
        }
    )

    if error:

        show_api_error(error)

    else:

        matches = data.get(
            "matches",
            []
        )

        rows = []

        for match in matches:

            score = match.get(
                "score",
                {}
            )

            full_time = score.get(
                "fullTime",
                {}
            )

            home = full_time.get(
                "home"
            )

            away = full_time.get(
                "away"
            )

            if (
                home is not None
                and away is not None
            ):

                rows.append({

                    "Domicile":
                        match.get(
                            "homeTeam",
                            {}
                        ).get(
                            "name"
                        ),

                    "Extérieur":
                        match.get(
                            "awayTeam",
                            {}
                        ).get(
                            "name"
                        ),

                    "HomeGoals":
                        home,

                    "AwayGoals":
                        away
                })

        df = pd.DataFrame(rows)

        if df.empty:

            st.info(
                "Pas encore assez de matchs terminés."
            )

        else:

            df["TotalGoals"] = (
                df["HomeGoals"]
                + df["AwayGoals"]
            )

            total_matches = len(df)

            total_goals = df[
                "TotalGoals"
            ].sum()

            avg_goals = df[
                "TotalGoals"
            ].mean()

            home_wins = (
                df["HomeGoals"]
                > df["AwayGoals"]
            ).sum()

            draws = (
                df["HomeGoals"]
                == df["AwayGoals"]
            ).sum()

            away_wins = (
                df["HomeGoals"]
                < df["AwayGoals"]
            ).sum()

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Matchs analysés",
                total_matches
            )

            c2.metric(
                "Buts",
                int(total_goals)
            )

            c3.metric(
                "Moyenne buts",
                f"{avg_goals:.2f}"
            )

            c4.metric(
                "Victoire domicile",
                int(home_wins)
            )

            st.divider()

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "🏠 Victoires domicile",
                int(home_wins)
            )

            c2.metric(
                "🤝 Matchs nuls",
                int(draws)
            )

            c3.metric(
                "✈️ Victoires extérieur",
                int(away_wins)
            )

            st.subheader(
                "⚽ Distribution des buts"
            )

            st.bar_chart(
                df[
                    "TotalGoals"
                ].value_counts()
                .sort_index()
            )

            st.subheader(
                "📊 Résultats"
            )

            result_data = pd.DataFrame({

                "Résultat": [
                    "Domicile",
                    "Nul",
                    "Extérieur"
                ],

                "Nombre": [
                    home_wins,
                    draws,
                    away_wins
                ]
            })

            st.bar_chart(
                result_data.set_index(
                    "Résultat"
                )
            )


# ============================================================
# COMPARAISON
# ============================================================

elif page == "⚔️ Comparaison":

    st.header(
        "⚔️ Comparaison de deux équipes"
    )

    data, error = api_request(
        f"/competitions/{competition_code}/teams",
        {
            "season": season
        }
    )

    if error:

        show_api_error(error)

    else:

        teams = data.get(
            "teams",
            []
        )

        team_names = [
            t.get(
                "name"
            )
            for t in teams
        ]

        if len(team_names) >= 2:

            col1, col2 = st.columns(2)

            with col1:

                team_a = st.selectbox(
                    "Équipe A",
                    team_names,
                    index=0
                )

            with col2:

                team_b = st.selectbox(
                    "Équipe B",
                    team_names,
                    index=1
                )

            if team_a == team_b:

                st.warning(
                    "Choisis deux équipes différentes."
                )

            else:

                standings_data, error = api_request(
                    f"/competitions/{competition_code}/standings",
                    {
                        "season": season
                    }
                )

                if standings_data:

                    table = standings_data.get(
                        "standings",
                        []
                    )

                    if table:

                        rows = table[0].get(
                            "table",
                            []
                        )

                        team_a_data = next(
                            (
                                x for x in rows
                                if x.get(
                                    "team",
                                    {}
                                ).get(
                                    "name"
                                ) == team_a
                            ),
                            None
                        )

                        team_b_data = next(
                            (
                                x for x in rows
                                if x.get(
                                    "team",
                                    {}
                                ).get(
                                    "name"
                                ) == team_b
                            ),
                            None
                        )

                        if (
                            team_a_data
                            and team_b_data
                        ):

                            comparison = pd.DataFrame({

                                team_a: [

                                    team_a_data.get(
                                        "position"
                                    ),

                                    team_a_data.get(
                                        "playedGames"
                                    ),

                                    team_a_data.get(
                                        "won"
                                    ),

                                    team_a_data.get(
                                        "draw"
                                    ),

                                    team_a_data.get(
                                        "lost"
                                    ),

                                    team_a_data.get(
                                        "goalsFor"
                                    ),

                                    team_a_data.get(
                                        "goalsAgainst"
                                    ),

                                    team_a_data.get(
                                        "goalDifference"
                                    ),

                                    team_a_data.get(
                                        "points"
                                    )
                                ],

                                team_b: [

                                    team_b_data.get(
                                        "position"
                                    ),

                                    team_b_data.get(
                                        "playedGames"
                                    ),

                                    team_b_data.get(
                                        "won"
                                    ),

                                    team_b_data.get(
                                        "draw"
                                    ),

                                    team_b_data.get(
                                        "lost"
                                    ),

                                    team_b_data.get(
                                        "goalsFor"
                                    ),

                                    team_b_data.get(
                                        "goalsAgainst"
                                    ),

                                    team_b_data.get(
                                        "goalDifference"
                                    ),

                                    team_b_data.get(
                                        "points"
                                    )
                                ]
                            }, index=[

                                "Position",
                                "Matchs",
                                "Victoires",
                                "Nuls",
                                "Défaites",
                                "Buts marqués",
                                "Buts encaissés",
                                "Différence",
                                "Points"
                            ])

                            st.dataframe(
                                comparison,
                                use_container_width=True
                            )


# ============================================================
# MATCH DETAILS
# ============================================================

elif page == "🔎 Match":

    st.header(
        "🔎 Recherche d'un match"
    )

    match_id = st.number_input(
        "ID du match",
        min_value=1,
        value=1,
        step=1
    )

    if st.button(
        "🔍 Rechercher",
        type="primary"
    ):

        with st.spinner(
            "Recherche..."
        ):

            data, error = api_request(
                f"/matches/{int(match_id)}"
            )

        if error:

            show_api_error(error)

        else:

            home = data.get(
                "homeTeam",
                {}
            )

            away = data.get(
                "awayTeam",
                {}
            )

            score = data.get(
                "score",
                {}
            )

            full_time = score.get(
                "fullTime",
                {}
            )

            c1, c2, c3 = st.columns(
                [2, 1, 2]
            )

            with c1:

                if home.get("crest"):

                    try:

                        st.image(
                            home["crest"],
                            width=100
                        )

                    except Exception:

                        pass

                st.subheader(
                    home.get(
                        "name",
                        "-"
                    )
                )

            with c2:

                st.markdown(
                    "<h1 style='text-align:center'>VS</h1>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <h2 style='text-align:center'>
                    {full_time.get('home', '-')}
                    -
                    {full_time.get('away', '-')}
                    </h2>
                    """,
                    unsafe_allow_html=True
                )

            with c3:

                if away.get("crest"):

                    try:

                        st.image(
                            away["crest"],
                            width=100
                        )

                    except Exception:

                        pass

                st.subheader(
                    away.get(
                        "name",
                        "-"
                    )
                )

            st.divider()

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Statut",
                data.get(
                    "status",
                    "-"
                )
            )

            c2.metric(
                "Journée",
                data.get(
                    "matchday",
                    "-"
                )
            )

            c3.metric(
                "Compétition",
                data.get(
                    "competition",
                    {}
                ).get(
                    "name",
                    "-"
                )
            )

            st.divider()

            with st.expander(
                "📦 Données API complètes"
            ):

                st.json(data)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "⚽ Football Analytics | "
    "Python + Streamlit + football-data.org"
)