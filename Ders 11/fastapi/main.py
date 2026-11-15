import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
model = joblib.load("../ml/model.pkl")


class House(BaseModel):
    city: str
    square_meters: float
    bedrooms: int
    bathrooms: int


@app.get("/")
def home():
    return {"status": "ok"}


@app.post("/predict")
def predict(house: House):
    data = pd.DataFrame([house.model_dump()])
    price = model.predict(data)[0]
    return {"price": round(float(price))}
