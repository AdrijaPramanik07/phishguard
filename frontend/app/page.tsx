"use client";

import React, { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  Activity,
  Terminal,
  Info,
  ShieldQuestion,
  Lock
} from "lucide-react";

import AnimatedBackground from "../components/AnimatedBackground";
import Gauge from "../components/Gauge";
import UrlAnatomy from "../components/UrlAnatomy";
import FactorList, { ReasonItem } from "../components/FactorList";

interface ScanResult {
  url: string;
  risk_score: number;
  verdict: "High Risk" | "Medium Risk" | "Low Risk";
  verdict_desc: string;
  plain_summary?: string;
  anatomy?: {
    scheme: string;
    subdomain: string;
    domain: string;
    path: string;
  };
  raised_risk?: ReasonItem[];
  lowered_risk?: ReasonItem[];
  phishing_reasons?: Array<{
    feature: string;
    value: string | number | boolean;
    shap_value: number;
    description?: string;
  }>;
  benign_reasons?: Array<{
    feature: string;
    value: string | number | boolean;
    shap_value: number;
    description?: string;
  }>;
}

const PRESETS = [
  {
    label: "PayPal Phishing Kit",
    url: "http://paypal-security.update-account.xyz/login",
    safe: false,
    tag: "Brand Spoof + .xyz"
  },
  {
    label: "Fake Banking Subdomains",
    url: "http://chase.online.verify-security.account-update.buzz/auth",
    safe: false,
    tag: "Chained Subdomains"
  },
  {
    label: "IP Direct Attack",
    url: "http://192.168.1.105/admin/login.php",
    safe: false,
    tag: "Raw IP Host"
  },
  {
    label: "Google Search (Safe)",
    url: "https://www.google.com/search?q=machine+learning+cybersecurity&oq=ml&sourceid=chrome",
    safe: true,
    tag: "Long Search Query"
  },
  {
    label: "GitHub Repo (Safe)",
    url: "https://github.com/explore",
    safe: true,
    tag: "Trusted HTTPS Domain"
  }
];

export default function PhishGuardApp() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const shouldReduceMotion = useReducedMotion();

  const handleScan = async (targetUrl?: string) => {
    let inputUrl = (targetUrl || url).trim();
    if (!inputUrl) {
      setError("Please provide a valid URL string to inspect.");
      return;
    }

    if (!inputUrl.startsWith("http://") && !inputUrl.startsWith("https://")) {
      inputUrl = "http://" + inputUrl;
      setUrl(inputUrl);
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: inputUrl })
      });

      if (!res.ok) throw new Error("Backend inference engine returned an error.");
      const data: ScanResult = await res.json();
      setResult(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to communicate with FastAPI backend.");
      }
    } finally {
      setLoading(false);
    }
  };

  const getVerdictCardStyles = (verdict: string) => {
    switch (verdict) {
      case "High Risk":
        return {
          border: "border-rose-500/40",
          glow: "shadow-[0_0_60px_-15px_rgba(244,63,94,0.3)]",
          bg: "bg-rose-950/20",
          badge: "bg-rose-500/20 text-rose-300 border-rose-500/30",
          icon: <ShieldAlert className="w-5 h-5 text-rose-400" />
        };
      case "Medium Risk":
        return {
          border: "border-amber-500/40",
          glow: "shadow-[0_0_60px_-15px_rgba(245,158,11,0.3)]",
          bg: "bg-amber-950/20",
          badge: "bg-amber-500/20 text-amber-300 border-amber-500/30",
          icon: <AlertTriangle className="w-5 h-5 text-amber-400" />
        };
      default:
        return {
          border: "border-emerald-500/40",
          glow: "shadow-[0_0_60px_-15px_rgba(16,185,129,0.3)]",
          bg: "bg-emerald-950/20",
          badge: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
          icon: <ShieldCheck className="w-5 h-5 text-emerald-400" />
        };
    }
  };

  const raisedList: ReasonItem[] =
    result?.raised_risk ||
    result?.phishing_reasons?.map((r) => ({
      feature: r.feature,
      value: r.value,
      shap_value: r.shap_value,
      impact_share: Math.round(Math.abs(r.shap_value) * 10),
      reason_text: r.description || `Feature '${r.feature}' elevated risk`
    })) ||
    [];

  const loweredList: ReasonItem[] =
    result?.lowered_risk ||
    result?.benign_reasons?.map((r) => ({
      feature: r.feature,
      value: r.value,
      shap_value: r.shap_value,
      impact_share: Math.round(Math.abs(r.shap_value) * 10),
      reason_text: r.description || `Feature '${r.feature}' favored safe status`
    })) ||
    [];

  return (
    <div className="min-h-screen bg-[#06080e] text-slate-100 flex flex-col justify-start font-sans relative selection:bg-cyan-500/30 selection:text-cyan-200 pb-16">
      <AnimatedBackground />

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 pt-12 sm:pt-16 relative z-10 w-full">
        {/* Header Hero */}
        <header className="text-center space-y-3 mb-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-950/30 text-cyan-400 text-xs tracking-wider uppercase font-mono">
            <Activity className="w-3.5 h-3.5 animate-pulse text-cyan-400" />
            Explainable AI · XGBoost · SHAP Attribution
          </div>

          <h1 className="text-4xl sm:text-6xl font-black tracking-tight">
            Phish
            <span className="bg-gradient-to-r from-cyan-400 via-sky-400 to-violet-400 bg-clip-text text-transparent">
              Guard
            </span>
          </h1>

          <p className="text-slate-400 text-sm sm:text-base max-w-lg mx-auto leading-relaxed">
            Inspect URL architecture and see why a link looks suspicious before opening it.
          </p>
        </header>

        {/* Input Card Container */}
        <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-2xl p-3 sm:p-4 shadow-2xl mb-6 relative overflow-hidden transition-all duration-300 focus-within:border-cyan-500/60 focus-within:shadow-[0_0_30px_-5px_rgba(6,182,212,0.3)]">
          {loading && !shouldReduceMotion && (
            <motion.div
              initial={{ x: "-100%" }}
              animate={{ x: "200%" }}
              transition={{ repeat: Infinity, duration: 1.2, ease: "easeInOut" }}
              className="absolute inset-y-0 w-1/3 bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent pointer-events-none"
            />
          )}

          <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-3">
            <div className="relative w-full">
              <input
                type="text"
                placeholder="Enter or paste any suspicious link to analyze..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleScan()}
                className="w-full bg-slate-950/80 border border-slate-800/90 focus:border-cyan-500/40 rounded-xl px-4 py-3.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none transition-all shadow-inner font-mono"
              />
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => handleScan()}
              disabled={loading}
              className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium text-sm flex items-center justify-center gap-2 transition-all shadow-lg shadow-cyan-500/20 disabled:opacity-50 whitespace-nowrap cursor-pointer group"
            >
              {loading ? (
                <>
                  <ShieldQuestion className="w-4 h-4 animate-spin text-white" />
                  <span>Scanning...</span>
                </>
              ) : (
                <>
                  <span>Inspect Link</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </motion.button>
          </div>

          {/* Test Preset Chips */}
          <div className="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t border-slate-800/70 text-xs">
            <span className="text-slate-500 font-medium flex items-center gap-1 mr-1">
              <Terminal className="w-3.5 h-3.5" /> Attack Presets:
            </span>
            {PRESETS.map((preset, idx) => (
              <motion.button
                key={idx}
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.96 }}
                type="button"
                onClick={() => {
                  setUrl(preset.url);
                  handleScan(preset.url);
                }}
                className={`px-2.5 py-1 rounded-lg border font-mono transition-all text-[11px] flex items-center gap-1.5 cursor-pointer ${
                  preset.safe
                    ? "bg-emerald-950/30 border-emerald-500/30 text-emerald-300 hover:bg-emerald-900/40"
                    : "bg-rose-950/30 border-rose-500/30 text-rose-300 hover:bg-rose-900/40"
                }`}
              >
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    preset.safe ? "bg-emerald-400" : "bg-rose-500"
                  }`}
                />
                {preset.label}
              </motion.button>
            ))}
          </div>
        </div>

        {/* Inline Error Notice */}
        {error && (
          <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs sm:text-sm mb-6 flex items-center gap-2.5">
            <Info className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        {/* Skeleton Placeholders */}
        {loading && (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-6 sm:p-8 space-y-6 animate-pulse">
            <div className="h-14 bg-slate-800/50 rounded-xl" />
            <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
              <div className="md:col-span-5 h-44 bg-slate-800/40 rounded-xl" />
              <div className="md:col-span-7 h-44 bg-slate-800/40 rounded-xl" />
            </div>
          </div>
        )}

        {/* Results Region */}
        <section aria-live="polite">
          <AnimatePresence mode="wait">
            {result && !loading && (
              <motion.div
                initial={shouldReduceMotion ? { opacity: 0 } : { opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.35, ease: "easeOut" }}
                className="space-y-6"
              >
                {/* 1. URL Anatomy Strip */}
                <UrlAnatomy url={result.url} anatomy={result.anatomy} />

                {/* 2. Main Threat Verdict Card */}
                <div
                  className={`rounded-2xl border ${getVerdictCardStyles(result.verdict).border} ${getVerdictCardStyles(result.verdict).bg} ${getVerdictCardStyles(result.verdict).glow} p-6 sm:p-8 backdrop-blur-md transition-all duration-500`}
                >
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
                    {/* Left Column: Gauge, Metric & Summary */}
                    <div className="md:col-span-5 flex flex-col items-center md:items-start text-center md:text-left space-y-4">
                      <div className="flex items-center gap-2.5">
                        <span
                          className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${getVerdictCardStyles(result.verdict).badge}`}
                        >
                          {getVerdictCardStyles(result.verdict).icon}
                          {result.verdict}
                        </span>
                      </div>

                      <Gauge score={result.risk_score} verdict={result.verdict} />

                      {result.plain_summary && (
                        <p className="text-xs sm:text-sm text-slate-300 font-medium bg-slate-900/70 border border-slate-800 p-3 rounded-xl w-full leading-relaxed">
                          💡 {result.plain_summary}
                        </p>
                      )}
                    </div>

                    {/* Right Column: Factor Bars */}
                    <div className="md:col-span-7 border-t md:border-t-0 md:border-l border-slate-800/80 pt-6 md:pt-0 md:pl-8">
                      <div className="mb-4">
                        <h3 className="text-xs font-mono uppercase tracking-widest text-slate-400">
                          Explainable AI Attribution Matrix
                        </h3>
                        <p className="text-slate-500 text-[11px] mt-0.5">
                          SHAP factor share isolating structural reasons behind this score.
                        </p>
                      </div>

                      <FactorList raisedRisk={raisedList} loweredRisk={loweredList} />
                    </div>
                  </div>

                  {/* High Risk Actions Banner */}
                  {result.verdict === "High Risk" && (
                    <motion.div
                      initial={{ opacity: 0, y: 6 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-6 pt-5 border-t border-rose-500/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-rose-200 bg-rose-950/30 p-3.5 rounded-xl"
                    >
                      <div>
                        <strong>What should I do?</strong> Do not open this link or enter passwords. Close the window and report it to the impersonated brand or your organization&apos;s security team.
                      </div>
                      <span className="shrink-0 px-2.5 py-1 bg-rose-500/20 rounded-md text-rose-300 border border-rose-500/30 font-medium">
                        Deceptive Host
                      </span>
                    </motion.div>
                  )}
                </div>

                {/* 3. Persistent Disclaimer Strip */}
                <div className="p-3.5 rounded-xl bg-slate-900/40 border border-slate-800 text-slate-400 text-xs flex items-center gap-2.5">
                  <Lock className="w-4 h-4 text-cyan-400 shrink-0" />
                  <span>
                    <strong>Statistical Risk Estimate:</strong> PhishGuard inspects structural URL properties without contacting the remote server. This is a risk estimate, not proof that a link is safe.
                  </span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </section>
      </div>
    </div>
  );
}