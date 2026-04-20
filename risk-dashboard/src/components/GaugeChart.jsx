import GaugeComponent from "react-gauge-component";
import { useEffect, useState } from "react";

export default function GaugeChart({ score }) {

  // ✅ FIX → score zaten 0–1 aralığında
  const normalizedScore = Number.isFinite(score)
    ? Math.max(0, Math.min(1, score))
    : 0;

  // 🎯 ANIMATION STATE
  const [animatedValue, setAnimatedValue] = useState(0);

  useEffect(() => {
    let start = 0;
    setAnimatedValue(0);

    const duration = 800;
    const stepTime = 10;
    const steps = duration / stepTime;
    const increment = normalizedScore / steps;

    const interval = setInterval(() => {
      start += increment;

      if (start >= normalizedScore) {
        start = normalizedScore;
        clearInterval(interval);
      }

      setAnimatedValue(start);
    }, stepTime);

    return () => clearInterval(interval);
  }, [normalizedScore]);

  // 🎯 GAUGE VALUE (0–100)
  const value = animatedValue * 100;

  // 🎨 RENK
  const getColor = () => {
    if (animatedValue < 0.33) return "#16a34a";
    if (animatedValue < 0.66) return "#facc15";
    return "#dc2626";
  };

  // 🏷️ BADGE
  const getBadge = () => {
    if (animatedValue < 0.33)
      return { label: "LOW", color: "#16a34a", type: "low" };
    if (animatedValue < 0.66)
      return { label: "MEDIUM", color: "#facc15", type: "medium" };
    return { label: "HIGH", color: "#dc2626", type: "high" };
  };

  const badge = getBadge();

  // 🔥 CONTAINER EFFECT
  const getContainerEffect = () => {
    if (badge.type === "high") {
      return {
        animation: "pulse 1.5s infinite",
        boxShadow: "0 0 25px rgba(220,38,38,0.4)"
      };
    }

    if (badge.type === "medium") {
      return {
        boxShadow: "0 0 15px rgba(250,204,21,0.3)"
      };
    }

    return {
      boxShadow: "0 0 10px rgba(22,163,74,0.2)"
    };
  };

  return (
    <div
      style={{
        background: "white",
        padding: "20px",
        borderRadius: "16px",
        textAlign: "center",
        fontFamily: "Inter, system-ui, sans-serif",
        maxWidth: "500px",
        margin: "0 auto",
        position: "relative",
        transition: "all 0.3s ease",
        ...getContainerEffect()
      }}
    >
      <h3
        style={{
          marginBottom: "8px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "6px",
          color: "#6b7280",
          fontSize: "16px"
        }}
      >
        📊 Risk Ölçeri
      </h3>

      {/* BADGE */}
      <div
        style={{
          position: "absolute",
          top: "12px",
          right: "12px",
          background: badge.color,
          color: "white",
          padding: "5px 10px",
          borderRadius: "999px",
          fontSize: "11px",
          fontWeight: "600",
          letterSpacing: "0.4px",
          boxShadow: "0 3px 8px rgba(0,0,0,0.15)",
          animation:
            badge.type === "high"
              ? "pulse 1.2s infinite"
              : "fadeIn 0.5s ease"
        }}
      >
        {badge.label}
      </div>

      {/* GAUGE */}
      <div style={{ height: "250px" }}>
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
                fontSize: "24px",
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
          marginTop: "8px",
          fontSize: "13px",
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
              transform: scale(0.85);
            }
            to {
              opacity: 1;
              transform: scale(1);
            }
          }

          @keyframes pulse {
            0% {
              transform: scale(1);
              box-shadow: 0 0 0 rgba(220,38,38,0.4);
            }
            50% {
              transform: scale(1.03);
              box-shadow: 0 0 20px rgba(220,38,38,0.6);
            }
            100% {
              transform: scale(1);
              box-shadow: 0 0 0 rgba(220,38,38,0.4);
            }
          }
        `}
      </style>
    </div>
  );
}