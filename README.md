# ⚽ Football Analytics Dashboard

Application web de visualisation et d'analyse de données footballistiques développée avec **Python**, **Streamlit**, **Pandas** et l'API **football-data.org**.

L'objectif du projet est de fournir une interface simple et professionnelle permettant d'explorer les compétitions, les classements, les matchs, les équipes et les statistiques des joueurs.

---

## 📌 Fonctionnalités

### 📊 Dashboard

Le dashboard fournit une vue globale de la compétition sélectionnée :

* Nombre de matchs
* Matchs terminés
* Matchs à venir
* Leader du championnat
* Points du leader
* Différence de buts
* Classement Top 10
* Prochains matchs
* Informations sur la saison

---

### 🏆 Classement

Affichage du classement de la compétition :

* Position
* Équipe
* Matchs joués
* Victoires
* Matchs nuls
* Défaites
* Buts marqués
* Buts encaissés
* Différence de buts
* Points

Possibilité d'exporter le classement au format CSV.

---

### 📅 Matchs

Consultation des matchs d'une compétition avec filtrage par statut :

* Tous
* Scheduled
* Timed
* In Play
* Paused
* Finished
* Postponed
* Canceled

Pour chaque match :

* Date
* Journée
* Équipe domicile
* Équipe extérieure
* Score
* Statut
* ID du match

Les données peuvent être exportées au format CSV.

---

### ⚽ Équipes

Affichage des équipes de la compétition avec :

* Logo
* Nom
* Nom court
* TLA
* Stade

Une recherche permet également de filtrer rapidement les équipes.

---

### 🥅 Meilleurs buteurs

Affichage des meilleurs buteurs disponibles via l'API :

* Position
* Joueur
* Équipe
* Nombre de buts
* Passes décisives
* Matchs joués

---

### 📈 Analyse statistique

Le module d'analyse permet d'étudier les matchs terminés et de calculer :

* Nombre de matchs analysés
* Nombre total de buts
* Moyenne de buts par match
* Victoires à domicile
* Matchs nuls
* Victoires à l'extérieur
* Distribution des buts
* Répartition des résultats

Cette partie constitue la base du futur module de **Data Analytics et Machine Learning**.

---

### ⚔️ Comparaison des équipes

Possibilité de sélectionner deux équipes et de comparer :

* Position
* Matchs joués
* Victoires
* Matchs nuls
* Défaites
* Buts marqués
* Buts encaissés
* Différence de buts
* Points

---

### 🔎 Recherche d'un match

Recherche d'un match à partir de son ID.

Les informations affichées comprennent :

* Équipe domicile
* Équipe extérieure
* Logos
* Score
* Statut
* Journée
* Compétition
* Données complètes retournées par l'API

---

## 🏟️ Compétitions disponibles

L'application prend actuellement en charge plusieurs compétitions :

| Compétition      | Code |
| ---------------- | ---- |
| Premier League   | PL   |
| La Liga          | PD   |
| Bundesliga       | BL1  |
| Serie A          | SA   |
| Ligue 1          | FL1  |
| Champions League | CL   |
| Eredivisie       | DED  |
| Primeira Liga    | PPL  |

La disponibilité exacte des données dépend du niveau d'accès de l'API utilisé.

---

## 🛠️ Technologies

### Backend / Data

* Python
* Requests
* Pandas

### Frontend

* Streamlit
* HTML/CSS

### API

* football-data.org API v4

### Environnement

* Python 3
* pip

---

## 📂 Structure du projet

```text
football_analytics/
│
├── app.py
├── requirements.txt
├── README.md
│
└── .streamlit/
    └── secrets.toml
```

---

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/USERNAME/football-analytics.git
```

Entrer dans le projet :

```bash
cd football-analytics
```

---

### 2. Créer un environnement virtuel

Windows :

```bash
python -m venv venv
```

Activer l'environnement :

```bash
venv\Scripts\activate
```

Linux / macOS :

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 🔑 Configuration de l'API

L'application utilise un token `football-data.org`.

Créer le dossier :

```text
.streamlit
```

Puis créer :

```text
.streamlit/secrets.toml
```

Ajouter :

```toml
FOOTBALL_API_TOKEN = "TON_TOKEN_ICI"
```

Dans `app.py`, le token est récupéré avec :

```python
API_TOKEN = st.secrets.get(
    "FOOTBALL_API_TOKEN",
    ""
)
```

---

## 🔒 Sécurité

Le fichier `secrets.toml` contient une information sensible.

Il ne doit **jamais être envoyé sur GitHub**.

Ajouter dans `.gitignore` :

```gitignore
.streamlit/secrets.toml
venv/
__pycache__/
*.pyc
```

Si un token est accidentellement publié, il faut le révoquer et en générer un nouveau.

---

## ▶️ Lancer l'application

Après l'installation :

```bash
streamlit run app.py
```

L'application sera accessible localement à :

```text
http://localhost:8501
```

---

## 🔌 Tester la connexion API

Dans la barre latérale :

1. Sélectionner une compétition.
2. Sélectionner la saison.
3. Cliquer sur **Tester la connexion**.
4. Vérifier que l'API retourne :

```text
🟢 API connectée
```

En cas de problème, l'application affiche automatiquement les erreurs principales :

* Token manquant
* Token invalide
* Accès refusé
* Ressource inexistante
* Limite de requêtes
* Timeout
* Erreur réseau

---

## ⚡ Cache des données

L'application utilise le cache Streamlit :

```python
@st.cache_data(
    ttl=300,
    show_spinner=False
)
```

Les données API sont donc conservées temporairement afin d'éviter des requêtes inutiles.

Cela permet notamment de :

* réduire le nombre de requêtes API ;
* améliorer les performances ;
* limiter les risques d'atteindre rapidement la limite de requêtes.

---

## 📊 Architecture fonctionnelle

```text
                    ┌──────────────────────┐
                    │  football-data.org   │
                    │       API v4         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     API Client       │
                    │      Requests        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Pandas          │
                    │ Transformation Data  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Streamlit       │
                    │     Dashboard        │
                    └──────────────────────┘
```

---

# 🤖 Roadmap

Le projet est conçu pour évoluer vers une véritable plateforme de **Football Data Analytics**.

### Version actuelle

* [x] Dashboard
* [x] Classement
* [x] Matchs
* [x] Équipes
* [x] Buteurs
* [x] Analyse statistique
* [x] Comparaison des équipes
* [x] Recherche de match
* [x] Export CSV
* [x] Cache API
* [x] Gestion des erreurs

### Prochaines fonctionnalités

#### 📈 Data Analytics

* [ ] Forme des équipes sur les 5 derniers matchs
* [ ] Statistiques domicile / extérieur
* [ ] Moyenne de buts
* [ ] Over 1.5
* [ ] Over 2.5
* [ ] Over 3.5
* [ ] BTTS
* [ ] Clean sheets
* [ ] Analyse offensive
* [ ] Analyse défensive
* [ ] Historique des confrontations

#### 🤖 Machine Learning

* [ ] Dataset historique
* [ ] Feature engineering
* [ ] Modèle de prédiction
* [ ] Prédiction 1X2
* [ ] Probabilité victoire domicile
* [ ] Probabilité match nul
* [ ] Probabilité victoire extérieur
* [ ] Prédiction Over/Under
* [ ] Prédiction BTTS
* [ ] Score probable

#### 📊 Visualisation

* [ ] Graphiques interactifs
* [ ] Évolution du classement
* [ ] Performance des équipes
* [ ] Graphiques des buts
* [ ] Radar des équipes

#### 🌐 Application

* [ ] Responsive UI
* [ ] Page d'accueil améliorée
* [ ] Système de favoris
* [ ] Recherche avancée
* [ ] Notifications
* [ ] Déploiement cloud

---

## 🧠 Objectif final

L'objectif à terme est de transformer ce dashboard en une plateforme complète de **Football Analytics & Prediction** permettant de :

```text
Données historiques
       │
       ▼
Data Cleaning
       │
       ▼
Feature Engineering
       │
       ▼
Machine Learning
       │
       ▼
Prédictions
       │
       ▼
Dashboard
       │
       ├── 1X2
       ├── Score probable
       ├── Over/Under
       ├── BTTS
       └── Analyse équipe
```

Le projet pourra ensuite évoluer vers une architecture plus complète avec :

* Python
* Pandas
* Scikit-learn
* XGBoost
* FastAPI
* PostgreSQL
* Docker
* Streamlit

---

## ⚠️ Limites

Les données disponibles dépendent de l'API `football-data.org` et du niveau d'accès du compte.

Certaines fonctionnalités peuvent être limitées selon le plan API utilisé, notamment certains endpoints ou certaines compétitions.

L'application doit également respecter les limites de requêtes de l'API.

---

## 📜 Licence

Projet développé à des fins éducatives, d'analyse de données et de démonstration.

Les données footballistiques sont fournies par **football-data.org**.

---

## 👨‍💻 Auteur

**Abdelhakim TELMOUDY**

Projet : **Football Analytics Dashboard**

Technologies :

```text
Python
Streamlit
Pandas
Requests
REST API
Data Analytics
Machine Learning
```
