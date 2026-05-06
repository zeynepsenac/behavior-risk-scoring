import GaugeComponent from "react-gauge-component";
import { useEffect, useState, useRef } from "react";

export default function GaugeChart({ score, predicted_band, financial_resilience_score }) {

  const normalize = (v) => {
    const n = Number(v);
    if (!Number.isFinite(n)) return null;
    return n > 1 ? n / 100 : n;
  };

  const safeScore =
    typeof score === "number" && Number.isFinite(score)
      ? Math.max(0, Math.min(1, score))
      : 0;

  const [animatedValue, setAnimatedValue] = useState(0);
  const prevScoreRef = useRef(0);

  const resilience = normalize(financial_resilience_score);
  let finalBand = predicted_band;

  const [isDark, setIsDark] = useState(
    window.matchMedia("(prefers-color-scheme: dark)").matches
  );

  const [isHover, setIsHover] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const listener = () => setIsDark(media.matches);

    media.addEventListener("change", listener);
    return () => media.removeEventListener("change", listener);
  }, []);

  useEffect(() => {
    let startTime = null;

    const startValue = prevScoreRef.current;
    const endValue = safeScore;

    const duration = 1200;

    function animate(timestamp) {
      if (!startTime) startTime = timestamp;

      const progress = Math.min((timestamp - startTime) / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);

      const currentValue = startValue + (endValue - startValue) * ease;
      setAnimatedValue(currentValue);

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        prevScoreRef.current = endValue;
      }
    }

    requestAnimationFrame(animate);
  }, [safeScore]);

  const value = Math.max(0, Math.min(100, animatedValue * 100));

  const getLevelFromBand = (band) => {
    if (band === "LOW") return "low";
    if (band === "MEDIUM") return "medium";
    return "high";
  };

  const level = getLevelFromBand(finalBand);

  const config = {
    low: {
      label: "DÜŞÜK RİSK",
      color: "#22c55e",
      glow: "0 0 20px #22c55e, 0 0 40px #22c55e55",
      glowHover: "0 0 30px #22c55e, 0 0 60px #22c55eaa"
    },
    medium: {
      label: "ORTA RİSK",
      color: "#f59e0b",
      glow: "0 0 20px #f59e0b, 0 0 40px #f59e0b55",
      glowHover: "0 0 30px #f59e0b, 0 0 60px #f59e0baa"
    },
    high: {
      label: "YÜKSEK RİSK",
      color: "#ef4444",
      glow: "0 0 20px #ef4444, 0 0 40px #ef444455",
      glowHover: "0 0 30px #ef4444, 0 0 60px #ef4444aa"
    }
  };

  const current = config[level];

  const theme = isDark
    ? {
        bg: "radial-gradient(circle at 30% 20%, #0f172a, #020617)",
        textMain: "#e2e8f0",
        textSoft: "#64748b",
        pointer: "#38bdf8",
        shadow: "0 0 20px rgba(0,0,0,0.6)"
      }
    : {
        bg: "linear-gradient(145deg, #ffffff, #f8fafc)",
        textMain: "#0f172a",
        textSoft: "#94a3b8",
        pointer: "#1e293b",
        shadow: "0 10px 30px rgba(0,0,0,0.08)"
      };

  return (
    <div
      onMouseEnter={() => setIsHover(true)}
      onMouseLeave={() => setIsHover(false)}
      style={{
        background: theme.bg,
        borderRadius: "18px",
        padding: "20px",
        maxWidth: "340px",
        margin: "0 auto",
        textAlign: "center",
        fontFamily: "Inter, system-ui, sans-serif",
        boxShadow: `
          ${theme.shadow},
          ${isDark ? (isHover ? current.glowHover : current.glow) : ""}
        `,
        transform: isHover ? "scale(1.02)" : "scale(1)",
        border: isDark ? "1px solid rgba(255,255,255,0.05)" : "none",
        transition: "all 0.3s ease",
        position: "relative"
      }}
    >
      <div style={{ height: "200px", position: "relative" }}>
        <GaugeComponent
          value={value}
          type="radial"
          animationDuration={0}
          arc={{
            gradient: true,
            width: 0.25,
            padding: 0.02,
            subArcs: [
              { limit: 33, color: "#22c55e" },
              { limit: 66, color: "#f59e0b" },
              { color: "#ef4444" }
            ]
          }}
          pointer={{
            type: "arrow",
            color: theme.pointer,
            length: 0.6,
            width: 12
          }}
          labels={{
            valueLabel: {
              formatTextValue: () => "" // 🔥 küçük yüzde tamamen kapatıldı
            }
          }}
        />

        <div
          style={{
            position: "absolute",
            top: "48%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            fontSize: "34px",
            fontWeight: "800",
            color: theme.textMain
          }}
        >
          {Math.round(value)}%
        </div>
      </div>

      <div
        style={{
          marginTop: "10px",
          fontSize: "14px",
          fontWeight: "700",
          color: current.color,
          animation:
            level === "low"
              ? "pulseSoft 2.5s infinite"
              : level === "medium"
              ? "pulseMedium 1.8s infinite"
              : "pulseStrong 1.2s infinite",
          textShadow: `0 0 10px ${current.color}`
        }}
      >
        {current.label}
      </div>

      <div style={{ fontSize: "12px", color: theme.textSoft, marginTop: "4px" }}>
        Risk seviyesi analiz edildi
      </div>
    </div>
  );
}