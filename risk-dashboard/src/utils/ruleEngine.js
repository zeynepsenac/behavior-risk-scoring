import rules from "../config/rules.json";

export const evaluateRule = (type, value) => {

  // 🔒 rule set kontrolü
  const ruleSet = rules?.[type];

  if (!Array.isArray(ruleSet) || ruleSet.length === 0) {
    return {
      label: "Unknown",
      color: "gray",
      description: "",
      action: null,
      priority: null,
      impact: 0
    };
  }

  // 🔒 value güvenli hale getir
  const safeValue = Number.isFinite(value) ? Number(value) : null;

  if (safeValue === null) {
    return {
      label: "Unknown",
      color: "gray",
      description: "",
      action: null,
      priority: null,
      impact: 0
    };
  }

  // 🎯 rule eşleşmesi
  const matched = ruleSet.find((r) => {

    const min = Number(r.min);
    const max = Number(r.max);

    const safeMin = Number.isFinite(min) ? min : -Infinity;
    const safeMax = Number.isFinite(max) ? max : Infinity;

    return safeValue >= safeMin && safeValue < safeMax;
  });

  // 🔒 fallback (NO UI COMMENT)
  if (!matched) {
    return {
      label: "Unknown",
      color: "gray",
      description: "",
      action: null,
      priority: null,
      impact: 0
    };
  }

  // 🔒 impact güvenliği
  const safeImpact = Number.isFinite(matched.impact)
    ? Number(matched.impact)
    : 0;

  // 🔒 priority normalize
  const safePriority =
    typeof matched.priority === "string"
      ? matched.priority.toUpperCase()
      : null;

  // 🔒 color fallback
  const safeColor = matched.color ?? "gray";

  // 🔒 description temiz (UI kontrolü dışarıda)
  const safeDescription =
    typeof matched.description === "string"
      ? matched.description
      : "";

  return {
    label: matched.label ?? "Unknown",
    color: safeColor,

    description: safeDescription,

    action: matched.action ?? null,
    priority: safePriority,

    impact: safeImpact
  };
};