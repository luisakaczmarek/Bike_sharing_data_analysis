# Bike_sharing_data_analysis



# Chicago Divvy Bike-Share — Time Series Analysis (2023)

**Luisa Johanna Kaczmarek · Student ID: 16242**

Analysis of the full-year 2023 Chicago Divvy bike-share dataset. The project covers data collection, quality assessment, classical time series decomposition, stationarity testing, autocorrelation analysis, a comparative city study (Chicago vs Washington D.C.), and baseline forecasting models.

---

## Project structure

```
.
├── notebooks/
│   ├── session_5_insights.ipynb     # Exploratory analysis and insights on trip data
│   ├── Session_6.ipynb              # Follow-up analysis / modeling
│   └── Session_7_8.ipynb            # Advanced analysis and extended tasks
│
├── scripts/
│   ├── task_1_1_fetch_es_stations.py    # Script to fetch and process station data
│   └── task_1_2_download_divvy_2023.py  # Script to download 2023 Divvy trip data
│
├── README.md            # Project documentation
├── requirements.txt     # Python dependencies
└── venv/                # Virtual environment (not tracked in version control)

---

## Notebooks & Scripts 

### Session 5 — Data Collection & Initial Exploration

**Task 1.1 — CityBikes API (task_1_1_fetch_es_stations.py)**
Connects to the [CityBikes API](https://api.citybik.es/v2/) to retrieve a live snapshot of all Divvy stations in Chicago. Extracts station coordinates, available bikes, and empty slots, then runs a quick quality check (missing values, inactive stations) and produces a geographic scatter map of current availability.

**Task 1.2 — S3 Download (task_1_2_download_divvy_2023.py)**
Downloads all 12 monthly Divvy trip archives for 2023 from the official AWS S3 bucket (`divvy-tripdata.s3.amazonaws.com`), skipping any files already present locally, and unzips each archive to `data/`.

**Task 1.3 — Quality Assessment & Initial Exploration (session_5_insights.ipynb)**
Loads and concatenates all 12 CSV files (~5.5M rows). Covers:
- Schema review and data types
- Missing value audit (station names missing for dockless e-bike trips — structural, not errors)
- Duplicate `ride_id` detection and removal
- Trip duration validation: flags negatives, zeros, false starts (<1 min), and unreturned bikes (>24 h); retains ~99% of rows
- Rideable type breakdown (classic bike, electric bike, docked bike)
- Member vs. casual rider split
- Monthly and daily trip count time series
- Top 10 most-used start stations

---

### Session 6 — Time Series Decomposition, Seasonality & Anomaly Research

Aggregates raw trip records into a daily time series (365 observations), assigns `America/Chicago` timezone, and saves the result as `daily_trips.parquet` for reuse in Session 7/8.

**Classical decomposition**
Additive model (`seasonal_decompose`, period=7) decomposing the series into trend, weekly seasonal, and residual components. Key results:
- Decomposition explains ≈ **86%** of total variance (residual SD / original SD ≈ 0.38)
- Strong annual trend: August peak ≈ **24,893** avg daily trips; January trough ≈ **6,139** (4× amplitude)
- Box–Cox test on the residual series gives λ ≈ **0.55** (≈ √y transform), indicating heteroskedasticity that should be addressed before ARIMA fitting

**Multiple seasonality analysis**
- Weekly: Saturday peak (≈ 16,992 trips), Monday/Sunday trough (≈ 14,000), Tuesday–Friday stable commuter baseline (≈ 15,800–16,500)
- Annual: clear summer peak, sharp winter suppression driven by Chicago's climate

**Anomaly detection & research**
Outlier identification uses `decomposition.resid` directly (both trend and seasonality removed) via dual IQR (1.5×) and Z-score (|z| > 2.5) methods. Identified anomalies with external explanations:

| Type | Date(s) | Driver |
|---|---|---|
| Negative | Late Jan / early Feb 2023 | Polar vortex — temperatures −15°C to −20°C |
| Negative | Early April 2023 | Late-season snowstorm |
| Positive | Aug 3–6, 2023 | Lollapalooza (400k+ visitors) |
| Positive | Memorial Day weekend, late June (Pride), warm September | Events + seasonality |
| Structural | Throughout 2023 | Divvy e-bike fleet expansion |

---

### Session 7 & 8 — Stationarity, Autocorrelation & Forecasting

Loads `daily_trips.parquet` produced in Session 6.

**Session 7 — Stationarity testing & autocorrelation**
- Rolling statistics (30-day window): mean variation ≈ 131% of overall mean; variance increases 3.4× from winter to summer
- ADF test on raw series: p = 0.79 → unit root present, series not stationary
- First differencing (d=1): ADF p = 1×10⁻¹³ → stationary
- ACF/PACF on differenced series (lags 0–30): strong MA(1) effect at lag 1 (ACF = −0.32***); significant positive spike at lag 7 confirming weekly autocorrelation survives simple differencing → SARIMA required

**Session 7 Extra — Comparative city analysis**
Downloads 2023 Capital Bikeshare data for Washington D.C. and compares additive decompositions side by side. Chicago shows stronger seasonal amplitude (~4× peak-to-trough vs DC's ~2.5×), larger weekly swings (±1,500 vs ±800–1,000), and more volatile residuals. DC exhibits flatter, more commuter-stable demand.

**Session 8 — Forecasting models**
All models are fitted on the differenced series (Δ trips); forecasts cover a 90-day test set and a 14-day forward horizon.

| Model | Test RMSE | Notes |
|---|---|---|
| MA-15 (15-day window) | ≈ 3,130 | Baseline |
| MA-90 (90-day window) | ≈ 3,007 | Marginally better; near-zero mean suits longer window |
| ARIMA(0,0,1) | comparable | Residuals still show weekly autocorrelation (Ljung-Box p ≈ 0.00) |

ARIMA(0,1,1) is also fitted on the raw trip-count levels as the preferred formulation (model handles differencing internally). Next step: **SARIMA(0,1,1)(1,0,0)[7]** with Box–Cox pre-transform.

---

## Setup

### Requirements

Python 3.10+ recommended. Install dependencies:

```bash
pip install -r requirements.txt
```

### Data

The notebooks are written for Google Colab with data stored in Google Drive. The download function in Session 5 writes to a local `data/` folder; update the path constants in Sessions 6 and 7/8 to match your environment:

```python
# Session 6 / 7/8 — update this path to wherever you saved the data
"/content/drive/MyDrive/emerging_topics_session_5/data/"
```

Run the notebooks in order:

```
Session_5.ipynb  →  Session_6.ipynb  →  Session_7_8.ipynb
```

Session 6 writes `daily_trips.parquet` which is read by Session 7/8.

---

## Data sources

| Source | Description |
|---|---|
| [Divvy Trip Data](https://divvy-tripdata.s3.amazonaws.com) | Monthly CSV archives, 2023 (Motivate International, Inc.) |
| [CityBikes API](https://api.citybik.es/v2/) | Live station metadata |
| [Capital Bikeshare](https://s3.amazonaws.com/capitalbikeshare-data/) | 2023 Washington D.C. trip data for comparative analysis |

Divvy data is made available under the [Divvy Data License Agreement](https://divvybikes.com/data-license-agreement).
