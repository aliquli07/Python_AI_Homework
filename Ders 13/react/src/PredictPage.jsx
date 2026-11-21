import { useState } from "react";
import { predict } from "./api.js";
import { cities } from "./cities.js";

function PredictPage() {
  const [city, setCity] = useState("Baku");
  const [sqm, setSqm] = useState(95);
  const [bedrooms, setBedrooms] = useState(3);
  const [bathrooms, setBathrooms] = useState(2);
  const [price, setPrice] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onPredict = async () => {
    setLoading(true);
    setError("");
    setPrice(null);

    try {
      const data = await predict({
        city: city,
        sqm: Number(sqm),
        bedrooms: Number(bedrooms),
        bathrooms: Number(bathrooms),
      });
      setPrice(Math.round(data.priceAZN));
    } catch (e) {
      setError(e.message);
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

      <label>Sqm</label>
      <input type="number" value={sqm} onChange={(e) => setSqm(e.target.value)} />

      <label>Bedrooms</label>
      <input type="number" value={bedrooms} onChange={(e) => setBedrooms(e.target.value)} />

      <label>Bathrooms</label>
      <input type="number" value={bathrooms} onChange={(e) => setBathrooms(e.target.value)} />

      <button onClick={onPredict} disabled={loading}>
        {loading ? "..." : "Predict"}
      </button>

      {price !== null && <div className="result">{price.toLocaleString("fr-FR")} AZN</div>}

      {error && <div className="error">{error}</div>}
    </div>
  );
}

export default PredictPage;
