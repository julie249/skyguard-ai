"""
LSTM Autoencoder for temporal anomaly detection in AWS time-series.
Architecture:
  - Sequence Length: 24 (4 hours of 10-minute intervals)
  - Encoder: LSTM layer -> Latent representation
  - Decoder: RepeatVector -> LSTM layer -> Linear reconstruction
  - Anomaly metric: Reconstruction Mean Squared Error (MSE)
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler


class LSTMAutoencoderNet(nn.Module):
    """PyTorch LSTM Autoencoder architecture."""

    def __init__(self, input_dim: int, hidden_dim: int = 32, latent_dim: int = 16):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim

        # Encoder
        self.encoder_lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.encoder_fc = nn.Linear(hidden_dim, latent_dim)

        # Decoder
        self.decoder_fc = nn.Linear(latent_dim, hidden_dim)
        self.decoder_lstm = nn.LSTM(hidden_dim, hidden_dim, batch_first=True)
        self.output_fc = nn.Linear(hidden_dim, input_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: [batch_size, seq_len, input_dim]
        _, (h_n, _) = self.encoder_lstm(x)
        # h_n shape: [1, batch_size, hidden_dim]
        latent = torch.relu(self.encoder_fc(h_n.squeeze(0)))  # [batch_size, latent_dim]

        # Repeat latent across sequence length
        seq_len = x.size(1)
        decoded_hidden = self.decoder_fc(latent).unsqueeze(1).repeat(1, seq_len, 1)

        dec_out, _ = self.decoder_lstm(decoded_hidden)
        reconstruction = self.output_fc(dec_out)
        return reconstruction


class LSTMAutoencoderDetector:
    """
    Detector wrapper managing sequence slicing, PyTorch training,
    state_dict checkpointing, and reconstruction error scoring.
    """

    def __init__(
        self,
        seq_len: int = 24,
        features: list[str] = ["temperature_c", "pressure_hpa", "humidity_pct"],
        hidden_dim: int = 32,
        latent_dim: int = 16,
        batch_size: int = 64,
        epochs: int = 5,
        lr: float = 0.003,
    ):
        self.seq_len = seq_len
        self.features = features
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
        self.batch_size = batch_size
        self.epochs = epochs
        self.lr = lr

        self.device = torch.device("cpu")
        self.model = LSTMAutoencoderNet(len(features), hidden_dim, latent_dim).to(self.device)
        self.scaler = StandardScaler()
        self.threshold: float = 0.5
        self.training_time_sec: float = 0.0
        self.fitted = False

    def _create_sequences(self, data: np.ndarray) -> np.ndarray:
        """Create sliding window sequences."""
        num_samples = len(data) - self.seq_len + 1
        if num_samples <= 0:
            return np.empty((0, self.seq_len, data.shape[1]))
        sequences = np.lib.stride_tricks.sliding_window_view(data, window_shape=(self.seq_len, data.shape[1]))
        return sequences.squeeze(axis=1)

    def fit(self, df: pd.DataFrame) -> LSTMAutoencoderDetector:
        """Train autoencoder on normal sequence reconstructions with early stopping."""
        start_time = time.perf_counter()
        raw_vals = df[self.features].values
        scaled_vals = self.scaler.fit_transform(raw_vals)

        sequences = self._create_sequences(scaled_vals)
        if len(sequences) == 0:
            return self

        dataset = TensorDataset(torch.tensor(sequences, dtype=torch.float32))
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)

        self.model.train()
        for epoch in range(self.epochs):
            for (batch_x,) in loader:
                batch_x = batch_x.to(self.device)
                optimizer.zero_grad()
                pred = self.model(batch_x)
                loss = criterion(pred, batch_x)
                loss.backward()
                optimizer.step()

        self.training_time_sec = time.perf_counter() - start_time
        self.fitted = True

        # Calculate threshold on training distribution (e.g. 98th percentile error)
        self.model.eval()
        with torch.no_grad():
            tensor_seq = torch.tensor(sequences, dtype=torch.float32).to(self.device)
            preds = self.model(tensor_seq)
            errors = torch.mean((preds - tensor_seq) ** 2, dim=[1, 2]).cpu().numpy()
            self.threshold = float(np.percentile(errors, 97))

        return self

    def predict(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Compute reconstruction MSE per sequence, map to [0, 1] normalized confidence."""
        if not self.fitted:
            self.fit(df)

        raw_vals = df[self.features].values
        scaled_vals = self.scaler.transform(raw_vals)
        n = len(df)

        # Pad initial steps that precede seq_len
        point_scores = np.zeros(n, dtype=float)
        sequences = self._create_sequences(scaled_vals)

        if len(sequences) > 0:
            self.model.eval()
            with torch.no_grad():
                tensor_seq = torch.tensor(sequences, dtype=torch.float32).to(self.device)
                preds = self.model(tensor_seq)
                # Last step reconstruction error represents the arrival point
                step_errors = torch.mean((preds[:, -1, :] - tensor_seq[:, -1, :]) ** 2, dim=1).cpu().numpy()
                point_scores[self.seq_len - 1 :] = step_errors
                # Mirror to beginning for initial window
                point_scores[: self.seq_len - 1] = step_errors[0] if len(step_errors) > 0 else 0.0

        norm_scores = np.clip(point_scores / (self.threshold * 2.5), 0.0, 1.0)
        is_anomaly = point_scores >= self.threshold
        return is_anomaly, np.round(norm_scores, 4)

    def save_state(self, path: str | Path) -> None:
        """Save PyTorch state_dict."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "state_dict": self.model.state_dict(),
                "threshold": float(self.threshold),
                "training_time_sec": float(self.training_time_sec),
                "scaler_mean": list(self.scaler.mean_),
                "scaler_scale": list(self.scaler.scale_),
            },
            path,
        )

    def load_state(self, path: str | Path) -> None:
        """Load PyTorch state_dict."""
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(checkpoint["state_dict"])
        self.threshold = float(checkpoint["threshold"])
        self.training_time_sec = float(checkpoint.get("training_time_sec", 0.0))
        self.scaler.mean_ = np.array(checkpoint["scaler_mean"])
        self.scaler.scale_ = np.array(checkpoint["scaler_scale"])
        self.fitted = True
