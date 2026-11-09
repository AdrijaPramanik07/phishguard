"use client";

import React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Heart } from "lucide-react";

export default function MarqueeFooter() {
  const shouldReduceMotion = useReducedMotion();
  const textItem = "Made with love, Adrija";

  return (
    <footer className="w-full border-t border-slate-800/80 bg-slate-950/90 backdrop-blur-md pt-5 pb-8 overflow-hidden relative select-none">
      {/* Edge Gradients for Soft Fade */}
      <div className="absolute left-0 top-0 bottom-0 w-16 sm:w-32 bg-gradient-to-r from-[#06080e] to-transparent z-10 pointer-events-none" />
      <div className="absolute right-0 top-0 bottom-0 w-16 sm:w-32 bg-gradient-to-l from-[#06080e] to-transparent z-10 pointer-events-none" />

      <div className="flex items-center">
        {!shouldReduceMotion ? (
          <motion.div
            className="flex items-center gap-8 whitespace-nowrap cursor-default"
            animate={{ x: ["0%", "-50%"] }}
            transition={{
              repeat: Infinity,
              duration: 26,
              ease: "linear"
            }}
            whileHover={{ transition: { duration: 100 } }} // Pauses on hover
          >
            {/* 16 duplicates ensure seamless looping across all viewport widths */}
            {Array.from({ length: 16 }).map((_, i) => (
              <div key={i} className="flex items-center gap-4 text-xs sm:text-sm font-mono tracking-widest uppercase">
                <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-violet-400 bg-clip-text text-transparent font-bold">
                  {textItem}
                </span>
                <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500 animate-pulse" />
              </div>
            ))}
          </motion.div>
        ) : (
          <div className="w-full text-center flex items-center justify-center gap-2 text-xs font-mono text-cyan-400">
            <span>{textItem}</span>
            <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500" />
          </div>
        )}
      </div>
    </footer>
  );
}