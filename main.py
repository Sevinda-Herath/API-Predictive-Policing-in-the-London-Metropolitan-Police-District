"""
Crime Prediction API using FastAPI
Predicts crime count for London Metropolitan Police District based on Year and Month
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# CONFIGURATION
# =============================================================================
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "crime_data_2024.csv"
MODEL_PATH = BASE_DIR / "random_forest_model.joblib"

# Model features in the correct order
FEATURES = [
    "LSOA_Latitude",
    "LSOA_Longitude",
    "LSOA_Shape_Area",
    "LSOA_Shape_Length",
    "Year",
    "Month",
    "month_sin",
    "month_cos",
    "is_summer",
    "is_winter",
    "is_spring",
    "is_autumn",
    "Total_Population",
    "pop_density",
    "income_per_capita",
    "Income_Deprivation",
    "Max_Temperature_Celsius",
    "Min_Temperature_Celsius",
    "Rainfall_mm",
    "Sunshine_Hours",
    "Air_Frost_Days",
    "crime_lag_1m",
    "crime_lag_2m",
    "crime_lag_3m",
    "crime_lag_6m",
    "crime_rolling_3m_mean",
    "crime_rolling_3m_std",
    "crime_rolling_6m_mean",
    "crime_rolling_6m_std",
    "msoa_avg_crime",
]

# Global variables to store loaded model and data
model_package = None
crime_df = None
location_column = None

LOCATION_COLUMN_CANDIDATES = [
    "LSOA_Name",
    "LSOA name",
    "LSOA_NAME",
    "LSOA_Code",
    "LSOA code",
    "LSOA_CODE",
]
FALLBACK_LOCATION_COLUMN = "LSOA_Name"


def resolve_location_column(df: pd.DataFrame) -> Optional[str]:
    """Pick the first available location-like column from known candidates."""
    for col in LOCATION_COLUMN_CANDIDATES:
        if col in df.columns:
            return col
    return None


# =============================================================================
# PYDANTIC MODELS (Request/Response schemas)
# =============================================================================
class PredictionRequest(BaseModel):
    """Request schema for crime prediction"""
    year: int = Field(..., description="Year (e.g., 2024)")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    location_name: str = Field(..., description="LSOA location name")


class CrimePrediction(BaseModel):
    """Individual crime prediction for a location"""
    location_name: str
    latitude: float
    longitude: float
    location_area: float
    location_length: float
    population: int
    pop_density: float
    predicted_crime_count: float
    prediction_interval_lower: Optional[float] = None
    prediction_interval_upper: Optional[float] = None


class PredictionResponse(BaseModel):
    """Response schema for crime predictions"""
    model_config = ConfigDict(protected_namespaces=())

    status: str
    year: int
    month: int
    location_name: str
    total_predictions: int
    total_predicted_crimes: float
    predictions: List[CrimePrediction]
    model_name: str
    model_mae: float
    model_r2: float


# =============================================================================
# STARTUP/SHUTDOWN
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model and data on startup, cleanup on shutdown"""
    global model_package, crime_df, location_column
    
    print("[STARTUP] Loading crime prediction model...")
    
    # Load model
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
    
    model_package = joblib.load(MODEL_PATH)
    print(f"✓ Model loaded: {model_package['model_name']}")
    print(f"✓ Features: {len(model_package['features_used'])} features")
    print(f"✓ Metrics - MAE: {model_package['metrics']['MAE']:.4f}, R²: {model_package['metrics']['R2']:.4f}")
    
    # Load crime data
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Data not found at {DATA_PATH}")
    
    crime_df = pd.read_csv(DATA_PATH)

    # Resolve location column, or build a stable fallback if source data has no LSOA name/code.
    location_column = resolve_location_column(crime_df)
    if location_column is None:
        crime_df[FALLBACK_LOCATION_COLUMN] = (
            "LSOA_"
            + crime_df["LSOA_Latitude"].astype(float).round(5).astype(str)
            + "_"
            + crime_df["LSOA_Longitude"].astype(float).round(5).astype(str)
        )
        location_column = FALLBACK_LOCATION_COLUMN
        print(
            "! No LSOA name/code column found; generated fallback names "
            "from coordinates in column 'LSOA_Name'."
        )

    if location_column != FALLBACK_LOCATION_COLUMN:
        crime_df[FALLBACK_LOCATION_COLUMN] = crime_df[location_column].astype(str)
        location_column = FALLBACK_LOCATION_COLUMN

    print(f"✓ Crime data loaded: {len(crime_df):,} records")
    print(f"✓ Years available: {sorted(crime_df['Year'].unique())}")
    print(f"✓ Months available: {sorted(crime_df['Month'].unique())}")
    print(f"✓ Location column used: {location_column}")
    
    yield
    
    print("[SHUTDOWN] Cleaning up...")


# =============================================================================
# CREATE APP
# =============================================================================
app = FastAPI(
    title="Crime Prediction API",
    description="Predict crime counts for London Metropolitan Police District",
    version="1.0.0",
    lifespan=lifespan,
)


# =============================================================================
# HEALTH CHECK
# =============================================================================
@app.get("/health", tags=["Health"])
async def health_check():
    """Check if API is running and model is loaded"""
    return {
        "status": "healthy",
        "model_loaded": model_package is not None,
        "data_loaded": crime_df is not None,
    }


# =============================================================================
# MODEL INFO
# =============================================================================
@app.get("/model/info", tags=["Model Info"])
async def model_info():
    """Get information about the loaded model"""
    if model_package is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_name": model_package["model_name"],
        "target": model_package["target"],
        "features_count": len(model_package["features_used"]),
        "features": model_package["features_used"],
        "train_years": model_package["train_years"],
        "test_year": model_package["test_year"],
        "metrics": model_package["metrics"],
        "is_no_lag_model": model_package["is_no_lag_model"],
    }


# =============================================================================
# PREDICTION ENDPOINT
# =============================================================================
@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict_crime(request: PredictionRequest):
    """
    Predict crime count for a given year, month, and location.
    
    **Parameters:**
    - year: The year (e.g., 2024)
    - month: The month (1-12)
    - location_name: LSOA location name
    
    **Returns:**
    - Prediction for the requested location
    - Total predicted crimes (for matched rows)
    - Confidence intervals
    """
    
    if model_package is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    if crime_df is None:
        raise HTTPException(status_code=503, detail="Crime data not loaded")
    
    year = request.year
    month = request.month
    location_name = request.location_name.strip()
    
    # Filter data for the requested year, month, and location (case-insensitive)
    mask = (
        (crime_df["Year"] == year)
        & (crime_df["Month"] == month)
        & (crime_df[location_column].astype(str).str.casefold() == location_name.casefold())
    )
    data_subset = crime_df[mask].copy()
    
    if len(data_subset) == 0:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No data found for year={year}, month={month}, "
                f"location_name='{location_name}'"
            ),
        )
    
    # Prepare features for prediction
    model_features = model_package["features_used"]
    X = data_subset[model_features].copy()
    
    # Check for missing values
    if X.isnull().any().any():
        print(f"Warning: Found {X.isnull().sum().sum()} missing values, filling with 0")
        X = X.fillna(0)
    
    # Get model and make predictions
    model = model_package["model"]
    y_pred_mean = model.predict(X)
    
    # Clip negative predictions to 0
    y_pred_mean = np.clip(y_pred_mean, 0, None)
    
    # Calculate prediction intervals using tree predictions
    all_tree_preds = np.array([tree.predict(X) for tree in model.estimators_])
    pred_std = all_tree_preds.std(axis=0)
    pred_low = np.clip(y_pred_mean - 1.96 * pred_std, 0, None)
    pred_high = y_pred_mean + 1.96 * pred_std
    
    # Build response predictions
    predictions = []
    for idx, (_, row) in enumerate(data_subset.iterrows()):
        pred = CrimePrediction(
            location_name=str(row[location_column]),
            latitude=float(row["LSOA_Latitude"]),
            longitude=float(row["LSOA_Longitude"]),
            location_area=float(row["LSOA_Shape_Area"]),
            location_length=float(row["LSOA_Shape_Length"]),
            population=int(row["Total_Population"]),
            pop_density=float(row["pop_density"]),
            predicted_crime_count=float(np.round(y_pred_mean[idx], 2)),
            prediction_interval_lower=float(np.round(pred_low[idx], 2)),
            prediction_interval_upper=float(np.round(pred_high[idx], 2)),
        )
        predictions.append(pred)
    
    # Sort by predicted crime count (highest first)
    predictions.sort(key=lambda x: x.predicted_crime_count, reverse=True)
    
    return PredictionResponse(
        status="success",
        year=year,
        month=month,
        location_name=location_name,
        total_predictions=len(predictions),
        total_predicted_crimes=float(np.sum(y_pred_mean)),
        predictions=predictions,
        model_name=model_package["model_name"],
        model_mae=model_package["metrics"]["MAE"],
        model_r2=model_package["metrics"]["R2"],
    )


# =============================================================================
# PREDICTION WITH HOTSPOT ANALYSIS
# =============================================================================
@app.post("/predict/hotspots", tags=["Predictions"])
async def predict_crime_hotspots(
    request: PredictionRequest,
    hotspot_percentile: int = Query(10, ge=1, le=50, description="Top N percentile to identify (1-50)")
):
    """
    Predict crime and identify top hotspot locations.
    
    **Parameters:**
    - year: The year (e.g., 2024)
    - month: The month (1-12)
    - location_name: LSOA location name
    - hotspot_percentile: Top N% to mark as hotspots (default: 10)
    
    **Returns:**
    - All predictions with hotspot flags
    - Hotspot statistics
    """
    
    if model_package is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    if crime_df is None:
        raise HTTPException(status_code=503, detail="Crime data not loaded")
    
    year = request.year
    month = request.month
    location_name = request.location_name.strip()
    
    # Filter data
    mask = (
        (crime_df["Year"] == year)
        & (crime_df["Month"] == month)
        & (crime_df[location_column].astype(str).str.casefold() == location_name.casefold())
    )
    data_subset = crime_df[mask].copy()
    
    if len(data_subset) == 0:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No data found for year={year}, month={month}, "
                f"location_name='{location_name}'"
            ),
        )
    
    # Prepare features
    model_features = model_package["features_used"]
    X = data_subset[model_features].copy()
    if X.isnull().any().any():
        X = X.fillna(0)
    
    # Predict
    model = model_package["model"]
    y_pred = np.clip(model.predict(X), 0, None)
    
    # Calculate prediction intervals
    all_tree_preds = np.array([tree.predict(X) for tree in model.estimators_])
    pred_std = all_tree_preds.std(axis=0)
    pred_low = np.clip(y_pred - 1.96 * pred_std, 0, None)
    pred_high = y_pred + 1.96 * pred_std
    
    # Identify hotspots based on percentile
    threshold = np.percentile(y_pred, 100 - hotspot_percentile)
    is_hotspot = y_pred >= threshold
    
    # Build response
    predictions_with_hotspots = []
    for idx, (_, row) in enumerate(data_subset.iterrows()):
        predictions_with_hotspots.append({
            "location_name": str(row[location_column]),
            "latitude": float(row["LSOA_Latitude"]),
            "longitude": float(row["LSOA_Longitude"]),
            "location_area": float(row["LSOA_Shape_Area"]),
            "location_length": float(row["LSOA_Shape_Length"]),
            "population": int(row["Total_Population"]),
            "pop_density": float(row["pop_density"]),
            "predicted_crime_count": float(np.round(y_pred[idx], 2)),
            "prediction_interval_lower": float(np.round(pred_low[idx], 2)),
            "prediction_interval_upper": float(np.round(pred_high[idx], 2)),
            "is_hotspot": bool(is_hotspot[idx]),
        })
    
    # Sort by predicted crime
    predictions_with_hotspots.sort(key=lambda x: x["predicted_crime_count"], reverse=True)
    
    hotspot_count = np.sum(is_hotspot)
    hotspot_crimes = np.sum(y_pred[is_hotspot])
    total_crimes = np.sum(y_pred)
    
    return {
        "status": "success",
        "year": year,
        "month": month,
        "location_name": location_name,
        "total_predictions": len(predictions_with_hotspots),
        "total_predicted_crimes": float(total_crimes),
        "hotspot_analysis": {
            "hotspot_percentile": hotspot_percentile,
            "hotspot_threshold": float(np.round(threshold, 2)),
            "hotspot_locations": int(hotspot_count),
            "crimes_in_hotspots": float(np.round(hotspot_crimes, 2)),
            "crime_concentration": float(np.round(hotspot_crimes / total_crimes * 100, 2)) if total_crimes > 0 else 0,
        },
        "predictions": predictions_with_hotspots,
        "model_name": model_package["model_name"],
        "model_mae": model_package["metrics"]["MAE"],
        "model_r2": model_package["metrics"]["R2"],
    }


# =============================================================================
# BATCH PREDICTION
# =============================================================================
@app.post("/predict/batch", tags=["Predictions"])
async def predict_batch(requests: List[PredictionRequest]):
    """
    Predict crime for multiple year-month combinations.
    
    **Parameters:**
    - List of {year, month, location_name} objects
    
    **Returns:**
    - Dictionary with predictions for each month
    """
    
    results = {}
    errors = {}
    
    for req in requests:
        key = f"{req.year}-{req.month:02d}-{req.location_name}"
        try:
            # Reuse single prediction logic
            response = await predict_crime(req)
            results[key] = response
        except Exception as e:
            errors[key] = str(e)
    
    return {
        "status": "completed",
        "total_requests": len(requests),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors if errors else None,
    }


# =============================================================================
# DATA INFO
# =============================================================================
@app.get("/data/info", tags=["Data Info"])
async def data_info():
    """Get information about the loaded crime dataset"""
    if crime_df is None:
        raise HTTPException(status_code=503, detail="Crime data not loaded")
    
    return {
        "total_records": len(crime_df),
        "total_locations": int(crime_df[location_column].nunique()),
        "location_column": location_column,
        "years": sorted(crime_df["Year"].unique().tolist()),
        "months": sorted(crime_df["Month"].unique().tolist()),
        "columns": crime_df.columns.tolist(),
        "spatial_coverage": {
            "min_latitude": float(crime_df["LSOA_Latitude"].min()),
            "max_latitude": float(crime_df["LSOA_Latitude"].max()),
            "min_longitude": float(crime_df["LSOA_Longitude"].min()),
            "max_longitude": float(crime_df["LSOA_Longitude"].max()),
        },
    }


@app.get("/locations", tags=["Data Info"])
async def list_locations(
    limit: int = Query(100, ge=1, le=5000),
    year: Optional[int] = Query(None, description="Optional year filter"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Optional month filter"),
):
    """List available location names for client input, with optional time filters."""
    if crime_df is None:
        raise HTTPException(status_code=503, detail="Crime data not loaded")

    subset = crime_df
    if year is not None:
        subset = subset[subset["Year"] == year]
    if month is not None:
        subset = subset[subset["Month"] == month]

    locations = sorted(subset[location_column].astype(str).dropna().unique().tolist())
    return {
        "location_column": location_column,
        "total_locations": len(locations),
        "returned": min(limit, len(locations)),
        "filters": {"year": year, "month": month},
        "locations": locations[:limit],
    }


# =============================================================================
# ROOT
# =============================================================================
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint with documentation links"""
    return {
        "name": "Crime Prediction API",
        "version": "1.0.0",
        "description": "Predict crime counts for London Metropolitan Police District",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "endpoints": {
            "health": "/health",
            "model_info": "/model/info",
            "data_info": "/data/info",
            "locations": "/locations",
            "predict": "/predict",
            "predict_hotspots": "/predict/hotspots",
            "predict_batch": "/predict/batch",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
