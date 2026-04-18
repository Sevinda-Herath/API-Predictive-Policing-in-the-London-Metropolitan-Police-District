from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, model_validator

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "crime_data_2024.csv"
MODEL_PATH = BASE_DIR / "random_forest_model.joblib"
MODEL_COMPARISON_GENERIC_PATH = BASE_DIR / "model_comparison_generic.csv"
MODEL_COMPARISON_SPECIFIC_PATH = BASE_DIR / "model_comparison_specific.csv"
HDA_IMAGE_PATH = BASE_DIR / "hda.png"
MPC_IMAGE_PATH = BASE_DIR / "mpc.png"

app = FastAPI(
    title="Crime Count Prediction API",
    description=(
        "Predict crime count using a trained Random Forest model by providing "
        "LSOA code or LSOA name with year and month."
    ),
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)


class PredictRequest(BaseModel):
    lsoa_code: str | None = Field(default=None, description="LSOA code, e.g. E01000001")
    lsoa_name: str | None = Field(default=None, description="LSOA name")
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)

    @model_validator(mode="after")
    def validate_lsoa_input(self) -> "PredictRequest":
        if not self.lsoa_code and not self.lsoa_name:
            raise ValueError("Provide either lsoa_code or lsoa_name.")
        return self


class HotspotsRequest(BaseModel):
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)
    top_x: int = Field(default=10, ge=1, le=500)


# Cache data and model at startup.
_df: pd.DataFrame | None = None
_model: Any = None
_features_used: list[str] = []
_target_name: str = "Crime_Count"


def _load_assets() -> None:
    global _df, _model, _features_used, _target_name

    if not DATA_PATH.exists():
        raise RuntimeError(f"Data file not found: {DATA_PATH}")
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model file not found: {MODEL_PATH}")

    _df = pd.read_csv(DATA_PATH)

    model_package = joblib.load(MODEL_PATH)
    if not isinstance(model_package, dict) or "model" not in model_package:
        raise RuntimeError("Model artifact format is invalid.")

    _model = model_package["model"]
    _features_used = list(model_package.get("features_used", []))
    _target_name = str(model_package.get("target", "Crime_Count"))

    if not _features_used:
        raise RuntimeError("No feature list found in model artifact.")

    missing = [f for f in _features_used if f not in _df.columns]
    if missing:
        raise RuntimeError(f"Missing required feature columns in CSV: {missing}")


@app.on_event("startup")
def on_startup() -> None:
    _load_assets()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Crime Count Prediction API is running.",
        "swagger_docs": "/docs",
        "openapi_schema": "/openapi.json",
        "model_comparison_generic": "/model-comparison/generic",
        "model_comparison_specific": "/model-comparison/specific",
        "image_hda": "/images/hda",
        "image_mpc": "/images/mpc",
    }


def _ensure_loaded() -> None:
    if _df is None or _model is None or not _features_used:
        _load_assets()


def _lookup_row(lsoa_code: str | None, lsoa_name: str | None, year: int, month: int) -> pd.Series:
    assert _df is not None

    filt = (_df["Year"] == year) & (_df["Month"] == month)
    if lsoa_code:
        filt = filt & (_df["LSOA_Code"].str.lower() == lsoa_code.strip().lower())
    elif lsoa_name:
        filt = filt & (_df["LSOA_Name"].str.lower() == lsoa_name.strip().lower())

    matches = _df.loc[filt]
    if matches.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                "No matching row found in CSV for the provided LSOA and date. "
                "Check LSOA code/name, year, and month."
            ),
        )

    # Keep deterministic behavior if duplicates exist.
    return matches.iloc[0]


def _predict_from_rows(rows: pd.DataFrame) -> np.ndarray:
    assert _model is not None
    features = rows[_features_used].astype(float)
    preds = _model.predict(features)
    return np.clip(preds, 0, None)


@app.get("/model-comparison/generic")
def get_model_comparison_generic() -> dict[str, Any]:
    if not MODEL_COMPARISON_GENERIC_PATH.exists():
        raise HTTPException(status_code=404, detail="model_comparison_generic.csv not found.")

    data = pd.read_csv(MODEL_COMPARISON_GENERIC_PATH)
    return {"rows": data.to_dict(orient="records")}


@app.get("/model-comparison/specific")
def get_model_comparison_specific() -> dict[str, Any]:
    if not MODEL_COMPARISON_SPECIFIC_PATH.exists():
        raise HTTPException(status_code=404, detail="model_comparison_specific.csv not found.")

    data = pd.read_csv(MODEL_COMPARISON_SPECIFIC_PATH)
    return {"rows": data.to_dict(orient="records")}


@app.get("/images/hda")
def get_hda_image() -> FileResponse:
    if not HDA_IMAGE_PATH.exists():
        raise HTTPException(status_code=404, detail="hda.png not found.")
    return FileResponse(path=HDA_IMAGE_PATH, media_type="image/png", filename="hda.png")


@app.get("/images/mpc")
def get_mpc_image() -> FileResponse:
    if not MPC_IMAGE_PATH.exists():
        raise HTTPException(status_code=404, detail="mpc.png not found.")
    return FileResponse(path=MPC_IMAGE_PATH, media_type="image/png", filename="mpc.png")


@app.post("/predict")
def predict_crime_count(payload: PredictRequest) -> dict[str, Any]:
    _ensure_loaded()
    row = _lookup_row(payload.lsoa_code, payload.lsoa_name, payload.year, payload.month)

    preds = _predict_from_rows(pd.DataFrame([row]))
    pred_value = float(np.round(preds[0], 4))

    return {
        "lsoa_code": str(row["LSOA_Code"]),
        "lsoa_name": str(row["LSOA_Name"]),
        "year": int(row["Year"]),
        "month": int(row["Month"]),
        "predicted_crime_count": pred_value,
        "target": _target_name,
    }


@app.post("/hotspots/top")
def top_hotspots(payload: HotspotsRequest) -> dict[str, Any]:
    _ensure_loaded()
    assert _df is not None

    subset = _df[(_df["Year"] == payload.year) & (_df["Month"] == payload.month)].copy()
    if subset.empty:
        raise HTTPException(
            status_code=404,
            detail="No rows found for the given year and month.",
        )

    preds = _predict_from_rows(subset)
    subset["predicted_crime_count"] = np.round(preds, 4)

    top = (
        subset[["LSOA_Code", "LSOA_Name", "predicted_crime_count"]]
        .sort_values("predicted_crime_count", ascending=False)
        .head(payload.top_x)
    )

    hotspots = [
        {
            "rank": idx + 1,
            "lsoa_code": str(row["LSOA_Code"]),
            "lsoa_name": str(row["LSOA_Name"]),
            "predicted_crime_count": float(row["predicted_crime_count"]),
        }
        for idx, (_, row) in enumerate(top.iterrows())
    ]

    return {
        "year": payload.year,
        "month": payload.month,
        "top_x": payload.top_x,
        "hotspots": hotspots,
    }
