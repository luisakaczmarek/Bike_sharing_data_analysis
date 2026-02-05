import requests
import pandas as pd

# 1) Networks holen
networks_url = "https://api.citybik.es/v2/networks"
networks = requests.get(networks_url, timeout=30).json()["networks"]
networks_df = pd.json_normalize(networks)

# 2) Chicago filtern (zur Kontrolle)
chicago_candidates = networks_df[
    networks_df["location.city"].str.contains("Chicago", case=False, na=False)
    | networks_df["name"].str.contains("Divvy", case=False, na=False)
][["id","name","location.city","location.country"]]

print(chicago_candidates)


# 3) (typisch) Divvy Network-ID wählen:
# Falls mehrere Ergebnisse: nimm die passende 'id' aus chicago_candidates.
network_id = chicago_candidates.iloc[0]["id"]  # ggf. manuell setzen, z.B. "divvy"

# 4) Station-Details holen
detail_url = f"https://api.citybik.es/v2/networks/{network_id}"
detail = requests.get(detail_url, timeout=30).json()

stations = detail["network"]["stations"]
stations_df = pd.DataFrame([{
    "station_id": s.get("id"),
    "name": s.get("name"),
    "latitude": s.get("latitude"),
    "longitude": s.get("longitude"),
    "free_bikes": s.get("free_bikes"),
    "empty_slots": s.get("empty_slots"),
    "timestamp": s.get("timestamp"),
} for s in stations])

stations_df.head(), stations_df.shape
