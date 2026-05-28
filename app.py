import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import joblib
import os
import sys

# Global model variable
model = None
MODEL_PATH = 'house_price_model.pkl'

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        # Load the existing model
        model = joblib.load(MODEL_PATH)
        print("✅ Model loaded from file.")
    else:
        # Train a new model if none exists
        train_model()

def train_model():
    global model
    try:
        # Load and prepare the data
        data = pd.read_csv("House_Price.csv")
        data = data[["lot area", "Price"]].dropna()

        X = data[["lot area"]]
        y = data["Price"]

        # Train the model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Save the model
        joblib.dump(model, MODEL_PATH)
        print("✅ Model trained and saved successfully!")

    except Exception as e:
        print(f"❌ Error training model: {str(e)}")
        raise

def predict_price(lot_area_value):
    try:
        lot_area = float(lot_area_value)
        prediction = model.predict([[lot_area]])[0]
        print(f"\n📊 Prediction for Lot Area = {lot_area}: ₹ {prediction:.2f}")
    except Exception as e:
        print(f"❌ Error in prediction: {str(e)}")

def health_check():
    print("🩺 Status: Healthy")

if __name__ == "__main__":
    load_model()

    if len(sys.argv) == 2:
        if sys.argv[1] == "health":
            health_check()
        else:
            predict_price(sys.argv[1])
    else:
        print("📌 Usage:")
        print("  python house_price_predictor.py 3000     # Predict for lot area = 3000")
        print("  python house_price_predictor.py health   # Health check")
