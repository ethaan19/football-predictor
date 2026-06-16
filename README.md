**[Leer en español 🇪🇸](docs/README.md)**

# ⚽ Football Match Predictor — Azure AI Foundry

> Football match outcome prediction powered by GPT-4o-mini deployed on Azure AI Foundry


[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://python.org)
[![Azure](https://img.shields.io/badge/Azure-AI%20Foundry-0078D4?logo=microsoftazure)](https://azure.microsoft.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

### **APP:** https://football-predictor-hazel.vercel.app/

---

## 📌 Description

Full-stack application that predicts the outcome of a football match between two selected teams. The user picks a home and away team from the top 5 European leagues, and the system returns win probabilities for each possible outcome using **GPT-4o-mini** deployed as a managed endpoint on **Azure AI Foundry**.

The prediction returns probabilities for four outcomes:
- ⚽ **Goals from each team (Home and Away)**
- 🏆 **Home team victory**
- 🤝 **Draw**
- 🏆 **Away team victory**

Team statistics (dynamic ELO rating, recent form, goals average) are automatically computed from real match data fetched from the **football-data.org API**.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                        │
│          Team selection → Prediction visualization          │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP REST
┌───────────────────────▼─────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│          Business logic + Feature Engineering               │
└───────────────────────┬─────────────────────────────────────┘
                        │ Azure OpenAI REST API
┌───────────────────────▼─────────────────────────────────────┐
│                  AZURE AI FOUNDRY                            │
│   ┌─────────────────────────────────────────────────────┐   │
│   │         GPT-4o-mini Managed Endpoint                │   │
│   │   Input: team stats + match context                 │   │
│   │   Output: { home_win, draw, away_win }              │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    MATCH DATA                                │
│   football-data.org API — Top 5 European leagues            │
│   110 teams · 3,500+ matches · Seasons 2024–2026            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 How It Works

### Team Features
Each team is profiled with the following stats, computed from real historical match data:

| Feature | Description |
|---------|-------------|
| `elo` | Dynamic ELO rating (updated after every match) |
| `form_pts` | Average points per game — last 10 matches |
| `form_gd` | Average goal difference — last 10 matches |
| `goals_avg` | Average goals scored — last 10 matches |
| `conceded_avg` | Average goals conceded — last 10 matches |

### AI Model: GPT-4o-mini on Azure AI Foundry
The backend sends a structured prompt with both teams' stats to the GPT-4o-mini endpoint. The model acts as a football analyst and returns a JSON with the three outcome probabilities.

```
Team stats → Prompt engineering → Azure AI Foundry (GPT-4o-mini) → Probabilities
```

---

## 🚀 Installation & Usage

### Prerequisites
- Python 3.13+
- Node.js 18+
- Azure account with an Azure AI Foundry resource
- Free API key from [football-data.org](https://www.football-data.org/)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/football-predictor.git
cd football-predictor
```

### 2. Set up environment variables
Create a `.env` file in the root folder:
```
FOOTBALL_DATA_API_KEY=your_api_key

AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_api_key
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

CORS_ORIGINS=http://localhost:5173
```

### 3. Fetch match data & generate team stats
```bash
python data/collect_data.py       # Downloads current season matches
python data/generate_teams.py     # Computes team stats → teams.json
```

### 4. Launch the backend
```bash
cd backend
py -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 5. Launch the frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` 🎉

---

## 📁 Project Structure

```
football-predictor/
├── README.md
├── .env.example
├── docker-compose.yml
│
├── data/
│   ├── collect_data.py       # Fetches matches from football-data.org
│   └── generate_teams.py     # Computes ELO + stats → teams.json
│
├── backend/
│   ├── main.py               # FastAPI app (REST endpoints)
│   ├── predictor.py          # Azure AI Foundry client (GPT-4o-mini)
│   ├── team_data.py          # Loads team catalog from teams.json
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── components/
│           ├── TeamSelector.jsx
│           ├── TeamCrest.jsx
│           ├── LeagueFilter.jsx
│           ├── MatchCard.jsx
│           ├── PredictionResult.jsx
│           └── LoadingOverlay.jsx
│
└── .github/
    └── workflows/
        └── ci.yml            # GitHub Actions CI
```

---

## 🔌 API Reference

### `POST /api/predict`
Predicts the outcome of a match between two teams.

**Request:**
```json
{
  "home_team": "Real Madrid CF",
  "away_team": "FC Barcelona"
}
```

**Response:**
```json
{
  "home_team": "Real Madrid CF",
  "away_team": "FC Barcelona",
  "home_win": 0.48,
  "draw": 0.24,
  "away_win": 0.28,
  "confidence": "MEDIA",
  "model_version": "gpt-4o-mini (Azure AI Foundry)"
}
```

### `GET /api/teams`
Returns the full list of available teams with their league.

### `GET /api/leagues`
Returns all available leagues with their teams.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, Custom CSS |
| **Backend** | Python 3.13, FastAPI, Uvicorn |
| **AI** | GPT-4o-mini on Azure AI Foundry |
| **Data** | football-data.org REST API |
| **Data Processing** | Pandas, NumPy (ELO + form stats) |
| **DevOps** | Docker, GitHub Actions |

---

## 👤 Author

**Ethan Macias**

- 🌐 LinkedIn: [https://www.linkedin.com/in/ethan-macias-termenon-b99a79338/?lipi=urn%3Ali%3Apage%3Ad_flagship3_feed%3BHyTNUHDhTkWj4qNTEeU%2BOg%3D%3D](https://linkedin.com)
- 💻 GitHub: [@ethaan19](https://github.com)
