"""
train.py
Train Random Forest and XGBoost, compare, save winner.
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Import from data_pipeline
from data_pipeline import process_files


def train_and_evaluate(train_xlsx, test_xlsx, model_output_dir='models'):
    """
    Full pipeline: load → clean → train both models → compare → save winner.
    """
    
    # ===== STEP 1: Load and clean =====
    df, features = process_files(train_xlsx, test_xlsx)
    
    # ===== STEP 2: Split data =====
    # Separate train (has Price) from test (no Price)
    has_price = df[df['Price'].notna()]
    no_price = df[df['Price'].isna()]
    
    X = has_price[features]
    y = has_price['Price']
    
    # 80/20 split for validation
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\n{'='*60}")
    print(f"Train: {X_train.shape[0]} | Val: {X_val.shape[0]}")
    print(f"{'='*60}")
    
    # ===== STEP 3: Train models =====
    print("\nTraining Random Forest...")
    rf = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    
    print("Training XGBoost...")
    xgb = XGBRegressor(n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42)
    xgb.fit(X_train, y_train)
    
    # ===== STEP 4: Evaluate both =====
    def evaluate(model, name):
        y_pred_train = model.predict(X_train)
        y_pred_val = model.predict(X_val)
        
        train_r2 = r2_score(y_train, y_pred_train)
        val_mae = mean_absolute_error(y_val, y_pred_val)
        val_rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))
        val_r2 = r2_score(y_val, y_pred_val)
        
        print(f"\n{name}")
        print(f"  Train R²:     {train_r2:.4f}")
        print(f"  Val MAE:      ₹{val_mae:,.0f}")
        print(f"  Val RMSE:     ₹{val_rmse:,.0f}")
        print(f"  Val R²:       {val_r2:.4f}")
        print(f"  Overfit gap:  {train_r2 - val_r2:.4f}")
        
        return {
            'model': model,
            'train_r2': train_r2,
            'val_mae': val_mae,
            'val_rmse': val_rmse,
            'val_r2': val_r2,
            'overfit_gap': train_r2 - val_r2
        }
    
    print(f"\n{'='*60}")
    print("EVALUATION")
    print(f"{'='*60}")
    
    rf_results = evaluate(rf, 'Random Forest')
    xgb_results = evaluate(xgb, 'XGBoost')
    
    # ===== STEP 5: Pick winner (lowest MAE) and save =====
    print(f"\n{'='*60}")
    print("WINNER")
    print(f"{'='*60}")
    
    if rf_results['val_mae'] < xgb_results['val_mae']:
        winner = rf_results
        winner_name = 'Random Forest'
    else:
        winner = xgb_results
        winner_name = 'XGBoost'
    
    print(f"\n✓ {winner_name} wins!")
    print(f"  Val MAE: ₹{winner['val_mae']:,.0f}")
    print(f"  Val R²:  {winner['val_r2']:.4f}")
    
    # Save model
    Path(model_output_dir).mkdir(exist_ok=True)
    model_path = Path(model_output_dir) / 'flight_price_model.pkl'
    joblib.dump(winner['model'], model_path)
    print(f"\n✓ Model saved to {model_path}")
    
    return winner['model'], features


if __name__ == '__main__':
    model, features = train_and_evaluate(
        'data/raw/Data_Train.xlsx',
        'data/raw/Test_set.xlsx',
        'models'
    )
