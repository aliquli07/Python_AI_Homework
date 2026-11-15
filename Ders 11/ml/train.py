import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

df = pd.read_csv("housing.csv")

X = df.drop(columns=["price"])
y = df["price"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

pre = ColumnTransformer([
    ("city", OneHotEncoder(handle_unknown="ignore"), ["city"])
], remainder="passthrough")

model = Pipeline([
    ("pre", pre),
    ("rf", RandomForestRegressor(n_estimators=100, min_samples_leaf=5, random_state=42))
])

model.fit(X_train, y_train)

pred = model.predict(X_test)
print("MAE:", round(mean_absolute_error(y_test, pred), 2))
print("R2:", round(r2_score(y_test, pred), 3))

test = pd.DataFrame([{"city": "Baku", "square_meters": 95, "bedrooms": 3, "bathrooms": 2}])
print(model.predict(test))

joblib.dump(model, "model.pkl")
