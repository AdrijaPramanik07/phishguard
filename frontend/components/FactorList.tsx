"use client";

import React, { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { TrendingUp, TrendingDown, ChevronDown, ChevronUp, AlertCircle, CheckCircle2 } from "lucide-react";

export interface ReasonItem {
  feature: string;
  value: string | number | boolean;
  shap_value: number;
  impact_share: number;
  reason_text: string;
}

interface FactorListProps {
  raisedRisk: ReasonItem[];
  loweredRisk: ReasonItem[];
}

export default function FactorList({ raisedRisk, loweredRisk }: FactorListProps) {
  const [showAllRaised, setShowAllRaised] = useState(false);
  const [showAllLowered, setShowAllLowered] = useState(false);
  const shouldReduceMotion = useReducedMotion();

  const displayedRaised = showAllRaised ? raisedRisk : raisedRisk.slice(0, 4);
  const displayedLowered = showAllLowered ? loweredRisk : loweredRisk.slice(0, 4);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
      {/* Column 1: Raised the Risk */}
      <div className="space-y-3">
        <div className="flex items-center justify-between pb-1 border-b border-rose-500/20">
          <span className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-rose-400">
            <TrendingUp className="w-4 h-4 text-rose-500" /> Raised the Risk
          </span>
          <span className="text-[10px] font-mono text-slate-400">{raisedRisk.length} factors</span>
        </div>

        <div className="space-y-2.5">
          <AnimatePresence initial={false}>
            {displayedRaised.length > 0 ? (
              displayedRaised.map((item, idx) => (
                <motion.div
                  key={`raised-${item.feature}-${idx}`}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.25, delay: shouldReduceMotion ? 0 : idx * 0.05 }}
                  className="p-3 rounded-xl bg-slate-900/60 border border-rose-500/20 space-y-2 hover:border-rose-500/40 transition-colors"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-start gap-1.5">
                      <AlertCircle className="w-3.5 h-3.5 text-rose-400 shrink-0 mt-0.5" />
                      <p className="text-xs text-slate-200 font-medium leading-snug">
                        {item.reason_text}
                      </p>
                    </div>
                    <span className="font-mono text-[11px] font-bold text-rose-400 shrink-0">
                      +{item.impact_share}%
                    </span>
                  </div>

                  <div className="w-full bg-slate-800/80 h-1.5 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(item.impact_share * 1.5, 100)}%` }}
                      transition={{ duration: 0.5, ease: "easeOut" }}
                      className="h-full bg-gradient-to-r from-rose-500 to-red-600 rounded-full"
                    />
                  </div>
                  <div className="text-[10px] font-mono text-slate-400 flex justify-between">
                    <span>{item.feature}</span>
                    <span>val: {String(item.value)}</span>
                  </div>
                </motion.div>
              ))
            ) : (
              <div className="p-4 rounded-xl bg-slate-900/30 border border-slate-800 text-xs text-slate-400 text-center">
                No dominant risk amplifiers detected.
              </div>
            )}
          </AnimatePresence>

          {raisedRisk.length > 4 && (
            <button
              type="button"
              onClick={() => setShowAllRaised(!showAllRaised)}
              className="w-full py-1.5 text-xs text-slate-400 hover:text-slate-200 flex items-center justify-center gap-1 transition-colors font-mono cursor-pointer"
            >
              {showAllRaised ? (
                <>
                  Show Less <ChevronUp className="w-3.5 h-3.5" />
                </>
              ) : (
                <>
                  Show All ({raisedRisk.length}) <ChevronDown className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Column 2: Lowered the Risk */}
      <div className="space-y-3">
        <div className="flex items-center justify-between pb-1 border-b border-emerald-500/20">
          <span className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-400">
            <TrendingDown className="w-4 h-4 text-emerald-500" /> Lowered the Risk
          </span>
          <span className="text-[10px] font-mono text-slate-400">{loweredRisk.length} factors</span>
        </div>

        <div className="space-y-2.5">
          <AnimatePresence initial={false}>
            {displayedLowered.length > 0 ? (
              displayedLowered.map((item, idx) => (
                <motion.div
                  key={`lowered-${item.feature}-${idx}`}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.25, delay: shouldReduceMotion ? 0 : idx * 0.05 }}
                  className="p-3 rounded-xl bg-slate-900/60 border border-emerald-500/20 space-y-2 hover:border-emerald-500/40 transition-colors"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-start gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                      <p className="text-xs text-slate-200 font-medium leading-snug">
                        {item.reason_text}
                      </p>
                    </div>
                    <span className="font-mono text-[11px] font-bold text-emerald-400 shrink-0">
                      -{item.impact_share}%
                    </span>
                  </div>

                  <div className="w-full bg-slate-800/80 h-1.5 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(item.impact_share * 1.5, 100)}%` }}
                      transition={{ duration: 0.5, ease: "easeOut" }}
                      className="h-full bg-gradient-to-r from-emerald-500 to-teal-600 rounded-full"
                    />
                  </div>
                  <div className="text-[10px] font-mono text-slate-400 flex justify-between">
                    <span>{item.feature}</span>
                    <span>val: {String(item.value)}</span>
                  </div>
                </motion.div>
              ))
            ) : (
              <div className="p-4 rounded-xl bg-slate-900/30 border border-slate-800 text-xs text-slate-400 text-center">
                No strong trust-building features identified.
              </div>
            )}
          </AnimatePresence>

          {loweredRisk.length > 4 && (
            <button
              type="button"
              onClick={() => setShowAllLowered(!showAllLowered)}
              className="w-full py-1.5 text-xs text-slate-400 hover:text-slate-200 flex items-center justify-center gap-1 transition-colors font-mono cursor-pointer"
            >
              {showAllLowered ? (
                <>
                  Show Less <ChevronUp className="w-3.5 h-3.5" />
                </>
              ) : (
                <>
                  Show All ({loweredRisk.length}) <ChevronDown className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}