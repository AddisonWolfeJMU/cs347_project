import xgboost as xgb

class XGBoostComfortScoreModel:
    """
    Defines the comfort score regression model architecture
    and maintains a centralized feature list.
    """

    # Class-level feature list (shared between training & inference)
    FEATURES = [
        "temp_min",
        "temp_max",
        "precipitation",
        "humidity_max",
        "wind_max",
        "lat",
        "lon",
        "cloudcover",
        "month",           
    ]

    def __init__(self):
        self.xgb_model = xgb.XGBRegressor(
        n_estimators=6000,        # deeper trees → fewer needed
        learning_rate=0.03,       # keep LR constant for stability
        max_depth=3,              # from 3 → 6 (massive improvement)
        min_child_weight=6,       # from 6 → 1 (lets spikes form)
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=5,
        random_state=42,
        early_stopping_rounds=150,
        )
        