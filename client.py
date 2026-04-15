"""
Example client for interacting with the Crime Prediction API
"""

import requests
import json
from typing import Dict, List

API_BASE_URL = "http://localhost:8000"


class CrimePredictionClient:
    """Client for Crime Prediction API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip('/')
    
    def health_check(self) -> Dict:
        """Check if API is healthy"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        response = requests.get(f"{self.base_url}/model/info")
        response.raise_for_status()
        return response.json()
    
    def get_data_info(self) -> Dict:
        """Get information about the crime dataset"""
        response = requests.get(f"{self.base_url}/data/info")
        response.raise_for_status()
        return response.json()
    
    def predict(self, year: int, month: int) -> Dict:
        """
        Predict crime for a specific year and month
        
        Args:
            year: Year (e.g., 2024)
            month: Month (1-12)
        
        Returns:
            Dictionary with predictions
        """
        payload = {"year": year, "month": month}
        response = requests.post(f"{self.base_url}/predict", json=payload)
        response.raise_for_status()
        return response.json()
    
    def predict_hotspots(self, year: int, month: int, hotspot_percentile: int = 10) -> Dict:
        """
        Predict crime and identify hotspots
        
        Args:
            year: Year (e.g., 2024)
            month: Month (1-12)
            hotspot_percentile: Top N% to mark as hotspots (default: 10)
        
        Returns:
            Dictionary with predictions and hotspot analysis
        """
        payload = {"year": year, "month": month}
        response = requests.post(
            f"{self.base_url}/predict/hotspots",
            json=payload,
            params={"hotspot_percentile": hotspot_percentile}
        )
        response.raise_for_status()
        return response.json()
    
    def predict_batch(self, requests_list: List[tuple]) -> Dict:
        """
        Predict crime for multiple year-month combinations
        
        Args:
            requests_list: List of (year, month) tuples
        
        Returns:
            Dictionary with batch results
        """
        payload = [{"year": year, "month": month} for year, month in requests_list]
        response = requests.post(f"{self.base_url}/predict/batch", json=payload)
        response.raise_for_status()
        return response.json()


def print_predictions(predictions_response: Dict, limit: int = 10):
    """Pretty print prediction results"""
    print(f"\n{'='*80}")
    print(f"Crime Predictions for {predictions_response['year']}-{predictions_response['month']:02d}")
    print(f"{'='*80}")
    print(f"Total Predictions: {predictions_response['total_predictions']}")
    print(f"Total Predicted Crimes: {predictions_response['total_predicted_crimes']:.2f}")
    print(f"Model: {predictions_response['model_name']}")
    print(f"Model MAE: {predictions_response['model_mae']:.4f}")
    print(f"Model R²: {predictions_response['model_r2']:.4f}\n")
    
    print(f"{'Rank':<6} {'Latitude':<12} {'Longitude':<12} {'Pop':<8} {'Predicted':<12} {'95% CI':<25}")
    print("-" * 80)
    
    for i, pred in enumerate(predictions_response['predictions'][:limit], 1):
        lat = pred['latitude']
        lon = pred['longitude']
        pop = pred['population']
        crime = pred['predicted_crime_count']
        lower = pred['prediction_interval_lower']
        upper = pred['prediction_interval_upper']
        ci = f"[{lower:.2f}, {upper:.2f}]"
        
        print(f"{i:<6} {lat:<12.5f} {lon:<12.5f} {pop:<8} {crime:<12.2f} {ci:<25}")
    
    if len(predictions_response['predictions']) > limit:
        print(f"\n... and {len(predictions_response['predictions']) - limit} more locations")


def print_hotspot_analysis(hotspot_response: Dict, limit: int = 15):
    """Pretty print hotspot analysis results"""
    print(f"\n{'='*80}")
    print(f"Hotspot Analysis for {hotspot_response['year']}-{hotspot_response['month']:02d}")
    print(f"{'='*80}")
    print(f"Total Predictions: {hotspot_response['total_predictions']}")
    print(f"Total Predicted Crimes: {hotspot_response['total_predicted_crimes']:.2f}")
    print(f"Model: {hotspot_response['model_name']}\n")
    
    hs = hotspot_response['hotspot_analysis']
    print(f"Hotspot Analysis (Top {hs['hotspot_percentile']}%):")
    print(f"  - Hotspot Threshold: {hs['hotspot_threshold']:.2f} crimes")
    print(f"  - Hotspot Locations: {hs['hotspot_locations']}")
    print(f"  - Crimes in Hotspots: {hs['crimes_in_hotspots']:.2f}")
    print(f"  - Crime Concentration: {hs['crime_concentration']:.2f}%\n")
    
    hotspot_preds = [p for p in hotspot_response['predictions'] if p['is_hotspot']]
    print(f"{'Rank':<6} {'Latitude':<12} {'Longitude':<12} {'Pop':<8} {'Predicted':<12} {'Hotspot':<10}")
    print("-" * 80)
    
    for i, pred in enumerate(hotspot_preds[:limit], 1):
        lat = pred['latitude']
        lon = pred['longitude']
        pop = pred['population']
        crime = pred['predicted_crime_count']
        hs_flag = "🔥 YES" if pred['is_hotspot'] else "NO"
        
        print(f"{i:<6} {lat:<12.5f} {lon:<12.5f} {pop:<8} {crime:<12.2f} {hs_flag:<10}")


# =============================================================================
# EXAMPLE USAGE
# =============================================================================
if __name__ == "__main__":
    # Initialize client
    client = CrimePredictionClient()
    
    # Check health
    print("1. Checking API health...")
    health = client.health_check()
    print(f"✓ API Status: {health['status']}")
    print(f"✓ Model Loaded: {health['model_loaded']}")
    print(f"✓ Data Loaded: {health['data_loaded']}\n")
    
    # Get model info
    print("2. Getting model information...")
    model_info = client.get_model_info()
    print(f"✓ Model: {model_info['model_name']}")
    print(f"✓ Features: {model_info['features_count']}")
    print(f"✓ MAE: {model_info['metrics']['MAE']:.4f}")
    print(f"✓ R²: {model_info['metrics']['R2']:.4f}\n")
    
    # Get data info
    print("3. Getting data information...")
    data_info = client.get_data_info()
    print(f"✓ Total Records: {data_info['total_records']:,}")
    print(f"✓ Years: {data_info['years']}")
    print(f"✓ Months: {data_info['months']}\n")
    
    # Single prediction
    print("4. Making a single prediction for 2024-01...")
    prediction = client.predict(year=2024, month=1)
    print_predictions(prediction, limit=5)
    
    # Hotspot analysis
    print("\n5. Getting hotspot analysis for 2024-01...")
    hotspots = client.predict_hotspots(year=2024, month=1, hotspot_percentile=10)
    print_hotspot_analysis(hotspots, limit=10)
    
    # Batch prediction
    print("\n6. Making batch predictions for multiple months...")
    batch_results = client.predict_batch([
        (2024, 1),
        (2024, 2),
        (2024, 3),
    ])
    print(f"✓ Successful: {batch_results['successful']}/{batch_results['total_requests']}")
    if batch_results['errors']:
        print(f"✓ Errors: {batch_results['errors']}")
    print(f"\nMonth    | Total Crimes | Predictions")
    print("-" * 50)
    for month_key, result in batch_results['results'].items():
        print(f"{month_key} | {result['total_predicted_crimes']:12.2f} | {result['total_predictions']}")
