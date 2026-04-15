# Quick Start Guide

Get the Crime Prediction API running in minutes!

## Prerequisites

- Python 3.8+
- Required files in the current directory:
  - `crime_data_2024.csv` ✓
  - `random_forest_model.joblib` ✓

## Option 1: Direct Python (Fastest)

```bash
# Install dependencies (first time only)
pip install -r requirements.txt

# Run the API
python main.py
```

The API will be available at: **http://localhost:8000**

## Option 2: Using Uvicorn (Recommended for Development)

```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Option 3: Docker (Production-Ready)

```bash
# Build the image
docker build -t crime-api .

# Run the container
docker run -p 8000:8000 crime-api

# Or use Docker Compose
docker-compose up --build
```

## Quick Test After Startup

### 1. Check API Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "data_loaded": true
}
```

### 2. View Interactive API Documentation
Open in your browser: **http://localhost:8000/docs**

### 3. Make Your First Prediction

```bash
# Using curl
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"year": 2024, "month": 1}'
```

### 4. Use Python Client

```python
from client import CrimePredictionClient, print_predictions

client = CrimePredictionClient()
predictions = client.predict(year=2024, month=1)
print_predictions(predictions, limit=5)
```

## Startup Checklist

After starting, you should see:

```
[STARTUP] Loading crime prediction model...
✓ Model loaded: RF - 200 trees, depth=10, leaf=2
✓ Features: 30 features
✓ Metrics - MAE: 4.3771, R²: 0.9486
✓ Crime data loaded: 62,626 records
✓ Years available: [2024]
✓ Months available: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
```

## Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | API health check |
| `/model/info` | GET | Model details and metrics |
| `/data/info` | GET | Dataset information |
| `/predict` | POST | Make crime prediction |
| `/predict/hotspots` | POST | Get hotspot analysis |
| `/predict/batch` | POST | Batch predictions |
| `/docs` | GET | Interactive API documentation |

## Common Issues

### "FileNotFoundError: crime_data_2024.csv"
- Make sure you're in the correct directory
- Verify the file exists: `ls -la crime_data_2024.csv`

### "Port 8000 already in use"
- Use a different port: `uvicorn main:app --port 8001`
- Or kill existing process: `lsof -i :8000` then `kill -9 <PID>`

### Model version warnings
- These are safe to ignore - related to scikit-learn version compatibility
- The model will still work correctly

## Next Steps

- Read [API_USAGE_GUIDE.md](API_USAGE_GUIDE.md) for detailed documentation
- Explore the interactive docs at http://localhost:8000/docs
- Try the Python client examples in [client.py](client.py)

## Getting Help

Check the startup logs for detailed error messages. Most issues are:
1. Missing files
2. Port already in use
3. Python version incompatibility

Refer to [API_USAGE_GUIDE.md](API_USAGE_GUIDE.md#troubleshooting) for more troubleshooting help.
