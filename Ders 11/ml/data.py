import numpy as np
import pandas as pd

np.random.seed(42)

cities = {"Baku": 1500, "Ganja": 850, "Sumgait": 800, "Mingachevir": 650, "Lankaran": 700}

n = 1500
city = np.random.choice(list(cities.keys()), n)
square_meters = np.random.randint(35, 220, n)
bedrooms = np.clip(np.round(square_meters / 35 + np.random.randn(n) * 0.5), 1, 6).astype(int)
bathrooms = np.clip(np.round(bedrooms / 2 + np.random.randn(n) * 0.4), 1, 4).astype(int)

base = np.array([cities[c] for c in city])
price = base * square_meters + bedrooms * 4000 + bathrooms * 3000 + np.random.randn(n) * 8000
price = price.round(0)

df = pd.DataFrame({
    "city": city,
    "square_meters": square_meters,
    "bedrooms": bedrooms,
    "bathrooms": bathrooms,
    "price": price
})

df.to_csv("housing.csv", index=False)
print(df.shape)
print(df.head())
