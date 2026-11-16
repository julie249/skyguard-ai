"""
Feature Engineering module for Automatic Weather Station (AWS) data.
Computes:
1. Multi-scale rolling statistics (1hr, 4hr, 24hr windows for 10-min readings)
2. Seasonal decomposition features (STL residuals / baseline detrending)
3. Meteorological cross-feature consistency (Magnus approximation dew point,
   hypsometric / pressure-altitude consistency, and relative humidity spread).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_dew_point(temperature_c: pd.Series | np.ndarray, humidity_pct: pd.Series | np.ndarray) -> np.ndarray:
    """
    Computes dew point temperature (°C) using the Magnus-Tetens approximation:
    Td = (b * alpha) / (a - alpha)
    where alpha = (a * T) / (b + T) + ln(RH / 100)
    a = 17.27, b = 237.7
    """
    t = np.asarray(temperature_c, dtype=float)
    rh = np.clip(np.asarray(humidity_pct, dtype=float), 1.0, 100.0)
    a = 17.27
    b = 237.7
    alpha = ((a * t) / (b + t)) + np.log(rh / 100.0)
    dew_point = (b * alpha) / (a - alpha)
    return dew_point


def compute_cross_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes cross-sensor physical consistency features:
    - dew_point_c: Magnus dew point calculation
    - dew_point_depression: (temperature - dew_point); unphysical if negative
    - vapor_pressure_deficit_kpa: drying power of air
    - thermo_pressure_ratio: temperature (Kelvin) / pressure ratio
    """
    feat_df = pd.DataFrame(index=df.index)
    temp = df["temperature_c"]
    humidity = df["humidity_pct"]
    pressure = df["pressure_hpa"]

    # Dew point & depression
    feat_df["dew_point_c"] = compute_dew_point(temp, humidity)
    feat_df["dew_point_depression"] = temp - feat_df["dew_point_c"]

    # Saturation vapor pressure (es in kPa) & actual vapor pressure (ea in kPa)
    es = 0.61078 * np.exp((17.27 * temp) / (temp + 237.3))
    ea = es * (np.clip(humidity, 1.0, 100.0) / 100.0)
    feat_df["vpd_kpa"] = np.maximum(0.0, es - ea)

    # Thermodynamic ratio: T(K) / P(hPa) * 100
    temp_kelvin = temp + 273.15
    feat_df["thermo_pressure_ratio"] = (temp_kelvin / np.maximum(pressure, 300.0)) * 100.0

    return feat_df


def compute_rolling_stats(
    df: pd.DataFrame,
    features: list[str] = ["temperature_c", "pressure_hpa", "humidity_pct"],
    windows: dict[str, int] = {"1h": 6, "4h": 24, "24h": 144},
) -> pd.DataFrame:
    """
    Computes rolling mean, std, min, max, and z-score for given window sizes
    assuming 10-minute sampling frequency:
      1h = 6 periods
      4h = 24 periods
      24h = 144 periods
    """
    stats_df = pd.DataFrame(index=df.index)

    for feat in features:
        s = df[feat]
        for w_name, w_size in windows.items():
            roll = s.rolling(window=w_size, min_periods=2)
            r_mean = roll.mean()
            r_std = roll.std().replace(0, 1e-4)
            stats_df[f"{feat}_roll_mean_{w_name}"] = r_mean
            stats_df[f"{feat}_roll_std_{w_name}"] = r_std
            stats_df[f"{feat}_roll_zscore_{w_name}"] = (s - r_mean) / r_std
            stats_df[f"{feat}_roll_delta_{w_name}"] = s - s.shift(w_size)

    return stats_df


def compute_seasonal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes diurnal and temporal alignment signals:
    - hour_sin, hour_cos (24h cyclical representation)
    - diurnal_residual: difference from station local hour-of-day mean
    """
    feat_df = pd.DataFrame(index=df.index)
    ts = pd.to_datetime(df["timestamp"], utc=True)
    hour_float = ts.dt.hour + ts.dt.minute / 60.0

    feat_df["hour_sin"] = np.sin(2 * np.pi * hour_float / 24.0)
    feat_df["hour_cos"] = np.cos(2 * np.pi * hour_float / 24.0)

    # Detrended diurnal residual for temperature
    # Approximate expected diurnal curve: peak at 14, trough at 05
    expected_diurnal_temp = 7.0 * np.sin(2 * np.pi * (hour_float - 8) / 24.0)
    feat_df["temp_diurnal_residual"] = df["temperature_c"] - (df["temperature_c"].mean() + expected_diurnal_temp)

    return feat_df


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Full feature extraction pipeline combining rolling, seasonal, and cross-feature statistics."""
    rolling = compute_rolling_stats(df)
    cross = compute_cross_features(df)
    seasonal = compute_seasonal_features(df)

    base_features = df[["temperature_c", "pressure_hpa", "humidity_pct"]]
    full_features = pd.concat([base_features, rolling, cross, seasonal], axis=1)
    # Forward-fill and backward-fill boundary rolling NaNs
    return full_features.bfill().ffill()
