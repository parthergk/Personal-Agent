import React from "react";
import Link from "next/link";
import CornerBox from "@/components/CornerBox";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service — VXYAK",
  description: "Terms and conditions governing the use of the VXYAK personal AI assistant.",
};

export default function TermsPage() {
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
            LEGAL / TERMS OF SERVICE
          </span>
          <h1 className="font-serif text-3xl sm:text-5xl md:text-6xl font-normal leading-[1.08] tracking-tight text-[#171717] mt-3">
            Terms of Service
          </h1>
          <p className="font-mono text-xs text-neutral-500 mt-3 tracking-wide">
            Effective Date: October 2026
          </p>
        </div>

        {/* Terms Body */}
        <div className="font-mono text-xs sm:text-[13px] text-neutral-700 leading-[1.9] tracking-wide space-y-10 border-t border-neutral-300 pt-8 sm:pt-10">
          {/* Section 1 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              01 // Acceptance of Terms
            </h2>
            <p>
              By accessing, registering for, or communicating with VXYAK (&ldquo;the Service&rdquo;), you agree to be bound by these Terms of Service. If you do not agree to these terms, please refrain from using the Service.
            </p>
          </section>

          {/* Section 2 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              02 // Description of Service
            </h2>
            <p>
              VXYAK provides personal memory indexing, semantic search, and scheduled reminder services delivered via WhatsApp. The Service allows users to save notes, voice memos, photos, and files, and retrieve them through conversational queries.
            </p>
          </section>

          {/* Section 3 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              03 // Account Registration & WhatsApp Identity
            </h2>
            <p>
              Access to VXYAK requires an active WhatsApp account. You agree to provide a valid phone number owned by you. You are responsible for maintaining the confidentiality of any verification codes sent to your phone and for all interactions initiated through your WhatsApp number.
            </p>
          </section>

          {/* Section 4 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              04 // Acceptable Use
            </h2>
            <p>
              You agree to use VXYAK exclusively for personal, lawful organizational purposes. You agree not to:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-neutral-700">
              <li>Upload malicious code, viruses, or corrupted media.</li>
              <li>Attempt to extract or exploit prompt engineering, database schemas, or system instructions.</li>
              <li>Transmit abusive, defamatory, or unlawful materials.</li>
              <li>Interfere with, overload, or disrupt background dispatch workers or API webhooks.</li>
            </ul>
          </section>

          {/* Section 5 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              05 // AI Capabilities & Disclaimers
            </h2>
            <p>
              VXYAK leverages probabilistic artificial intelligence models for language understanding, voice transcription, and visual analysis. While engineered for precision:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-neutral-700">
              <li>Responses may occasionally be incomplete or misinterpret complex colloquialisms.</li>
              <li>VXYAK is not a substitute for certified medical, financial, or legal counsel. Critical reminders or life-essential dates should not rely solely on automated chat notifications.</li>
            </ul>
          </section>

          {/* Section 6 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              06 // Third-Party Dependencies
            </h2>
            <p>
              Service delivery depends on Meta Platforms and third-party telecom infrastructure for WhatsApp message delivery. VXYAK is not liable for temporary delays or carrier interruptions outside our direct control.
            </p>
          </section>

          {/* Section 7 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              07 // Limitation of Liability
            </h2>
            <p>
              To the maximum extent permitted by applicable law, VXYAK and its operators shall not be liable for any indirect, incidental, or consequential damages resulting from lost memories, missed reminders, or service downtime.
            </p>
          </section>

          {/* Section 8 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              08 // Termination & Modifications
            </h2>
            <p>
              We reserve the right to suspend or terminate accounts that violate these Terms. We may update these Terms periodically by updating this page with the revised effective date.
            </p>
          </section>

          {/* Section 9 */}
          <section className="space-y-3">
            <h2 className="text-neutral-900 font-semibold tracking-wider uppercase text-[11px] sm:text-xs">
              09 // Contact
            </h2>
            <p>
              For inquiries regarding these Terms, please reach out to <span className="text-neutral-900 font-medium">legal@vxyak.com</span>.
            </p>
          </section>
        </div>

        {/* Back Link */}
        <div className="mt-12 sm:mt-16 pt-6 border-t border-neutral-300 flex items-center justify-between font-mono text-xs sm:text-[13px]">
          <Link
            href="/"
            className="text-neutral-600 hover:text-neutral-900 transition-colors inline-flex items-center gap-1.5"
          >
            &larr; Back to Home
          </Link>
          <Link
            href="/privacy"
            className="text-neutral-600 hover:text-neutral-900 transition-colors inline-flex items-center gap-1.5"
          >
            Privacy Policy &rarr;
          </Link>
        </div>
      </article>

      {/* ─── FOOTER ─── */}
      <footer className="w-full max-w-[1360px] mx-auto px-6 sm:px-12 mt-8 md:mt-6 font-mono text-[10px] sm:text-[11px] tracking-wider text-neutral-600">
        <div className="w-full pt-4 pb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-4 border-t border-neutral-500/50">
          <div>&copy; 2026 Vxyak.</div>
          <div className="flex items-center gap-3">
            <Link href="/privacy" className="hover:opacity-75 transition-opacity">
              Privacy Policy
            </Link>
            <span>|</span>
            <Link href="/terms" className="font-medium text-neutral-800">
              Terms of Service
            </Link>
          </div>
        </div>
      </footer>
    </main>
  );
}
