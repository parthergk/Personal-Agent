import React from "react";
import Link from "next/link";
import Image from "next/image";
import CornerBox from "@/components/CornerBox";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About — VXYAK",
  description:
    "Why we built VXYAK: a personal memory and task assistant that lives natively inside WhatsApp.",
};

export default function AboutPage() {
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
          <span className="relative inline-flex items-center justify-center px-1.5 py-0.5 select-none font-semibold text-[#171717]">
            <span>ABOUT</span>
            <CornerBox dimension="58 x 15" />
          </span>

          <Link
            href="/register"
            className="group relative inline-flex items-center justify-center px-1.5 py-0.5 select-none"
          >
            <span>LOG IN</span>
            <CornerBox hoverOnly dimension="62 x 15" />
          </Link>
        </nav>
      </header>

      {/* ─── MAIN CONTENT ─── */}
      <div className="w-full max-w-[1360px] mx-auto px-5 sm:px-12 py-16 sm:py-24 flex flex-col gap-16 sm:gap-24">
        {/* Top Section: Story on Left, Image on Right */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-center">
          {/* Left Column: Title, Story & Action Link */}
          <div className="lg:col-span-6 flex flex-col items-start gap-6 sm:gap-8">
            <h1 className="font-serif text-3xl sm:text-5xl md:text-6xl xl:text-[68px] font-normal leading-[1.08] tracking-tight text-[#171717]">
              A calmer way
              <br />
              to remember.
            </h1>

            <div className="font-mono text-xs sm:text-[13px] text-neutral-700 leading-[1.9] tracking-wide space-y-6 sm:space-y-7 max-w-xl">
              <p>
                Most productivity tools demand new routines: opening a dedicated app, managing complex dashboards, and manually tagging notes into folders you rarely revisit.
              </p>

              <p>
                VXYAK is built on a simpler premise: useful intelligence should meet you where your conversations already happen. It lives directly inside WhatsApp, turning everyday interactions into a calm, indexed memory.
              </p>

              <p>
                Whether it is a voice note in Hindi or English, a photo of a document, or a quick reminder for tomorrow evening, you simply message it as you would a thoughtful friend. It organizes your notes into a private vector space, ready to be recalled by meaning whenever you ask.
              </p>
            </div>

            <div className="pt-2 sm:pt-4">
              <Link
                href="/register"
                className="inline-flex items-center gap-1.5 font-mono text-xs sm:text-[13px] tracking-[0.14em] text-[#171717] font-medium border-b border-[#171717] pb-0.5 hover:opacity-70 transition-opacity"
              >
                Meet your agent &rarr;
              </Link>
            </div>
          </div>

          {/* Right Column: Editorial Image with Blueprint CornerBox */}
          <div className="lg:col-span-6 flex justify-center lg:justify-end w-full">
            <div className="relative group max-w-[540px] w-full border border-neutral-300/80 bg-[#fbfaf7] p-3 sm:p-3.5 shadow-xs">
              <CornerBox hoverOnly dimension="540 x 405" />
              <div className="relative aspect-[4/3] w-full overflow-hidden bg-neutral-200/50">
                <Image
                  src="/about.jpg"
                  alt="Minimalist workspace with open linen notebook and pen in soft natural sunlight"
                  fill
                  sizes="(max-width: 1024px) 100vw, 540px"
                  priority
                  className="object-cover transition-transform duration-700 ease-out group-hover:scale-[1.02]"
                />
              </div>
              <div className="mt-3 flex items-center justify-between font-mono text-[9.5px] sm:text-[10px] text-neutral-500 uppercase tracking-widest px-0.5">
                <span>01 // IN QUIET SYNC</span>
                <span>WHATSAPP NATIVE</span>
              </div>
            </div>
          </div>
        </section>

        {/* Full-width AT A GLANCE Section (Below Main Content) */}
        <section className="w-full pt-12 sm:pt-16 border-t border-neutral-300">
          <div className="flex items-center justify-between mb-8">
            <span className="font-mono text-[10px] sm:text-[11px] tracking-[0.24em] text-neutral-500 uppercase font-medium">
              AT A GLANCE
            </span>
            <Link
              href="/"
              className="font-mono text-xs text-neutral-500 hover:text-neutral-800 transition-colors inline-flex items-center gap-1.5"
            >
              &larr; Back to Home
            </Link>
          </div>

          <dl className="w-full divide-y divide-neutral-300/70 font-mono text-xs sm:text-[13px]">
            <div className="py-4 sm:py-5 flex flex-col sm:flex-row sm:items-baseline justify-between gap-1 sm:gap-4">
              <dt className="text-neutral-500 uppercase tracking-wider text-[11px] sm:w-48 shrink-0">Channel</dt>
              <dd className="text-neutral-800 font-medium sm:text-right">WhatsApp (no app download required)</dd>
            </div>

            <div className="py-4 sm:py-5 flex flex-col sm:flex-row sm:items-baseline justify-between gap-1 sm:gap-4">
              <dt className="text-neutral-500 uppercase tracking-wider text-[11px] sm:w-48 shrink-0">Inputs</dt>
              <dd className="text-neutral-800 font-medium sm:text-right">Voice notes, photos, text, and documents</dd>
            </div>

            <div className="py-4 sm:py-5 flex flex-col sm:flex-row sm:items-baseline justify-between gap-1 sm:gap-4">
              <dt className="text-neutral-500 uppercase tracking-wider text-[11px] sm:w-48 shrink-0">Languages</dt>
              <dd className="text-neutral-800 font-medium sm:text-right">English, Hindi, and Hinglish</dd>
            </div>

            <div className="py-4 sm:py-5 flex flex-col sm:flex-row sm:items-baseline justify-between gap-1 sm:gap-4">
              <dt className="text-neutral-500 uppercase tracking-wider text-[11px] sm:w-48 shrink-0">Functions</dt>
              <dd className="text-neutral-800 font-medium sm:text-right">Save memories, semantic search, reminders</dd>
            </div>

            <div className="py-4 sm:py-5 flex flex-col sm:flex-row sm:items-baseline justify-between gap-1 sm:gap-4">
              <dt className="text-neutral-500 uppercase tracking-wider text-[11px] sm:w-48 shrink-0">Privacy</dt>
              <dd className="text-neutral-800 font-medium sm:text-right">Strict per-user isolated vector space</dd>
            </div>
          </dl>
        </section>
      </div>

      {/* ─── FOOTER ─── */}
      <footer className="w-full max-w-[1360px] mx-auto px-6 sm:px-12 mt-8 md:mt-6 font-mono text-[10px] sm:text-[11px] tracking-wider text-neutral-600">
        <div className="w-full pt-4 pb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-4 border-t border-neutral-500/50">
          <div>&copy; 2026 Vxyak.</div>
          <div className="flex items-center gap-3">
            <a href="#privacy" className="hover:opacity-75 transition-opacity">
              Privacy Policy
            </a>
            <span>|</span>
            <a href="#terms" className="hover:opacity-75 transition-opacity">
              Terms of Service
            </a>
          </div>
        </div>
      </footer>
    </main>
  );
}
