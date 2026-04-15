# Crime Prediction API - Complete Guide

A FastAPI-based REST API for predicting crime counts in the London Metropolitan Police District based on year and month, using a Random Forest model.

## Features

- **Crime Prediction**: Predict crime counts for all locations (LSOA areas) for a given year and month
- **Hotspot Analysis**: Identify crime hotspots (top N% predicted areas)
- **Prediction Intervals**: 95% confidence intervals for predictions
- **Batch Processing**: Make predictions for multiple months in a single request
- **Interactive Documentation**: Swagger UI and ReDoc documentation built-in
- **Health Checks**: API health monitoring
- **Docker Support**: Easy containerization and deployment

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Running the API

#### Option A: Direct Python
```bash
python main.py
```

The API will start on `http://localhost:8000`

#### Option B: Using Uvicorn
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Option C: Docker
```bash
# Build and run with Docker Compose
docker-compose up --build
```

Or with Docker only:
```bash
docker build -t crime-prediction-api .
docker run -p 8000:8000 crime-prediction-api
```

### 3. Access the API

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### Health & Info Endpoints

#### Health Check
```
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "data_loaded": true
}
```

#### Get Model Information
```
GET /model/info
```
**Response:**
```json
{
  "model_name": "RF - tuned model",
  "target": "Crime_Count",
  "features_count": 30,
  "features": ["LSOA_Latitude", "LSOA_Longitude", ...],
  "train_years": [2020, 2021, 2022, 2023],
  "test_year": 2024,
  "metrics": {
    "MAE": 2.5432,
    "RMSE": 4.1234,
    "R2": 0.7856,
    "MAPE": 45.23
  }
}
```

#### Get Data Information
```
GET /data/info
```
**Response:**
```json
{
  "total_records": 50000,
  "years": [2024],
  "months": [1, 2, 3, ...],
  "columns": ["LSOA_Latitude", "LSOA_Longitude", ...],
  "spatial_coverage": {
    "min_latitude": 51.38,
    "max_latitude": 51.63,
    "min_longitude": -0.35,
    "max_longitude": 0.15
  }
}
```

### Prediction Endpoints

#### Basic Prediction
```
POST /predict
```

**Request:**
```json
{
  "year": 2024,
  "month": 1
}
```

**Response:**
```json
{
  "status": "success",
  "year": 2024,
  "month": 1,
  "total_predictions": 4835,
  "total_predicted_crimes": 125430.45,
  "predictions": [
    {
      "latitude": 51.5202,
      "longitude": -0.0952,
      "location_area": 6949.15,
      "location_length": 421.17,
      "population": 2172,
      "pop_density": 0.3126,
      "predicted_crime_count": 15.42,
      "prediction_interval_lower": 12.34,
      "prediction_interval_upper": 18.50
    },
    ...
  ],
  "model_name": "RF - tuned model",
  "model_mae": 2.5432,
  "model_r2": 0.7856
}
```

#### Hotspot Analysis
```
POST /predict/hotspots?hotspot_percentile=10
```

**Request:**
```json
{
  "year": 2024,
  "month": 1
}
```

**Query Parameters:**
- `hotspot_percentile` (1-50): Top N% to identify as hotspots (default: 10)

**Response:**
```json
{
  "status": "success",
  "year": 2024,
  "month": 1,
  "total_predictions": 4835,
  "total_predicted_crimes": 125430.45,
  "hotspot_analysis": {
    "hotspot_percentile": 10,
    "hotspot_threshold": 28.50,
    "hotspot_locations": 484,
    "crimes_in_hotspots": 62580.25,
    "crime_concentration": 49.85
  },
  "predictions": [
    {
      "latitude": 51.5202,
      "longitude": -0.0952,
      "location_area": 6949.15,
      "location_length": 421.17,
      "population": 2172,
      "pop_density": 0.3126,
      "predicted_crime_count": 15.42,
      "prediction_interval_lower": 12.34,
      "prediction_interval_upper": 18.50,
      "is_hotspot": false
    },
    ...
  ],
  "model_name": "RF - tuned model",
  "model_mae": 2.5432,
  "model_r2": 0.7856
}
```

#### Batch Prediction
```
POST /predict/batch
```

**Request:**
```json
{
  "requests": [
    {"year": 2024, "month": 1},
    {"year": 2024, "month": 2},
    {"year": 2024, "month": 3}
  ]
}
```

**Response:**
```json
{
  "status": "completed",
  "total_requests": 3,
  "successful": 3,
  "failed": 0,
  "results": {
    "2024-01": { ... },
    "2024-02": { ... },
    "2024-03": { ... }
  },
  "errors": null
}
```

## Usage Examples

### Python Client (Recommended)

```python
from client import CrimePredictionClient, print_predictions

# Create client
client = CrimePredictionClient("http://localhost:8000")

# Make a prediction
predictions = client.predict(year=2024, month=1)
print_predictions(predictions, limit=10)

# Get hotspot analysis
hotspots = client.predict_hotspots(year=2024, month=1, hotspot_percentile=10)

# Batch predictions
batch = client.predict_batch([
    (2024, 1),
    (2024, 2),
    (2024, 3)
])
```

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Get model info
curl http://localhost:8000/model/info

# Make a prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"year": 2024, "month": 1}'

# Get hotspots (top 10%)
curl -X POST "http://localhost:8000/predict/hotspots?hotspot_percentile=10" \
  -H "Content-Type: application/json" \
  -d '{"year": 2024, "month": 1}'
```

### Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Make prediction
response = requests.post(
    f"{BASE_URL}/predict",
    json={"year": 2024, "month": 1}
)
data = response.json()

print(f"Total predicted crimes: {data['total_predicted_crimes']:.2f}")
print(f"Locations: {data['total_predictions']}")

# Get top 5 hotspots
for pred in sorted(data['predictions'], 
                   key=lambda x: x['predicted_crime_count'], 
                   reverse=True)[:5]:
    print(f"Lat: {pred['latitude']:.4f}, "
          f"Lon: {pred['longitude']:.4f}, "
          f"Crimes: {pred['predicted_crime_count']:.2f}")
```

### JavaScript/Node.js

```javascript
const BASE_URL = 'http://localhost:8000';

async function predictCrime(year, month) {
    const response = await fetch(`${BASE_URL}/predict`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ year, month })
    });
    
    return response.json();
}

// Usage
predictCrime(2024, 1).then(data => {
    console.log(`Total crimes: ${data.total_predicted_crimes}`);
    console.log(`Locations: ${data.total_predictions}`);
});
```

## Model Information

### Features Used (30 total)

**Spatial Features:**
- LSOA_Latitude, LSOA_Longitude
- LSOA_Shape_Area, LSOA_Shape_Length

**Temporal Features:**
- Year, Month
- month_sin, month_cos (cyclical encoding)
- is_summer, is_winter, is_spring, is_autumn

**Demographic Features:**
- Total_Population, pop_density
- income_per_capita, Income_Deprivation

**Weather Features:**
- Max_Temperature_Celsius, Min_Temperature_Celsius
- Rainfall_mm, Sunshine_Hours, Air_Frost_Days

**Lagged Crime Features:**
- crime_lag_1m, crime_lag_2m, crime_lag_3m, crime_lag_6m
- crime_rolling_3m_mean, crime_rolling_3m_std
- crime_rolling_6m_mean, crime_rolling_6m_std
- msoa_avg_crime

### Model Performance

```
Model: Random Forest Regressor
Training Years: 2020-2023
Test Year: 2024
Training Samples: ~385,600
Test Samples: ~48,350

Metrics:
  - MAE (Mean Absolute Error): ~2.54
  - RMSE (Root Mean Squared Error): ~4.12
  - R² Score: ~0.79
  - MAPE (Mean Absolute Percentage Error): ~45.23%
```

## Data Requirements

The API expects two files in the working directory:

1. **crime_data_2024.csv** - Crime data with all required features
   - Must contain all features listed above
   - Should include multiple years and months
   - CSV format with headers

2. **random_forest_model.joblib** - Trained model package
   - Contains the model, features list, and metrics
   - Created by the training script
   - Binary joblib format

## Error Handling

### Common Errors

```
404 - No data found for year=2024, month=13
  → Invalid month (must be 1-12)

404 - No data found for year=2030, month=1
  → Year not available in dataset

503 - Model not loaded
  → Model file not found or failed to load

503 - Crime data not loaded
  → Crime data file not found or failed to load
```

## Performance

- **Single Prediction**: ~50-200ms (depends on number of locations)
- **Hotspot Analysis**: ~75-300ms
- **Batch (3 months)**: ~200-600ms

## Deployment

### Local Development
```bash
uvicorn main:app --reload --port 8000
```

### Production
```bash
# Using Gunicorn with Uvicorn workers
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Production
```bash
docker build -t crime-prediction-api .
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/crime_data_2024.csv:/app/crime_data_2024.csv:ro \
  -v $(pwd)/random_forest_model.joblib:/app/random_forest_model.joblib:ro \
  crime-prediction-api
```

## Monitoring

Check the startup logs for model loading:

```
[STARTUP] Loading crime prediction model...
✓ Model loaded: RF - tuned model
✓ Features: 30 features
✓ Metrics - MAE: 2.5432, R²: 0.7856
✓ Crime data loaded: 50000 records
✓ Years available: [2024]
✓ Months available: [1, 2, 3, ..., 12]
```

## API Response Times

```
Endpoint                    Time (ms)    Notes
/health                     5-10         Very fast health check
/model/info                 5-10         Metadata only
/data/info                  20-50        Quick aggregation
/predict (1 month)          100-300      Depends on location count
/predict/hotspots           150-400      Includes analysis
/predict/batch (3 items)    300-900      Parallel processing
```

## Troubleshooting

### Model not loading
- Check file path: `random_forest_model.joblib`
- Verify file permissions
- Check file is valid joblib format

### No data found for year/month
- Check available data: `GET /data/info`
- Verify year and month in dataset
- Ensure CSV has been loaded correctly

### High prediction latency
- Check API server resources
- Monitor CPU/memory usage
- Consider running multiple API instances with load balancer

## Contributing

To extend the API:

1. Add new endpoints in `main.py`
2. Update request/response models in Pydantic
3. Test with various year/month combinations
4. Update documentation

## License

This project is part of the Predictive Policing initiative for the London Metropolitan Police District.
