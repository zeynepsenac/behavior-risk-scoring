import rules from "../config/rules.json";

export const evaluateRule = (type, value) => {

  const ruleSet = rules?.[type];

  // ✅ FIX 1: daha güvenli normalize (0–100 / 0–1 karışık veri için)
  const normalize = (v) => {
    const num = Number(v);
    if (!Number.isFinite(num)) return null;

    // 🔥 FIX: sadece gerçekten büyük değerleri ölçekle
    if (num > 100) return num / 100;
    if (num > 1 && num <= 100) return num / 100;

    return num;
  };

  const safeValueRaw = Number(value);
  const safeValue = normalize(safeValueRaw);

  if (!Array.isArray(ruleSet) || ruleSet.length === 0) {
    return {
      label: "Unknown",
      color: "gray",
      description: "No rule defined",
      action: null,
      priority: "LOW",
      impact: 0,
      insight: "Missing rule configuration",
      explanation: "This metric is not mapped in rule engine.",
      featureType: type
    };
  }

  if (safeValue === null) {
    return {
      label: "Invalid",
      color: "gray",
      description: "Invalid numeric input",
      action: null,
      priority: "LOW",
      impact: 0,
      insight: "Value could not be parsed",
      explanation: "Non-numeric or missing data detected.",
      featureType: type
    };
  }

  // ✅ RULE MATCHING (fix: edge-safe)
  const matched = ruleSet.find((r) => {
    const min = Number.isFinite(Number(r?.min)) ? Number(r.min) : -Infinity;
    const max = Number.isFinite(Number(r?.max)) ? Number(r.max) : Infinity;

    return safeValue >= min && safeValue < max;
  });

  if (!matched) {
    return {
      label: "Unmapped",
      color: "gray",
      description: "No matching rule range",
      action: null,
      priority: "LOW",
      impact: 0,
      insight: "Value outside defined segmentation",
      explanation: "Rule ranges do not cover this value.",
      featureType: type
    };
  }

  const safeImpact = Number(matched?.impact ?? 0);
  const safePriority = (matched?.priority || "LOW").toUpperCase();
  const safeColor = matched?.color || "gray";
  const safeDescription = (matched?.description || "").trim();

  // ✅ FIX 2: tek threshold standard (tüm sistemle uyumlu)
  const getLevel = (v) => {
    if (v < 0.6) return "low";
    if (v < 0.8) return "medium";
    return "high";
  };

  const level = getLevel(safeValue);

  // 🔥 FIX 3: label override daha net ve deterministik
  const getLabel = () => {

    if (type === "financial_resilience") {
      if (safeValue < 0.2) return "Kritik";
      if (safeValue < 0.6) return "Zayıf";
      if (safeValue < 0.8) return "Orta";
      return "Güçlü";
    }

    if (type === "payment_discipline") {
      if (safeValue < 0.6) return "Zayıf";
      if (safeValue < 0.8) return "Orta";
      return "Güçlü";
    }

    if (type === "income_stability") {
      if (safeValue < 0.6) return "Dengesiz";
      if (safeValue < 0.8) return "Orta";
      return "Stabil";
    }

    return matched?.label || "Unknown";
  };

  // 🧠 FIX 4: insight daha tutarlı hale getirildi
  const buildInsight = (label, impact, type) => {

    if (type === "financial_resilience") {
      if (safeValue < 0.2) {
        return "Critical financial vulnerability: no buffer against shocks.";
      }
      if (safeValue < 0.6) {
        return "Low financial resilience increases risk exposure.";
      }
      return "Financial resilience contributes to stability.";
    }

    if (type === "income_stability") {
      if (safeValue < 0.6) {
        return "Income instability increases risk variability.";
      }
      return "Stable income improves predictability.";
    }

    if (type === "payment_discipline") {
      if (safeValue < 0.6) {
        return "Weak payment discipline increases default risk.";
      }
      return "Strong payment discipline reduces risk.";
    }

    // FIX 5: impact fallback daha doğru
    if (impact < 0) return `${label} reduces risk.`;
    if (impact > 0.15) return `${label} strongly impacts risk.`;
    if (impact > 0.05) return `${label} moderately impacts risk.`;

    return `${label} has neutral impact.`;
  };

  const buildAction = (action, label, impact, type) => {

    if (type === "financial_resilience" && safeValue < 0.2) {
      return {
        title: "Build emergency buffer",
        desc: "Critical financial vulnerability detected.",
        priority: "HIGH"
      };
    }

    if (type === "payment_discipline" && safeValue < 0.6) {
      return {
        title: "Improve payment discipline",
        desc: "Late payments increase risk exposure.",
        priority: "HIGH"
      };
    }

    return {
      title: action || `${label} optimization`,
      desc: safeDescription || "AI recommendation from rule engine.",
      priority: safePriority
    };
  };

  const finalLabel = getLabel();

  return {
    label: finalLabel,
    color: safeColor,
    description: safeDescription,
    impact: safeImpact,
    priority: safePriority,

    insight: buildInsight(finalLabel, safeImpact, type),
    explanation: buildInsight(finalLabel, safeImpact, type),
    action: buildAction(matched?.action, finalLabel, safeImpact, type),

    featureType: type
  };
};