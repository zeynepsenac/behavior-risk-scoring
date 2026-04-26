export const riskDataContract = (data) => {
  if (!data) return null;

  const clean = (v) => {
    if (v === null || v === undefined || v === "") {
      return { value: null, status: "missing" };
    }

    const n = Number(v);

    if (!Number.isFinite(n)) {
      return { value: null, status: "invalid" };
    }

    return { value: n, status: "valid" }; // 0 burada VALID!
  };

  return {
    score: clean(data.predicted_risk_score),

    confidence: clean(data.model_confidence),

    features: [
      {
        name: "Payment Discipline",
        ...clean(data.payment_discipline_score),
        impact: clean(data.payment_discipline_score_bias)
      },
      {
        name: "Income Stability",
        ...clean(data.income_stability_index),
        impact: clean(data.income_stability_index_bias)
      },
      {
        name: "Financial Resilience",
        ...clean(data.financial_resilience_score),
        impact: clean(data.financial_resilience_score_bias)
      }
    ]
  };
};