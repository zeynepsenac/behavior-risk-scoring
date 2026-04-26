// 🧠 AI EXPLANATION COMPONENT (AIExplanation.jsx)

import { useMemo, useState } from "react";

export default function AIExplainabilityDashboard({ data }) {
  const [selectedFeature, setSelectedFeature] = useState(null);

  const fallbackData = {
    predicted_risk_score: null,
    predicted_band: null,
    model_confidence: null,
    payment_discipline_score: null,
    income_stability_index: null,
    financial_resilience_score: null,
    warnings: []
  };

  const safeData =
    data && Object.keys(data).length > 0 ? data : fallbackData;

  const THRESHOLDS = {
    LOW: 50,
    MEDIUM: 70,
    HIGH: 85
  };

  const normalize = (v) => {
    const n = Number(v);
    if (!Number.isFinite(n)) return null;
    if (n >= 0 && n <= 1) return n;
    if (n > 1 && n <= 100) return n / 100;
    return (n % 100) / 100;
  };

  const getLevel = (value) => {
    if (value === null) return "unknown";
    if (value < THRESHOLDS.LOW / 100) return "low";
    if (value < THRESHOLDS.MEDIUM / 100) return "medium";
    if (value < THRESHOLDS.HIGH / 100) return "high";
    return "very_high";
  };

  const analysis = useMemo(() => {
    const features = [
      {
        name: "Payment Discipline",
        key: "payment_discipline",
        raw: safeData.payment_discipline_score,
        value: normalize(safeData.payment_discipline_score)
      },
      {
        name: "Income Stability",
        key: "income_stability",
        raw: safeData.income_stability_index,
        value: normalize(safeData.income_stability_index)
      },
      {
        name: "Financial Resilience",
        key: "financial_resilience",
        raw: safeData.financial_resilience_score,
        value: normalize(safeData.financial_resilience_score)
      }
    ];

    return {
      score: normalize(safeData.predicted_risk_score),
      band: safeData.predicted_band ?? "MEDIUM",
      confidence: normalize(safeData.model_confidence),
      features
    };
  }, [safeData]);

  const getColor = (v) => {
    if (v === null) return "#6b7280";
    if (v < 0.15) return "#16a34a";
    if (v < 0.35) return "#f59e0b";
    return "#ef4444";
  };

  const getBand = (b) => {
    const map = {
      HIGH: "High risk exposure",
      MEDIUM: "Moderate risk exposure",
      LOW: "Low risk exposure"
    };
    return map[b] ?? "Moderate risk exposure";
  };

  const explain = (f) => {
    if (f.value === null) return "Veri eksik";

    const level = getLevel(f.value);

    if (f.key === "financial_resilience") {
      if (f.value < 0.2) return "KRİTİK: Finansal dayanıklılık çok zayıf";
      if (level === "low") return "Zayıf finansal dayanıklılık";
      if (level === "medium") return "Orta finansal dayanıklılık";
      return "Güçlü finansal dayanıklılık";
    }

    if (f.key === "payment_discipline") {
      if (level === "low") return "Zayıf ödeme disiplini → risk artırır";
      if (level === "medium") return "Orta ödeme disiplini";
      return "Güçlü ödeme disiplini → koruyucu faktör";
    }

    if (f.key === "income_stability") {
      if (f.value < 0.5) return "Gelir dalgalı → risk artar";
      if (f.value < 0.7) return "Orta gelir istikrarı";
      return "Stabil gelir yapısı → risk azaltır";
    }

    return "Nötr";
  };

  const score = analysis.score;
  const confidence = analysis.confidence;

  const aiExplanation = (() => {
    const resilience = safeData.financial_resilience_score;
    const conf = normalize(safeData.model_confidence);

    if (conf !== null && conf < 0.6) {
      return "Model düşük güven seviyesine sahiptir. Sonuçlar dikkatle değerlendirilmelidir.";
    }

    if (conf !== null && conf < 0.85) {
      if (resilience !== null && resilience < 40) {
        return "Model düşük risk tahmini üretmekle birlikte finansal dayanıklılık zayıf olduğu için kırılganlık riski vardır.";
      }
      return "Model düşük-orta güvenle risk tahmini üretmektedir, bazı değişkenler dikkat gerektirir.";
    }

    if (resilience !== null && resilience < 40) {
      return "Risk düşük görünse de finansal dayanıklılık zayıf olduğu için kırılganlık riski vardır.";
    }

    return "Model finansal davranışları analiz ederek güvenilir düşük risk seviyesi belirlemiştir.";
  })();

  return (
    <div className="grid xl:grid-cols-3 gap-6 p-6 bg-gray-50">

      {/* SCORE */}
      <div className="bg-white p-6 rounded-2xl shadow-md">
        <div className="text-sm font-semibold text-gray-700">
          Risk Skoru
        </div>

        <div
          className="text-5xl font-bold mt-3"
          style={{ color: getColor(score) }}
        >
          {score === null ? "N/A" : score.toFixed(3)}
        </div>

        <div className="text-base font-medium text-gray-800 mt-2">
          {getBand(analysis.band)}
        </div>

        <div className="text-sm text-gray-700 mt-1">
          Güven: {confidence === null ? "N/A" : (confidence * 100).toFixed(1) + "%"}
        </div>
      </div>

      {/* FEATURES */}
      <div className="bg-white p-6 rounded-2xl space-y-4 shadow-md">
        {analysis.features.map((f, i) => (
          <div key={i} className="p-4 border rounded-xl hover:bg-gray-50 transition">

            <div className="text-base font-semibold text-gray-900">
              {f.name}
            </div>

            <div className="text-sm text-gray-700 mt-1">
              Değer: {f.raw == null ? "Veri yok" : f.raw}
            </div>

            <div className="text-base font-medium text-gray-900 mt-2 leading-relaxed">
              {explain(f)}
            </div>

          </div>
        ))}
      </div>

      {/* INFO */}
      <div className="bg-white p-6 rounded-2xl shadow-md">
        <div className="text-lg font-bold text-gray-900 mb-3">
          🟢AI Açıklama
        </div>

        {/* 🔥 FULL DARK FIX */}
        <div className="text-base font-medium text-gray-900 leading-relaxed">
          {aiExplanation}
        </div>
      </div>

    </div>
  );
}