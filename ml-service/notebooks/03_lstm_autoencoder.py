"""
03_LSTM_Autoencoder — PyTorch Sequence-to-Sequence Reconstruction Error Anomaly Detection.
Sequences of 24 time-steps (4 hours) evaluated for latent reconstruction fidelity.
"""

# %%
import pandas as pd
import numpy as np
import torch
from app.src.models.lstm_autoencoder import LSTMAutoencoderDetector
from app.src.evaluate import evaluate_metrics

# %%
df = pd.read_csv("../data/synthetic/aws_synthetic_3pct.csv")
y_true = df["is_anomaly"].fillna(False).values

# %%
# Train PyTorch LSTM Autoencoder
lstm_model = LSTMAutoencoderDetector(epochs=3, batch_size=64, seq_len=24)
lstm_model.fit(df)
print(f"LSTM Autoencoder CPU Training Time: {lstm_model.training_time_sec:.2f}s")

# %%
# Evaluate Reconstruction
lstm_preds, lstm_scores = lstm_model.predict(df)
lstm_metrics = evaluate_metrics(y_true, lstm_preds)
print("LSTM Autoencoder Metrics:", lstm_metrics)
