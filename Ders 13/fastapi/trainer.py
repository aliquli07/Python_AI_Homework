import os
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "housing_az_realistic.csv"
MODEL_PATH = BASE_DIR / "models" / "models_az.pkl"

FEATURES = ["Bedrooms", "Bathrooms", "Sqm", "City"]
TARGET = "PriceAZN"


def build_pipeline():
    numeric_features = ["Bedrooms", "Bathrooms", "Sqm"]
    categorical_features = ["City"]

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer(transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features)
    ])

    rf = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)

    return Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", rf)
    ])


def train(data):
    X = data[FEATURES]
    y = data[TARGET].astype(float)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipe = build_pipeline()
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)

    metrics = {
        "mae": round(float(mean_absolute_error(y_test, y_pred)), 2),
        "mse": round(float(mse), 2),
        "rmse": round(float(np.sqrt(mse)), 2),
        "r2": round(float(r2_score(y_test, y_pred)), 4),
    }

    bundle = {
        "pipeline": pipe,
        "featured_order": FEATURES,
    }

    return bundle, metrics, len(data)


def save_bundle(bundle):
    tmp_path = MODEL_PATH.with_suffix(".tmp")
    joblib.dump(bundle, tmp_path)
    os.replace(tmp_path, MODEL_PATH)


if __name__ == "__main__":
    data = pd.read_csv(DATA_PATH)
    bundle, metrics, rows = train(data)
    save_bundle(bundle)
    print("Rows:", rows)
    print(metrics)
    print("Saved:", MODEL_PATH, datetime.now().isoformat(timespec="seconds"))
