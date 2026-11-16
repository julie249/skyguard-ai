"""
Data loader and synthetic dataset generation for Automatic Weather Stations (AWS).
Generates realistic multi-station time series with diurnal, seasonal, and microclimate variations.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


def generate_synthetic_station_data(
    station_id: str,
    start_date: str = "2026-01-01 00:00:00",
    days: int = 30,
    freq_minutes: int = 10,
    base_temp: float = 24.0,
    base_pressure: float = 1013.25,
    base_humidity: float = 65.0,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate realistic canonical AWS readings with diurnal cycle and natural weather drifts."""
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range(
        start=start_date, periods=days * (24 * 60 // freq_minutes), freq=f"{freq_minutes}min", tz="UTC"
    )
    n = len(timestamps)

    # Time factors
    hour_of_day = timestamps.hour + timestamps.minute / 60.0
    day_of_year = getattr(timestamps, "day_of_year", getattr(timestamps, "dayofyear", 1))

    # Diurnal cycle: peak temperature around 14:00 (hour 14), lowest around 05:00 (hour 5)
    temp_diurnal = 7.0 * np.sin(2 * np.pi * (hour_of_day - 8) / 24.0)
    temp_seasonal = 3.0 * np.sin(2 * np.pi * day_of_year / 365.25)
    # Weather synoptic wave (multi-day pressure/temp fluctuations)
    synoptic_wave = 2.0 * np.sin(2 * np.pi * np.arange(n) / (6 * 24 * 6))

    # Temperature series
    temp_noise = rng.normal(0, 0.4, n)
    temperature = base_temp + temp_diurnal + temp_seasonal + synoptic_wave + temp_noise

    # Pressure series (semi-diurnal atmospheric tide + synoptic system, inverse correlation with temp)
    pressure_tide = 1.2 * np.sin(4 * np.pi * hour_of_day / 24.0)
    pressure_synoptic = -3.5 * synoptic_wave
    pressure_noise = rng.normal(0, 0.25, n)
    pressure = base_pressure + pressure_tide + pressure_synoptic + pressure_noise

    # Humidity series (strongly anti-correlated with temperature diurnal cycle)
    humidity_diurnal = -18.0 * np.sin(2 * np.pi * (hour_of_day - 8) / 24.0)
    humidity_noise = rng.normal(0, 1.2, n)
    humidity = base_humidity + humidity_diurnal - 1.5 * synoptic_wave + humidity_noise
    humidity = np.clip(humidity, 10.0, 99.0)

    df = pd.DataFrame(
        {
            "station_id": station_id,
            "timestamp": timestamps.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "temperature_c": np.round(temperature, 2),
            "pressure_hpa": np.round(pressure, 2),
            "humidity_pct": np.round(humidity, 2),
            "is_anomaly": False,
            "anomaly_type": None,
        }
    )
    return df


def load_dataset(csv_path: str | Path) -> pd.DataFrame:
    """Load canonical CSV reading records."""
    df = pd.read_csv(csv_path)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return df


def save_dataset(df: pd.DataFrame, output_path: str | Path) -> None:
    """Save canonical reading records ensuring directory existence."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
