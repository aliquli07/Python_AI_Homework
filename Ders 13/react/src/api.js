const API = "http://localhost:5000/api/AI";

async function send(url, options) {
  let res;
  try {
    res = await fetch(API + url, options);
  } catch (e) {
    throw { message: "Servere qosulmaq olmadi" };
  }

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const detail = data && data.detail;
    if (detail && typeof detail === "object" && !Array.isArray(detail)) {
      throw { message: detail.message, errors: detail.errors || [] };
    }
    if (Array.isArray(detail)) {
      throw { message: "Melumat duzgun deyil" };
    }
    throw { message: detail || "Xeta bas verdi (" + res.status + ")" };
  }

  return data;
}

export function predict(data) {
  return send("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function addApartment(data) {
  return send("/apartments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function importCsv(file) {
  const form = new FormData();
  form.append("file", file);
  return send("/apartments/import", {
    method: "POST",
    body: form,
  });
}

export function retrain() {
  return send("/retrain", { method: "POST" });
}
