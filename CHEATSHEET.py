#!/usr/bin/env python3
"""
Crime Prediction API - Quick Reference Cheatsheet
A handy reference for the most common API operations
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                 CRIME PREDICTION API - QUICK REFERENCE                     ║
║                London Metropolitan Police District                         ║
╚════════════════════════════════════════════════════════════════════════════╝

📍 API URL: http://localhost:8000
📚 Docs: http://localhost:8000/docs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 QUICK START
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Install & Start:
   $ pip install -r requirements.txt
   $ python main.py

2. Test in Browser:
   Open: http://localhost:8000/docs

3. Python Example:
   from client import CrimePredictionClient
   client = CrimePredictionClient()
   predictions = client.predict(year=2024, month=1)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔌 API ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Health & Info:
  GET  /health                      Check API is running
  GET  /model/info                  Model details & metrics
  GET  /data/info                   Dataset information

Predictions:
  POST /predict                     Crime prediction for year/month
  POST /predict/hotspots            Identify hotspot locations
  POST /predict/batch               Multiple predictions at once

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐚 CURL EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Health Check
$ curl http://localhost:8000/health

# Basic Prediction
$ curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d '{"year": 2024, "month": 1}'

# Hotspot Analysis (Top 10%)
$ curl -X POST "http://localhost:8000/predict/hotspots?hotspot_percentile=10" \\
  -H "Content-Type: application/json" \\
  -d '{"year": 2024, "month": 1}'

# Model Information
$ curl http://localhost:8000/model/info

# Data Information
$ curl http://localhost:8000/data/info

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐍 PYTHON CLIENT EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Initialize
from client import CrimePredictionClient

client = CrimePredictionClient()

# Get Model Info
info = client.get_model_info()

# Get Data Info
data_info = client.get_data_info()

# Make Prediction
predictions = client.predict(year=2024, month=1)

# Get Hotspots
hotspots = client.predict_hotspots(
    year=2024, month=1, hotspot_percentile=10
)

# Batch Predictions
batch = client.predict_batch([
    (2024, 1),
    (2024, 2),
    (2024, 3),
])

# Print Results
from client import print_predictions, print_hotspot_analysis

print_predictions(predictions, limit=10)
print_hotspot_analysis(hotspots, limit=15)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 REQUEST/RESPONSE FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REQUEST (Prediction):
{
  "year": 2024,
  "month": 1
}

RESPONSE (Prediction):
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
      "predicted_crime_count": 15.42,
      "prediction_interval_lower": 12.34,
      "prediction_interval_upper": 18.50,
      "population": 2172
    }
  ],
  "model_mae": 4.3771,
  "model_r2": 0.9486
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 AVAILABLE DATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Years:     2024 (full year)
Months:    1-12 (all months available)
Locations: 4,835 LSOA areas
Records:   62,626 total

Valid Year/Month Combinations:
  2024-01 through 2024-12 ✓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ PERFORMANCE METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Endpoint                Type        Time         Data Points
────────────────────────────────────────────────────────────
/health                 GET         5-10 ms      -
/model/info             GET         5-10 ms      30 features
/data/info              GET         20-50 ms     62,626 records
/predict                POST        100-300 ms   4,835 locations
/predict/hotspots       POST        150-400 ms   with analysis
/predict/batch (3)      POST        300-900 ms   14,505 predictions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 DEPLOYMENT OPTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Development:
$ python main.py

Production:
$ uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

Docker:
$ docker-compose up --build

Gunicorn:
$ pip install gunicorn
$ gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓 MODEL INFO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Algorithm:        Random Forest Regressor
Trees:            200
Train Years:      2020-2023 (385,600+ records)
Test Year:        2024 (62,626 locations)
Features:         30 (spatial, temporal, demographic, weather, lag-based)

Performance:
  MAE (Mean Absolute Error):     4.3771
  R² (R-squared):                0.9486
  RMSE:                          6.8392
  MAPE%:                         38.23%

Feature Categories:
  Spatial (4):      Latitude, Longitude, Area, Length
  Temporal (8):     Year, Month, trig encodings, seasons
  Demographic (4):  Population, density, income, deprivation
  Weather (5):      Temperature, rainfall, sunshine, frost
  Lag-based (9):    Crime lags (1m-6m) and rolling stats

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ COMMON ERRORS & SOLUTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"Connection refused"
  → Make sure API is running: python main.py

"Port 8000 already in use"
  → Kill existing process: lsof -i :8000 | kill -9 $(awk 'NR>1 {print $2}')
  → Or use different port: uvicorn main:app --port 8001

"No data found for year=2030, month=1"
  → Check available data: curl http://localhost:8000/data/info
  → Only 2024 data available

"Model not loaded"
  → Check model file exists: ls -la random_forest_model.joblib
  → File should be 12 MB

"FileNotFoundError"
  → Make sure you're in correct directory
  → Check both CSV and model files exist

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Files:
  README_API.md          ← Start here
  QUICKSTART.md          ← 5-minute quick start
  API_USAGE_GUIDE.md     ← Complete documentation
  PROJECT_SUMMARY.md     ← Technical details
  examples.py            ← Code examples
  client.py              ← Python client library

Interactive:
  http://localhost:8000/docs       ← Swagger UI
  http://localhost:8000/redoc      ← ReDoc
  http://localhost:8000/openapi.json ← OpenAPI spec

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚦 STATUS CODES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

200 OK              Success
400 Bad Request     Invalid parameters
404 Not Found       Data not available for that month
422 Validation Error Parameter validation failed
503 Service Down    Model or data not loaded

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 PRO TIPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Use batch predictions for multiple months (faster)
2. Filter hotspots by percentile to focus on high-risk areas
3. Cache predictions when repeated requests are needed
4. Use confidence intervals to understand prediction uncertainty
5. Monitor API logs for debugging: check startup messages
6. Use Docker for consistent deployment across systems
7. Explore the interactive docs at /docs for testing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Need help? Check PROJECT_SUMMARY.md or API_USAGE_GUIDE.md

Last Updated: April 15, 2026
API Version: 1.0.0 | Status: ✓ Production Ready
""")
