"use client";

import React, { useEffect, useState } from "react";
import { motion, useSpring, useTransform, useReducedMotion } from "framer-motion";

interface GaugeProps {
  score: number;
  verdict: "High Risk" | "Medium Risk" | "Low Risk";
}

export default function Gauge({ score, verdict }: GaugeProps) {
  const shouldReduceMotion = useReducedMotion();
  const clampedScore = Math.min(Math.max(score, 1), 99);
  const [mounted, setMounted] = useState<boolean>(false);
  const [currentAngle, setCurrentAngle] = useState<number>(-90);
  const [displayValue, setDisplayValue] = useState<string>(
    clampedScore >= 99 ? "99%+" : `${clampedScore}%`
  );

  const springValue = useSpring(0, {
    stiffness: 60,
    damping: 18,
    restDelta: 0.001
  });

  const needleAngle = useTransform(springValue, [0, 100], [-90, 90]);

  useEffect(() => {
    setMounted(true);
    springValue.set(clampedScore);

    const unsubScore = springValue.on("change", (latest: number) => {
      const val = Math.round(latest);
      setDisplayValue(val >= 99 ? "99%+" : `${val}%`);
    });

    const unsubAngle = needleAngle.on("change", (latest: number) => {
      setCurrentAngle(latest);
    });

    return () => {
      unsubScore();
      unsubAngle();
    };
  }, [clampedScore, springValue, needleAngle]);

  const targetStaticAngle = (clampedScore / 100) * 180 - 90;

  return (
    <div
      className="relative flex flex-col items-center justify-center select-none"
      role="meter"
      aria-valuenow={clampedScore}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Calibrated Risk Score: ${clampedScore} percent`}
    >
      <div className="relative w-56 h-28 sm:w-64 sm:h-32 overflow-hidden flex items-end justify-center">
        <svg viewBox="0 0 200 100" className="w-full h-full">
          <defs>
            <linearGradient id="gaugeTrack" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10b981" />
              <stop offset="35%" stopColor="#10b981" />
              <stop offset="55%" stopColor="#f59e0b" />
              <stop offset="75%" stopColor="#f43f5e" />
              <stop offset="100%" stopColor="#e11d48" />
            </linearGradient>
          </defs>

          {/* Background Track */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="#1e293b"
            strokeWidth="16"
            strokeLinecap="round"
          />

          {/* Active Gradient Arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="url(#gaugeTrack)"
            strokeWidth="16"
            strokeLinecap="round"
            opacity="0.9"
          />
        </svg>

        {/* Animated Needle */}
        <div
          style={{
            transform: `rotate(${!shouldReduceMotion && mounted ? currentAngle : targetStaticAngle}deg)`,
            transformOrigin: "50% 100%"
          }}
          className="absolute bottom-0 w-1.5 h-20 sm:h-24 bg-slate-100 rounded-t-full shadow-[0_0_12px_rgba(255,255,255,0.8)] transition-transform duration-75"
        />

        {/* Center Hub */}
        <div className="absolute -bottom-3 w-6 h-6 rounded-full bg-slate-900 border-2 border-slate-200 shadow-lg z-10" />
      </div>

      {/* Numerical Counter Display */}
      <div className="mt-2 text-center">
        <span className="text-4xl sm:text-5xl font-black tracking-tight text-white font-mono">
          {displayValue}
        </span>
        <div className="text-[11px] font-mono uppercase tracking-widest text-slate-400 mt-0.5">
          Calibrated Probability
        </div>
      </div>

      {/* Zone Indicators */}
      <div className="flex justify-between w-full max-w-[240px] text-[10px] font-mono uppercase mt-2 px-1">
        <span className="text-emerald-400 font-semibold">0% Low</span>
        <span className="text-amber-400 font-semibold">35% Med</span>
        <span className="text-rose-400 font-semibold">70% High</span>
      </div>
    </div>
  );
}