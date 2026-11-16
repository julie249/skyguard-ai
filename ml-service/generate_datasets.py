"""
Script to generate synthetic datasets for 5+ stations with 1%, 3%, and 8% anomaly rates.
"""

from pathlib import Path
import pandas as pd
from app.src.data_loader import generate_synthetic_station_data, save_dataset
from app.src.anomaly_injector import AnomalyInjector

def main():
    metadata_path = Path("data/station_metadata.csv")
    meta = pd.read_csv(metadata_path)

    stations = meta["station_id"].tolist()
    print(f"Generating base datasets for {len(stations)} stations: {stations}")

    # Rates: 1%, 3%, 8%
    rates = [0.01, 0.03, 0.08]

    for rate in rates:
        rate_pct = int(rate * 100)
        combined_dfs = []

        for idx, st_id in enumerate(stations):
            # Seed varies by station and rate for realism
            seed = 1000 * (idx + 1) + rate_pct
            base_df = generate_synthetic_station_data(
                station_id=st_id,
                days=30,
                base_temp=22.0 + idx * 1.5,
                base_pressure=1012.0 - idx * 0.8,
                base_humidity=60.0 + idx * 2.0,
                seed=seed,
            )

            injector = AnomalyInjector(seed=seed + 55)
            corrupted, _ = injector.inject(base_df, {"rate": rate})
            combined_dfs.append(corrupted)

        full_df = pd.concat(combined_dfs, ignore_index=True)
        out_file = Path(f"data/synthetic/aws_synthetic_{rate_pct}pct.csv")
        save_dataset(full_df, out_file)
        anomalies_count = full_df["is_anomaly"].sum()
        total_count = len(full_df)
        print(f"Generated {out_file}: {anomalies_count}/{total_count} anomalies ({anomalies_count/total_count*100:.2f}%)")

if __name__ == "__main__":
    main()
