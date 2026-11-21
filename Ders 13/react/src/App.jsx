import { useState } from "react";
import PredictPage from "./PredictPage.jsx";
import DataPage from "./DataPage.jsx";

function App() {
  const [page, setPage] = useState("predict");

  return (
    <div className="app">
      <nav className="nav">
        <button
          className={page === "predict" ? "active" : ""}
          onClick={() => setPage("predict")}
        >
          Proqnoz
        </button>
        <button
          className={page === "data" ? "active" : ""}
          onClick={() => setPage("data")}
        >
          Melumatlar
        </button>
      </nav>

      {page === "predict" ? <PredictPage /> : <DataPage />}
    </div>
  );
}

export default App;
