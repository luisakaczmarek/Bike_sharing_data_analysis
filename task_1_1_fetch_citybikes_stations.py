"""Task 1.1 — Fetch Divvy/Chicago station metadata from CityBikes.

Outputs (written into data/raw/citybikes/):
- networks.json: full CityBikes network list (raw)
- chicago_candidates.csv: filtered candidate networks for Chicago/Divvy (for transparency)
- stations_chicago.csv: station-level snapshot for the selected network_id
- selected_network_id.txt: the network_id used to fetch station details
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import requests


def project_root() -> Path:
    # scripts/ -> project root
    return Path(__file__).resolve().parents[1]


def fetch_citybikes_networks(timeout: int = 30) -> list[dict]:
    url = "https://api.citybik.es/v2/networks"
    return requests.get(url, timeout=timeout).json()["networks"]


def main() -> None:
    out_dir = project_root() / "data" / "raw" / "citybikes"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) Networks holen
    networks = fetch_citybikes_networks()
    (out_dir / "networks.json").write_text(json.dumps(networks, ensure_ascii=False, indent=2), encoding="utf-8")

    networks_df = pd.json_normalize(networks)

    # 2) Chicago/Divvy filtern (zur Kontrolle + Reproduzierbarkeit)
    chicago_candidates = networks_df[
        networks_df["location.city"].str.contains("Chicago", case=False, na=False)
        | networks_df["name"].str.contains("Divvy", case=False, na=False)
    ][["id", "name", "location.city", "location.country"]].copy()

    chicago_candidates.to_csv(out_dir / "chicago_candidates.csv", index=False)

    # 3) Network-ID wählen
    # Default: erster Treffer. Falls du einen anderen willst: setze network_id manuell.
    if len(chicago_candidates) == 0:
        raise RuntimeError("Keine Chicago/Divvy Netzwerke gefunden. Prüfe 'networks.json' oder Filterlogik.")

    network_id = str(chicago_candidates.iloc[0]["id"])
    (out_dir / "selected_network_id.txt").write_text(network_id, encoding="utf-8")

    # 4) Station-Details holen
    detail_url = f"https://api.citybik.es/v2/networks/{network_id}"
    detail = requests.get(detail_url, timeout=30).json()

    stations = detail["network"]["stations"]
    stations_df = pd.DataFrame(
        [
            {
                "station_id": s.get("id"),
                "name": s.get("name"),
                "latitude": s.get("latitude"),
                "longitude": s.get("longitude"),
                "free_bikes": s.get("free_bikes"),
                "empty_slots": s.get("empty_slots"),
                "timestamp": s.get("timestamp"),
            }
            for s in stations
        ]
    )

    stations_df.to_csv(out_dir / "stations_chicago.csv", index=False)

    print(f"Wrote: {out_dir / 'stations_chicago.csv'}  (rows={len(stations_df)})")


if __name__ == "__main__":
    main()
