# 🚔 Crime Prediction API - London Metropolitan Police District

A production-ready **FastAPI** application for predicting crime counts across London's LSOA (Lower Layer Super Output Area) regions using Random Forest machine learning.

## ✨ Features

- 🎯 **Simple Input** - Just provide year and month
- 🔮 **Intelligent Predictions** - Model automatically extracts 30+ features
- 🎪 **Multiple Endpoints** - Single predictions, hotsport analysis, batch processing
- 📊 **Confidence Intervals** - 95% prediction intervals included
- 🗺️ **Spatial Analysis** - Hotspot identification with crime concentration metrics
- 📈 **Well Documented** - Interactive API docs, comprehensive guides, examples
- 🐳 **Docker Ready** - Easy containerization and deployment

## 🚀 Quick Start

```bash
# 1. Install dependencies (one time)
pip install -r requirements.txt

# 2. Run the API
python main.py

# 3. Open in browser
# Visit: http://localhost:8000/docs
```

**That's it!** The API is now running and ready to use.

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute getting started guide |
| [API_USAGE_GUIDE.md](API_USAGE_GUIDE.md) | Complete API reference (1000+ lines) |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Technical overview and architecture |

## 🔗 API Endpoints

### Core Endpoints

```
GET  /                          # Root with links to all endpoints
GET  /health                    # Health check
GET  /model/info               # Model details & metrics
GET  /data/info                # Dataset information
```

### Prediction Endpoints

```
POST /predict                   # Make crime prediction
POST /predict/hotspots         # Get hotspot analysis
POST /predict/batch            # Batch predictions for multiple months
```

## 💡 Usage Examples

### Example 1: Simple Prediction with cURL

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"year": 2024, "month": 1}'
```

### Example 2: Python Client

```python
from client import CrimePredictionClient, print_predictions

client = CrimePredictionClient()
predictions = client.predict(year=2024, month=1)
print_predictions(predictions, limit=10)
```

### Example 3: Get Hotspots

```python
hotspots = client.predict_hotspots(year=2024, month=1, hotspot_percentile=10)
# Returns top 10% crime hotspots with concentration metrics
```

### Example 4: Comprehensive Examples

```bash
# Run all examples to see the API in action
python examples.py
```

## 📊 Response Example

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
      "population": 2172,
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

## 🏗️ Architecture

```
Random Forest Model (30 features, 200 trees)
          ↓
    FastAPI Server
          ↓
    ┌─────┴─────┐
    ↓           ↓
  JSON      WebSocket
  REST      (Real-time)
    ↓           ↓
  HTTP      Subscriptions
  Clients   (Optional)
```

## 📋 Model Details

| Aspect | Value |
|--------|-------|
| **Algorithm** | Random Forest Regressor |
| **Trees** | 200 |
| **Training Data** | 2020-2023 (385,600+ records) |
| **Test Data** | 2024 (62,626 locations) |
| **Features** | 30 (spatial, temporal, demographic, weather, lag-based) |
| **MAE** | 4.3771 |
| **R²** | 0.9486 |
| **MAPE** | 38.23% |

## 🎓 How It Works

### 1️⃣ **Input**: Year & Month Only
```python
{"year": 2024, "month": 1}
```

### 2️⃣ **The API**:
- Filters dataset for that year/month
- Extracts all 30 features automatically
- Passes to Random Forest model
- Calculates prediction intervals

### 3️⃣ **Output**: Rich Predictions
```python
{
  "total_predictions": 4835,           # All LSOA locations
  "total_predicted_crimes": 125430.45,
  "predictions": [                    # Per-location details
    {
      "latitude": 51.52,
      "longitude": -0.095,
      "predicted_crime_count": 15.42,
      "prediction_interval_lower": 12.34,
      "prediction_interval_upper": 18.50
    }
  ]
}
```

## 🔧 Deployment Options

### Option 1: Direct Python (Development)
```bash
python main.py
```

### Option 2: Uvicorn (Recommended)
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Option 3: Docker (Production)
```bash
docker build -t crime-api .
docker run -p 8000:8000 crime-api
```

### Option 4: Docker Compose
```bash
docker-compose up --build
```

### Option 5: Production with Gunicorn
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📈 Performance

| Operation | Time | Data Points |
|-----------|------|------------|
| Health Check | 5-10 ms | - |
| Single Prediction | 100-300 ms | 4,835 locations |
| Hotspot Analysis | 150-400 ms | Includes analysis |
| Batch (3 months) | 300-900 ms | 14,505 predictions |

## 📂 Project Structure

```
project/
├── main.py                    # Main FastAPI application
├── client.py                  # Python client library
├── examples.py                # Usage examples (8 scenarios)
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose setup
├── start_api.sh              # Startup script
├── .gitignore                # Git ignore rules
│
├── QUICKSTART.md             # 5-min getting started
├── API_USAGE_GUIDE.md        # Complete documentation
├── PROJECT_SUMMARY.md        # Technical details
├── README.md                 # This file
│
├── crime_data_2024.csv       # 62,626 location-month records
└── random_forest_model.joblib # Trained model (30 features)
```

## 🌐 Available Data

- **Years**: 2024 (full year)
- **Months**: 1-12 (all months)
- **Locations**: 4,835 LSOA areas across Greater London
- **Records**: 62,626 total predictions available

## 🛠️ Features Used in Model

**Spatial** (4):
- LSOA_Latitude, LSOA_Longitude, LSOA_Shape_Area, LSOA_Shape_Length

**Temporal** (8):
- Year, Month, month_sin, month_cos
- is_summer, is_winter, is_spring, is_autumn

**Demographic** (4):
- Total_Population, pop_density, income_per_capita, Income_Deprivation

**Weather** (5):
- Max_Temperature_Celsius, Min_Temperature_Celsius, Rainfall_mm, Sunshine_Hours, Air_Frost_Days

**Lag-Based** (9):
- crime_lag_1m/2m/3m/6m, crime_rolling_3m/6m_mean/std, msoa_avg_crime

## 🔒 API Security

- Input validation with Pydantic
- Type checking on all endpoints
- Error handling and validation
- Health monitoring built-in

## 🐛 Troubleshooting

### API won't start
```bash
# Check Python version
python --version        # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check port availability
lsof -i :8000
```

### No predictions
- Verify data files exist: `ls -la crime_data_2024.csv random_forest_model.joblib`
- Check year/month in dataset: `curl http://localhost:8000/data/info`
- Review logs for errors

### Performance issues
- Check CPU/memory availability
- Consider Docker deployment
- Use Docker Compose for load balancing

## 📞 Support Resources

1. **Getting Started**: [QUICKSTART.md](QUICKSTART.md)
2. **Full Documentation**: [API_USAGE_GUIDE.md](API_USAGE_GUIDE.md)
3. **Technical Overview**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
4. **Interactive Docs**: http://localhost:8000/docs
5. **Code Examples**: [examples.py](examples.py)

## 🎯 What's Included

✅ Production-ready FastAPI application
✅ Comprehensive REST API documentation
✅ Python client library with examples
✅ Docker & Docker Compose configuration
✅ 8 complete usage examples
✅ Health checks and monitoring
✅ Input validation
✅ Error handling
✅ Interactive Swagger UI
✅ Bash startup script

## 🚀 Next Steps

1. **Start the API**
   ```bash
   python main.py
   ```

2. **View Interactive Documentation**
   - Open: http://localhost:8000/docs

3. **Try Examples**
   ```bash
   python examples.py
   ```

4. **Integrate with Your App**
   - Use the Python client: `from client import CrimePredictionClient`
   - Or use REST with cURL/requests
   - Or deploy with Docker

5. **Deploy to Production**
   - Use Docker Compose
   - Or deploy to cloud (AWS, GCP, Azure)
   - Or use in Kubernetes

## 💻 Technology Stack

- **Framework**: FastAPI (modern, fast, async)
- **Server**: Uvicorn (ASGI)
- **ML Model**: Scikit-learn Random Forest
- **Data Processing**: Pandas, NumPy
- **Documentation**: Swagger UI, ReDoc
- **Containerization**: Docker

## 📝 Files Guide

| File | Size | Description |
|------|------|-------------|
| main.py | 16 KB | Core API application |
| client.py | 7.6 KB | Python client library |
| examples.py | 14 KB | 8 comprehensive examples |
| crime_data_2024.csv | 17 MB | 62,626 location records |
| random_forest_model.joblib | 12 MB | Trained model |
| Dockerfile | 1 KB | Docker configuration |
| QUICKSTART.md | 3.2 KB | Quick start guide |
| API_USAGE_GUIDE.md | 11 KB | Complete API documentation |

## ⚡ Performance Tips

1. **Use batch predictions** for multiple months
2. **Docker deployment** for production
3. **Load balancing** with multiple instances
4. **Caching** predictions when possible
5. **Async clients** for concurrent requests

## 📄 License

This project is part of the Predictive Policing initiative for London Metropolitan Police District.

## 🎉 Getting Started Right Now

```bash
# 1. Install (30 seconds)
pip install -r requirements.txt

# 2. Run (5 seconds)
python main.py

# 3. Test (10 seconds)
# Open: http://localhost:8000/docs

# 4. Predict! (< 1 second)
# Click "Try it out" on /predict endpoint
```

---

**Created**: April 15, 2026
**API Version**: 1.0.0
**Status**: ✅ Production Ready
