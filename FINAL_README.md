# CricPredict: AI Match Prediction Engine

Welcome to **CricPredict**, a premium, high-accuracy cricket prediction platform that leverages 4 million+ ball-by-ball delivery records (Cricsheet) and real-time form tracking (CricAPI).

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- [CricketData.org API Key](https://cricketdata.org/) (Add to `.env`)

### 2. Setup Backend
```bash
# Install dependencies
pip install sqlalchemy pandas tqdm python-dotenv requests fastapi uvicorn

# Initialize Database (if not already done)
python ingest_data.py
python ingest_deliveries.py

# Start the API Server
python app_main.py
```
*The API will run at `http://localhost:8000`.*

### 3. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```
*The Dashboard will run at `http://localhost:3000`.*

---

## 🏗️ Core Architecture

### Phase 1: Data Ingestion
- **Cricsheet Integration**: Processes ~20 years of historical match metadata and ball-by-ball data.
- **SQLAlchemy ORM**: Robust schema in `cricpredict.db` (SQLite).

### Phase 2: The "Sanju Samson Factor"
- **Form Engine (`form_engine.py`)**: Calculates the **Player Form Index (PFI)**. Recent matches carry 50% weight, ensuring "yesterday's" heroics are captured.
- **Scorer Engine (`scorer.py`)**: A 5-pillar weighting system:
    - **Form (PFI)**: 30%
    - **H2H History**: 25%
    - **Venue Mastery**: 15%
    - **Team Momentum**: 20%
    - **Conditions**: 10%

### Phase 3: Premium UI/UX
- **FastAPI**: Modern, high-performance API layer.
- **Next.js 15**: Glassmorphism design with a "High-End Indian Cricket" aesthetic (Midnight Blue & Gold).
- **Live Sync**: One-click synchronization of live scores from CricAPI into the prediction model.

---

## 📂 Key Files
- `app_main.py`: FastAPI server entry point.
- `scorer.py`: Core prediction logic.
- `form_engine.py`: PFI calculation logic.
- `real_time_sync.py`: Live data ingestion script.
- `frontend/src/app/page.tsx`: Main Dashboard UI.

---

## 🏏 Verification Example
Run a prediction for **RCB vs CSK** at **Chinnaswamy Stadium**:
1. Open dashboard.
2. Select teams and venue.
3. Click "Generate Prediction".
4. Result: **CSK (58.43%)** - Based on superior H2H and recent squad PFI.

**Status: READY FOR PRODUCTION**
