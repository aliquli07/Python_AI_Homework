import io
import math
import os
import threading
import traceback
from datetime import datetime
from typing import Optional

import joblib
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from trainer import DATA_PATH, MODEL_PATH, save_bundle, train

app = FastAPI(title="Price Prediction AI Service")

data_lock = threading.Lock()
train_lock = threading.Lock()

REQUIRED_COLUMNS = ["PriceAZN", "Bedrooms", "Bathrooms", "Sqm", "City"]

try:
    loaded = joblib.load(MODEL_PATH)
    PIPELINE = loaded["pipeline"]
    FEATURES = loaded.get("featured_order", ["Bedrooms", "Bathrooms", "Sqm", "City"])
    print(f"Model loaded from {MODEL_PATH}")
except Exception as e:
    print(f"Failed to load model from {MODEL_PATH} - {e}")
    PIPELINE = None
    FEATURES = ["Bedrooms", "Bathrooms", "Sqm", "City"]


class PredictIn(BaseModel):
    bedrooms: float
    bathrooms: float
    sqm: float
    city: str


class ApartmentIn(BaseModel):
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    sqm: Optional[float] = None
    city: Optional[str] = None
    priceAZN: Optional[float] = None


def to_number(value):
    if value is None:
        return None
    try:
        number = float(str(value).strip())
    except ValueError:
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def check_apartment(bedrooms, bathrooms, sqm, city, price):
    bedrooms = to_number(bedrooms)
    bathrooms = to_number(bathrooms)
    sqm = to_number(sqm)
    price = to_number(price)
    city = "" if city is None else str(city).strip()

    if bedrooms is None or bedrooms <= 0 or not bedrooms.is_integer():
        return None, "Bedrooms musbet tam eded olmalidir"
    if bathrooms is None or bathrooms <= 0 or not bathrooms.is_integer():
        return None, "Bathrooms musbet tam eded olmalidir"
    if sqm is None or sqm <= 0:
        return None, "Sqm musbet eded olmalidir"
    if city == "":
        return None, "City bos ola bilmez"
    if price is None or price <= 0:
        return None, "PriceAZN musbet eded olmalidir"

    return {
        "PriceAZN": int(price) if price.is_integer() else price,
        "Bedrooms": int(bedrooms),
        "Bathrooms": int(bathrooms),
        "Sqm": sqm,
        "City": city,
    }, None


def append_rows(rows):
    with data_lock:
        text = DATA_PATH.read_text(encoding="utf-8")
        header = text.splitlines()[0].split(",")

        if not text.endswith("\n"):
            text += "\n"

        for row in rows:
            text += ",".join(str(row[col]) for col in header) + "\n"

        tmp_path = DATA_PATH.with_suffix(".tmp")
        tmp_path.write_text(text, encoding="utf-8")
        os.replace(tmp_path, DATA_PATH)

        return len(text.strip().splitlines()) - 1


def read_data():
    with data_lock:
        return pd.read_csv(DATA_PATH)


@app.get("/")
def home():
    return {"status": "ok", "modelLoaded": PIPELINE is not None}


@app.post("/predict")
def predict(request: PredictIn):
    if PIPELINE is None:
        raise HTTPException(status_code=503, detail="Model yuklenmeyib")

    try:
        features = {
            "Bedrooms": [request.bedrooms],
            "Bathrooms": [request.bathrooms],
            "Sqm": [request.sqm],
            "City": [request.city],
        }
        features_data = pd.DataFrame(features, columns=FEATURES)
        prediction = PIPELINE.predict(features_data)[0]
        return {"priceAZN": float(prediction)}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Proqnoz alinmadi: {e}")


@app.post("/apartments")
def add_apartment(apartment: ApartmentIn):
    row, error = check_apartment(
        apartment.bedrooms,
        apartment.bathrooms,
        apartment.sqm,
        apartment.city,
        apartment.priceAZN,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    total = append_rows([row])
    return {"message": "Menzil elave olundu", "added": 1, "total": total}


@app.post("/apartments/import")
async def import_apartments(file: UploadFile = File(...)):
    content = await file.read()

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Fayl UTF-8 formatinda olmalidir")

    if text.strip() == "":
        raise HTTPException(status_code=400, detail="Fayl bosdur")

    try:
        data = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    except Exception:
        raise HTTPException(status_code=400, detail="CSV faylini oxumaq olmadi")

    data.columns = [col.strip() for col in data.columns]
    missing = [col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Sutunlar catismir: {', '.join(missing)}")

    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Faylda melumat yoxdur")

    rows = []
    errors = []
    for i, item in data.iterrows():
        row, error = check_apartment(
            item["Bedrooms"],
            item["Bathrooms"],
            item["Sqm"],
            item["City"],
            item["PriceAZN"],
        )
        if error:
            errors.append({"row": i + 2, "error": error})
        else:
            rows.append(row)

    if errors:
        raise HTTPException(status_code=400, detail={
            "message": "Idxal redd olundu, CSV deyismedi",
            "errors": errors,
        })

    total = append_rows(rows)
    return {"message": "Idxal ugurla bitdi", "added": len(rows), "total": total}


@app.post("/retrain")
def retrain():
    global PIPELINE, FEATURES

    if not train_lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="Yeniden oyretme artiq davam edir")

    try:
        data = read_data()
        bundle, metrics, rows = train(data)
        save_bundle(bundle)
        PIPELINE = bundle["pipeline"]
        FEATURES = bundle["featured_order"]
        return {
            "message": "Model yeniden oyredildi",
            "rows": rows,
            "metrics": metrics,
            "trainedAt": datetime.now().isoformat(timespec="seconds"),
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Oyretme alinmadi, kohne model saxlanildi: {e}")
    finally:
        train_lock.release()
