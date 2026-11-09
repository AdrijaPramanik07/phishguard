"use client";

import React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { ExternalLink, ShieldAlert, BookOpen, Terminal, PhoneCall } from "lucide-react";

interface ResourceLink {
  name: string;
  href: string;
}

interface ResourceSection {
  title: string;
  icon: React.ReactNode;
  links: ResourceLink[];
}

const SECTIONS: ResourceSection[] = [
  {
    title: "Phishing & Scams",
    icon: <ShieldAlert className="w-4 h-4 text-rose-400" />,
    links: [
      { name: "CISA: Recognize & Report Phishing", href: "https://www.cisa.gov/secure-our-world/recognize-and-report-phishing" },
      { name: "Anti-Phishing Working Group (APWG)", href: "https://apwg.org" },
      { name: "Google Safe Browsing Report", href: "https://safebrowsing.google.com/safebrowsing/report_phish/" }
    ]
  },
  {
    title: "Cybersecurity Basics",
    icon: <BookOpen className="w-4 h-4 text-cyan-400" />,
    links: [
      { name: "OWASP Top 10 Security Risks", href: "https://owasp.org/www-project-top-ten/" },
      { name: "Have I Been Pwned (Breach Check)", href: "https://haveibeenpwned.com" },
      { name: "CERT-In National Advisory", href: "https://www.cert-in.org.in" }
    ]
  },
  {
    title: "Ethical Hacking Labs",
    icon: <Terminal className="w-4 h-4 text-violet-400" />,
    links: [
      { name: "TryHackMe Practice Labs", href: "https://tryhackme.com" },
      { name: "Hack The Box Academy", href: "https://www.hackthebox.com" },
      { name: "PortSwigger Web Security Academy", href: "https://portswigger.net/web-security" }
    ]
  },
  {
    title: "Report Cyber Fraud",
    icon: <PhoneCall className="w-4 h-4 text-amber-400" />,
    links: [
      { name: "National Cyber Crime Portal (India)", href: "https://cybercrime.gov.in" },
      { name: "Emergency Helpline: 1930", href: "tel:1930" }
    ]
  }
];

export default function LearnLinks() {
  const shouldReduceMotion = useReducedMotion();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: shouldReduceMotion ? 0 : 0.08
      }
    }
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 16 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.35, ease: "easeOut" }
    }
  };

  return (
    <section className="mt-20 space-y-6">
      <div className="text-center space-y-1.5">
        <h2 className="text-2xl font-bold tracking-tight text-white">
          Learn More {"&"} Stay Safe
        </h2>
        <p className="text-slate-400 text-xs sm:text-sm">
          Verified resources, reporting hotlines, and security foundations.
        </p>
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-50px" }}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {SECTIONS.map((sec, idx) => (
          <motion.div
            key={idx}
            variants={cardVariants}
            whileHover={{ y: -4, borderColor: "rgba(56,189,248,0.4)" }}
            className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800/80 backdrop-blur-md transition-all shadow-lg flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="flex items-center gap-2 font-semibold text-sm text-slate-200">
                {sec.icon}
                <span>{sec.title}</span>
              </div>

              <ul className="space-y-2">
                {sec.links.map((link, lIdx) => {
                  const isTel = link.href.startsWith("tel:");
                  return (
                    <li key={lIdx}>
                      <a
                        href={link.href}
                        target={isTel ? "_self" : "_blank"}
                        rel={isTel ? undefined : "noopener noreferrer"}
                        className="group flex items-center justify-between text-xs text-slate-400 hover:text-cyan-300 transition-colors"
                      >
                        <span className="truncate pr-1">{link.name}</span>
                        <ExternalLink className="w-3 h-3 text-slate-600 group-hover:text-cyan-400 transition-colors shrink-0" />
                      </a>
                    </li>
                  );
                })}
              </ul>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </section>
  );
}