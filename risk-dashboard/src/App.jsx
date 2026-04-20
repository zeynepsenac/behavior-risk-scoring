import { useEffect, useState } from "react";
import { getRiskScore } from "./services/api";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

import GaugeChart from "./components/GaugeChart";
import RuleScoreCard from "./components/RuleScoreCard";
import AIExplanation from "./components/AIExplanation";

import Skeleton from "./components/Skeleton";
import ErrorBox from "./components/ErrorBox";
import EmptyState from "./components/EmptyState";

function App() {
  const [data, setData] = useState(null);
  const [showRules, setShowRules] = useState(false);
  const [customerId, setCustomerId] = useState(1);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    getRiskScore(customerId)
      .then((res) => {
        console.log("API RESPONSE:", res);
        console.log("BAND DEBUG:", res.predicted_band, res.risk_band);

        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error("API ERROR:", err);

        setData(null);
        setError("API bağlantı hatası");
        setLoading(false);
      });

  }, [customerId]);

  if (loading) return <Skeleton />;
  if (error) return <ErrorBox message={error} />;
  if (!data) return <EmptyState />;

  // =========================
  // 🔥 SCORE FIX (TEK KAYNAK)
  // =========================
  const rawScore = Number(data.predicted_risk_score);
  const score = Number.isFinite(rawScore) ? rawScore : 0;

  // =========================
  // 🔥 BAND FIX (TEK TRUTH SOURCE)
  // =========================
  const rawBand =
    data.predicted_band ??
    data.risk_band ??
    data.risk_label ??
    "MEDIUM";

  const finalBand = String(rawBand).toUpperCase().trim();

  // sadece geçerli band’ler
  const validBands = ["LOW", "MEDIUM", "HIGH"];

  const safeBand = validBands.includes(finalBand)
    ? finalBand
    : "MEDIUM";

  // =========================
  // COMPONENTS SAFE
  // =========================
  const rawComponents = data.components ?? {
    payment_discipline_score: 0,
    income_stability_index: 0,
    financial_resilience_score: 0,
  };

  const normalizedComponents = {
    payment_discipline_score: rawComponents.payment_discipline_score / 100,
    income_stability_index: rawComponents.income_stability_index / 100,
    financial_resilience_score: rawComponents.financial_resilience_score / 100,
  };

  // =========================
  // EXPLANATION SAFE PARSE
  // =========================
  let contributions = null;

  try {
    if (typeof data.lime_explanation === "string") {
      contributions = JSON.parse(data.lime_explanation);
    } else {
      contributions = data.lime_explanation;
    }
  } catch {
    contributions = null;
  }

  // =========================
  // COLOR LOGIC (UNCHANGED)
  // =========================
  const getScoreColor = (s) => {
    const safe = Number.isFinite(s) ? s : 0;

    if (safe < 0.01) return "#16a34a";
    if (safe < 0.03) return "#f59e0b";
    return "#dc2626";
  };

  // =========================
  // PDF EXPORT
  // =========================
  const exportPDF = () => {
    const doc = new jsPDF();

    doc.setFontSize(18);
    doc.text("Davranış Tabanlı Risk Raporu", 14, 20);

    doc.setFontSize(12);
    doc.text(`Customer ID: ${customerId}`, 14, 30);
    doc.text(`Risk Skoru: ${score.toFixed(6)}`, 14, 38);
    doc.text(`Risk Bandı: ${safeBand}`, 14, 46);

    autoTable(doc, {
      startY: 55,
      head: [["Özellik", "Değer"]],
      body: [
        ["Ödeme Disiplini", rawComponents.payment_discipline_score],
        ["Gelir İstikrarı", rawComponents.income_stability_index],
        ["Finansal Dayanıklılık", rawComponents.financial_resilience_score],
      ],
    });

    doc.save("risk-report.pdf");
  };

  return (
    <div style={{
      padding: "30px",
      fontFamily: "Inter, sans-serif",
      maxWidth: "1100px",
      margin: "0 auto"
    }}>

      <div style={{ marginBottom: "20px" }}>
        <input
          type="number"
          value={customerId}
          onChange={(e) => setCustomerId(Number(e.target.value))}
          style={{
            padding: "8px",
            borderRadius: "8px",
            border: "1px solid #ccc",
            marginRight: "10px"
          }}
        />

        <button onClick={exportPDF}>📄 PDF Rapor</button>

        <button onClick={() => setShowRules(!showRules)}>
          📊 Kural Kartı
        </button>
      </div>

      <h1>📊 Risk Kontrol Paneli</h1>

      <div className="dashboard-container">

        <div className="card">
          <h2>Risk Puanı</h2>

          <h1 style={{ color: getScoreColor(score) }}>
            {score.toFixed(6)}
          </h1>

          <p style={{ color: getScoreColor(score) }}>
            {safeBand}
          </p>
        </div>

        <div className="card">
          <GaugeChart score={score} band={safeBand} />
        </div>

        <div className="card">
          <h3>🧠 Model</h3>
          <p>Versiyon: {data.model_version ?? "v1.0"}</p>
        </div>

        <div className="card">
          <h3>📈 Özellikler</h3>
          <p>Ödeme: {rawComponents.payment_discipline_score}</p>
          <p>Gelir: {rawComponents.income_stability_index}</p>
          <p>Dayanıklılık: {rawComponents.financial_resilience_score}</p>
        </div>

        <div style={{ gridColumn: "1 / -1" }}>
          <AIExplanation
            components={normalizedComponents}
            score={score}
            contributions={contributions}
            band={safeBand}
          />
        </div>

        {showRules && (
          <div style={{ gridColumn: "1 / -1" }}>
            <RuleScoreCard components={rawComponents} />
          </div>
        )}

      </div>
    </div>
  );
}

export default App;