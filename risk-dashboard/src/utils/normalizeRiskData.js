export const normalizeValue = (v) => {
  // 🧠 NULL / undefined / empty string = missing data
  if (v === null || v === undefined || v === "") {
    return {
      value: null,
      isMissing: true
    };
  }

  // 🧠 Convert to number
  const n = Number(v);

  // ❌ invalid number = missing data
  if (!Number.isFinite(n)) {
    return {
      value: null,
      isMissing: true
    };
  }

  // ✅ valid numeric value (0 dahil!)
  return {
    value: n,
    isMissing: false
  };
};