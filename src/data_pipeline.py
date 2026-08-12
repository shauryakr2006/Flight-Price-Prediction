"""
data_pipeline.py
Load raw data, clean it, engineer features. Done.
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path


def parse_duration(duration_str):
    """
    Convert "2h 50m" -> 170 minutes. Handle edge cases.
    """
    if pd.isna(duration_str):
        return np.nan
    
    duration_str = str(duration_str).strip()
    total_minutes = 0
    
    hours_match = re.search(r'(\d+)\s*h', duration_str)
    if hours_match:
        total_minutes += int(hours_match.group(1)) * 60
    
    mins_match = re.search(r'(\d+)\s*m', duration_str)
    if mins_match:
        total_minutes += int(mins_match.group(1))
    
    return total_minutes if total_minutes > 0 else np.nan


def extract_time_component(time_str, component='hour'):
    """
    Safely extract hour or minute from time string (HH:MM).
    Returns NaN if string is malformed.
    """
    if pd.isna(time_str):
        return np.nan
    
    time_str = str(time_str).strip()
    
    # Only process if it looks like time (contains ':')
    if ':' not in time_str:
        return np.nan
    
    try:
        parts = time_str.split(':')
        if component == 'hour':
            return int(parts[0])
        else:  # minute
            return int(parts[1])
    except:
        return np.nan


def clean_and_engineer(df):
    """
    Take raw dataframe, extract features, return clean dataframe.
    """
    df = df.copy()
    
    # Extract date features
    df['Date'] = pd.to_datetime(df['Date_of_Journey'], format='%d/%m/%Y').dt.day
    df['Month'] = pd.to_datetime(df['Date_of_Journey'], format='%d/%m/%Y').dt.month
    df['Year'] = pd.to_datetime(df['Date_of_Journey'], format='%d/%m/%Y').dt.year
    
    # Extract time features (handle mixed formats safely)
    df['Dept_hour'] = df['Dep_Time'].apply(lambda x: extract_time_component(x, 'hour')).astype('Int64')
    df['Dept_min'] = df['Dep_Time'].apply(lambda x: extract_time_component(x, 'minute')).astype('Int64')
    df['Arrival_hour'] = df['Arrival_Time'].apply(lambda x: extract_time_component(x, 'hour')).astype('Int64')
    df['Arrival_min'] = df['Arrival_Time'].apply(lambda x: extract_time_component(x, 'minute')).astype('Int64')
    
    # Parse duration
    df['Duration_mins'] = df['Duration'].apply(parse_duration)
    
    # Fix Total_Stops (convert string values to numbers, then fill NaN)
    def convert_stops(val):
        if pd.isna(val):
            return np.nan
        if isinstance(val, (int, float)):
            return int(val)
        val_str = str(val).strip().lower()
        if val_str == 'non-stop':
            return 0
        try:
            return int(val_str)
        except:
            return np.nan
    
    df['Total_Stops'] = df['Total_Stops'].apply(convert_stops).fillna(1).astype(int)
    
    # Extract Additional_Info flags
    df['Additional_Info'] = df['Additional_Info'].fillna('')
    df['has_meal'] = df['Additional_Info'].str.contains('meal', case=False, na=False).astype(int)
    df['has_baggage'] = df['Additional_Info'].str.contains('baggage', case=False, na=False).astype(int)
    df['has_layover'] = df['Additional_Info'].str.contains('layover', case=False, na=False).astype(int)
    
    # One-hot encode categorical features
    df = pd.get_dummies(df, columns=['Airline', 'Source', 'Destination'], drop_first=True)
    
    # Convert bool columns to int (XGBoost requirement)
    bool_cols = df.select_dtypes(include='bool').columns
    df[bool_cols] = df[bool_cols].astype(int)
    
    # Drop original string columns (including Route which we don't need)
    cols_to_drop = ['Date_of_Journey', 'Dep_Time', 'Arrival_Time', 'Duration', 'Additional_Info', 'Route']
    df = df.drop(columns=cols_to_drop, errors='ignore')
    
    return df


def process_files(train_xlsx, test_xlsx):
    """
    Load raw files, clean both, return combined dataframe and feature list.
    """
    print("Loading data...")
    train_df = pd.read_excel(train_xlsx)
    test_df = pd.read_excel(test_xlsx)
    
    print(f"Train: {train_df.shape[0]} rows | Test: {test_df.shape[0]} rows")
    
    # Clean both
    print("Cleaning and engineering features...")
    train_clean = clean_and_engineer(train_df)
    test_clean = clean_and_engineer(test_df)
    
    # Combine (test rows will have NaN for Price)
    df = pd.concat([train_clean, test_clean], ignore_index=True)
    
    print(f"Final: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"Price column nulls: {df['Price'].isna().sum()} (these are test rows)")
    
    # Feature list (everything except Price)
    features = [col for col in df.columns if col != 'Price']
    
    return df, features


if __name__ == '__main__':
    # Test it
    train_path = 'data/raw/Data_Train.xlsx'
    test_path = 'data/raw/Test_set.xlsx'
    
    df, features = process_files(train_path, test_path)
    print(f"\nFeatures ({len(features)}): {features[:5]}...")
    print(f"\nSample row:\n{df.iloc[0]}")
