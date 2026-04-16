import joblib
import numpy as np
import pandas as pd
import os

# Load model at import time
MODEL_PATH = os.path.join(os.path.dirname(__file__), "xgb_pipeline.joblib")
model = joblib.load(MODEL_PATH)

# Training stats for Stage 2 context
TRAIN_STATS = {
    "median_price": 161625,
    "mean_price": 180208,
    "min_price": 12789,
    "max_price": 745000,
    "q25": 129900,
    "q75": 212500,
    "year_built_range": "1872-2010",
    "year_built_median": 1973,
    "gr_liv_area_median": 1442,
    "overall_qual_median": 6
}

# Default values for missing features (training set medians/modes)
DEFAULTS = {
    "Overall Qual": 6,
    "Gr Liv Area": 1442.0,
    "Total Bsmt SF": 988.0,
    "Garage Cars": 2,
    "Garage Finish": "Unf",
    "Fireplaces": 1,
    "Kitchen Qual": "TA",
    "Neighborhood": "NAmes",
    "Year Built": 1973,
    "Year Remod/Add": 1993,
    "Full Bath": 2,
    "Half Bath": 0
}


def predict_price(features) -> float:
    """Take extracted features, apply engineering, and predict price."""

    feature_dict = {
        "Overall Qual": features.overall_qual or DEFAULTS["Overall Qual"],
        "Gr Liv Area": features.gr_liv_area or DEFAULTS["Gr Liv Area"],
        "Total Bsmt SF": features.total_bsmt_sf or DEFAULTS["Total Bsmt SF"],
        "Garage Cars": features.garage_cars if features.garage_cars is not None else DEFAULTS["Garage Cars"],
        "Garage Finish": features.garage_finish or DEFAULTS["Garage Finish"],
        "Fireplaces": features.fireplaces if features.fireplaces is not None else DEFAULTS["Fireplaces"],
        "Kitchen Qual": features.kitchen_qual or DEFAULTS["Kitchen Qual"],
        "Neighborhood": features.neighborhood or DEFAULTS["Neighborhood"],
        "Year Built": features.year_built or DEFAULTS["Year Built"],
        "Year Remod/Add": features.year_remod or features.year_built or DEFAULTS["Year Remod/Add"],
        "Full Bath": features.full_bath if features.full_bath is not None else DEFAULTS["Full Bath"],
        "Half Bath": features.half_bath if features.half_bath is not None else DEFAULTS["Half Bath"]
    }

    # Feature engineering (same as training)
    input_df = pd.DataFrame([feature_dict])
    input_df["Years Since Remod"] = input_df["Year Remod/Add"].max() - input_df["Year Remod/Add"]
    input_df["House Age"] = input_df["Year Built"].max() - input_df["Year Built"]
    input_df["Total Bath"] = input_df["Full Bath"] + (0.5 * input_df["Half Bath"])
    input_df = input_df.drop(columns=["Year Built", "Year Remod/Add", "Full Bath", "Half Bath"])

    # Predict (model was trained on log scale)
    log_price = model.predict(input_df)[0]
    return float(np.expm1(log_price))