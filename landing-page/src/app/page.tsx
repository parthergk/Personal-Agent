export default function Home() {
  return (
    <main className="relative isolate min-h-svh w-full overflow-x-hidden bg-[#f6f4ef] text-[#171717] flex flex-col justify-between">
      {/* Decorative background */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 -z-10"
        style={{
          backgroundImage: "url('/bg.png')",
          backgroundRepeat: "no-repeat",
          backgroundPosition: "top center",
          backgroundSize: "cover",
        }}
      />

      {/* ─── TOP NAVIGATION ─── */}
      <header className="w-full max-w-[1360px] mx-auto px-5 sm:px-12 pt-6 sm:pt-10 flex items-center justify-between text-[11px] sm:text-xs font-mono tracking-[0.16em] sm:tracking-[0.25em] font-medium uppercase z-20">
        <div className="flex items-center gap-2">
          <span>MUSE / PERSONAL AGENT</span>
        </div>
        <nav className="flex items-center gap-5 sm:gap-12">
          <a href="#about" className="hover:opacity-60 transition-opacity">
            ABOUT
          </a>
          <a href="#login" className="hover:opacity-60 transition-opacity">
            LOG IN
          </a>
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
        <div className="flex flex-col items-center text-center max-w-2xl mt-10 sm:mt-8 px-2">
          {/* Main Headline */}
          <h1 className="font-serif text-5xl sm:text-6xl md:text-7xl xl:text-[84px] font-normal leading-[1.08] tracking-tight text-[#171717] break-words">
            Your world,
            <br />
            in quiet sync.
          </h1>

          {/* Badge */}
          <div className="mt-6 sm:mt-8 mb-5 sm:mb-6">
            <span className="inline-block border border-neutral-400/80 bg-[#f6f4ef]/60 backdrop-blur-[2px] px-5 sm:px-6 py-2 text-[10px] sm:text-xs font-mono tracking-[0.2em] sm:tracking-[0.28em] uppercase text-neutral-800 font-medium">
              PERSONAL AI AGENT
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
            <a
              href="#agent"
              className="inline-flex items-center justify-center bg-[#171717] text-[#f6f4ef] px-6 sm:px-7 py-3 sm:py-3.5 text-xs sm:text-[13px] font-mono tracking-[0.14em] hover:bg-neutral-800 transition duration-200 shadow-sm"
            >
              Meet your agent &rarr;
            </a>
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
              MUSE understands your context and helps you move
              through everyday tasks — from organizing plans to
              handling the busywork.
            </p>

            {/* Feature Line Tabs - Clean responsive wrap */}
            <div className="pt-2 flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 font-mono text-[11px] sm:text-xs text-neutral-700 tracking-wider">
              <span>Remember what matters</span>
              <span className="hidden sm:inline text-neutral-400">|</span>
              <span>Plan your next step</span>
              <span className="hidden sm:inline text-neutral-400">|</span>
              <span>Take care of routine tasks</span>
            </div>

            {/* Action Link */}
            <div className="pt-2 sm:pt-3">
              <a
                href="#agent"
                className="inline-flex items-center gap-1.5 font-mono text-xs sm:text-[13px] tracking-[0.14em] text-[#171717] font-medium border-b border-[#171717] pb-0.5 hover:opacity-70 transition-opacity"
              >
                Meet your agent &rarr;
              </a>
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
              <p className="leading-relaxed">&ldquo;Help me plan my week.&rdquo;</p>
              <div className="w-12 h-[1px] bg-neutral-400/80 mt-5" />
            </div>

            <div>
              <p className="leading-relaxed">&ldquo;Take care of the little</p>
              <p className="leading-relaxed">things.&rdquo;</p>
            </div>
          </div>
        </div>
      </section>

      {/* ─── FOOTER ─── */}
      <footer className="w-full max-w-[1360px] mx-auto px-6 sm:px-12 py-8 flex flex-col sm:flex-row items-center justify-between gap-4 font-mono text-[10px] sm:text-[11px] tracking-wider text-neutral-600 border-t border-neutral-300/40">
        <div>
          &copy; 2026 Muse. All rights reserved.
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
      </footer>
    </main>
  );
}
