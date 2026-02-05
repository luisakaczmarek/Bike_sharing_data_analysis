import requests
from pathlib import Path
import zipfile

def download_divvy_2023(dest_folder="data", unzip=True):
    dest = Path(dest_folder)
    dest.mkdir(parents=True, exist_ok=True)

    base = "https://divvy-tripdata.s3.amazonaws.com"
    months = [f"{m:02d}" for m in range(1, 13)]

    downloaded = []
    skipped = []

    for mm in months:
        fname = f"2023{mm}-divvy-tripdata.zip"
        url = f"{base}/{fname}"
        out_zip = dest / fname

        # Skip if already downloaded
        if out_zip.exists() and out_zip.stat().st_size > 0:
            skipped.append(fname)
            continue

        # Check if file exists on server
        head = requests.head(url, timeout=30)
        if head.status_code != 200:
            print(f"[MISSING] {fname} (HTTP {head.status_code})")
            continue

        print(f"[DOWNLOADING] {fname}")
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(out_zip, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

        downloaded.append(fname)

        if unzip:
            try:
                with zipfile.ZipFile(out_zip, "r") as z:
                    z.extractall(dest)
                print(f"[UNZIPPED] {fname}")
            except zipfile.BadZipFile:
                print(f"[ERROR] Bad zip: {fname}")

    print("\nDone.")
    print("Downloaded:", len(downloaded), downloaded[:3], "..." if len(downloaded) > 3 else "")
    print("Skipped:", len(skipped), skipped[:3], "..." if len(skipped) > 3 else "")

download_divvy_2023(dest_folder="data", unzip=True)
