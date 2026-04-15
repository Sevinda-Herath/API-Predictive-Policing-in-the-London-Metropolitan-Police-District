#!/bin/bash

# Crime Prediction API Startup Script

set -e

echo "=========================================="
echo "Crime Prediction API Startup"
echo "=========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if requirements are installed
echo "✓ Checking dependencies..."
python3 -c "import fastapi, uvicorn, pandas, sklearn, joblib" 2>/dev/null || {
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
}

# Check if required files exist
if [ ! -f "crime_data_2024.csv" ]; then
    echo "❌ Error: crime_data_2024.csv not found"
    exit 1
fi

if [ ! -f "random_forest_model.joblib" ]; then
    echo "❌ Error: random_forest_model.joblib not found"
    exit 1
fi

echo "✓ All requirements met"
echo ""
echo "Starting API server..."
echo "📍 API available at: http://localhost:8000"
echo "📚 Documentation at: http://localhost:8000/docs"
echo ""

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
