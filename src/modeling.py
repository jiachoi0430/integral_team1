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

FEATURES = ["adsorbent", "adsorbent_mass_g", "dye_concentration", "time_min"]
TARGETS = ["r", "g", "b", "clear"]
REQUIRED_COLUMNS = ["experiment_id", *FEATURES, *TARGETS]
NUMERIC = ["adsorbent_mass_g", "dye_concentration", "time_min"]


def validate_data(data: pd.DataFrame) -> pd.DataFrame:
    missing = [name for name in REQUIRED_COLUMNS if name not in data.columns]
    if missing:
        raise ValueError(f"필수 열이 없습니다: {', '.join(missing)}")
    clean = data.loc[~data["experiment_id"].astype(str).str.startswith("#"), REQUIRED_COLUMNS].copy()
    for name in [*NUMERIC, *TARGETS]:
        clean[name] = pd.to_numeric(clean[name], errors="coerce")
    clean = clean.dropna(subset=REQUIRED_COLUMNS)
    if clean["experiment_id"].nunique() < 4:
        raise ValueError("실험 회차가 부족합니다. 독립된 experiment_id를 최소 4개 이상 확보한 뒤 평가하세요.")
    if (clean["adsorbent_mass_g"] < 0).any() or (clean["time_min"] < 0).any():
        raise ValueError("흡착제 질량과 경과 시간은 음수가 될 수 없습니다.")
    return clean


def build_model() -> Pipeline:
    preprocess = ColumnTransformer([
        ("numeric", "passthrough", NUMERIC),
        ("categorical", OneHotEncoder(handle_unknown="ignore"), ["adsorbent"]),
    ])
    return Pipeline([
        ("preprocess", preprocess),
        ("model", RandomForestRegressor(n_estimators=300, random_state=42)),
    ])


def train_and_evaluate(data: pd.DataFrame):
    clean = validate_data(data)
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
    train_idx, test_idx = next(
        splitter.split(clean[FEATURES], clean[TARGETS], groups=clean["experiment_id"])
    )
    train_data, test_data = clean.iloc[train_idx], clean.iloc[test_idx]
    model = build_model()
    model.fit(train_data[FEATURES], train_data[TARGETS])
    prediction = model.predict(test_data[FEATURES])
    actual = test_data[TARGETS]
    metrics = {
        "MAE": float(mean_absolute_error(actual, prediction)),
        "RMSE": float(np.sqrt(mean_squared_error(actual, prediction))),
        "R2": float(r2_score(actual, prediction)) if len(test_data) >= 2 else float("nan"),
    }
    comparison = test_data[["experiment_id", *TARGETS]].reset_index(drop=True).copy()
    comparison[[f"pred_{target}" for target in TARGETS]] = prediction
    return model, metrics, comparison


def save_model(model: Pipeline, path: str | Path = "models/random_forest_rgb_clear.joblib"):
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output)
    return output
