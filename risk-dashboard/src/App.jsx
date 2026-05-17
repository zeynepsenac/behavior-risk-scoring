import { useState, useEffect } from "react";
import { getRiskScore } from "./services/api";

import html2canvas from "html2canvas";
import jsPDF from "jspdf";

import GaugeChart from "./components/GaugeChart";
import RuleScoreCard from "./components/RuleScoreCard";
import AIExplainabilityDashboard from "./components/AIExplanation";
import Skeleton from "./components/Skeleton";

export default function App() {
  const [id, setId] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const [animatedScore, setAnimatedScore] = useState(0);

  // ✅ PDF DOWNLOAD
  const downloadPDF = async () => {
    const element = document.getElementById("risk-report");

    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
    });

    const imgData = canvas.toDataURL("image/png");

    const pdf = new jsPDF("p", "mm", "a4");

    const pdfWidth = pdf.internal.pageSize.getWidth();

    const pdfHeight =
      (canvas.height * pdfWidth) / canvas.width;

    pdf.addImage(
      imgData,
      "PNG",
      0,
      0,
      pdfWidth,
      pdfHeight
    );

    pdf.save("risk-report.pdf");
  };

  const fallbackData = {
    predicted_risk_score: 0.28,
    predicted_band: "MEDIUM",
    model_confidence: 0.65,
    payment_discipline_score: 55,
    income_stability_index: 48,
    financial_resilience_score: 22,
    components: []
  };

  const isInvalidData = (d) => {
    if (!d) return true;

    return (
      d.predicted_risk_score === null ||
      d.predicted_risk_score === undefined ||
      isNaN(d.predicted_risk_score)
    );
  };

  const safeData = data ?? fallbackData;

  useEffect(() => {
    if (safeData.predicted_risk_score === null) return;

    let startTime = null;
    const duration = 1000;

    const animate = (time) => {
      if (!startTime) startTime = time;

      const progress = Math.min(
        (time - startTime) / duration,
        1
      );

      const eased = 1 - Math.pow(1 - progress, 3);

      const value =
        eased * safeData.predicted_risk_score;

      setAnimatedScore(value.toFixed(3));

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);

  }, [safeData.predicted_risk_score]);

  const handleFetch = async () => {
    if (!id) return;

    setLoading(true);

    try {
      const res = await getRiskScore(id);

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
          res?.components ?? []
      };

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

  return (
    <div id="risk-report">

      <div className="top-panel">
        <h1>📊 Risk Kontrol Paneli</h1>

        <p className="subtitle">
          Rapor No: RISK-{id || "-"}
        </p>

        <div
          style={{
            marginTop: "18px",
            display: "flex",
            alignItems: "center",
            gap: "10px"
          }}
        >
          <input
            placeholder="Müşteri ID (1-1200)"
            value={id}
            onChange={(e) => setId(e.target.value)}
          />

          <button
            className="btn-analyze"
            onClick={handleFetch}
            disabled={loading}
          >
            {loading
              ? "Analiz ediliyor..."
              : "📊 Analiz Et"}
          </button>

          <button
            className="btn-pdf"
            disabled={loading}
            onClick={downloadPDF}
          >
            📄 PDF Rapor
          </button>
        </div>

        <p className="helper-text">
          Lütfen bir müşteri ID girerek analizi başlatın.
        </p>
      </div>

      {loading && <Skeleton />}

      {!loading && !data && (
        <div
          style={{
            color: "#6b7280",
            padding: "20px",
            textAlign: "center"
          }}
        >
          Henüz analiz yapılmadı
        </div>
      )}

      {!loading && data && (
        <div className="dashboard-container">

          <div className="card score-card">
            <h2>Risk Skoru</h2>

            <div className="score-value">
              {safeData.predicted_risk_score !== null
                ? animatedScore
                : "N/A"}
            </div>

            <p className="risk-info">
              (0 ile 1 arasında normalize edilmiş skor)
            </p>
          </div>

          <div className="card gauge-card">
            <h2>Risk Ölçer</h2>

            <GaugeChart
              score={safeData.predicted_risk_score}
              predicted_band={safeData.predicted_band}
              financial_resilience_score={
                safeData.financial_resilience_score
              }
            />
          </div>

          <div className="card ai-card">
            <AIExplainabilityDashboard
              data={safeData}
            />
          </div>

          <div className="card rules-card">
            <h2>Kural Tabanlı Analiz</h2>

            <RuleScoreCard
              components={safeData.components || []}
              model_confidence={
                safeData.model_confidence
              }
            />
          </div>

        </div>
      )}
    </div>
  );
}