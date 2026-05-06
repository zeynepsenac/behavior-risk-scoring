import { useMemo, useState, useEffect } from "react";

export default function AIExplainabilityDashboard({ data }) {
  const [typedText, setTypedText] = useState("");

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

  const normalize = (v) => {
    const n = Number(v);
    if (!Number.isFinite(n)) return null;
    return n > 1 ? n / 100 : n;
  };

  const getLevel = (key, value) => {
    if (value === null) return "unknown";

    if (key === "financial_resilience") {
      if (value < 0.3) return "high";
      if (value < 0.6) return "medium";
      return "low";
    }

    if (value < 0.4) return "high";
    if (value < 0.7) return "medium";
    return "low";
  };

  const analysis = useMemo(() => {
    const features = [
      {
        name: "Ödeme Disiplini",
        key: "payment_discipline",
        value: normalize(safeData.payment_discipline_score)
      },
      {
        name: "Gelir İstikrarı",
        key: "income_stability",
        value: normalize(safeData.income_stability_index)
      },
      {
        name: "Finansal Dayanıklılık",
        key: "financial_resilience",
        value: normalize(safeData.financial_resilience_score)
      }
    ];

    // 🔥 YENİ: importance sıralama
    const priority = {
      high: 3,
      medium: 2,
      low: 1,
      unknown: 0
    };

    features.sort((a, b) => {
      const levelA = getLevel(a.key, a.value);
      const levelB = getLevel(b.key, b.value);

      return priority[levelB] - priority[levelA];
    });

    return {
      score: normalize(safeData.predicted_risk_score),
      band: safeData.predicted_band ?? "MEDIUM",
      confidence: normalize(safeData.model_confidence),
      features
    };
  }, [safeData]);

  const getBand = (b) => {
    const map = {
      HIGH: "Yüksek risk",
      MEDIUM: "Orta risk",
      LOW: "Düşük risk"
    };
    return map[b] ?? "Orta risk";
  };

  const explain = (f) => {
    if (f.value === null) return "Veri eksik";

    const level = getLevel(f.key, f.value);

    if (f.key === "financial_resilience") {
      if (f.value < 0.2) return "KRİTİK: Finansal dayanıklılık çok zayıf";
      if (level === "high") return "Zayıf finansal dayanıklılık";
      if (level === "medium") return "Orta finansal dayanıklılık";
      return "Güçlü finansal dayanıklılık";
    }

    if (f.key === "payment_discipline") {
      if (level === "high") return "Zayıf ödeme disiplini → risk artırır";
      if (level === "medium") return "Orta ödeme disiplini";
      return "Güçlü ödeme disiplini → koruyucu faktör";
    }

    if (f.key === "income_stability") {
      if (level === "high") return "Gelir dalgalı → risk artar";
      if (level === "medium") return "Orta gelir istikrarı";
      return "Stabil gelir yapısı → risk azaltır";
    }

    return "Nötr";
  };

  const score = analysis.score;
  const confidence = analysis.confidence;

  let finalBand = analysis.band;
  const resilience = normalize(safeData.financial_resilience_score);

  if (resilience !== null && resilience < 0.3 && finalBand === "LOW") {
    finalBand = "MEDIUM";
  }

  const aiExplanation = (() => {
    const conf = normalize(safeData.model_confidence);
    const originalBand = safeData.predicted_band;

    if (
      resilience !== null &&
      resilience < 0.3 &&
      originalBand === "LOW"
    ) {
      return "Model düşük risk tahmini üretmiş olsa da finansal dayanıklılık kritik seviyededir. Bu durum müşterinin ani finansal şoklara karşı yüksek kırılganlık taşıdığını gösterir.";
    }

    if (conf !== null && conf < 0.6) {
      return "Modelin güven seviyesi düşüktür. Sonuçlar dikkatle değerlendirilmelidir.";
    }

    if (resilience !== null && resilience < 0.2) {
      return "Finansal dayanıklılık kritik seviyede. Bu durum müşterinin finansal şoklara karşı ciddi şekilde savunmasız olduğunu gösterir.";
    }

    if (resilience !== null && resilience < 0.4) {
      return "Finansal dayanıklılık zayıf. Risk düşük görünse bile kırılganlık riski bulunmaktadır.";
    }

    if (conf !== null && conf < 0.85) {
      return "Model orta seviyede güven ile tahmin üretmiştir. Bazı faktörler dikkat gerektirebilir.";
    }

    return "Model finansal davranışlara göre düşük risk seviyesini güvenilir şekilde belirlemiştir.";
  })();

  useEffect(() => {
    let index = 0;
    setTypedText("");

    const interval = setInterval(() => {
      setTypedText(aiExplanation.slice(0, index));
      index++;
      if (index > aiExplanation.length) clearInterval(interval);
    }, 18);

    return () => clearInterval(interval);
  }, [aiExplanation]);

  return (
    <div className="ai-card">
      <div className="ai-content">

        <div className="ai-sticky-header">
          <h3>AI Analiz Paneli</h3>
        </div>

        <div className="ai-section">
          <h4>Risk Özeti</h4>
          <p>
            {score === null ? "N/A" : score.toFixed(3)} - {getBand(finalBand)}
          </p>
          <p>
            Güven: {confidence === null ? "N/A" : (confidence * 100).toFixed(1) + "%"}
          </p>
        </div>

        <div className="ai-section">
          <h4>Faktörler</h4>

          {analysis.features.map((f, i) => {
            const level = getLevel(f.key, f.value);

            const levelClass =
              level === "high"
                ? "bad"
                : level === "medium"
                ? "medium"
                : level === "low"
                ? "good"
                : "neutral";

            const icon =
              level === "high"
                ? "🔴"
                : level === "medium"
                ? "🟡"
                : level === "low"
                ? "🟢"
                : "⚪";

            return (
              <div key={i} className={`ai-item ${levelClass}`}>
                <span style={{ marginRight: "8px" }}>{icon}</span>
                {f.name}: {explain(f)}
              </div>
            );
          })}
        </div>

        <div className="ai-section highlight">
          <div className="ai-header">
            <h4>AI Açıklama</h4>
          </div>

          <div className="ai-text">
            {typedText}
            <span className="cursor"></span>
          </div>
        </div>

      </div>

      <style>{`
        .ai-item.good {
          background: rgba(22,163,74,0.1);
          color: #16a34a;
        }

        .ai-item.medium {
          background: rgba(245,158,11,0.15);
          color: #f59e0b;
        }

        .ai-item.bad {
          background: rgba(220,38,38,0.12);
          color: #dc2626;
        }

        .ai-item.neutral {
          background: #f1f5f9;
          color: #64748b;
        }
      `}</style>
    </div>
  );
}