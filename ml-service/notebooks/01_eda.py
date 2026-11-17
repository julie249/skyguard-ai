"""
01_EDA — Exploratory Data Analysis of Automatic Weather Station (AWS) Meteorological Telemetry.
Analyzes temperature, barometric pressure, and relative humidity diurnal cycles,
seasonal drifts, and inter-sensor correlations.
"""

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# %%
# Load station metadata
metadata = pd.read_csv("../data/station_metadata.csv")
print("AWS Station Network:")
display(metadata)

# %%
# Load 3% synthetic benchmark dataset
df = pd.read_csv("../data/synthetic/aws_synthetic_3pct.csv")
print(f"Total Telemetry Records: {len(df)}")
print(f"Anomalous Records: {df['is_anomaly'].sum()} ({df['is_anomaly'].mean()*100:.2f}%)")
display(df.head())

# %%
# Summary statistics per meteorological feature
df[["temperature_c", "pressure_hpa", "humidity_pct"]].describe()

# %%
# Anomaly Type Breakdown
df["anomaly_type"].value_counts(dropna=False)
