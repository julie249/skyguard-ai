# SkyGuard AI — Model Evaluation & Benchmark Report

## Overview
Automated evaluation across multi-station Automatic Weather Station (AWS) datasets.
Both Point-Level and Event-Level Precision, Recall, and F1 metrics are evaluated.

| Dataset / Rate | Model | Point Prec | Point Rec | Point F1 | Event Prec | Event Rec | Event F1 |
|---|---|---|---|---|---|---|---|
| Synthetic 1% | Statistical (Z+IQR) | 1.0000 | 0.0736 | 0.1372 | 1.0000 | 0.3600 | 0.5294 |
| Synthetic 1% | Isolation Forest | 0.1620 | 0.4884 | 0.2432 | 0.0979 | 0.8400 | 0.1753 |
| Synthetic 1% | LSTM Autoencoder | 0.0567 | 0.7791 | 0.1058 | 0.0120 | 0.9600 | 0.0236 |
| Synthetic 1% | Hybrid Ensemble | 0.5342 | 0.4535 | 0.4906 | 0.4156 | 0.7600 | 0.5373 |
| Synthetic 3% | Statistical (Z+IQR) | 1.0000 | 0.0675 | 0.1265 | 1.0000 | 0.2877 | 0.4468 |
| Synthetic 3% | Isolation Forest | 0.3586 | 0.3623 | 0.3605 | 0.3614 | 0.7534 | 0.4885 |
| Synthetic 3% | LSTM Autoencoder | 0.2372 | 0.2701 | 0.2526 | 0.4345 | 0.7123 | 0.5398 |
| Synthetic 3% | Hybrid Ensemble | 0.5951 | 0.1260 | 0.2079 | 0.9216 | 0.5342 | 0.6764 |
| Synthetic 8% | Statistical (Z+IQR) | 1.0000 | 0.0648 | 0.1218 | 1.0000 | 0.2957 | 0.4564 |
| Synthetic 8% | Isolation Forest | 0.4332 | 0.1655 | 0.2395 | 0.6857 | 0.5860 | 0.6320 |
| Synthetic 8% | LSTM Autoencoder | 0.3968 | 0.1483 | 0.2159 | 0.9205 | 0.5645 | 0.6998 |
| Synthetic 8% | Hybrid Ensemble | 0.5510 | 0.0928 | 0.1589 | 0.7864 | 0.4032 | 0.5331 |

## Methodology
- **Point-Level Evaluation**: Strict timestamp-by-timestamp classification accuracy.
- **Event-Level Evaluation**: Segment-based detection. A sensor fault or weather event spanning several 10-minute intervals is considered successfully caught if alerted during its duration.
- **Sanity Check**: Always-normal baseline scores 0.0 recall, validating the evaluation harness.