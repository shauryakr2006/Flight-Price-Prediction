"""
app.py
Streamlit web app: input flight details, get price prediction.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from predict import FlightPredictor
from data_pipeline import process_files

# Page config - WIDE layout
st.set_page_config(page_title="Flight Price Predictor", layout="wide")

# Title
st.title("✈️ Flight Price Predictor")
st.markdown("Enter flight details to get an instant price prediction")

# Load model and features (cache to avoid reloading)
@st.cache_resource
def load_model():
    """Load trained model and get feature names."""
    print("Loading model...")
    df, features = process_files('data/raw/Data_Train.xlsx', 'data/raw/Test_set.xlsx')
    predictor = FlightPredictor('models/flight_price_model.pkl', features)
    return predictor, features

predictor, features = load_model()

# Input form
with st.form("flight_form"):
    st.subheader("Flight Details")
    
    # 3 columns for main inputs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📍 SELECTION**")
        
        st.caption("Which airline operates this flight?")
        airline = st.selectbox(
            "Airline",
            ["Air India", "GoAir", "IndiGo", "Jet Airways", "Jet Airways Business", 
             "Multiple carriers", "Multiple carriers Premium economy", "SpiceJet", 
             "Trujet", "Vistara", "Vistara Premium economy"],
            label_visibility="collapsed"
        )
        
        st.caption("Where are you flying from?")
        source = st.selectbox(
            "Source City",
            ["Bangalore", "Chennai", "Delhi", "Kolkata", "Mumbai"],
            label_visibility="collapsed"
        )
        
        st.caption("Where are you flying to?")
        destination = st.selectbox(
            "Destination City",
            ["Bangalore", "Cochin", "Delhi", "Hyderabad", "Kolkata", "Mumbai"],
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("**📅 JOURNEY**")
        
        st.caption("When do you want to travel?")
        date_of_journey = st.date_input("Date of Journey", label_visibility="collapsed")
        
        st.caption("How many stops/connections? (0 = direct flight)")
        total_stops = st.number_input("Number of Stops", min_value=0, max_value=4, value=1, label_visibility="collapsed")
        
        st.caption("Total flight duration in hours")
        duration_hours = st.number_input("Duration (hours)", min_value=0.5, max_value=50.0, step=0.5, value=2.0, label_visibility="collapsed")
    
    with col3:
        st.markdown("**⏰ TIMES**")
        
        st.caption("What time does the flight depart?")
        dep_time = st.time_input("Departure Time", label_visibility="collapsed")
        
        st.caption("What time does it arrive?")
        arrival_time = st.time_input("Arrival Time", label_visibility="collapsed")
        
        st.markdown("")  # Spacing
    
    st.divider()
    
    # Additional info - actual flight conditions
    st.markdown("**✈️ FLIGHT CONDITIONS**")
    col_cond1, col_cond2, col_cond3, col_cond4 = st.columns(4)
    
    with col_cond1:
        st.markdown("**Meal Service**")
        st.caption("Is food/beverage included?")
        meal_included = st.selectbox(
            "Meal Service",
            ["No info", "In-flight meal not included", "Meal included"],
            help="Is meal service included?",
            label_visibility="collapsed"
        )
    
    with col_cond2:
        st.markdown("**Baggage**")
        st.caption("Can you check luggage?")
        baggage_info = st.selectbox(
            "Baggage",
            ["No info", "No check-in baggage included", "Baggage included"],
            help="Baggage allowance",
            label_visibility="collapsed"
        )
    
    with col_cond3:
        st.markdown("**Layover**")
        st.caption("Length of connection wait (if any)")
        layover_info = st.selectbox(
            "Layover",
            ["No info", "1 Short layover", "1 Long layover", "2 Long layover"],
            help="Layover duration and count",
            label_visibility="collapsed"
        )
    
    with col_cond4:
        st.markdown("**Special**")
        st.caption("Any other special conditions?")
        special_info = st.selectbox(
            "Special",
            ["No info", "Business class", "Red-eye flight", "Change airports"],
            help="Other special conditions",
            label_visibility="collapsed"
        )
    
    # Build Additional_Info from selections
    additional_info_parts = []
    if meal_included != "No info":
        additional_info_parts.append(meal_included)
    if baggage_info != "No info":
        additional_info_parts.append(baggage_info)
    if layover_info != "No info":
        additional_info_parts.append(layover_info)
    if special_info != "No info":
        additional_info_parts.append(special_info)
    
    additional_info = " | ".join(additional_info_parts) if additional_info_parts else "No info"
    
    st.divider()
    
    # Submit button (full width)
    submitted = st.form_submit_button("🔍 Predict Price", use_container_width=True)

# Make prediction
if submitted:
    # Format inputs
    date_str = date_of_journey.strftime('%d/%m/%Y')
    dep_str = dep_time.strftime('%H:%M')
    arr_str = arrival_time.strftime('%H:%M')
    duration_str = f"{int(duration_hours)}h {int((duration_hours % 1) * 60)}m"
    
    # Create flight dict
    flight_dict = {
        'Date_of_Journey': date_str,
        'Dep_Time': dep_str,
        'Arrival_Time': arr_str,
        'Duration': duration_str,
        'Airline': airline,
        'Source': source,
        'Destination': destination,
        'Total_Stops': int(total_stops),
        'Additional_Info': additional_info
    }
    
    # Predict
    try:
        price = predictor.predict_single(flight_dict)
        
        # Display result in wide boxes
        col_result1, col_result2 = st.columns([2, 1])
        
        with col_result1:
            st.success("✅ Prediction successful!")
            st.metric("Predicted Price", f"₹{price:,.0f}", delta="Based on ML model")
        
        with col_result2:
            st.info(
                f"**Route:** {source} → {destination}\n\n"
                f"**Airline:** {airline}\n\n"
                f"**Stops:** {int(total_stops)}"
            )
        
        # Show breakdown
        with st.expander("📋 Full Flight Summary", expanded=False):
            summary_df = pd.DataFrame({
                'Detail': ['Airline', 'Route', 'Stops', 'Departure', 'Arrival', 'Duration', 'Services'],
                'Value': [
                    airline,
                    f"{source} → {destination}",
                    f"{int(total_stops)} stop(s)",
                    f"{date_str} {dep_str}",
                    f"{arr_str}",
                    duration_str,
                    additional_info
                ]
            })
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.error(f"❌ Error making prediction: {e}")

# Footer with metrics
st.divider()
col_foot1, col_foot2, col_foot3 = st.columns(3)

with col_foot1:
    st.markdown("""
    #### How it works
    - Select flight details
    - Check any services
    - Click "Predict Price"
    - Get instant prediction
    """)

with col_foot2:
    st.markdown("""
    #### Model Info
    - **Type:** Random Forest
    - **Training Data:** 10K+ flights
    - **Performance:** MAE ₹756
    """)

with col_foot3:
    st.markdown("""
    #### Accuracy Metrics
    - **R² Score:** 0.8842
    - **RMSE:** ₹1,565
    - **Avg Error:** ±₹756
    """)
