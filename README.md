# ⚽ Football Match Predictor — Azure AI Foundry

> Predicción de partidos de fútbol usando Machine Learning desplegado en Azure AI Foundry

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Azure](https://img.shields.io/badge/Azure-AI%20Foundry-0078D4?logo=microsoftazure)](https://azure.microsoft.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Descripción

Aplicación full-stack que predice el resultado de un partido de fútbol entre dos equipos seleccionados. El corazón del sistema es un modelo **XGBoost** entrenado con datos históricos de partidos, desplegado como un **Managed Online Endpoint en Azure AI Foundry (Azure ML)**.

La predicción devuelve probabilidades para cuatro resultados:
- **⚽Goles de cada equipo (Local y Visitante)**
- **Victoria equipo local**
- **Empate**
- **Victoria equipo visitante**

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                      │
│         Selección de equipos → Visualización resultados     │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP REST
┌───────────────────────▼─────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│     Lógica de negocio + Feature Engineering                 │
└───────────────────────┬─────────────────────────────────────┘
                        │ Azure ML SDK / REST
┌───────────────────────▼─────────────────────────────────────┐
│              AZURE AI FOUNDRY                                │
│   ┌─────────────────────────────────────────────────────┐   │
│   │   Managed Online Endpoint (XGBoost Model)           │   │
│   │   Input: features del partido                       │   │
│   │   Output: [P(local_win), P(draw), P(away_win)]     │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                  DATOS HISTÓRICOS                            │
│   football-data.org API — Ligas europeas (2015–2024)        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Modelo de Machine Learning

### Features utilizadas
| Feature | Descripción |
|---------|------------|
| `home_elo` | Rating ELO del equipo local |
| `away_elo` | Rating ELO del equipo visitante |
| `elo_diff` | Diferencia de ELO (home - away) |
| `home_form_pts` | Puntos últimos 5 partidos (local) |
| `away_form_pts` | Puntos últimos 5 partidos (visitante) |
| `home_goals_avg` | Media de goles marcados (local, últimas 10 jornadas) |
| `away_goals_avg` | Media de goles marcados (visitante) |
| `home_goals_conceded_avg` | Media de goles encajados (local) |
| `away_goals_conceded_avg` | Media de goles encajados (visitante) |
| `h2h_home_wins` | Victorias head-to-head (local) |
| `h2h_draws` | Empates head-to-head |
| `h2h_away_wins` | Victorias head-to-head (visitante) |
| `home_advantage` | Factor cancha (siempre 1 para el local) |

### Algoritmo: XGBoost (Multiclass)
- **Target**: `result` ∈ {0=local_win, 1=draw, 2=away_win}
- **Métrica principal**: Log-Loss + Accuracy
- **Validación**: TimeSeriesSplit (respeta orden temporal de los datos)

---

## 🚀 Instalación y uso

### Pre-requisitos
- Python 3.11+
- Node.js 18+
- Cuenta de Azure con Azure ML Workspace
- API key de [football-data.org](https://www.football-data.org/) (gratuita)

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/football-predictor.git
cd football-predictor
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales de Azure y football-data.org
```

### 3. Recolectar datos y entrenar el modelo
```bash
cd model
pip install -r requirements.txt
python ../data/collect_data.py          # Descarga datos históricos
python train.py                          # Entrena y guarda el modelo
```

### 4. Desplegar en Azure AI Foundry
```bash
python deploy_azure.py                   # Crea endpoint y despliega modelo
```

### 5. Lanzar el backend
```bash
cd ../backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 6. Lanzar el frontend
```bash
cd ../frontend
npm install
npm run dev
```

Accede a `http://localhost:5173` 🎉

---

## 📁 Estructura del proyecto

```
football-predictor/
├── README.md
├── .env.example
├── docker-compose.yml
│
├── data/
│   └── collect_data.py         # Descarga datos de football-data.org
│
├── model/
│   ├── train.py                # Entrenamiento del modelo XGBoost
│   ├── features.py             # Feature engineering (ELO, form, h2h)
│   ├── deploy_azure.py         # Despliegue en Azure AI Foundry
│   ├── score.py                # Script de inferencia (Azure ML)
│   └── requirements.txt
│
├── backend/
│   ├── main.py                 # FastAPI app (endpoints REST)
│   ├── predictor.py            # Cliente del endpoint Azure ML
│   ├── team_data.py            # Catálogo de equipos y stats
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
│           ├── PredictionResult.jsx
│           └── MatchCard.jsx
│
└── .github/
    └── workflows/
        └── deploy.yml          # CI/CD con GitHub Actions
```

---

## 🔌 API Reference

### `POST /api/predict`
Predice el resultado de un partido.

**Request:**
```json
{
  "home_team": "Real Madrid",
  "away_team": "FC Barcelona"
}
```

**Response:**
```json
{
  "home_team": "Real Madrid",
  "away_team": "FC Barcelona",
  "predictions": {
    "home_win": 0.48,
    "draw": 0.24,
    "away_win": 0.28
  },
  "model_version": "xgboost-v1.2",
  "confidence": "HIGH"
}
```

### `GET /api/teams`
Devuelve la lista de equipos disponibles.

---

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| **Frontend** | React 18, Vite, Tailwind CSS |
| **Backend** | Python, FastAPI, Uvicorn |
| **ML** | XGBoost, Scikit-learn, Pandas |
| **Cloud** | Azure AI Foundry (Azure ML), Azure Container Registry |
| **Datos** | football-data.org REST API |
| **DevOps** | Docker, GitHub Actions |

---

## 📊 Resultados del modelo

| Métrica | Valor |
|---------|-------|
| Accuracy | ~58% |
| Log-Loss | ~0.98 |
| F1-Score (macro) | ~0.54 |

> ℹ️ Predecir fútbol es inherentemente difícil. La literatura científica sitúa el techo humano experto en torno al 60–65% de accuracy en partidos individuales.

---

## 👥 Autor

**[Tu Nombre]** — Alumno de Master IA + Big Data en Tajamar (Microsoft Partner)

- 🌐 LinkedIn: [linkedin.com/in/tu-perfil](https://linkedin.com)
- 💻 GitHub: [@tu-usuario](https://github.com)

---

## 📄 Licencia

MIT © 2025
