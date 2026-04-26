import { useState } from "react";
import { getRiskScore } from "./services/api";

import GaugeChart from "./components/GaugeChart";
import RuleScoreCard from "./components/RuleScoreCard";
import AIExplainabilityDashboard from "./components/AIExplanation";
import Skeleton from "./components/Skeleton";

export default function App() {
  const [id, setId] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fallbackData = {
    predicted_risk_score: 0.28,
    predicted_band: "MEDIUM",
    model_confidence: 0.65,
    payment_discipline_score: 55,
    income_stability_index: 48,
    financial_resilience_score: 22,
    components: []
  };

  // =========================
  // DATA VALIDATION (GÜÇLENDİRİLDİ)
  // =========================
  const isInvalidData = (d) => {
    if (!d) return true;

    return (
      d.predicted_risk_score === null ||
      d.predicted_risk_score === undefined ||
      isNaN(d.predicted_risk_score)
    );
  };

  const safeData = isInvalidData(data) ? fallbackData : data;

  // =========================
  // FETCH
  // =========================
  const handleFetch = async () => {
    if (!id) return;

    setLoading(true);

    try {
      const res = await getRiskScore(id);

      // =========================
      // SAFE MAPPING (BACKEND UYUMLU)
      // =========================
      const mapped = {
        predicted_risk_score:
          res?.predicted_risk_score ??
          res?.risk_score ??
          null,

        predicted_band:
          res?.predicted_band ?? "MEDIUM",

        model_confidence:
          res?.model_confidence ??
          res?.confidence ??
          null,

        payment_discipline_score:
          res?.payment_discipline_score ??
          res?.features?.payment_discipline_score ??
          null,

        income_stability_index:
          res?.income_stability_index ??
          res?.features?.income_stability_index ??
          null,

        financial_resilience_score:
          res?.financial_resilience_score ??
          res?.features?.financial_resilience_score ??
          null,

        components:
          res?.components ??
          []
      };

      // =========================
      // NORMALIZATION (KRİTİK FIX)
      // =========================

      // score 100 scale gelirse normalize et
      if (mapped.predicted_risk_score > 1) {
        mapped.predicted_risk_score /= 100;
      }

      if (mapped.model_confidence > 1) {
        mapped.model_confidence /= 100;
      }

      setData(mapped);

    } catch (err) {
      console.error("API Error:", err);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // UI
  // =========================
  return (
    <div>

      {/* HEADER */}
      <div style={{ marginBottom: "16px" }}>
        <h1>📊 Risk Kontrol Paneli</h1>

        <p style={{ marginTop: "4px", color: "#6b7280" }}>
          Rapor No: RISK-{id || "-"}
        </p>

        <div style={{ marginTop: "12px", display: "flex", gap: "10px" }}>
          <input
            placeholder="Müşteri ID (1-1200)"
            value={id}
            onChange={(e) => setId(e.target.value)}
          />

          <button onClick={handleFetch}>
            Analiz Et
          </button>

          {/* PDF FRONTEND BUTTON FIX */}
          <button
            onClick={() =>
              window.open("http://127.0.0.1:8000/report", "_blank")
            }
          >
            PDF Rapor
          </button>
        </div>
      </div>

      {/* LOADING */}
      {loading && <Skeleton />}

      {/* EMPTY STATE */}
      {!loading && !data && (
        <div style={{ color: "#6b7280", padding: "20px" }}>
          Lütfen bir müşteri ID girerek analizi başlatın.
        </div>
      )}

      {/* DASHBOARD */}
      {!loading && data && (
        <div className="dashboard-container">

          {/* SCORE */}
          <div className="card score-card">
            <h2>Risk Skoru</h2>

            <div
              style={{
                fontSize: "32px",
                fontWeight: "bold",
                color: "#ef4444"
              }}
            >
              {safeData.predicted_risk_score !== null
                ? safeData.predicted_risk_score.toFixed(3)
                : "N/A"}
            </div>
          </div>

          {/* GAUGE */}
          <div className="card gauge-card">
            <h2>Risk Ölçer</h2>
            <GaugeChart score={safeData.predicted_risk_score} />
          </div>

          {/* AI EXPLANATION */}
          <div className="card ai-card">
            <AIExplainabilityDashboard data={safeData} />
          </div>

          {/* RULES */}
          <div className="card rules-card">
            <h2>Kural Tabanlı Analiz</h2>

            <RuleScoreCard
              components={safeData.components || []}
              model_confidence={safeData.model_confidence}
            />
          </div>

        </div>
      )}
    </div>
  );
}
