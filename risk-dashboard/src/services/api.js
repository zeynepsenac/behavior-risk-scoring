const BASE_URL = "http://127.0.0.1:8000";

// ==========================================
// 🔥 RISK SCORE API (STABLE + UI FRIENDLY)
// ==========================================
export const getRiskScore = async (id) => {
  try {
    // ======================================
    // 🔥 INPUT SAFETY
    // ======================================
    const safeId = Number(id);

    if (!Number.isInteger(safeId) || safeId < 1 || safeId > 1200) {
      throw new Error("Geçersiz müşteri numarası (1-1200)");
    }

    const response = await fetch(
      `${BASE_URL}/risk-score/${safeId}?explain=true`
    );

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }

    const data = await response.json();

    if (!data || typeof data !== "object") {
      throw new Error("Invalid backend response");
    }

    // ======================================
    // 🔥 SCORE SAFE PARSE (CRITICAL FIX)
    // ======================================
    let score = Number(data?.predicted_risk_score ?? data?.risk_score);

    if (!Number.isFinite(score)) score = 0;

    // 🔥 normalize (0-100 → 0-1)
    if (score > 1) score = score / 100;

    const safeScore = Math.max(0, Math.min(1, score));

    // ======================================
    // 🔥 BAND NORMALIZATION
    // ======================================
    const rawBand =
      data?.predicted_band ??
      data?.risk_band ??
      data?.risk_label ??
      "MEDIUM";

    const normalizedBand = String(rawBand).toUpperCase().trim();

    const allowedBands = ["LOW", "MEDIUM", "HIGH"];

    const finalBand = allowedBands.includes(normalizedBand)
      ? normalizedBand
      : "MEDIUM";

    // ======================================
    // 🔥 COMPONENTS SAFE PARSE
    // ======================================
    const components = {
      payment_discipline_score: Number(
        data?.components?.payment_discipline_score ??
        data?.payment_discipline_score ??
        0
      ),

      income_stability_index: Number(
        data?.components?.income_stability_index ??
        data?.income_stability_index ??
        0
      ),

      financial_resilience_score: Number(
        data?.components?.financial_resilience_score ??
        data?.financial_resilience_score ??
        0
      ),
    };

    // ======================================
    // 🔥 FEATURE IMPORTANCE
    // ======================================
    const feature_importance = Array.isArray(data?.feature_importance)
      ? data.feature_importance
      : null;

    // ======================================
    // 🔥 MODEL CONFIDENCE (FIX)
    // ======================================
    let model_confidence = Number(data?.model_confidence ?? data?.confidence);

    if (!Number.isFinite(model_confidence)) model_confidence = 0;

    if (model_confidence > 1) model_confidence /= 100;

    // ======================================
    // 🔥 EXPLANATION SAFE
    // ======================================
    const explanation =
      typeof data?.explanation === "string" &&
      data.explanation.trim().length > 0
        ? data.explanation
        : "Model açıklaması mevcut değil";

    // ======================================
    // 🔥 RETURN CLEAN UI OBJECT
    // ======================================
    return {
      ...data,

      // CORE
      predicted_risk_score: safeScore,
      risk_score: safeScore,

      // BAND
      risk_band: finalBand,
      predicted_band: finalBand,
      risk_label: finalBand,

      // OPTIONAL COLOR
      risk_color: data?.risk_color ?? null,

      // COMPONENTS
      components,

      // EXTRA
      feature_importance,
      model_confidence,
      explanation,

      // DEBUG
      raw_band: rawBand,
    };

  } catch (error) {
    console.error("getRiskScore ERROR:", error);

    // ======================================
    // 🔥 UI FALLBACK (NEVER BREAK DASHBOARD)
    // ======================================
    return {
      predicted_risk_score: 0,
      risk_score: 0,

      risk_band: "MEDIUM",
      predicted_band: "MEDIUM",
      risk_label: "MEDIUM",

      risk_color: "#f59e0b",

      components: {
        payment_discipline_score: 0,
        income_stability_index: 0,
        financial_resilience_score: 0,
      },

      feature_importance: null,
      model_confidence: 0,

      explanation: "Backend bağlantısı kurulamadı (fallback data)",

      raw_band: "MEDIUM",
    };
  }
};