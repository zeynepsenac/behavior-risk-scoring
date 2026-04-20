const BASE_URL = "http://127.0.0.1:8000";

// ==========================================
// 🔥 RISK SCORE API (FIXED VERSION)
// ==========================================
export const getRiskScore = async (id) => {
  try {
    const response = await fetch(
      `${BASE_URL}/risk-score/${id}?explain=true`
    );

    const data = await response.json();

    if (!data) {
      throw new Error("Empty response from backend");
    }

    // ======================================
    // 🔥 SCORE NORMALIZATION
    // ======================================
    const score = Number(data.predicted_risk_score);

    // ======================================
    // 🔥 BAND NORMALIZATION (CRITICAL FIX)
    // ======================================
    const rawBand =
      data.risk_band ??
      data.predicted_band ??
      data.risk_label ??
      "MEDIUM";

    const normalizedBand = String(rawBand)
      .toUpperCase()
      .trim();

    const allowedBands = ["LOW", "MEDIUM", "HIGH"];

    const finalBand = allowedBands.includes(normalizedBand)
      ? normalizedBand
      : "MEDIUM";

    // ======================================
    // 🔥 RETURN SAFE OBJECT
    // ======================================
    return {
      ...data,

      // SCORE
      predicted_risk_score: Number.isFinite(score) ? score : 0,

      // BAND (FIXED SINGLE SOURCE OF TRUTH)
      risk_band: finalBand,
      risk_label: finalBand,

      risk_color: data.risk_color ?? null,

      // ======================================
      // COMPONENTS SAFE
      // ======================================
      components: {
        payment_discipline_score:
          data.components?.payment_discipline_score ??
          data.payment_discipline_score ??
          0,

        income_stability_index:
          data.components?.income_stability_index ??
          data.income_stability_index ??
          0,

        financial_resilience_score:
          data.components?.financial_resilience_score ??
          data.financial_resilience_score ??
          0,
      },

      // ======================================
      // EXPLANATION SAFE
      // ======================================
      explanation:
        data.explanation && data.explanation.trim() !== ""
          ? data.explanation
          : "Model açıklaması mevcut değil",

      // OPTIONAL
      feature_importance: data.feature_importance ?? null,

      model_confidence: Number.isFinite(data.model_confidence)
        ? data.model_confidence
        : null,
    };

  } catch (error) {
    console.error("getRiskScore ERROR:", error);

    // ======================================
    // 🔥 SAFE FALLBACK (CONSISTENT MEDIUM)
    // ======================================
    return {
      predicted_risk_score: 0,

      risk_band: "MEDIUM",
      risk_label: "MEDIUM",
      risk_color: "#f59e0b",

      components: {
        payment_discipline_score: 0,
        income_stability_index: 0,
        financial_resilience_score: 0,
      },

      feature_importance: null,
      model_confidence: null,
      explanation: "Backend bağlantısı kurulamadı (fallback data)",
    };
  }
};