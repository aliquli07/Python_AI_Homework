import { useState } from "react";

const cities = ["Baku", "Ganja", "Sumgait", "Mingachevir", "Lankaran"];

function App() {
  const [city, setCity] = useState("Baku");
  const [squareMeters, setSquareMeters] = useState(95);
  const [bedrooms, setBedrooms] = useState(3);
  const [bathrooms, setBathrooms] = useState(2);
  const [price, setPrice] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const predict = async () => {
    setLoading(true);
    setError("");
    setPrice(null);

    try {
      const res = await fetch("http://localhost:5000/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          city: city,
          square_meters: Number(squareMeters),
          bedrooms: Number(bedrooms),
          bathrooms: Number(bathrooms),
        }),
      });

      if (!res.ok) {
        throw new Error("server error");
      }

      const data = await res.json();
      setPrice(data.price);
    } catch (e) {
      setError("Qiymeti hesablamaq olmadi");
    }

    setLoading(false);
  };

  return (
    <div className="card">
      <h1>Price Predictor</h1>

      <label>City</label>
      <select value={city} onChange={(e) => setCity(e.target.value)}>
        {cities.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>

      <label>Square meters</label>
      <input
        type="number"
        value={squareMeters}
        onChange={(e) => setSquareMeters(e.target.value)}
      />

      <label>Bedrooms</label>
      <input
        type="number"
        value={bedrooms}
        onChange={(e) => setBedrooms(e.target.value)}
      />

      <label>Bathrooms</label>
      <input
        type="number"
        value={bathrooms}
        onChange={(e) => setBathrooms(e.target.value)}
      />

      <button onClick={predict} disabled={loading}>
        {loading ? "..." : "Predict"}
      </button>

      {price !== null && (
        <div className="result">{price.toLocaleString("fr-FR")} AZN</div>
      )}

      {error && <div className="error">{error}</div>}
    </div>
  );
}

export default App;
