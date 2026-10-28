import Link from "next/link";
import CornerBox from "@/components/CornerBox";

export default function Home() {
  return (
    <main className="relative isolate min-h-svh w-full overflow-x-hidden bg-[#f6f4ef] text-[#171717] flex flex-col justify-between">
      {/* Decorative background */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 -z-10 bg-[position:35%_top] sm:bg-[position:top_center]"
        style={{
          backgroundImage: "url('/bg.webp')",
          backgroundRepeat: "no-repeat",
          // backgroundPosition: "top center",
          backgroundSize: "cover",
        }}
      />

      {/* ─── TOP NAVIGATION ─── */}
      <header className="w-full max-w-[1360px] mx-auto px-5 sm:px-12 pt-6 sm:pt-10 flex items-center justify-between text-[11px] sm:text-xs font-mono tracking-[0.16em] sm:tracking-[0.25em] font-medium uppercase z-20">
        <div className="flex items-center gap-2">
          <Link
            href="/"
            className="group relative inline-flex items-center gap-2 select-none"
          >
            {/* VXYAK with selection box */}
            <span className="relative inline-flex items-center justify-center px-1.5 py-0.5">
              <span>VXYAK</span>
              <CornerBox hoverOnly dimension="58 x 15" />
            </span>

            {/* Subtitle */}
            <span className="text-neutral-500 font-normal tracking-[0.16em] sm:tracking-[0.25em]">
              / AGENT
            </span>
          </Link>
        </div>
        <nav className="flex items-center gap-5 sm:gap-12">
          <a
            href="#about"
            className="group relative inline-flex items-center justify-center px-1.5 py-0.5 select-none"
          >
            <span>ABOUT</span>
            <CornerBox hoverOnly dimension="58 x 15" />
          </a>

          <Link
            href="/register"
            className="group relative inline-flex items-center justify-center px-1.5 py-0.5 select-none"
          >
            <span>LOG IN</span>
            <CornerBox hoverOnly dimension="62 x 15" />
          </Link>
        </nav>
      </header>

      {/* ─── HERO SECTION (FOLD 1) ─── */}
      <section className="relative w-full max-w-[1360px] mx-auto px-5 sm:px-12 pt-10 sm:pt-20 pb-28 sm:pb-48 flex flex-col items-center justify-center">
        {/* Left Side Label (A CALMER WAY TO WORK) - Visible on xl+ to prevent overlap */}
        <div className="hidden xl:flex flex-col items-start absolute left-8 2xl:left-12 top-24 select-none font-mono text-[11px] leading-[1.8]">
          <div className="tracking-[0.24em] uppercase text-neutral-800 font-medium">
            <p>A</p>
            <p>CALMER</p>
            <p>WAY</p>
            <p>TO WORK</p>
          </div>
          <div className="w-[1px] h-7 bg-neutral-400/80 my-3 ml-0.5" />
          <div className="tracking-wide text-neutral-500">
            <p>Organize</p>
            <p>Automate</p>
            <p>Simplify</p>
            <p>Live better</p>
          </div>
        </div>

        {/* Right Side Index (PLANS, IDEAS, TASKS...) - Visible on xl+ to prevent overlap */}
        <div className="hidden xl:flex flex-col items-start absolute right-8 2xl:right-12 top-10 select-none font-mono text-[10px] leading-[1.9]">
          <div className="tracking-[0.28em] uppercase text-neutral-600 font-medium">
            <p>PLANS</p>
            <p>IDEAS</p>
            <p>TASKS</p>
            <p>INFORMATION</p>
            <p>PEOPLE</p>
          </div>
          <div className="w-[1px] h-7 bg-neutral-400/80 my-2.5 ml-0.5" />
          <div className="tracking-[0.28em] uppercase text-neutral-600 font-medium">
            <p>ALL</p>
            <p>IN</p>
            <p>ONE</p>
            <p>PLACE</p>
          </div>
        </div>

        {/* Center Hero Content */}
        <div className="flex flex-col items-center text-center max-w-2xl mt-18 sm:mt-8 px-2">
          {/* Main Headline */}
          <h1 className="font-serif text-5xl sm:text-6xl md:text-7xl xl:text-[84px] font-normal leading-[1.08] tracking-tight text-[#171717] break-words">
            Your world,
            <br />
            in quiet sync.
          </h1>

          {/* Badge */}
          <div className="mt-6 sm:mt-8 mb-5 sm:mb-6">
            <span className="relative inline-flex items-center justify-center bg-[#f6f4ef]/60 backdrop-blur-[2px] px-5 sm:px-6 py-2 text-[10px] sm:text-xs font-mono tracking-[0.2em] sm:tracking-[0.28em] uppercase text-neutral-800 font-medium select-none">
              <span>PERSONAL AI AGENT</span>
              <CornerBox />
            </span>
          </div>

          {/* Subtitle */}
          <p className="font-mono text-xs sm:text-[13px] tracking-[0.06em] sm:tracking-[0.08em] text-neutral-600 leading-relaxed max-w-md">
            Think less about the busywork.
            <br />
            Focus on what matters.
          </p>

          {/* CTA Button */}
          <div className="mt-7 sm:mt-8">
            <Link
              href="/register"
              className="inline-flex items-center justify-center bg-[#171717] text-[#f6f4ef] px-6 sm:px-7 py-3 sm:py-3.5 text-xs sm:text-[13px] font-mono tracking-[0.14em] hover:bg-neutral-800 transition duration-200 shadow-sm"
            >
              Meet your agent &rarr;
            </Link>
          </div>
        </div>
      </section>

      {/* ─── SECOND SECTION: "MORE TIME FOR WHAT MATTERS." (FOLD 2) ─── */}
      <section className="relative w-full max-w-[1360px] mx-auto px-5 sm:px-12 py-16 sm:py-28">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-8 items-start">
          {/* Left Column Content */}
          <div className="lg:col-span-8 flex flex-col items-start gap-5 sm:gap-7">
            <span className="font-mono text-[10px] sm:text-[11px] tracking-[0.22em] sm:tracking-[0.25em] text-neutral-600 uppercase font-medium">
              A LITTLE HELP, EVERY DAY
            </span>

            <h2 className="font-serif text-3xl sm:text-5xl md:text-6xl xl:text-[68px] font-normal leading-[1.08] tracking-tight text-[#171717]">
              More time
              <br />
              for what matters.
            </h2>

            <p className="font-mono text-xs sm:text-[13px] tracking-wide text-neutral-600 leading-relaxed max-w-lg">
              VXYAK helps you capture thoughts, remember what matters,
              and stay on top of your day — all through a
              simple conversation.
            </p>

            {/* Feature Line Tabs - Clean responsive wrap */}
            <div className="pt-2 flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 font-mono text-[11px] sm:text-xs text-neutral-700 tracking-wider">
              <span>Less mental clutter</span>
              <span className="hidden sm:inline text-neutral-400">|</span>
              <span>Instant recall</span>
              <span className="hidden sm:inline text-neutral-400">|</span>
              <span>Life in quiet sync</span>
            </div>

            {/* Action Link */}
            <div className="pt-2 sm:pt-3">
              <Link
                href="/register"
                className="inline-flex items-center gap-1.5 font-mono text-xs sm:text-[13px] tracking-[0.14em] text-[#171717] font-medium border-b border-[#171717] pb-0.5 hover:opacity-70 transition-opacity"
              >
                Meet your agent &rarr;
              </Link>
            </div>
          </div>

          {/* Right Column Quotes */}
          <div className="lg:col-span-4 flex flex-col justify-center pt-8 lg:pt-14 border-t border-neutral-300/40 lg:border-t-0 space-y-6 sm:space-y-8 font-mono text-xs sm:text-[13px] text-neutral-700 tracking-wide">
            <div>
              <p className="leading-relaxed">&ldquo;Remind me to follow up</p>
              <p className="leading-relaxed">tomorrow.&rdquo;</p>
              <div className="w-12 h-[1px] bg-neutral-400/80 mt-5" />
            </div>

            <div>
              <p className="leading-relaxed">&ldquo;Where did I save that</p>
              <p className="leading-relaxed">note from last week?&rdquo;</p>
              <div className="w-12 h-[1px] bg-neutral-400/80 mt-5" />
            </div>

            <div>
              <p className="leading-relaxed">&ldquo;Hold onto this thought</p>
              <p className="leading-relaxed">for me.&rdquo;</p>
            </div>
          </div>
        </div>
      </section>

      {/* ─── FOOTER ─── */}
      <footer className="w-full max-w-[1360px] mx-auto px-6 sm:px-12 mt-8 md:mt-6 font-mono text-[10px] sm:text-[11px] tracking-wider text-neutral-600">
        <div className="w-full pt-4 pb-6 flex flex-col  sm:flex-row item-start sm:items-center justify-between gap-2 sm:gap-4  border-t border-neutral-500/50">
          <div>
            &copy; 2026 Vxyak.
          </div>
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
