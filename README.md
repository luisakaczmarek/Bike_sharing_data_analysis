# Bike_sharing_data_analysis

# Chicago Divvy Bike-Share — Time Series Analysis (2023)

Analysis of the full-year 2023 Chicago Divvy bike-share dataset. The project covers data collection, quality assessment, classical time series decomposition, stationarity testing, autocorrelation analysis, a comparative city study (Chicago vs Washington D.C.), and baseline forecasting models.

## Repository contents

```
.
├── Session_5_insights.ipynb
├── Session_6.ipynb
├── Session_7_8.ipynb
├── task_1_1_fetch_citybikes_stations.py
├── task_1_2_download_divvy_2023.py
├── requirements.txt
└── README.md
```

## Setup

- Python: 3.10+
- Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Data download (recommended)

### 1) Divvy trip data (2023)

Downloads the 12 monthly zip files and extracts the contained CSVs into:

- `data/raw/divvy/2023/zips/`
- `data/raw/divvy/2023/csv/`

Run:

```bash
python task_1_2_download_divvy_2023.py
```

### 2) CityBikes station snapshot (optional)

Fetches Divvy/Chicago station metadata from the CityBikes API and writes:

- `data/raw/citybikes/networks.json`
- `data/raw/citybikes/chicago_candidates.csv`
- `data/raw/citybikes/selected_network_id.txt`
- `data/raw/citybikes/stations_chicago.csv`

Run:

```bash
python task_1_1_fetch_citybikes_stations.py
```

## Notebooks

Run in this order:

1. `Session_5_insights.ipynb`
2. `Session_6.ipynb` (writes `daily_trips.parquet`)
3. `Session_7_8.ipynb` (reads `daily_trips.parquet`)

### Path configuration (Colab vs local)

The notebooks include Google Colab / Google Drive mounting cells and some hard-coded Drive paths.

For local execution, change the input glob to the CSV directory produced by `task_1_2_download_divvy_2023.py`, e.g.:

```python
# Local example
trip_data = load_trip_data("data/raw/divvy/2023/csv/*-divvy-tripdata.csv")
```

For Colab execution, keep the `/content/drive/...` paths (after mounting Drive).

## Data sources

- Divvy Trip Data (monthly CSV archives): `https://divvy-tripdata.s3.amazonaws.com`
- CityBikes API (live station metadata): `https://api.citybik.es/v2/`
- Capital Bikeshare (for comparative analysis): `https://s3.amazonaws.com/capitalbikeshare-data/`

Divvy data is made available under the Divvy Data License Agreement.
