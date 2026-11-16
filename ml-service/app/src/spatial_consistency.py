"""
Spatial Consistency & Geospatial Validation Engine.
Calculates Haversine distances between stations and determines spatial consensus
among k-nearest neighbor weather stations.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on the earth in km."""
    r = 6371.0  # Earth radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


class SpatialConsistencyValidator:
    """
    Validates station anomalies against neighboring AWS nodes.
    Distinguishes genuine widespread extreme weather (co-occurring anomalies across neighbors)
    from localized hardware/sensor failures (single node deviation).
    """

    def __init__(self, metadata_path: str | Path = "data/station_metadata.csv", k_neighbors: int = 3):
        self.metadata_path = Path(metadata_path)
        self.k_neighbors = k_neighbors
        self.stations_df: pd.DataFrame = pd.DataFrame()
        self.load_metadata()

    def load_metadata(self) -> None:
        """Load station coordinates and metadata."""
        if self.metadata_path.exists():
            self.stations_df = pd.read_csv(self.metadata_path)
        else:
            # Fallback default metadata if file not in current cwd
            self.stations_df = pd.DataFrame([
                {"station_id": "AWS001", "latitude": 28.6139, "longitude": 77.2090},
                {"station_id": "AWS002", "latitude": 28.5665, "longitude": 77.1031},
                {"station_id": "AWS003", "latitude": 28.6280, "longitude": 77.3649},
                {"station_id": "AWS004", "latitude": 28.4949, "longitude": 77.0895},
                {"station_id": "AWS005", "latitude": 28.4089, "longitude": 77.3178},
                {"station_id": "AWS006", "latitude": 28.7032, "longitude": 77.4378},
            ])

    def find_nearest_neighbors(self, target_station_id: str, k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find the k nearest AWS stations with their distance in km."""
        k = k or self.k_neighbors
        target = self.stations_df[self.stations_df["station_id"] == target_station_id]
        if target.empty:
            return []

        t_lat = float(target.iloc[0]["latitude"])
        t_lon = float(target.iloc[0]["longitude"])

        neighbors = []
        for _, row in self.stations_df.iterrows():
            st_id = str(row["station_id"])
            if st_id == target_station_id:
                continue
            dist = haversine_distance_km(t_lat, t_lon, float(row["latitude"]), float(row["longitude"]))
            neighbors.append({
                "station_id": st_id,
                "distance_km": round(dist, 2),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
            })

        neighbors.sort(key=lambda x: x["distance_km"])
        return neighbors[:k]

    def compute_spatial_agreement(
        self,
        target_station_id: str,
        target_reading: Dict[str, float],
        neighbor_readings: List[Dict[str, Any]],
        tolerances: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Compare reading against neighbor stations co-temporal readings.
        tolerances: allowable deviation (e.g. temp: 4.5°C, pressure: 5.0 hPa, humidity: 15.0%)
        Returns:
          {
            "agreement_score": float [0.0 - 1.0],  (1.0 = full consensus with neighbors, 0.0 = severe divergence)
            "agreeing_neighbors_count": int,
            "compared_neighbors": list,
            "is_corroborated": bool,
            "spatial_mean_delta": float,
            "suggested_correction": Optional[float]
          }
        """
        if not tolerances:
            tolerances = {
                "temperature_c": 4.5,
                "pressure_hpa": 5.0,
                "humidity_pct": 18.0,
            }

        if not neighbor_readings:
            return {
                "agreement_score": 0.5,
                "agreeing_neighbors_count": 0,
                "compared_neighbors": [],
                "is_corroborated": False,
                "suggested_correction": None,
                "summary": "No neighbor station readings available for spatial cross-validation.",
            }

        target_temp = target_reading.get("temperature_c")
        if target_temp is None:
            return {"agreement_score": 0.5, "is_corroborated": False, "suggested_correction": None}

        compared = []
        agreeing = 0
        neighbor_temps = []

        for n_read in neighbor_readings:
            n_st_id = n_read.get("station_id", "unknown")
            n_temp = n_read.get("temperature_c")
            if n_temp is not None:
                delta = abs(float(target_temp) - float(n_temp))
                is_close = delta <= tolerances["temperature_c"]
                if is_close:
                    agreeing += 1
                neighbor_temps.append(float(n_temp))
                compared.append({
                    "station_id": n_st_id,
                    "temperature_c": float(n_temp),
                    "delta": round(delta, 2),
                    "agrees": is_close,
                })

        total = len(compared)
        agreement_score = round(agreeing / total, 3) if total > 0 else 0.5
        is_corroborated = agreement_score >= 0.5
        suggested_corr = round(float(np.mean(neighbor_temps)), 2) if neighbor_temps else None

        return {
            "agreement_score": agreement_score,
            "agreeing_neighbors_count": agreeing,
            "total_neighbors_evaluated": total,
            "compared_neighbors": compared,
            "is_corroborated": is_corroborated,
            "suggested_correction": suggested_corr,
            "summary": f"{agreeing}/{total} neighbor stations corroborate observation (consensus: {agreement_score*100:.0f}%).",
        }
