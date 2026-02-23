"""Task 1.2 — Download Divvy Tripdata (2023) from the official S3 bucket.

Outputs (written into data/raw/divvy/2023/):
- zips/*.zip : downloaded monthly archives
- csv/*.csv  : extracted monthly trip files
"""

from __future__ import annotations

from pathlib import Path
import zipfile

import requests


def project_root() -> Path:
    # scripts/ -> project root
    return Path(__file__).resolve().parents[1]


def download_divvy_2023(unzip: bool = True) -> None:
    base = "https://divvy-tripdata.s3.amazonaws.com"
    months = [f"{m:02d}" for m in range(1, 13)]

    raw_dir = project_root() / "data" / "raw" / "divvy" / "2023"
    zip_dir = raw_dir / "zips"
    csv_dir = raw_dir / "csv"
    zip_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)

    downloaded, skipped = [], []

    for mm in months:
        fname = f"2023{mm}-divvy-tripdata.zip"
        url = f"{base}/{fname}"
        out_zip = zip_dir / fname

        # Skip if already downloaded
        if out_zip.exists() and out_zip.stat().st_size > 0:
            skipped.append(fname)
        else:
            head = requests.head(url, timeout=30)
            if head.status_code != 200:
                print(f"[MISSING] {fname} (HTTP {head.status_code})")
                continue

            print(f"[DOWNLOADING] {fname}")
            with requests.get(url, stream=True, timeout=180) as r:
                r.raise_for_status()
                with open(out_zip, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
            downloaded.append(fname)

        if unzip:
            try:
                with zipfile.ZipFile(out_zip, "r") as z:
                    # Divvy zips typically contain exactly one CSV; extract into csv/
                    z.extractall(csv_dir)
                print(f"[UNZIPPED] {fname} -> {csv_dir}")
            except zipfile.BadZipFile:
                print(f"[ERROR] Bad zip: {fname}")

    print("\nDone.")
    print(f"Downloaded: {len(downloaded)}  Skipped: {len(skipped)}")
    print(f"CSV folder: {csv_dir}")


if __name__ == "__main__":
    download_divvy_2023(unzip=True)
