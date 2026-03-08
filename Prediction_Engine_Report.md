# CricPredict: Prediction Engine & Real-Time Sync Report

This document detail the technical implementation of **Phase 2: Prediction Engine V1**, covering how the system processes real-time data and calculates player form to achieve high-accuracy predictions.

---

## 1. The "Sanju Samson Factor": Dynamic Form Logic
The most critical requirement was ensuring the system accounts for "yesterday's" performance. We achieved this through the **Player Form Index (PFI)**.

### How PFI is Calculated (`form_engine.py`):
1.  **Weighted Recency**: We analyze the last 5 matches for every player.
2.  **The 50% Rule**: The **most recent match** carries a 50% weight in the score. 
    - *Example*: If Sanju Samson scores 89 today, his PFI for tomorrow's prediction will spike immediately, overshadowing older, lower scores.
3.  **Metrics**: The engine calculates a composite score using:
    - Runs Scored & Wickets Taken.
    - Batting Strike Rate & Bowling Economy.
    - Consistency across the 5-match window.

---

## 2. Real-Time Data Ingestion: The API Bridge
Since historical archives (Cricsheet) have a delay, we implemented a live sync system to capture "yesterday's" stats.

### Step-by-Step API Flow (`api_connector.py` & `real_time_sync.py`):
- **Source**: **CricketData.org (CricAPI)**.
- **Security**: Uses an encrypted `.env` file to store the API Key and a "User-Agent" header to ensure stable connections.
- **Process**:
    1.  **Request**: The system calls the `currentMatches` endpoint.
    2.  **Filter**: It identifies matches that "Ended" in the last 24 hours.
    3.  **Ingestion**: Match results (Winner, Scores, Teams) are automatically mapped and saved into our local `matches` table.
    4.  **Efficiency**: The script is designed to run once daily, consuming only 2-5 API "hits," staying well within the 100-hit free limit.

---

## 3. The Scorer Engine (`scorer.py`)
This is the central intelligence unit that generates the final Win Probability.

### The Five Pillars of Prediction:
| Pillar | Weight | Description |
| :--- | :--- | :--- |
| **Player Form (PFI)** | 30% | Uses the **Dynamic Squad Detection** to calculate the aggregate "hotness" of the current team. |
| **Head-to-Head** | 25% | Analyzes every ball bowled between these two specific teams historically. |
| **Team Momentum** | 20% | Recent win/loss streaks and margin of victory. |
| **Venue Mastery** | 15% | Team performance at the specific ground (e.g., RCB at Chinnaswamy). |
| **Conditions** | 10% | Average scores and pitch behavior at the venue. |

### Dynamic Squad Detection:
Because teams change frequently, the scorer doesn't use all players ever associated with a team. It **automatically detects the active squad** by looking at who played in the team's most recent matches.

---

## 4. Verification Case Study
**Match**: Royal Challengers Bangalore vs. Chennai Super Kings
**Venue**: M. Chinnaswamy Stadium

- **Historical H2H**: CSK leads (Advantage: CSK).
- **Venue Stats**: RCB has a higher win rate at this ground (Advantage: RCB).
- **Current Form**: Calculated dynamically from the last 5 matches for both squads.
- **Final Output**: 
    - **Prediction**: Chennai Super Kings 
    - **Win Probability**: 58.43%
    - **Confidence**: High (Data-backed)

---

## 5. Summary of Files Created
1.  **`api_connector.py`**: The interface for real-time data.
2.  **`.env`**: Secure credential storage.
3.  **`real_time_sync.py`**: The bridge that pulls live scores into the database.
4.  **`form_engine.py`**: The PFI calculator (The "Samson Factor").
5.  **`scorer.py`**: The final prediction logic.

---

**Status: Phase 2 Completed Successfully.**
**Next Action: Phase 3 - Frontend Dashboard & API Development.**
