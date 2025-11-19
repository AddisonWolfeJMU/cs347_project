import pandas as pd
from backend.ml.utils import compute_comfort_index

def add_comfort_scores(data):
    """
    data: list of dicts or a pandas DataFrame containing forecast weather fields
    returns: DataFrame with a new 'comfort_index' column
    """

    # If the incoming data is a list of dicts (common for API calls)
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    df["comfort_index"] = df.apply(compute_comfort_index, axis=1)
    return df

def add_dates(data):
    """
    data: list of dicts or a pandas DataFrame containing forecast weather fields
    returns: DataFrame with new 'date' column extracted from 'datetime' field
    """

    # If the incoming data is a list of dicts (common for API calls)
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    return df


import pandas as pd
from backend.ml.xgboost_comfort_score import XGBoostComfortScoreModel
import joblib
import os

# Load model once at import time
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "comfort_model.pkl")
MODEL_PATH = os.path.normpath(MODEL_PATH)
model = joblib.load(MODEL_PATH)

def predict_comfort(input_row: dict) -> float:
    df = pd.DataFrame([input_row])

    numeric_cols = [
        "temp_min", "temp_max", "precipitation",
        "humidity_max", "wind_max", "cloudcover",
        "lat", "lon", "month"
    ]

    # convert first
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df[numeric_cols] = df[numeric_cols].astype(float)

    # check for NaNs
    if df[numeric_cols].isnull().any().any():
        raise ValueError(f"NaNs found in input: \n{df[numeric_cols]}")

    X = df[XGBoostComfortScoreModel.FEATURES]
    pred = model.predict(X)[0]
    return float(pred)
