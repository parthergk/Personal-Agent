import React from "react";
import Link from "next/link";
import CornerBox from "@/components/CornerBox";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy — VXYAK",
  description: "How VXYAK handles, isolates, and protects your personal data and messages.",
};

export default function PrivacyPage() {
  return (
    <main className="relative min-h-svh w-full bg-[#f6f4ef] text-[#171717] flex flex-col justify-between selection:bg-neutral-800 selection:text-[#f6f4ef]">
      {/* ─── TOP NAVIGATION ─── */}
      <header className="w-full max-w-[1360px] mx-auto px-5 sm:px-12 pt-6 sm:pt-10 flex items-center justify-between text-[11px] sm:text-xs font-mono tracking-[0.16em] sm:tracking-[0.25em] font-medium uppercase z-20">
        <div className="flex items-center gap-2">
          <Link
            href="/"
            className="group relative inline-flex items-center gap-2 select-none"
          >
            <span className="relative inline-flex items-center justify-center px-1.5 py-0.5">
              <span>VXYAK</span>
              <CornerBox hoverOnly dimension="58 x 15" />
            </span>
            <span className="text-neutral-500 font-normal tracking-[0.16em] sm:tracking-[0.25em]">
              / AGENT
            </span>
          </Link>
        </div>

        <nav className="flex items-center gap-5 sm:gap-12">
          <Link
            href="/about"
            className="group relative inline-flex items-center justify-center px-1.5 py-0.5 select-none"
          >
            <span>ABOUT</span>
            <CornerBox hoverOnly dimension="58 x 15" />
          </Link>

          <Link
            href="/register"
            className="group relative inline-flex items-center justify-center px-1.5 py-0.5 select-none"
          >
            <span>LOG IN</span>
            <CornerBox hoverOnly dimension="62 x 15" />
          </Link>
        </nav>
      </header>

      {/* ─── LEGAL CONTENT ─── */}
      <article className="w-full max-w-[820px] mx-auto px-5 sm:px-12 py-16 sm:py-24 flex flex-col">
        {/* Title & Effective Date */}
        <div className="mb-8 sm:mb-12">
          <span className="font-mono text-[10px] sm:text-[11px] tracking-[0.24em] text-neutral-500 uppercase font-medium">
            LEGAL / PRIVACY POLICY
          </span>
          <h1 className="font-serif text-3xl sm:text-5xl md:text-6xl font-normal leading-[1.08] tracking-tight text-[#171717] mt-3">
            Privacy Policy
          </h1>
          <p className="font-mono text-xs text-neutral-500 mt-3 tracking-wide">
            Effective Date: October 2026
          </p>
        </div>

        {/* Policy Body */}
        <div className="font-mono text-xs sm:text-[13px] text-neutral-700 leading-[1.9] tracking-wide space-y-10 border-t border-neutral-300 pt-8 sm:pt-10">
          {/* Section 1 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              01 // Introduction
            </h2>
            <p>
              VXYAK (&ldquo;we&rdquo;, &ldquo;our&rdquo;, or &ldquo;the Service&rdquo;) is an AI-powered personal memory and reminder assistant accessed through WhatsApp. This Privacy Policy outlines what information we collect, how it is processed and stored, and how we protect your personal privacy.
            </p>
          </section>

          {/* Section 2 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              02 // Information We Collect
            </h2>
            <ul className="list-disc pl-5 space-y-2 text-neutral-700">
              <li>
                <strong className="text-neutral-900 font-medium">Account Details:</strong> Your phone number and display name, provided during registration and verified via WhatsApp OTP.
              </li>
              <li>
                <strong className="text-neutral-900 font-medium">Conversational Content:</strong> Messages, voice notes, photos, documents, and captions you send to VXYAK on WhatsApp.
              </li>
              <li>
                <strong className="text-neutral-900 font-medium">Reminders & Tasks:</strong> Time-based alerts and task descriptions you instruct the agent to schedule.
              </li>
            </ul>
          </section>

          {/* Section 3 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              03 // How Information is Processed
            </h2>
            <p>
              We process data strictly to provide conversational memory and reminder services:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-neutral-700">
              <li>
                <strong className="text-neutral-900 font-medium">Audio Transcription:</strong> Voice recordings are converted to text using Sarvam AI speech models. Audio files sent purely for reminders are discarded once parsed.
              </li>
              <li>
                <strong className="text-neutral-900 font-medium">Visual Understanding:</strong> Uploaded images are analyzed using OpenAI Vision models to generate descriptive summaries before being stored.
              </li>
              <li>
                <strong className="text-neutral-900 font-medium">Vector Embeddings:</strong> Saved notes and descriptions are converted into mathematical embeddings to enable semantic search via Qdrant Vector Database.
              </li>
            </ul>
          </section>

          {/* Section 4 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              04 // Strict Multi-Tenant Data Isolation
            </h2>
            <p>
              Your data is isolated. Every vector point and database record is indexed strictly under your unique, authenticated phone identity. No other user can access, query, or view your stored memories or media files. We never sell your personal data or conversation records.
            </p>
          </section>

          {/* Section 5 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              05 // Third-Party Infrastructure Providers
            </h2>
            <p>
              To deliver our service over WhatsApp with high reliability, we rely on established infrastructure partners:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-neutral-700">
              <li>Meta WhatsApp Cloud API (messaging transport)</li>
              <li>OpenAI (vector embeddings, language model reasoning, and vision analysis)</li>
              <li>Sarvam AI (speech-to-text transcription)</li>
              <li>Qdrant (vector database storage)</li>
            </ul>
            <p>
              Data is transmitted to these providers solely for the purpose of executing your requests in real time.
            </p>
          </section>

          {/* Section 6 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              06 // Data Retention & Your Rights
            </h2>
            <p>
              You maintain ownership of your data. You may request the export or complete deletion of your account, conversation history, and stored vector memories at any time by contacting support.
            </p>
          </section>

          {/* Section 7 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              07 // Contact Us
            </h2>
            <p>
              For privacy-related questions or data deletion requests, contact us at <span className="text-neutral-900 font-medium">privacy@vxyak.com</span>.
            </p>
          </section>
        </div>

      </article>

      {/* ─── FOOTER ─── */}
      <footer className="w-full max-w-[1360px] mx-auto px-6 sm:px-12 mt-8 md:mt-6 font-mono text-[10px] sm:text-[11px] tracking-wider text-neutral-600">
        <div className="w-full pt-4 pb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-4 border-t border-neutral-500/50">
          <div>&copy; 2026 Vxyak.</div>
          <div className="flex items-center gap-3">
            <Link href="/privacy" className="font-medium text-neutral-800">
              Privacy Policy
            </Link>
            <span>|</span>
            <Link href="/terms" className="hover:opacity-75 transition-opacity">
              Terms of Service
            </Link>
          </div>
        </div>
      </footer>
    </main>
  );
}
