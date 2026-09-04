from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

FEATURES = [
    "sand_ratio", "potting_soil_ratio", "adsorbent", "adsorbent_mass_g",
    "dye_concentration", "dye_volume_ml", "time_min", "position",
]
TARGETS = ["r", "g", "b"]
REQUIRED_COLUMNS = ["experiment_id", *FEATURES, *TARGETS]
CATEGORICAL = ["adsorbent", "position"]
NUMERIC = [column for column in FEATURES if column not in CATEGORICAL]


def validate_data(data: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"필수 열이 없습니다: {', '.join(missing)}")
    clean = data[REQUIRED_COLUMNS].dropna().copy()
    if clean["experiment_id"].nunique() < 2:
        raise ValueError("학습과 평가를 위해 서로 다른 experiment_id가 2개 이상 필요합니다.")
    return clean


def build_model() -> Pipeline:
    preprocess = ColumnTransformer([
        ("numeric", "passthrough", NUMERIC),
        ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
    ])
    regressor = RandomForestRegressor(n_estimators=300, random_state=42)
    return Pipeline([("preprocess", preprocess), ("model", regressor)])


def train_and_evaluate(data: pd.DataFrame):
    clean = validate_data(data)
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
    train_index, test_index = next(
        splitter.split(clean[FEATURES], clean[TARGETS], groups=clean["experiment_id"])
    )
    train_data, test_data = clean.iloc[train_index], clean.iloc[test_index]
    model = build_model()
    model.fit(train_data[FEATURES], train_data[TARGETS])
    prediction = model.predict(test_data[FEATURES])
    metrics = {
        "MAE": float(mean_absolute_error(test_data[TARGETS], prediction)),
        "RMSE": float(np.sqrt(mean_squared_error(test_data[TARGETS], prediction))),
        "R2": float(r2_score(test_data[TARGETS], prediction)),
    }
    comparison = test_data[["experiment_id", *TARGETS]].reset_index(drop=True)
    comparison[["pred_r", "pred_g", "pred_b"]] = prediction
    return model, metrics, comparison


def save_model(model: Pipeline, path: str | Path = "models/random_forest_rgb.joblib"):
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output)
    return output
