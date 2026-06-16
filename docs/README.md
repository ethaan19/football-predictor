🌐 **[English Version](../README.md)**

# ⚽ Predicción de Partidos de Fútbol — Azure AI Foundry

> Predicción de resultados de partidos de fútbol potenciada por GPT-4o-mini desplegado en Azure AI Foundry

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://python.org)
[![Azure](https://img.shields.io/badge/Azure-AI%20Foundry-0078D4?logo=microsoftazure)](https://azure.microsoft.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

### **APP:** https://football-predictor-hazel.vercel.app/

---

## 📌 Descripción

Aplicación full-stack que predice el resultado de un partido de fútbol entre dos equipos seleccionados. El usuario elige un equipo local y uno visitante de las 5 principales ligas europeas, y el sistema devuelve las probabilidades de victoria para cada resultado posible utilizando **GPT-4o-mini** desplegado como un endpoint administrado en **Azure AI Foundry**.

La predicción devuelve probabilidades para cuatro resultados:
- ⚽ **Goles de cada equipo (Local y Visitante)**
- 🏆 **Victoria del equipo local**
- 🤝 **Empate**
- 🏆 **Victoria del equipo visitante**

Las estadísticas de los equipos (clasificación ELO dinámica, racha reciente, promedio de goles) se calculan automáticamente a partir de datos reales de partidos obtenidos de la **API football-data.org**.

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                        │
│          Selección de equipos → Visualización de predicción │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP REST
┌───────────────────────▼─────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│          Lógica de negocio + Ingeniería de características  │
└───────────────────────┬─────────────────────────────────────┘
                        │ Azure OpenAI REST API
┌───────────────────────▼─────────────────────────────────────┐
│                  AZURE AI FOUNDRY                            │
│   ┌─────────────────────────────────────────────────────┐   │
│   │         Endpoint Administrado GPT-4o-mini           │   │
│   │   Entrada: estadísticas de equipo + contexto partido │   │
│   │   Salida: { home_win, draw, away_win }              │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    DATOS DE PARTIDOS                        │
│   API football-data.org — 5 principales ligas europeas      │
│   110 equipos · 3,500+ partidos · Temporadas 2024–2026      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Cómo funciona

### Características de los Equipos
Cada equipo se perfila con las siguientes estadísticas, calculadas a partir de datos históricos reales de partidos:

| Característica | Descripción |
|----------------|-------------|
| `elo` | Clasificación ELO dinámica (actualizada después de cada partido) |
| `form_pts` | Promedio de puntos por partido — últimos 10 partidos |
| `form_gd` | Promedio de diferencia de goles — últimos 10 partidos |
| `goals_avg` | Promedio de goles anotados — últimos 10 partidos |
| `conceded_avg` | Promedio de goles concedidos — últimos 10 partidos |

### Modelo de IA: GPT-4o-mini en Azure AI Foundry
El backend envía un prompt estructurado con las estadísticas de ambos equipos al endpoint GPT-4o-mini. El modelo actúa como analista de fútbol y devuelve un JSON con las tres probabilidades de resultado.

```
Estadísticas equipo → Ingeniería de prompts → Azure AI Foundry (GPT-4o-mini) → Probabilidades
```

---

## 🚀 Instalación y Uso

### Requisitos previos
- Python 3.13+
- Node.js 18+
- Cuenta de Azure con un recurso de Azure AI Foundry
- Clave de API gratuita de [football-data.org](https://www.football-data.org/)

### 1. Clonar el repositorio
```bash
git clone https://github.com/YOUR_USERNAME/football-predictor.git
cd football-predictor
```

### 2. Configurar variables de entorno
Crea un archivo `.env` en la carpeta raíz:
```
FOOTBALL_DATA_API_KEY=your_api_key

AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_api_key
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

CORS_ORIGINS=http://localhost:5173
```

### 3. Obtener datos de partidos y generar estadísticas de equipos
```bash
python data/collect_data.py       # Descarga partidos de la temporada actual
python data/generate_teams.py     # Calcula estadísticas de equipos → teams.json
```

### 4. Iniciar el backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 5. Iniciar el frontend
```bash
cd frontend
npm install
npm run dev
```

Abre `http://localhost:5173` 🎉

---

## 📁 Estructura del Proyecto

```
football-predictor/
├── README.md
├── .env.example
├── docker-compose.yml
│
├── data/
│   ├── collect_data.py       # Obtiene partidos de football-data.org
│   └── generate_teams.py     # Calcula ELO + estadísticas de racha → teams.json
│
├── backend/
│   ├── main.py               # Aplicación FastAPI (endpoints REST)
│   ├── predictor.py          # Cliente de Azure AI Foundry (GPT-4o-mini)
│   ├── team_data.py          # Carga el catálogo de equipos de teams.json
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
        └── ci.yml            # CI de GitHub Actions
```

---

## 🔌 Referencia de la API

### `POST /api/predict`
Predice el resultado de un partido entre dos equipos.

**Petición:**
```json
{
  "home_team": "Real Madrid CF",
  "away_team": "FC Barcelona"
}
```

**Respuesta:**
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
Devuelve la lista completa de equipos disponibles con su liga.

### `GET /api/leagues`
Devuelve todas las ligas disponibles con sus equipos.

---

## 🛠️ Tecnologías utilizadas

| Capa | Tecnología |
|-------|-----------|
| **Frontend** | React 18, Vite, CSS Personalizado |
| **Backend** | Python 3.13, FastAPI, Uvicorn |
| **IA** | GPT-4o-mini en Azure AI Foundry |
| **Datos** | API REST football-data.org |
| **Procesamiento de Datos** | Pandas, NumPy (ELO + estadísticas de racha) |
| **DevOps** | Docker, GitHub Actions |

---

## 👤 Autor

**Ethan Macias**

- 🌐 LinkedIn: [https://www.linkedin.com/in/ethan-macias-termenon-b99a79338/?lipi=urn%3Ali%3Apage%3Ad_flagship3_feed%3BHyTNUHDhTkWj4qNTEeU%2BOg%3D%3D](https://linkedin.com)
- 💻 GitHub: [@ethaan19](https://github.com)
