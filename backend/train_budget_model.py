import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error

# 1. Dataset Configuration
DATA_FILE = "budget_data.csv"
MODEL_DIR = os.path.join("backend", "app", "ml")
MODEL_FILE = os.path.join(MODEL_DIR, "budget_model.joblib")

def generate_mock_luxury_data(num_samples=1200):
    """
    Generates a highly realistic dataset based on actual high-end interior design
    cost factors for boutique projects in US markets.
    """
    np.random.seed(42)
    
    # Locations and cost indexes (Miami = 1.25, Austin = 1.12, Scottsdale = 1.08)
    locations = ["Miami", "Austin", "Scottsdale"]
    loc_probs = [0.4, 0.35, 0.25]
    
    # Room types and base cost multiplier per square foot
    room_types = {
        "Living Room": 120,
        "Kitchen": 280,
        "Master Bedroom": 90,
        "Bathroom": 220,
        "Dining Room": 110,
        "Foyer": 75
    }
    room_choices = list(room_types.keys())
    
    # Scopes: 1 = Furnishing & Styling, 2 = Soft Remodel, 3 = Gut Renovation
    scopes = [1, 2, 3]
    scope_multipliers = {1: 0.85, 2: 1.30, 3: 2.40}
    
    # Material Tiers: 1 = Premium, 2 = Luxury, 3 = Ultra-Luxury
    materials = [1, 2, 3]
    material_multipliers = {1: 1.0, 2: 1.65, 3: 2.80}

    data = []
    for _ in range(num_samples):
        loc = np.random.choice(locations, p=loc_probs)
        room = np.random.choice(room_choices)
        scope = np.random.choice(scopes, p=[0.4, 0.4, 0.2])
        material = np.random.choice(materials, p=[0.5, 0.35, 0.15])
        
        # Room area sizing based on type (luxury sizing guidelines)
        if room == "Kitchen":
            area = np.random.randint(150, 450)
        elif room == "Living Room":
            area = np.random.randint(250, 800)
        elif room in ["Bathroom", "Foyer"]:
            area = np.random.randint(50, 200)
        else: # Bedrooms / Dining
            area = np.random.randint(150, 500)
            
        # Regional cost index mapping
        loc_index = 1.25 if loc == "Miami" else (1.12 if loc == "Austin" else 1.08)
        
        # Calculate realistic baseline design cost
        base_rate = room_types[room]
        base_cost = area * base_rate
        
        # Apply multipliers
        calculated_cost = base_cost * loc_index * scope_multipliers[scope] * material_multipliers[material]
        
        # Add random noise (variance representing unique craftsmanship, shipping fees, structural surprises)
        noise = np.random.normal(0, calculated_cost * 0.08)
        final_cost = max(8000, round(calculated_cost + noise, -2)) # Minimum project cost $8k
        
        data.append({
            "location": loc,
            "room_type": room,
            "area_sqft": area,
            "scope_level": scope,
            "material_tier": material,
            "cost": final_cost
        })
        
    df = pd.DataFrame(data)
    df.to_csv(DATA_FILE, index=False)
    print(f"Generated realistic mock luxury dataset: '{DATA_FILE}' ({num_samples} records).")
    return df

def main():
    # Load dataset or generate if missing
    if os.path.exists(DATA_FILE):
        print(f"Loading dataset from: '{DATA_FILE}'...")
        df = pd.read_csv(DATA_FILE)
    else:
        df = generate_mock_luxury_data()
        
    # Split features and target
    X = df.drop(columns=["cost"])
    y = df["cost"]
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Define preprocessing for categorical & numerical features
    categorical_features = ["location", "room_type"]
    numerical_features = ["area_sqft", "scope_level", "material_tier"]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), categorical_features),
            ("num", StandardScaler(), numerical_features)
        ]
    )
    
    # Define Gradient Boosting Regressor Pipeline
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", GradientBoostingRegressor(random_state=42))
    ])
    
    # Set up simple hyperparameter grid search to show professional tuning
    param_grid = {
        "regressor__n_estimators": [100, 150],
        "regressor__learning_rate": [0.05, 0.1],
        "regressor__max_depth": [3, 4, 5]
    }
    
    print("Tuning Gradient Boosting hyperparameters...")
    grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring="r2", n_jobs=-1)
    grid_search.fit(X_train, y_train)
    
    best_model = grid_search.best_estimator_
    print(f"Best parameters found: {grid_search.best_params_}")
    
    # Evaluation
    y_pred = best_model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    print(f"\n--- Model Evaluation ---")
    print(f"R-squared Score: {r2:.4f}")
    print(f"Mean Absolute Error: ${mae:,.2f}")
    print(f"------------------------\n")
    
    # Save model and preprocessor pipeline
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(best_model, MODEL_FILE)
    print(f"Saved trained Gradient Boosting pipeline to: '{MODEL_FILE}'")

if __name__ == "__main__":
    main()
