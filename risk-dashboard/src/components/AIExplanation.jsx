import { useState, useMemo } from "react";
import { evaluateRule } from "../utils/ruleEngine";

export default function AIExplanation({ components, score, contributions, band }) {

  const [simulatedScore, setSimulatedScore] = useState(null);

  const getScoreColor = (s) => {
    const safe = Number.isFinite(s) ? s : 0;

    if (safe < 0.01) return "#16a34a";
    if (safe < 0.03) return "#f59e0b";
    return "#dc2626";
  };

  const analysis = useMemo(() => {

    if (!components) {
      return { text: "Veri bulunamadı.", actions: [], factors: [] };
    }

    const actionList = [];
    const factorComments = [];

    // =====================================================
    // 🔥 BAND FIX (CRITICAL PATCH)
    // =====================================================
    const safeBandRaw = band ?? "MEDIUM";

    const safeBand = safeBandRaw
      .toString()
      .trim()
      .toUpperCase();

    // 🔥 HARD GUARD (BUG FIX)
    const allowedBands = ["LOW", "MEDIUM", "HIGH"];
    const finalBand = allowedBands.includes(safeBand) ? safeBand : "MEDIUM";

    const isLowRisk = finalBand === "LOW";

    // =====================================================
    // 🔥 MODEL EXPLAINABILITY (UNCHANGED)
    // =====================================================
    if (contributions && contributions.length > 0) {

      const sorted = contributions
        .filter((item) => Number.isFinite(item?.impact))
        .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact));

      if (sorted.length > 0) {
        const top = sorted[0];

        const factorNameMap = {
          payment_discipline_score: "Ödeme Disiplini",
          income_stability_index: "Gelir İstikrarı",
          financial_resilience_score: "Finansal Dayanıklılık"
        };

        const mainReason = factorNameMap[top.feature] || top.feature;

        const impactPercent = Math.min(
          100,
          Math.abs(Number(top.impact) || 0) * 100
        );

        actionList.push(
          `📊 Model analizi: ${mainReason} faktörü riski %${impactPercent.toFixed(2)} oranında etkilemektedir.`
        );
      }

    } else {

      actionList.push("📊 Model açıklaması yerine kural bazlı analiz kullanıldı.");

      if (components.payment_discipline_score < 0.5) {
        actionList.push("Ödeme disiplini düşük olduğu için risk artmaktadır.");
      }

      if (components.income_stability_index < 0.5) {
        actionList.push("Gelir istikrarı düşük olduğu için risk artmaktadır.");
      }

      if (components.financial_resilience_score < 0.5) {
        actionList.push("Finansal dayanıklılık zayıf olduğu için risk artmaktadır.");
      }
    }

    // =====================================================
    // 🔥 RULE ENGINE (UNCHANGED)
    // =====================================================
    const mapping = [
      {
        key: "financial_resilience",
        value: components?.financial_resilience_score
      },
      {
        key: "payment_discipline",
        value: components?.payment_discipline_score
      },
      {
        key: "income_stability",
        value: components?.income_stability_index
      }
    ];

    mapping.forEach((item) => {

      if (item.value === null || item.value === undefined) return;

      const rule = evaluateRule(item.key, item.value);
      if (!rule) return;

      if (rule.description && !isLowRisk) {
        factorComments.push(rule.description);
      }

      if (rule.action) {
        actionList.push({
          text: rule.action,
          priority: rule.priority,
          impact: Number(rule.impact) || 0,
          color: rule.color
        });
      }
    });

    // =====================================================
    // 🔥 EXECUTIVE SUMMARY (100% SAFE)
    // =====================================================
    const summaryMap = {
      LOW: "Müşteri düşük risk grubundadır; mevcut finansal davranışlar genel olarak stabildir.",
      MEDIUM: "Müşteri orta risk grubundadır; bazı finansal göstergelerde iyileştirme gerekmektedir.",
      HIGH: "Müşteri yüksek risk grubundadır; finansal davranışlarda kritik iyileştirmeler gereklidir."
    };

    const summary =
      summaryMap[finalBand] ?? summaryMap.MEDIUM;

    return {
      text: summary + " (Kural bazlı analiz ile desteklenmiştir.)",
      actions: actionList,
      factors: factorComments
    };

  }, [components, score, contributions, band]);

  const { text, actions, factors } = analysis;

  const simulateImpact = () => {

    if (!actions?.length) return;

    const totalImpact = actions.reduce(
      (sum, a) => sum + (Number(a?.impact) || 0),
      0
    );

    const safeScore = Number.isFinite(score) ? score : 0;

    const newScore = Math.max(
      0,
      safeScore - Math.abs(totalImpact) * 0.01
    );

    setSimulatedScore(newScore);
  };

  return (
    <div className="card">
      <h3>🧠 AI Açıklama</h3>

      <p style={{ lineHeight: "1.7", marginBottom: "16px" }}>
        {text}
      </p>

      {factors.length > 0 && (
        <div style={{ marginBottom: "16px", fontSize: "14px", color: "#6b7280" }}>
          {factors.map((f, i) => (
            <div key={i}>• {f}</div>
          ))}
        </div>
      )}

      {actions.length > 0 && (
        <div>
          <h4>📌 Önerilen Aksiyonlar</h4>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {actions.map((a, i) => (
              <div
                key={i}
                style={{
                  padding: "10px",
                  borderRadius: "8px",
                  background: "#f9fafb",
                  borderLeft: `5px solid ${a.color}`,
                  display: "flex",
                  justifyContent: "space-between"
                }}
              >
                <span>{a.text}</span>
                <span style={{ fontWeight: "bold", color: a.color }}>
                  {a.priority}
                </span>
              </div>
            ))}
          </div>

          <button
            onClick={simulateImpact}
            style={{
              marginTop: "12px",
              padding: "10px 14px",
              background: "#111827",
              color: "white",
              borderRadius: "10px",
              fontWeight: "600",
              cursor: "pointer"
            }}
          >
            🎯 Etkiyi Simüle Et
          </button>
        </div>
      )}

      {simulatedScore !== null && (
        <div style={{ marginTop: "20px" }}>
          <strong>Skor Değişimi:</strong>

          <div style={{
            marginTop: "10px",
            padding: "12px",
            borderRadius: "10px",
            background: "#f3f4f6",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            fontSize: "18px",
            fontWeight: "600"
          }}>
            <span style={{ color: getScoreColor(score) }}>
              {(Number(score) || 0).toFixed(6)}
            </span>

            ➡️

            <span style={{ color: getScoreColor(simulatedScore) }}>
              {simulatedScore.toFixed(6)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}