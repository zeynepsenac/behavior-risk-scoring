import { useMemo } from "react";

export default function RuleScoreCard({ components, model_confidence }) {

  const safe = Array.isArray(components)
    ? components[0] ?? {}
    : components ?? {};

  const normalize = (v) => {
    const num = Number(v);
    if (!Number.isFinite(num)) return null;
    return num > 1 ? num / 100 : num;
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

  const explainValue = (key, rawValue) => {
    const value = normalize(rawValue);
    if (value === null) return "Veri bulunamadı";

    const level = getLevel(key, value);

    if (key === "financial_resilience") {
      if (value < 0.2)
        return (
          <>
            <b>KRİTİK:</b> Finansal dayanıklılık çok zayıf →{" "}
            <b>yüksek kırılganlık</b>
          </>
        );

      if (level === "high")
        return "Zayıf finansal yapı → risk artırır";

      if (level === "medium")
        return "Orta finansal yapı → sınırlı koruma";

      return "Güçlü finansal yapı → koruyucu faktör";
    }

    if (key === "payment_discipline") {
      if (level === "high")
        return "Zayıf ödeme disiplini → risk artırır";

      if (level === "medium")
        return "Orta ödeme disiplini → nötr etki";

      return "Güçlü ödeme disiplini → koruyucu faktör";
    }

    if (key === "income_stability") {
      if (level === "high")
        return "Gelir dalgalı → risk artar";

      if (level === "medium")
        return "Orta gelir istikrarı → sınırlı güven";

      return "Stabil gelir → risk azaltır";
    }

    return "Bilinmeyen özellik";
  };

  const rules = useMemo(() => [
    {
      name: "Finansal Dayanıklılık",
      key: "financial_resilience",
      value: safe.financial_resilience_score,
    },
    {
      name: "Ödeme Disiplini",
      key: "payment_discipline",
      value: safe.payment_discipline_score,
    },
    {
      name: "Gelir İstikrarı",
      key: "income_stability",
      value: safe.income_stability_index,
    },
  ], [safe]);

  const worstRule = useMemo(() => {
    return rules
      .map(r => ({
        ...r,
        value: normalize(r.value)
      }))
      .filter(r => r.value !== null)
      .sort((a, b) => a.value - b.value)[0];
  }, [rules]);

  return (
    <div className="rule-layout">

      <div className="rule-card-wrapper">
        <h3 className="rule-title-main">📊 Kural Tabanlı Skor Kartı</h3>

        {worstRule && (
          <div className="worst-box">
            ⚠️ En etkili faktör: {worstRule.name}
          </div>
        )}

        <div className="rule-list">
          {rules.map((rule, i) => {
            const value = normalize(rule.value);

            if (value === null) {
              return (
                <div key={i} className="rule-item muted">
                  Veri bulunamadı
                </div>
              );
            }

            const level = getLevel(rule.key, value);
            const isWorst = worstRule?.key === rule.key;

            return (
              <div
                key={i}
                className={`rule-item ${level} ${isWorst ? "highlight" : ""}`}
                style={{
                  borderLeft: `4px solid ${
                    level === "high"
                      ? "#dc2626"
                      : level === "medium"
                      ? "#f59e0b"
                      : "#16a34a"
                  }`
                }}
              >
                <span className="rule-icon">
                  {level === "high" ? "🔴" : level === "medium" ? "🟡" : "🟢"}
                </span>

                <div>
                  <div className="rule-name">{rule.name}</div>

                  <div className="rule-label">
                    <b>
                      {level === "high"
                        ? "Yüksek Risk"
                        : level === "medium"
                        ? "Orta Risk"
                        : "Düşük Risk"}
                    </b>
                  </div>

                  <div className="rule-desc">
                    {explainValue(rule.key, rule.value)}
                  </div>
                </div>

                <div className="rule-score">
                  {value.toFixed(2)}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="rule-right">

        <div className="mini-card">
          <h4>🧠 Model</h4>
          <p><b>Versiyon:</b> v1.0</p>
          <p>
            <b>Güven:</b>{" "}
            {typeof model_confidence === "number"
              ? (model_confidence > 1
                  ? model_confidence
                  : model_confidence * 100
                ).toFixed(1) + "%"
              : "N/A"}
          </p>
        </div>

        <div className="mini-card">
          <h4>📌 Özellikler</h4>

          <p>Finansal: {explainValue("financial_resilience", safe.financial_resilience_score)}</p>
          <p>Ödeme: {explainValue("payment_discipline", safe.payment_discipline_score)}</p>
          <p>Gelir: {explainValue("income_stability", safe.income_stability_index)}</p>
        </div>

      </div>

      <style>{`
        .rule-layout {
          display: flex;
          gap: 16px;
        }

        .rule-card-wrapper {
          flex: 2;
        }

        .rule-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .rule-item {
          position: relative;
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 12px;
          border-radius: 10px;
          background: #f9fafb;
        }

        .rule-item.low { background: rgba(22,163,74,0.1); }
        .rule-item.medium { background: rgba(245,158,11,0.1); }
        .rule-item.high { background: rgba(220,38,38,0.1); }

        .rule-item.highlight {
          box-shadow: 0 0 0 2px rgba(220,38,38,0.35);
        }

        .rule-icon {
          font-size: 14px;
        }

        .rule-score {
          position: absolute;
          top: 8px;
          right: 10px;
          font-size: 13px;
          font-weight: 800;
          color: #2563eb;
          background: white;
          padding: 4px 8px;
          border-radius: 8px;
        }
      `}</style>
    </div>
  );
}