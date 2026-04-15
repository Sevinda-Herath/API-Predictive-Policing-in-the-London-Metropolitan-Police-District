"""
Complete API Usage Examples
Demonstrates all features of the Crime Prediction API
"""

import requests
import json
from datetime import datetime
from typing import Dict, List


BASE_URL = "http://localhost:8000"


def pretty_print(data: Dict, title: str = ""):
    """Pretty print JSON response"""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    print(json.dumps(data, indent=2))


# =============================================================================
# EXAMPLE 1: HEALTH CHECK AND INITIALIZATION
# =============================================================================
def example_health_check():
    """Example 1: Check API health"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Health Check and API Status")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/health")
    health = response.json()
    
    print(f"Status: {health['status']}")
    print(f"Model Loaded: {health['model_loaded']}")
    print(f"Data Loaded: {health['data_loaded']}")
    
    if health['status'] == 'healthy':
        print("✓ API is ready to use!")
    else:
        print("✗ API has issues - please check startup logs")
        return False
    return True


# =============================================================================
# EXAMPLE 2: GET MODEL INFORMATION
# =============================================================================
def example_model_info():
    """Example 2: Get detailed model information"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Model Information")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/model/info")
    model_info = response.json()
    
    print(f"\nModel Name: {model_info['model_name']}")
    print(f"Target Variable: {model_info['target']}")
    print(f"Features Used: {model_info['features_count']}")
    print(f"Training Years: {model_info['train_years']}")
    print(f"Test Year: {model_info['test_year']}")
    
    print(f"\nModel Metrics:")
    for metric, value in model_info['metrics'].items():
        print(f"  {metric}: {value:.4f}")
    
    print(f"\nFeatures ({model_info['features_count']}):")
    for i, feature in enumerate(model_info['features'], 1):
        print(f"  {i:2d}. {feature}")


# =============================================================================
# EXAMPLE 3: GET DATA INFORMATION
# =============================================================================
def example_data_info():
    """Example 3: Get dataset information"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Dataset Information")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/data/info")
    data_info = response.json()
    
    print(f"\nTotal Records: {data_info['total_records']:,}")
    print(f"Years Available: {data_info['years']}")
    print(f"Months Available: {data_info['months']}")
    
    print(f"\nSpatial Coverage (London Metropolitan Police District):")
    print(f"  Latitude Range:  {data_info['spatial_coverage']['min_latitude']:.4f} to {data_info['spatial_coverage']['max_latitude']:.4f}")
    print(f"  Longitude Range: {data_info['spatial_coverage']['min_longitude']:.4f} to {data_info['spatial_coverage']['max_longitude']:.4f}")
    
    print(f"\nColumns in Dataset ({len(data_info['columns'])}):")
    for col in data_info['columns'][:10]:
        print(f"  - {col}")
    print(f"  ... and {len(data_info['columns']) - 10} more")


# =============================================================================
# EXAMPLE 4: SIMPLE CRIME PREDICTION
# =============================================================================
def example_simple_prediction():
    """Example 4: Make a simple crime prediction"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Simple Crime Prediction for January 2024")
    print("="*80)
    
    payload = {"year": 2024, "month": 1}
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    data = response.json()
    
    print(f"\nPrediction Summary:")
    print(f"  Year: {data['year']}")
    print(f"  Month: {data['month']}")
    print(f"  Total Locations (LSOAs): {data['total_predictions']:,}")
    print(f"  Total Predicted Crimes: {data['total_predicted_crimes']:.2f}")
    print(f"  Model: {data['model_name']}")
    print(f"  Model MAE: {data['model_mae']:.4f}")
    print(f"  Model R²: {data['model_r2']:.4f}")
    
    print(f"\nTop 10 Highest Crime Prediction Locations:")
    print(f"{'Rank':<6} {'Latitude':<12} {'Longitude':<12} {'Population':<12} {'Predicted':<12} {'95% CI':<20}")
    print("-" * 80)
    
    for i, pred in enumerate(data['predictions'][:10], 1):
        ci = f"[{pred['prediction_interval_lower']:.2f}, {pred['prediction_interval_upper']:.2f}]"
        print(f"{i:<6} "
              f"{pred['latitude']:<12.5f} "
              f"{pred['longitude']:<12.5f} "
              f"{pred['population']:<12} "
              f"{pred['predicted_crime_count']:<12.2f} "
              f"{ci:<20}")


# =============================================================================
# EXAMPLE 5: HOTSPOT ANALYSIS
# =============================================================================
def example_hotspot_analysis():
    """Example 5: Identify crime hotspots"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Crime Hotspot Analysis (Top 10%)")
    print("="*80)
    
    payload = {"year": 2024, "month": 1}
    response = requests.post(
        f"{BASE_URL}/predict/hotspots",
        json=payload,
        params={"hotspot_percentile": 10}
    )
    data = response.json()
    
    hs = data['hotspot_analysis']
    print(f"\nHotspot Analysis Results:")
    print(f"  Hotspot Definition: Top {hs['hotspot_percentile']}% (threshold: {hs['hotspot_threshold']:.2f} crimes)")
    print(f"  Hotspot Locations Identified: {hs['hotspot_locations']:,}")
    print(f"  Total Crimes in Hotspots: {hs['crimes_in_hotspots']:.2f}")
    print(f"  Crime Concentration: {hs['crime_concentration']:.2f}% of all crimes")
    
    hotspot_preds = [p for p in data['predictions'] if p['is_hotspot']]
    
    print(f"\nTop 8 Crime Hotspot Locations:")
    print(f"{'Rank':<6} {'Latitude':<12} {'Longitude':<12} {'Population':<12} {'Predicted':<12}")
    print("-" * 60)
    
    for i, pred in enumerate(hotspot_preds[:8], 1):
        print(f"{i:<6} "
              f"{pred['latitude']:<12.5f} "
              f"{pred['longitude']:<12.5f} "
              f"{pred['population']:<12} "
              f"{pred['predicted_crime_count']:<12.2f}")
    
    print(f"\n💡 Insight: {hs['hotspot_locations']} locations ({hs['hotspot_percentile']}% of area) ")
    print(f"   account for {hs['crime_concentration']:.1f}% of predicted crimes")


# =============================================================================
# EXAMPLE 6: BATCH PREDICTION (Multiple Months)
# =============================================================================
def example_batch_prediction():
    """Example 6: Make predictions for multiple months"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Batch Prediction (Q1 2024)")
    print("="*80)
    
    payload = [
        {"year": 2024, "month": 1},
        {"year": 2024, "month": 2},
        {"year": 2024, "month": 3},
    ]
    
    response = requests.post(f"{BASE_URL}/predict/batch", json=payload)
    data = response.json()
    
    print(f"\nBatch Processing Results:")
    print(f"  Total Requests: {data['total_requests']}")
    print(f"  Successful: {data['successful']}")
    print(f"  Failed: {data['failed']}")
    
    print(f"\nQuarterly Summary:")
    print(f"{'Month':<15} {'Total Crimes':<20} {'Locations':<15} {'Avg per Location':<20}")
    print("-" * 70)
    
    for month_key in sorted(data['results'].keys()):
        result = data['results'][month_key]
        total_crimes = result['total_predicted_crimes']
        locations = result['total_predictions']
        avg_crime = total_crimes / locations if locations > 0 else 0
        
        print(f"{month_key:<15} {total_crimes:<20.2f} {locations:<15} {avg_crime:<20.4f}")
    
    # Calculate quarterly stats
    total_q1_crimes = sum(r['total_predicted_crimes'] for r in data['results'].values())
    print(f"\nQ1 2024 Total Predicted Crimes: {total_q1_crimes:.2f}")


# =============================================================================
# EXAMPLE 7: COMPARE MULTIPLE MONTHS/HOTSPOTS
# =============================================================================
def example_trend_analysis():
    """Example 7: Analyze crime trends across months"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Crime Trend Analysis (First Half of 2024)")
    print("="*80)
    
    months = list(range(1, 7))  # January to June
    results = []
    
    print("\nCollecting predictions for all 6 months...")
    
    for month in months:
        payload = {"year": 2024, "month": month}
        response = requests.post(f"{BASE_URL}/predict", json=payload)
        data = response.json()
        
        results.append({
            'month': month,
            'total_crimes': data['total_predicted_crimes'],
            'locations': data['total_predictions'],
        })
    
    print(f"\nCrime Trend Analysis:")
    print(f"{'Month':<10} {'Jan':<12} {'Feb':<12} {'Mar':<12} {'Apr':<12} {'May':<12} {'Jun':<12}")
    print("-" * 82)
    
    print("Crimes     ", end="")
    for r in results:
        print(f"{r['total_crimes']:<12.0f}", end="")
    print()
    
    # Calculate trends
    print(f"\nTrend Analysis:")
    for i in range(1, len(results)):
        month_name = ['', 'January', 'February', 'March', 'April', 'May', 'June'][results[i]['month']]
        prev_month_name = ['', 'January', 'February', 'March', 'April', 'May', 'June'][results[i-1]['month']]
        
        change = results[i]['total_crimes'] - results[i-1]['total_crimes']
        pct_change = (change / results[i-1]['total_crimes']) * 100
        direction = "↑" if change > 0 else "↓"
        
        print(f"  {month_name} vs {prev_month_name}: {direction} {abs(pct_change):.1f}% "
              f"({change:+.0f} crimes)")


# =============================================================================
# EXAMPLE 8: STATISTICS AND INSIGHTS
# =============================================================================
def example_statistics():
    """Example 8: Generate statistics and insights"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Statistical Analysis")
    print("="*80)
    
    payload = {"year": 2024, "month": 1}
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    data = response.json()
    
    predictions = data['predictions']
    
    # Extract crime counts
    crime_counts = [p['predicted_crime_count'] for p in predictions]
    
    # Calculate statistics
    import statistics
    
    total = sum(crime_counts)
    mean = statistics.mean(crime_counts)
    median = statistics.median(crime_counts)
    stdev = statistics.stdev(crime_counts) if len(crime_counts) > 1 else 0
    min_crime = min(crime_counts)
    max_crime = max(crime_counts)
    
    print(f"\nPrediction Statistics for January 2024:")
    print(f"  Total Predicted Crimes: {total:,.2f}")
    print(f"  Total Locations: {len(crime_counts):,}")
    print(f"  Mean Crime per Location: {mean:.4f}")
    print(f"  Median Crime per Location: {median:.4f}")
    print(f"  Standard Deviation: {stdev:.4f}")
    print(f"  Min (lowest prediction): {min_crime:.4f}")
    print(f"  Max (highest prediction): {max_crime:.4f}")
    print(f"  Range: {max_crime - min_crime:.4f}")
    
    # Distribution analysis
    print(f"\nPrediction Distribution:")
    deciles = [statistics.quantiles(crime_counts, n=10) for _ in [None]][0] if len(crime_counts) > 10 else []
    if deciles:
        print(f"  10th percentile: {deciles[0]:.4f}")
        print(f"  25th percentile: {deciles[2]:.4f}")
        print(f"  Median (50th):   {median:.4f}")
        print(f"  75th percentile: {deciles[7]:.4f}")
        print(f"  90th percentile: {deciles[8]:.4f}")
    
    # High crime distribution
    high_crime = sum(1 for c in crime_counts if c > mean + stdev)
    print(f"\nLocations with high crime (> 1 std dev above mean): {high_crime} ({high_crime/len(crime_counts)*100:.1f}%)")


# =============================================================================
# MAIN EXECUTION
# =============================================================================
if __name__ == "__main__":
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  CRIME PREDICTION API - COMPREHENSIVE EXAMPLES".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    try:
        # Run all examples
        if example_health_check():
            example_model_info()
            example_data_info()
            example_simple_prediction()
            example_hotspot_analysis()
            example_batch_prediction()
            example_trend_analysis()
            example_statistics()
            
            print("\n" + "="*80)
            print("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
            print("="*80)
            print("\nNext Steps:")
            print("  1. Explore the interactive API docs: http://localhost:8000/docs")
            print("  2. Use the Python client: client.py")
            print("  3. Integrate with your application")
            print("\nFor more information, see:")
            print("  - API_USAGE_GUIDE.md (comprehensive documentation)")
            print("  - QUICKSTART.md (getting started)")
            print("\n")
        else:
            print("\n✗ API health check failed. Please check the API is running.")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API at", BASE_URL)
        print("  Make sure the API is running: python main.py")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
