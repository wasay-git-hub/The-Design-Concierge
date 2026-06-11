import os
import joblib
import pandas as pd
from src.fast_api.config import MODEL_PATH

# Global model cache
_model = None

def load_cost_model():
    """
    Loads the serialized GradientBoostingRegressor pipeline from disk.
    Caches the model to avoid reading from disk on every API request.
    """
    global _model
    if _model is not None:
        return _model
        
    if os.path.exists(MODEL_PATH):
        try:
            _model = joblib.load(MODEL_PATH)
            print(f"Cost prediction model successfully loaded from: '{MODEL_PATH}'")
            return _model
        except Exception as e:
            print(f"Error loading model from disk: {e}")
    else:
        print(f"Warning: Model file not found at '{MODEL_PATH}'. Running on rule-based cost fallback.")
        
    return None

def predict_design_cost(location: str, room_type: str, area_sqft: int, scope_level: int, material_tier: int):
    """
    Predicts cost based on the Gradient Boosting model.
    Returns: (min_estimate, max_estimate)
    """
    model = load_cost_model()
    
    # 1. Prepare input DataFrame matching the features during training
    input_data = pd.DataFrame([{
        "location": location,
        "room_type": room_type,
        "area_sqft": area_sqft,
        "scope_level": scope_level,
        "material_tier": material_tier
    }])
    
    if model is not None:
        try:
            predicted_cost = float(model.predict(input_data)[0])
            # High-end boutique projects display as a target range (+/- 10%)
            min_estimate = round(predicted_cost * 0.90, -2)
            max_estimate = round(predicted_cost * 1.10, -2)
            return min_estimate, max_estimate
        except Exception as e:
            print(f"ML Inference error: {e}. Falling back to rule-based estimation.")
            
    # 2. Rule-Based Fallback (matching the statistics in train_budget_model.py)
    # Average cost per sqft for luxury interior design room types
    room_types_base = {
        "Living Room": 120,
        "Kitchen": 280,
        "Master Bedroom": 90,
        "Bathroom": 220,
        "Dining Room": 110,
        "Foyer": 75
    }
    
    # Get base rate (defaulting to standard room value if not found)
    base_rate = room_types_base.get(room_type, 100)
    base_cost = area_sqft * base_rate
    
    # Location multipliers
    loc_multipliers = {"Miami": 1.25, "Austin": 1.12, "Scottsdale": 1.08}
    loc_index = loc_multipliers.get(location, 1.0)
    
    # Scope multipliers
    scope_multipliers = {1: 0.85, 2: 1.30, 3: 2.40}
    scope_mult = scope_multipliers.get(scope_level, 1.0)
    
    # Material tier multipliers
    material_multipliers = {1: 1.0, 2: 1.65, 3: 2.80}
    material_mult = material_multipliers.get(material_tier, 1.0)
    
    calculated_cost = base_cost * loc_index * scope_mult * material_mult
    
    # Return estimated range
    min_estimate = round(calculated_cost * 0.90, -2)
    max_estimate = round(calculated_cost * 1.10, -2)
    return max_estimate if min_estimate > max_estimate else min_estimate, max_estimate
