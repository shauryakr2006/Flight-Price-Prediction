"""
predict.py
Load trained model and make predictions on new flight data.
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from data_pipeline import clean_and_engineer, process_files


class FlightPredictor:
    """
    Load model, preprocess input like training did, predict price.
    """
    
    def __init__(self, model_path='models/flight_price_model.pkl', feature_names=None):
        """Load the trained model and expected features."""
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        self.model = joblib.load(self.model_path)
        self.feature_names = feature_names  # Will be set from training data
        print(f"✓ Model loaded from {model_path}")
    
    def predict_single(self, flight_dict):
        """
        Predict price for ONE flight.
        
        Input dict must have keys:
            Date_of_Journey, Dep_Time, Arrival_Time, Duration,
            Airline, Source, Destination, Total_Stops, Additional_Info
        
        Returns: predicted price (float)
        """
        # Create single-row dataframe
        df = pd.DataFrame([flight_dict])
        
        # Apply same preprocessing as training
        df_clean = clean_and_engineer(df)
        
        # Reindex to match training features exactly
        if self.feature_names:
            # Add missing columns with 0, drop extra columns
            df_clean = df_clean.reindex(columns=self.feature_names, fill_value=0)
        
        # Predict
        price = self.model.predict(df_clean)[0]
        return price


def predict_batch(model_path, flights_list, features):
    """
    Predict prices for multiple flights.
    
    flights_list: list of dicts, each with flight details
    features: feature names from training
    
    Returns: list of prices
    """
    predictor = FlightPredictor(model_path, features)
    
    prices = []
    for flight in flights_list:
        price = predictor.predict_single(flight)
        prices.append(price)
    
    return prices


if __name__ == '__main__':
    # Get feature names from training data
    print("Loading feature names from training data...")
    df, features = process_files('data/raw/Data_Train.xlsx', 'data/raw/Test_set.xlsx')
    
    # Initialize predictor with correct features
    predictor = FlightPredictor('models/flight_price_model.pkl', features)
    
    # Example flight
    sample_flight = {
        'Date_of_Journey': '15/03/2019',
        'Dep_Time': '10:30',
        'Arrival_Time': '14:45',
        'Duration': '4h 15m',
        'Airline': 'Jet Airways',
        'Source': 'Delhi',
        'Destination': 'Mumbai',
        'Total_Stops': 1,
        'Additional_Info': 'No info'
    }
    
    price = predictor.predict_single(sample_flight)
    print(f"\nPredicted price: ₹{price:,.0f}")
