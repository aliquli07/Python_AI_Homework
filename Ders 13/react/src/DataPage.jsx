import { useState } from "react";
import { addApartment, importCsv, retrain } from "./api.js";
import { cities } from "./cities.js";

const emptyForm = { city: "", sqm: "", bedrooms: "", bathrooms: "", priceAZN: "" };

function isPositiveInt(value) {
  return Number.isInteger(Number(value)) && Number(value) > 0 && value !== "";
}

function isPositive(value) {
  return value !== "" && Number(value) > 0;
}

function checkForm(form) {
  if (form.city === "") return "Seheri secin";
  if (!isPositive(form.sqm)) return "Sahe musbet eded olmalidir";
  if (!isPositiveInt(form.bedrooms)) return "Yataq otagi musbet tam eded olmalidir";
  if (!isPositiveInt(form.bathrooms)) return "Vanna otagi musbet tam eded olmalidir";
  if (!isPositive(form.priceAZN)) return "Qiymet musbet eded olmalidir";
  return "";
}

function DataPage() {
  const [form, setForm] = useState(emptyForm);
  const [adding, setAdding] = useState(false);
  const [addMessage, setAddMessage] = useState("");
  const [addError, setAddError] = useState("");

  const [file, setFile] = useState(null);
  const [fileKey, setFileKey] = useState(0);
  const [importing, setImporting] = useState(false);
  const [importMessage, setImportMessage] = useState("");
  const [importError, setImportError] = useState(null);

  const [training, setTraining] = useState(false);
  const [trainResult, setTrainResult] = useState(null);
  const [trainError, setTrainError] = useState("");

  const change = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setAddMessage("");
    setAddError("");
  };

  const onAdd = async () => {
    setAddMessage("");
    setAddError("");

    const error = checkForm(form);
    if (error) {
      setAddError(error);
      return;
    }

    setAdding(true);
    try {
      const data = await addApartment({
        city: form.city,
        sqm: Number(form.sqm),
        bedrooms: Number(form.bedrooms),
        bathrooms: Number(form.bathrooms),
        priceAZN: Number(form.priceAZN),
      });
      setAddMessage(data.message + ". Umumi yazi sayi: " + data.total);
      setForm(emptyForm);
    } catch (e) {
      setAddError(e.message);
    }
    setAdding(false);
  };

  const onImport = async () => {
    setImportMessage("");
    setImportError(null);

    if (!file) {
      setImportError({ message: "CSV fayli secin", errors: [] });
      return;
    }

    setImporting(true);
    try {
      const data = await importCsv(file);
      setImportMessage(data.message + ". Elave olundu: " + data.added + ", umumi: " + data.total);
      setFile(null);
      setFileKey(fileKey + 1);
    } catch (e) {
      setImportError({ message: e.message, errors: e.errors || [] });
    }
    setImporting(false);
  };

  const onRetrain = async () => {
    setTraining(true);
    setTrainResult(null);
    setTrainError("");
    try {
      const data = await retrain();
      setTrainResult(data);
    } catch (e) {
      setTrainError(e.message);
    }
    setTraining(false);
  };

  return (
    <div className="page">
      <div className="card">
        <h2>Menzil elave et</h2>

        <label>City</label>
        <select name="city" value={form.city} onChange={change}>
          <option value="">Secin</option>
          {cities.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        <label>Sqm</label>
        <input name="sqm" type="number" value={form.sqm} onChange={change} />

        <label>Bedrooms</label>
        <input name="bedrooms" type="number" value={form.bedrooms} onChange={change} />

        <label>Bathrooms</label>
        <input name="bathrooms" type="number" value={form.bathrooms} onChange={change} />

        <label>PriceAZN</label>
        <input name="priceAZN" type="number" value={form.priceAZN} onChange={change} />

        <button onClick={onAdd} disabled={adding}>
          {adding ? "..." : "Menzil elave et"}
        </button>

        {addMessage && <div className="success">{addMessage}</div>}
        {addError && <div className="error">{addError}</div>}
      </div>

      <div className="card">
        <h2>CSV idxal et</h2>
        <p className="hint">Sutunlar: PriceAZN,Bedrooms,Bathrooms,Sqm,City</p>

        <input
          key={fileKey}
          type="file"
          accept=".csv"
          onChange={(e) => {
            setFile(e.target.files[0] || null);
            setImportMessage("");
            setImportError(null);
          }}
        />

        <button onClick={onImport} disabled={importing}>
          {importing ? "..." : "Idxal et"}
        </button>

        {importMessage && <div className="success">{importMessage}</div>}
        {importError && (
          <div className="error">
            {importError.message}
            {importError.errors.length > 0 && (
              <ul>
                {importError.errors.map((err) => (
                  <li key={err.row}>
                    Setir {err.row}: {err.error}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>

      <div className="card">
        <h2>Model</h2>

        <button onClick={onRetrain} disabled={training}>
          {training ? "Yeniden oyretme davam edir…" : "Retrain — modeli yeniden oyret"}
        </button>

        {trainResult && (
          <div className="metrics">
            <div className="success">{trainResult.message}</div>
            <div>Yazi sayi: {trainResult.rows}</div>
            <div>MAE: {trainResult.metrics.mae}</div>
            <div>MSE: {trainResult.metrics.mse}</div>
            <div>RMSE: {trainResult.metrics.rmse}</div>
            <div>R2: {trainResult.metrics.r2}</div>
            <div>Vaxt: {trainResult.trainedAt}</div>
          </div>
        )}
        {trainError && <div className="error">{trainError}</div>}
      </div>
    </div>
  );
}

export default DataPage;
