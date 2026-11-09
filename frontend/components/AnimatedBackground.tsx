"use client";

import React, { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";

const SPOKE_ANGLES = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330];

export default function AnimatedBackground() {
  const shouldReduceMotion = useReducedMotion();
  const [loadProgress, setLoadProgress] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setLoadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(timer);
          return 100;
        }
        return prev + 2;
      });
    }, 25);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0 flex items-center justify-center">
      {/* 1. Deep Space Cyber Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0ea5e908_1px,transparent_1px),linear-gradient(to_bottom,#0ea5e908_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_60%_at_50%_50%,#000_50%,transparent_100%)]" />

      {/* 2. Ambient Glow Blobs */}
      {!shouldReduceMotion && (
        <>
          <motion.div
            animate={{
              scale: [1, 1.15, 1],
              opacity: [0.12, 0.22, 0.12],
              x: [0, 30, 0],
              y: [0, -20, 0]
            }}
            transition={{ duration: 14, repeat: Infinity, ease: "easeInOut" }}
            className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-600/15 rounded-full blur-[140px]"
          />
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.1, 0.18, 0.1],
              x: [0, -40, 0],
              y: [0, 30, 0]
            }}
            transition={{ duration: 18, repeat: Infinity, ease: "easeInOut", delay: 2 }}
            className="absolute bottom-1/4 right-1/4 w-[28rem] h-[28rem] bg-violet-600/15 rounded-full blur-[160px]"
          />
        </>
      )}

      {/* 3. Centered Heavy-Spoke Cyber Wheel (Broad rims & spokes, no words) */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[520px] h-[520px] sm:w-[680px] sm:h-[680px] select-none opacity-30">
        <motion.div
          animate={shouldReduceMotion ? { rotate: 0 } : { rotate: 360 }}
          transition={{ duration: 50, repeat: Infinity, ease: "linear" }}
          className="relative w-full h-full rounded-full border-4 border-cyan-500/30 bg-gradient-to-br from-cyan-950/10 via-transparent to-violet-950/10 shadow-[0_0_100px_-10px_rgba(6,182,212,0.25)]"
        >
          {/* Broad Outer & Mid Concentric Rims */}
          <div className="absolute inset-4 rounded-full border-2 border-dashed border-cyan-400/25" />
          <div className="absolute inset-16 rounded-full border-4 border-slate-700/40" />
          <div className="absolute inset-32 rounded-full border-2 border-cyan-500/20" />
          
          {/* Heavy Central Core Hub */}
          <div className="absolute inset-[38%] rounded-full bg-cyan-500/15 border-4 border-cyan-400/50 backdrop-blur-sm shadow-[0_0_35px_rgba(6,182,212,0.4)]" />
          <div className="absolute inset-[44%] rounded-full border-2 border-dashed border-cyan-300/60" />

          {/* Broad Radiating Spokes (No text labels) */}
          {SPOKE_ANGLES.map((angle, idx) => (
            <div
              key={idx}
              className="absolute top-1/2 left-1/2 w-full origin-left -translate-y-1/2"
              style={{ transform: `rotate(${angle}deg)` }}
            >
              {/* Thick spoke blade */}
              <div className="w-1/2 h-[3px] bg-gradient-to-r from-cyan-400/60 via-cyan-500/30 to-transparent rounded-full shadow-[0_0_8px_rgba(6,182,212,0.4)]" />
              {/* Accent marker block along each spoke */}
              <div className="absolute left-[30%] -top-[3px] w-2.5 h-2.5 bg-cyan-400/50 border border-cyan-300/80 rounded-sm" />
            </div>
          ))}
        </motion.div>
      </div>

      {/* 4. Bottom System Sync Progress Bar */}
      {loadProgress < 100 && (
        <div className="fixed bottom-0 left-0 right-0 h-1 bg-slate-900/80 z-50">
          <motion.div
            className="h-full bg-gradient-to-r from-cyan-500 via-sky-400 to-violet-500 shadow-[0_0_12px_rgba(6,182,212,0.8)]"
            style={{ width: `${loadProgress}%` }}
          />
          <div className="absolute bottom-2 right-4 font-mono text-[10px] text-cyan-400/80 tracking-widest uppercase">
            System Initializing · {loadProgress}%
          </div>
        </div>
      )}
    </div>
  );
}