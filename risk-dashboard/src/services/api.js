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
    // 🔥 SCORE SAFE PARSE
    // ======================================
    const score = Number(data?.predicted_risk_score);
    const safeScore = Number.isFinite(score) ? score : 0;

    // ======================================
    // 🔥 BAND NORMALIZATION (UI SAFE)
    // ======================================
    const rawBand =
      data?.predicted_band ??
      data?.risk_band ??
      data?.risk_label ??
      "MEDIUM";

    const normalizedBand = String(rawBand)
      .toUpperCase()
      .trim();

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
    // 🔥 FEATURE IMPORTANCE SAFE
    // ======================================
    const feature_importance = Array.isArray(data?.feature_importance)
      ? data.feature_importance
      : null;

    // ======================================
    // 🔥 MODEL CONFIDENCE SAFE
    // ======================================
    const model_confidence = Number.isFinite(data?.model_confidence)
      ? Number(data.model_confidence)
      : 0;

    // ======================================
    // 🔥 EXPLANATION SAFE TEXT
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

      // CORE METRICS
      predicted_risk_score: safeScore,
      risk_score: safeScore,

      risk_band: finalBand,
      predicted_band: finalBand,
      risk_label: finalBand,

      // OPTIONAL UI COLOR (backend yoksa null)
      risk_color: data?.risk_color ?? null,

      // CLEAN COMPONENTS
      components,

      // FEATURE IMPORTANCE
      feature_importance,

      // MODEL CONFIDENCE
      model_confidence,

      // TEXT SAFE
      explanation,

      // DEBUG / FUTURE USE
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