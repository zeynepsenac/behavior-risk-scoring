import GaugeComponent from "react-gauge-component";
import { useEffect, useState } from "react";

export default function GaugeChart({ score }) {

  // ✅ HARDENED SAFE SCORE
  const safeScore =
    typeof score === "number" && Number.isFinite(score)
      ? Math.max(0, Math.min(1, score))
      : 0;

  const [animatedValue, setAnimatedValue] = useState(0);

  useEffect(() => {
    let start = 0;
    setAnimatedValue(0);

    const duration = 700;
    const stepTime = 10;
    const steps = duration / stepTime;

    // ✅ safety fix (division by zero protection)
    const increment = steps > 0 ? safeScore / steps : safeScore;

    const interval = setInterval(() => {
      start += increment;

      if (start >= safeScore) {
        start = safeScore;
        clearInterval(interval);
      }

      setAnimatedValue(start);
    }, stepTime);

    return () => clearInterval(interval);
  }, [safeScore]);

  // % value
  const value = Math.max(0, Math.min(100, animatedValue * 100));

  // ✅ TEK DOĞRU KAYNAK (ANİMASYON DEĞİL GERÇEK SCORE)
  const getLevel = (v) => {
    if (v < 0.33) return "low";
    if (v < 0.66) return "medium";
    return "high";
  };

  const level = getLevel(safeScore);

  const getColor = () => {
    if (level === "low") return "#16a34a";
    if (level === "medium") return "#facc15";
    return "#dc2626";
  };

  const getBadge = () => {
    if (level === "low")
      return { label: "DÜŞÜK", color: "#16a34a", type: "low" };

    if (level === "medium")
      return { label: "ORTA", color: "#facc15", type: "medium" };

    return { label: "YÜKSEK", color: "#dc2626", type: "high" };
  };

  const badge = getBadge();

  const getContainerEffect = () => {
    if (badge.type === "high") {
      return {
        animation: "pulse 1.5s infinite",
        boxShadow: "0 0 18px rgba(220,38,38,0.3)"
      };
    }

    if (badge.type === "medium") {
      return {
        boxShadow: "0 0 10px rgba(250,204,21,0.25)"
      };
    }

    return {
      boxShadow: "0 0 8px rgba(22,163,74,0.2)"
    };
  };

  return (
    <div
      style={{
        background: "white",
        padding: "14px",
        borderRadius: "14px",
        textAlign: "center",
        fontFamily: "Inter, system-ui, sans-serif",
        maxWidth: "320px",
        margin: "0 auto",
        position: "relative",
        transition: "all 0.3s ease",
        ...getContainerEffect()
      }}
    >
      <h3
        style={{
          marginBottom: "6px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "6px",
          color: "#6b7280",
          fontSize: "14px"
        }}
      >
        📊 Risk Ölçeri
      </h3>

      {/* BADGE */}
      <div
        style={{
          position: "absolute",
          top: "10px",
          right: "10px",
          background: badge.color,
          color: "white",
          padding: "4px 8px",
          borderRadius: "999px",
          fontSize: "10px",
          fontWeight: "600",
          boxShadow: "0 2px 6px rgba(0,0,0,0.15)",
          animation:
            badge.type === "high"
              ? "pulse 1.2s infinite"
              : "fadeIn 0.5s ease"
        }}
      >
        {badge.label}
      </div>

      <div style={{ height: "180px" }}>
        <GaugeComponent
          value={value}
          type="radial"
          arc={{
            gradient: true,
            subArcs: [
              { limit: 33, color: "#16a34a" },
              { limit: 66, color: "#facc15" },
              { color: "#dc2626" }
            ]
          }}
          pointer={{
            type: "arrow",
            color: "#111827"
          }}
          labels={{
            valueLabel: {
              style: {
                fontSize: "18px",
                fontWeight: "700",
                fill: getColor()
              },
              formatTextValue: (v) => `${Math.round(v)}%`
            }
          }}
        />
      </div>

      <p
        style={{
          marginTop: "6px",
          fontSize: "12px",
          color: "#6b7280"
        }}
      >
        Risk seviyesi:{" "}
        <strong style={{ color: badge.color }}>
          {badge.label}
        </strong>
      </p>

      <style>
        {`
          @keyframes fadeIn {
            from {
              opacity: 0;
              transform: scale(0.9);
            }
            to {
              opacity: 1;
              transform: scale(1);
            }
          }

          @keyframes pulse {
            0% {
              transform: scale(1);
              box-shadow: 0 0 0 rgba(220,38,38,0.3);
            }
            50% {
              transform: scale(1.02);
              box-shadow: 0 0 15px rgba(220,38,38,0.4);
            }
            100% {
              transform: scale(1);
              box-shadow: 0 0 0 rgba(220,38,38,0.3);
            }
          }
        `}
      </style>
    </div>
  );
}