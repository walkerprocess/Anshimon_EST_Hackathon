# Heatwave and Older-Adult Heat-Illness Model

This component predicts next-day heatwave probability for Seoul and estimates older-adult heat-illness risk from weather and historical illness data.

## What Is Included

- Historical raw and processed CSV datasets under `data/`
- Preprocessing code under `preprocessing/`
- Training, tuning, and evaluation scripts under `training/`
- Serialized scikit-learn/XGBoost artifacts and thresholds under `models/`
- Forecast and validation outputs under `outputs/`
- `main.py` for the combined next-day forecast
- `predict.py` for batch risk scoring from a weather CSV

## Install

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run a Next-Day Seoul Forecast

```bash
python main.py 2026-08-18 Seoul
```

The current model supports Seoul only. The requested date must be exactly one day after the latest date in `data/processed/heat_data_seoul.csv`.

The output includes:

- `heatwave_risk_score`: probability from 0 to 1
- `heatwave_prediction`: `O` or `X` based on the trained threshold
- `elderly_heat_illness_risk_score`: estimated risk from 0 to 1
- `historical_analog_rows`: number of historical seasonal analogs used

## Score a Weather CSV

```bash
python predict.py path/to/weather.csv -o outputs/predictions.csv
```

The input must contain the Korean column names expected by the training pipeline, including the date column `일시`. `predict.py` appends `risk_score` and `prediction` to the original rows.

## Reproduce Training and Evaluation

```bash
python preprocessing/preprocess.py
python training/train_xgboost.py
python training/tune_threshold.py
python training/evaluate_test.py
python training/train_next_day_heatwave.py
```

Serialized model artifacts are Python-library-version sensitive. For reproducible deployment, pin tested versions of pandas, scikit-learn, XGBoost, and joblib before retraining or serving the model.
