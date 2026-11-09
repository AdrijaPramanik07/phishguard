"use client";

import React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Globe, ArrowRight } from "lucide-react";

interface UrlAnatomyProps {
  url: string;
  anatomy?: {
    scheme: string;
    subdomain: string;
    domain: string;
    path: string;
  };
}

export default function UrlAnatomy({ url, anatomy }: UrlAnatomyProps) {
  const shouldReduceMotion = useReducedMotion();

  // Fallback parsing via browser URL API if backend anatomy payload is absent
  let parsedScheme = "http://";
  let parsedSub = "";
  let parsedDomain = "";
  let parsedPath = "/";

  if (anatomy && anatomy.domain) {
    parsedScheme = anatomy.scheme || "http://";
    parsedSub = anatomy.subdomain || "";
    parsedDomain = anatomy.domain || "";
    parsedPath = anatomy.path || "/";
  } else {
    try {
      const formatted = url.startsWith("http") ? url : `http://${url}`;
      const obj = new URL(formatted);
      parsedScheme = `${obj.protocol}//`;
      const hostParts = obj.hostname.split(".");
      if (hostParts.length > 2) {
        parsedSub = hostParts.slice(0, hostParts.length - 2).join(".");
        parsedDomain = hostParts.slice(-2).join(".");
      } else {
        parsedDomain = obj.hostname;
      }
      parsedPath = obj.pathname + obj.search;
    } catch {
      parsedDomain = url;
    }
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: shouldReduceMotion ? 0 : 0.08
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -8 },
    visible: { opacity: 1, x: 0, transition: { duration: 0.3 } }
  };

  return (
    <div className="rounded-2xl border border-slate-800/80 bg-slate-900/50 backdrop-blur-md p-4 sm:p-5 space-y-3">
      <div className="flex items-center justify-between text-xs font-mono tracking-wider text-slate-400 uppercase">
        <span className="flex items-center gap-2 text-cyan-400">
          <Globe className="w-4 h-4" /> URL Anatomy Inspector
        </span>
        <span className="text-[11px] text-slate-500">Structural Decomposition</span>
      </div>

      {/* Split Anatomy Pill Strip */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="font-mono text-xs sm:text-sm bg-slate-950/90 rounded-xl p-3 border border-slate-800/90 flex flex-wrap items-center gap-1.5 overflow-x-auto shadow-inner"
      >
        <motion.span variants={itemVariants} className="text-slate-500 select-all">
          {parsedScheme}
        </motion.span>

        {parsedSub && (
          <motion.span
            variants={itemVariants}
            className="text-rose-400/90 bg-rose-950/30 line-through decoration-rose-500/70 decoration-2 px-2 py-0.5 rounded border border-rose-500/30"
            title="Attackers prefix brand names here to deceive victims"
          >
            {parsedSub}.
          </motion.span>
        )}

        <motion.span
          variants={itemVariants}
          className="text-emerald-300 bg-emerald-950/40 font-bold px-2.5 py-0.5 rounded border border-emerald-400/50 shadow-[0_0_15px_rgba(16,185,129,0.2)]"
        >
          {parsedDomain}
        </motion.span>

        <motion.span variants={itemVariants} className="text-slate-400 break-all select-all">
          {parsedPath}
        </motion.span>
      </motion.div>

      {/* Explanatory Caption */}
      <div className="flex items-start gap-2 text-xs text-slate-300">
        <ArrowRight className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
        <p>
          The highlighted green section (
          <strong className="text-emerald-300 font-mono font-semibold">{parsedDomain}</strong>
          ) is who actually owns and operates this link. Everything preceding it is decorative routing.
        </p>
      </div>
    </div>
  );
}