import { evaluateRule } from "../utils/ruleEngine";

export default function RuleScoreCard({ components }) {

  const safe = components ?? {};

  const rules = [
    {
      name: "Finansal Dayanıklılık",
      key: "financial_resilience",
      value: safe.financial_resilience_score
    },
    {
      name: "Ödeme Disiplini",
      key: "payment_discipline",
      value: safe.payment_discipline_score
    },
    {
      name: "Gelir İstikrarı",
      key: "income_stability",
      value: safe.income_stability_index
    }
  ];

  return (
    <div className="card">
      <h3>📊 Kural Tabanlı Skor Kartı</h3>

      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {rules.map((rule, i) => {

          // ======================================
          // 🔥 SAFE NUMBER CHECK (FIXED)
          // ======================================
          const rawValue = rule.value;

          const isValidNumber =
            typeof rawValue === "number" && Number.isFinite(rawValue);

          if (!isValidNumber) {
            return (
              <div
                key={i}
                style={{
                  padding: "12px",
                  borderRadius: "10px",
                  background: "#f9fafb",
                  borderLeft: `6px solid #9ca3af`
                }}
              >
                <strong>{rule.name}</strong>
                <div style={{ fontSize: "12px", color: "#9ca3af" }}>
                  Veri bulunamadı
                </div>
              </div>
            );
          }

          // ======================================
          // 🔥 SCALE NORMALIZATION (CRITICAL FIX)
          // ======================================
          // Eğer backend 0–100 gönderirse 0–1'e çek
          const value =
            rawValue > 1 ? rawValue / 100 : rawValue;

          // ======================================
          // 🔥 RULE ENGINE SAFE CALL
          // ======================================
          const matched = evaluateRule(rule.key, value);

          const safeMatched = matched ?? {
            label: "Bilinmiyor",
            color: "#9ca3af",
            description: "Kural bulunamadı",
            rule: null
          };

          return (
            <div
              key={i}
              style={{
                padding: "12px",
                borderRadius: "10px",
                background: "#f9fafb",
                borderLeft: `6px solid ${safeMatched.color}`,
                display: "flex",
                flexDirection: "column",
                gap: "4px"
              }}
            >
              {/* ÜST SATIR */}
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <strong>{rule.name}</strong>

                {/* SAFE DISPLAY */}
                <span style={{ fontWeight: "bold", color: safeMatched.color }}>
                  {Number(value).toFixed(2)}
                </span>
              </div>

              {/* LABEL */}
              <div style={{ fontSize: "13px", color: safeMatched.color }}>
                {safeMatched.label}
              </div>

              {/* AÇIKLAMA */}
              <div style={{ fontSize: "11px", color: "#6b7280" }}>
                {safeMatched.description}
              </div>

              {/* RULE */}
              {safeMatched.rule && (
                <div style={{ fontSize: "11px", color: "#9ca3af" }}>
                  {safeMatched.rule}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}