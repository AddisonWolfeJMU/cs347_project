import os
import sys
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import joblib

# -------------------------------------------------------------------
# FIX: Add project root so we can import backend.ml.*
# -------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(PROJECT_ROOT)

# Now imports from backend work
from backend.ml.xgboost_comfort_score import XGBoostComfortScoreModel

# -------------------------------------------------------------------
# Load Dataset
# -------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "historical_weather_scored.csv")
DATA_PATH = os.path.normpath(DATA_PATH)

df = pd.read_csv(DATA_PATH)

# Ensure date is parsed
df["date"] = pd.to_datetime(df["date"])
df["month"] = df["date"].dt.month

# -------------------------------------------------------------------
# Prepare features
# -------------------------------------------------------------------
features = XGBoostComfortScoreModel.FEATURES
X = df[features]
y = df["comfort_index"]

# Train/validation split
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------------------------------------------
# Train Model
# -------------------------------------------------------------------
model_def = XGBoostComfortScoreModel()
xgb_model = model_def.xgb_model

xgb_model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    verbose=False
)

best = xgb_model.best_iteration + 1

y_train_pred = xgb_model.predict(X_train, iteration_range=(0, best))
y_val_pred   = xgb_model.predict(X_val,   iteration_range=(0, best))

train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
val_rmse   = np.sqrt(mean_squared_error(y_val,   y_val_pred))

print(f"\nBest trees: {best}")
print(f"Train RMSE: {train_rmse:.2f}")
print(f"Valid RMSE: {val_rmse:.2f}")

# -------------------------------------------------------------------
# Save model
# -------------------------------------------------------------------
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "comfort_model.pkl")
MODEL_PATH = os.path.normpath(MODEL_PATH)

joblib.dump(xgb_model, MODEL_PATH)
print(f"\nModel saved to: {MODEL_PATH}")
