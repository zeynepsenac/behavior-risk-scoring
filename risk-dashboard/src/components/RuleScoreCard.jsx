import { evaluateRule } from "../utils/ruleEngine";
import { useMemo } from "react";

export default function RuleScoreCard({ components, model_confidence }) {

  // ✅ components güvenli erişim
  const safe = Array.isArray(components)
    ? components[0] ?? {}
    : components ?? {};

  // 🔧 SAFE NORMALIZATION (tek kaynak)
  const normalize = (v) => {
    const num = Number(v);
    if (!Number.isFinite(num)) return null;
    return num > 1 ? num / 100 : num;
  };

  // 🔥 TEK THRESHOLD SOURCE (tutarlı)
  const getLevel = (value) => {
    if (value === null) return "unknown";
    if (value < 0.6) return "low";
    if (value < 0.8) return "medium";
    return "high";
  };

  // 🧠 EXPLANATION (rule + level SENKRON)
  const explainValue = (key, rawValue) => {
    const value = normalize(rawValue);
    if (value === null) return "Veri bulunamadı";

    const level = getLevel(value);

    if (key === "financial_resilience") {
      if (value < 0.2) return "KRİTİK: Finansal dayanıklılık çok zayıf";
      if (level === "low") return "Zayıf finansal dayanıklılık";
      if (level === "medium") return "Orta seviye finansal dayanıklılık";
      return "Güçlü finansal dayanıklılık";
    }

    if (key === "payment_discipline") {
      if (level === "low") return "Zayıf ödeme disiplini → risk artırır";
      if (level === "medium") return "Orta ödeme disiplini";
      return "Güçlü ödeme disiplini → koruyucu faktör";
    }

    if (key === "income_stability") {
      if (level === "low") return "Gelir dalgalı → risk artar";
      if (level === "medium") return "Orta gelir istikrarı";
      return "Stabil gelir yapısı → risk azaltır";
    }

    return "Bilinmeyen özellik";
  };

  // 📦 RULE LIST (tek kaynak veri akışı)
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

  return (
    <div className="rule-layout">

      {/* LEFT */}
      <div className="rule-card-wrapper">
        <h3 className="rule-title-main">📊 Kural Tabanlı Skor Kartı</h3>

        <div className="rule-list">
          {rules.map((rule, i) => {
            const rawValue = rule.value;
            const value = normalize(rawValue);

            if (value === null) {
              return (
                <div key={i} className="rule-item muted">
                  <div>
                    <div className="rule-name">{rule.name}</div>
                    <div className="rule-desc">Veri bulunamadı</div>
                  </div>
                </div>
              );
            }

            // 🔥 TEK SOURCE OF TRUTH
            const matched = evaluateRule(rule.key, value);

            const safeMatched = matched ?? {
              label: "Bilinmiyor",
              color: "#9ca3af",
            };

            return (
              <div
                key={i}
                className="rule-item"
                style={{ borderLeft: `4px solid ${safeMatched.color}` }}
              >
                <div>
                  <div className="rule-name">{rule.name}</div>

                  <div
                    className="rule-label"
                    style={{ color: safeMatched.color }}
                  >
                    {safeMatched.label}
                  </div>

                  <div className="rule-desc">
                    {explainValue(rule.key, rawValue)}
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

      {/* RIGHT */}
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

          <p>
            Finansal:{" "}
            {explainValue(
              "financial_resilience",
              safe.financial_resilience_score
            )}
          </p>

          <p>
            Ödeme:{" "}
            {explainValue(
              "payment_discipline",
              safe.payment_discipline_score
            )}
          </p>

          <p>
            Gelir:{" "}
            {explainValue(
              "income_stability",
              safe.income_stability_index
            )}
          </p>
        </div>

      </div>

      {/* STYLE (DEĞİŞMEDİ) */}
      <style>{`
        .rule-layout {
          display: flex;
          gap: 16px;
          align-items: stretch;
        }

        .rule-card-wrapper {
          flex: 2;
          margin-top: 10px;
        }

        .rule-title-main {
          font-size: 14px;
          font-weight: 600;
          margin-bottom: 12px;
          color: #111827;
        }

        .rule-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .rule-item {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          padding: 12px;
          border-radius: 12px;
          background: #f9fafb;
          box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        }

        .rule-item.muted {
          border-left: 4px solid #d1d5db;
        }

        .rule-name {
          font-size: 13px;
          font-weight: 600;
          color: #111827;
        }

        .rule-label {
          font-size: 12px;
          font-weight: 600;
          margin-top: 2px;
        }

        .rule-desc {
          font-size: 11px;
          color: #6b7280;
          margin-top: 2px;
        }

        .rule-score {
          font-size: 12px;
          font-weight: 700;
          color: #2563eb;
          background: white;
          padding: 4px 8px;
          border-radius: 8px;
        }

        .rule-right {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .mini-card {
          background: #ffffff;
          border-radius: 12px;
          padding: 12px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.06);
          border: 1px solid #eef0f3;
        }

        .mini-card h4 {
          font-size: 13px;
          margin-bottom: 8px;
          color: #111827;
        }

        .mini-card p {
          font-size: 12px;
          color: #4b5563;
          margin: 4px 0;
        }
      `}</style>
    </div>
  );
}