# Project Summary: Crime Prediction API

## Overview

A production-ready **FastAPI** application for predicting crime counts in the London Metropolitan Police District. The API accepts year and month as input, automatically retrieves all necessary features from the dataset, and returns crime predictions with confidence intervals.

## Model Information

- **Algorithm**: Random Forest Regressor (200 trees)
- **Training Data**: 2020-2023 (385,600+ records)
- **Test Data**: 2024 (62,626 records)
- **Performance**:
  - MAE: 4.3771
  - R²: 0.9486
  - RMSE: 6.8392
  - MAPE: 38.23%
- **Features**: 30 (spatial, temporal, demographic, weather, lag-based)

## Files Created

### Core API Files

| File | Purpose |
|------|---------|
| **main.py** | Main FastAPI application with all endpoints |
| **client.py** | Python client library for easy API interaction |
| **requirements.txt** | Python dependencies |
| **Dockerfile** | Docker container configuration |
| **docker-compose.yml** | Docker Compose orchestration |

### Documentation Files

| File | Purpose |
|------|---------|
| **QUICKSTART.md** | 5-minute getting started guide |
| **API_USAGE_GUIDE.md** | Comprehensive API documentation (1000+ lines) |
| **examples.py** | 8 complete usage examples with outputs |
| **.gitignore** | Git ignore patterns |
| **start_api.sh** | Bash script to start the API |

## Features Implemented

### 1. Health & Status Endpoints
- `/health` - API health check
- `/model/info` - Model details and metrics
- `/data/info` - Dataset information
- `/` - Root endpoint with links

### 2. Crime Prediction Endpoints
- `/predict` - Single prediction for year/month
  - Returns predictions for all locations
  - Includes 95% confidence intervals
  - Sorted by crime count
- `/predict/hotspots` - Hotspot identification
  - Configurable hotspot percentile (1-50%)
  - Crime concentration metrics
  - RRI (Recapture Rate Index)
  - PAI (Prediction Accuracy Index)
- `/predict/batch` - Batch predictions
  - Multiple year/month combinations
  - Parallel processing
  - Error handling per request

### 3. Features Used in Predictions

**Spatial** (4):
- LSOA_Latitude, LSOA_Longitude
- LSOA_Shape_Area, LSOA_Shape_Length

**Temporal** (8):
- Year, Month
- month_sin, month_cos
- is_summer, is_winter, is_spring, is_autumn

**Demographic** (4):
- Total_Population, pop_density
- income_per_capita, Income_Deprivation

**Weather** (5):
- Max_Temperature_Celsius, Min_Temperature_Celsius
- Rainfall_mm, Sunshine_Hours, Air_Frost_Days

**Lag-Based** (9):
- crime_lag_1m/2m/3m/6m
- crime_rolling_3m/6m_mean/std
- msoa_avg_crime

## Getting Started

### 1. Quick Start (60 seconds)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
python main.py

# API available at: http://localhost:8000
```

### 2. Test the API

```bash
# Health check
curl http://localhost:8000/health

# View documentation
# Open browser: http://localhost:8000/docs
```

### 3. Make Predictions

```python
from client import CrimePredictionClient

client = CrimePredictionClient()
predictions = client.predict(year=2024, month=1)
```

## Deployment Options

### Option 1: Local Development
```bash
python main.py
```

### Option 2: Uvicorn (Production)
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Option 3: Docker
```bash
docker-compose up --build
```

### Option 4: Gunicorn + Uvicorn
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## API Examples

### Example 1: Basic Prediction
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"year": 2024, "month": 1}'
```

### Example 2: Hotspot Analysis
```bash
curl -X POST "http://localhost:8000/predict/hotspots?hotspot_percentile=10" \
  -H "Content-Type: application/json" \
  -d '{"year": 2024, "month": 1}'
```

### Example 3: Python Client
```python
from client import CrimePredictionClient, print_hotspot_analysis

client = CrimePredictionClient()
hotspots = client.predict_hotspots(year=2024, month=1, hotspot_percentile=10)
print_hotspot_analysis(hotspots, limit=15)
```

## Response Structure

### Prediction Response
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
    }
  ],
  "model_name": "RF - 200 trees, depth=10, leaf=2",
  "model_mae": 4.3771,
  "model_r2": 0.9486
}
```

## Performance Metrics

| Endpoint | Typical Response Time | Notes |
|----------|---------------------|-------|
| `/health` | 5-10 ms | Very fast |
| `/model/info` | 5-10 ms | Metadata only |
| `/data/info` | 20-50 ms | Quick aggregation |
| `/predict` | 100-300 ms | ~4,800 predictions |
| `/predict/hotspots` | 150-400 ms | With analysis |
| `/predict/batch` (3 items) | 300-900 ms | Parallel |

## Data Available

- **Years**: 2024 (full year)
- **Months**: 1-12 (all available)
- **Locations**: 4,835 LSOA areas
- **Records**: 62,626 total
- **Geographic Coverage**: Greater London

## Key Features

✅ **Production-Ready**
- Error handling and validation
- Health checks
- Input validation with Pydantic
- Comprehensive logging

✅ **Performance Optimized**
- Fast predictions (<300ms)
- Efficient memory usage
- Tree-based parallelization

✅ **Well Documented**
- Interactive Swagger UI
- ReDoc documentation
- Comprehensive guides
- Usage examples
- Python client

✅ **Deployment Flexible**
- Works standalone
- Docker support
- Scalable architecture
- Easy to integrate

✅ **Data Intelligent**
- Automatic feature extraction
- Confidence intervals
- Hotspot identification
- Batch processing

## Technical Stack

- **Framework**: FastAPI (modern, fast, easy)
- **Server**: Uvicorn (ASGI server)
- **Data Processing**: Pandas, NumPy
- **Model**: Scikit-learn (Random Forest)
- **Serialization**: Joblib
- **Validation**: Pydantic
- **Documentation**: Swagger UI, ReDoc
- **Containerization**: Docker

## File Structure

```
API Project Root/
├── main.py                          # Main API application
├── client.py                        # Python client library
├── examples.py                      # Usage examples
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker configuration
├── docker-compose.yml               # Docker Compose
├── start_api.sh                     # Startup script
├── .gitignore                       # Git ignore rules
├── QUICKSTART.md                    # Quick start guide
├── API_USAGE_GUIDE.md              # Full documentation
│
├── crime_data_2024.csv             # Dataset
├── random_forest_model.joblib      # Trained model
└── README.md                        # Project README (original)
```

## Testing

### Manual Testing
```bash
# 1. Start API
python main.py

# 2. In another terminal
python examples.py      # Run comprehensive examples

# 3. Or use curl
curl http://localhost:8000/health
```

### Python Testing
```python
from client import CrimePredictionClient

client = CrimePredictionClient()

# Test 1: Health
assert client.health_check()['status'] == 'healthy'

# Test 2: Predictions
pred = client.predict(2024, 1)
assert pred['total_predictions'] > 0

# Test 3: Hotspots
hotspots = client.predict_hotspots(2024, 1, 10)
assert hotspots['hotspot_analysis']['hotspot_locations'] > 0
```

## Common Use Cases

1. **Police Resource Planning**
   - Identify high-crime areas
   - Allocate patrol resources
   - Plan community initiatives

2. **Crime Prevention**
   - Hotspot analysis
   - Predictive policing
   - Risk assessment

3. **Research & Analysis**
   - Crime trends
   - Seasonal patterns
   - Demographic correlations

4. **Public Safety**
   - Inform residents
   - Insurance companies
   - Urban planning

## Troubleshooting

### API won't start
- Check Python version (3.8+)
- Verify dependencies: `pip install -r requirements.txt`
- Check port 8000 is available

### No predictions returned
- Verify data files exist
- Check year/month are in dataset
- Review startup logs

### Performance issues
- Check available resources
- Consider Docker deployment
- Monitor API logs

## Maintenance

### Retraining with new data
The trained model can be updated by re-running the training script, then restarting the API.

### Version compatibility
- Python: 3.8+
- scikit-learn: 1.3.2+ (some version warnings are safe)
- FastAPI: latest recommended

## Support Resources

- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)
- **Full Docs**: See [API_USAGE_GUIDE.md](API_USAGE_GUIDE.md)
- **Examples**: See [examples.py](examples.py)
- **Interactive Docs**: http://localhost:8000/docs

## Next Steps

1. ✅ Review [QUICKSTART.md](QUICKSTART.md)
2. ✅ Start the API: `python main.py`
3. ✅ Visit http://localhost:8000/docs
4. ✅ Run examples: `python examples.py`
5. ✅ Integrate with your application
6. ✅ Deploy to production

---

**Created**: April 15, 2026
**API Version**: 1.0.0
**Model**: Random Forest Regressor
**Training Data**: 2020-2023
