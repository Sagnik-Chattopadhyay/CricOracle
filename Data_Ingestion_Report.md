# CricPredict: Data Foundation & Ingestion Report

This document provides a detailed, A-to-Z technical overview of the completed **Phase 1: Data Foundation & Ingestion** for the CricPredict project.

---

## 1. Project Objective
The goal of this phase was to establish a high-performance, structured database populated with historical cricket data to serve as the training ground for the CricPredict AI engine.

## 2. Data Sources & Acquisition
The primary data source for this project is **Cricsheet**, which provides comprehensive ball-by-ball data in CSV format.

### Data Collected:
| Format | Matches | Source URL |
| :--- | :--- | :--- |
| **IPL** | 1,169 | https://cricsheet.org/downloads/ipl_csv2.zip |
| **T20I** | 3,196 | https://cricsheet.org/downloads/t20is_male_csv2.zip |
| **ODI** | 2,513 | https://cricsheet.org/downloads/odis_male_csv2.zip |
| **Tests** | 877 | https://cricsheet.org/downloads/tests_male_csv2.zip |

### Collection Method:
I developed `download_data.py` to automate the acquisition process. The script:
1.  Fetches ZIP files from Cricsheet.
2.  Extracts individual CSV files into format-specific directories (`data/IPL/`, `data/T20I/`, etc.).
3.  Implements "Skip if exists" logic to avoid redundant bandwidth usage.

---

## 3. Database Architecture
I implemented a relational database using **SQLite** (local fallback) and **PostgreSQL** (Supabase ready). The schema is managed via **SQLAlchemy ORM** in `models.py`.

### Core Tables:
1.  **`teams`**: Stores team names and unique identifiers.
2.  **`players`**: Stores player names and their global **Cricsheet Registry IDs** (ensuring no duplicates across different formats).
3.  **`venues`**: Ground names and cities.
4.  **`matches`**: High-level metadata (date, toss, winner, margin).
5.  **`deliveries`**: Individual ball-by-ball records (~4 million rows).

---

## 4. The Ingestion Pipeline (Step-by-Step)

### Step A: Metadata Ingestion (`ingest_data.py`)
This script processes the `_info.csv` files accompanying every match.
- **Challenge**: Cricsheet `_info` files have varying columns.
- **Solution**: Developed a custom line-by-line parser to robustly extract keys like `winner`, `toss_decision`, and `venue`.
- **Player Mapping**: It extracts the `registry` IDs for every player in the match, ensuring that "Virat Kohli" in an IPL match is correctly identified as the same person in an ODI match.

### Step B: Delivery Ingestion (`ingest_deliveries.py`)
This script handles the heavy lifting of processing millions of rows.
- **Optimization**: To handle the massive volume, I implemented:
    - **Global Caching**: Pre-loading all teams and players into memory to avoid 4 million individual DB lookups.
    - **Bulk Inserts**: Using `bulk_save_objects` to push data in chunks, significantly reducing I/O time.
- **Processing**: Converts raw ball numbers (e.g., `0.1`) into distinct `over` and `ball` integers for easier querying.

### Step C: Verification (`verify_data.py`)
A dedicated script was created to validate the ingestion.
- **Volume Checks**: Ensuring row counts match expectations.
- **Integrity Checks**: Verifying that FK relationships (Player -> Team -> Match) are correctly linked.

---

## 5. Final Statistics (A-to-Z Summary)
After running the full pipeline, the database currently holds:

*   **Total Matches**: 7,755
*   **Total Deliveries**: 4,025,616
*   **Unique Players**: 6,169
*   **Unique Teams**: 128
*   **Distinct Venues**: 314

### Sample Data Point Verified:
- **Match Date**: 2017-04-05 (IPL)
- **Batting**: Sunrisers Hyderabad
- **Ball 0.1**: T.S. Mills (RCB) to D.A. Warner (SRH) -> 0 runs.

---

## 7. Handling "Current Form": The Sanju Samson Factor

To account for a player's performance "yesterday" (e.g., Sanju Samson scoring 89), the system uses a **Hybrid Data Model**:

*   **Career Baseline (Historical)**: Derived from the 4 million delivery records. We know Samson's strike rate against specific bowling types and his performance at various venues.
*   **Player Form Index (PFI)**: A weighted rolling window of the last 10 matches.
    *   **Last Match (50% weight)**: Impactful knocks from yesterday spike the PFI immediately.
    *   **Recent Series (30% weight)**: Captures recent consistency.
    *   **Season Trend (20% weight)**: Provides a stability floor.
*   **Real-Time Bridge**: Since Cricsheet archives have a slight lag, we integrate **CricAPI** to ingest "Yesterday's Scorecard" dynamically before running today's prediction.

---

## 8. Next Steps: Phase 2 - Prediction Engine Development
With the data foundation and form-tracking logic defined, we proceed to:
1.  **Weighted Scorer Implementation**: Coding the PFI and H2H scoring logic.
2.  **Backtesting**: Validating the model against historical results.

**Status: Phase 1 Completed Successfully.**
**Next Action: Phase 2 - Prediction Engine Development.**
