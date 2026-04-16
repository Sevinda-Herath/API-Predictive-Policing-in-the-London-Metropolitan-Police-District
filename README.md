# Crime Count Prediction API (FastAPI)

This project serves a trained Random Forest model through FastAPI to predict crime counts using:
- `LSOA_Code` or `LSOA_Name`
- `Year`
- `Month`

The API automatically looks up all required model features from `crime_data_2024.csv` and feeds them into `random_forest_model.joblib`.

## Project Structure

- `app/main.py` - FastAPI application
- `crime_data_2024.csv` - source feature data used for lookup
- `random_forest_model.joblib` - trained model package
- `requirements.txt` - Python dependencies

## Requirements

- Python 3.10+

## Install

```bash
python -m pip install -r requirements.txt
```

## Run API

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server URLs:
- API root: `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Endpoints

### 1) Predict Crime Count

`POST /predict`

Input:
- `year` (int)
- `month` (1-12)
- one of:
  - `lsoa_code` (string)
  - `lsoa_name` (string)

Example request (with code):

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "lsoa_code": "E01000001",
    "year": 2024,
    "month": 6
  }'
```

Example request (with name):

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "lsoa_name": "Camden 001A",
    "year": 2024,
    "month": 6
  }'
```

Example response:

```json
{
  "lsoa_code": "E01000001",
  "lsoa_name": "Camden 001A",
  "year": 2024,
  "month": 6,
  "predicted_crime_count": 27.4185,
  "target": "Crime_Count"
}
```

### 2) Top Crime Hotspots

`POST /hotspots/top`

Input:
- `year` (int)
- `month` (1-12)
- `top_x` (int, default 10)

Example request:

```bash
curl -X POST "http://localhost:8000/hotspots/top" \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2024,
    "month": 6,
    "top_x": 5
  }'
```

Example response:

```json
{
  "year": 2024,
  "month": 6,
  "top_x": 5,
  "hotspots": [
    {
      "rank": 1,
      "lsoa_code": "E01000001",
      "lsoa_name": "Camden 001A",
      "predicted_crime_count": 51.9932
    }
  ]
}
```

## Notes

- The API returns `404` if no matching row exists for the given LSOA + year + month in `crime_data_2024.csv`.
- If there are duplicate matches, the first match is used.
- Predictions are clipped to non-negative values.

## Quick Test

After starting the server, open Swagger:

`http://localhost:8000/docs`

You can run and test all endpoints interactively from the docs page.
