#!/bin/bash
set -e

echo "=========================================================="
echo "SkyGuard AI — Automated Model Training & Evaluation Suite"
echo "=========================================================="

cd "$(dirname "$0")/../ml-service"

echo "[1/3] Setting up Python environment..."
python -m venv .venv
source .venv/bin/activate || source .venv/Scripts/activate
pip install -r requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cpu

echo "[2/3] Generating synthetic datasets..."
python generate_datasets.py

echo "[3/3] Running multi-model benchmark and generating docs/model_report.md..."
python run_benchmark.py

echo "Model training and evaluation successfully completed!"
