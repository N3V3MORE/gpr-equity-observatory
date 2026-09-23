import { ResearchDashboard } from "@/components/ResearchDashboard";

export default function Page() {
  return (
    <>
      <a
        href="#research-content"
        className="sr-only rounded bg-surface px-4 py-3 font-semibold text-accent focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:ring-2 focus:ring-accent"
      >
        Skip to research findings
      </a>
      <header className="border-b border-surface-border bg-[linear-gradient(180deg,#f8fafc_0%,#ffffff_72%)]">
        <div className="mx-auto max-w-6xl px-4 py-8 sm:py-10">
          <p className="text-xs font-semibold uppercase tracking-wider text-accent">GPR Equity Observatory</p>
          <h1 className="mt-3 max-w-4xl text-3xl font-bold leading-tight text-ink sm:text-4xl">
            How are geopolitical risk jumps associated with returns in developed and emerging equity markets?
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-relaxed text-ink-soft">
            Daily geopolitical-risk data and country ETF returns, examined through event studies and panel regressions.
            Read the current snapshot, its key evidence, and the methods behind it.
          </p>
          <p className="mt-4 max-w-4xl rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-sm leading-relaxed text-ink-soft">
            <strong className="text-amber-700">Research limitations:</strong> USD-traded country ETFs are proxies for equity markets.
            Estimates describe associations, not causal effects. Event-study inference does not adjust for dependence
            between ETFs exposed to common events. This is not investment advice.
          </p>
          <div className="mt-5 flex flex-wrap gap-x-6 gap-y-3 text-sm font-semibold">
            <a className="rounded text-accent underline underline-offset-4 focus:outline-none focus:ring-2 focus:ring-accent" href="https://github.com/N3V3MORE/gpr-equity-observatory">
              Research code
            </a>
            <a className="rounded text-accent underline underline-offset-4 focus:outline-none focus:ring-2 focus:ring-accent" href="https://github.com/N3V3MORE/gpr-equity-observatory/blob/main/reports/RESULTS_BRIEF.md">
              Results brief
            </a>
            <a className="rounded text-accent underline underline-offset-4 focus:outline-none focus:ring-2 focus:ring-accent" href="#data-and-methods">
              Data, methods &amp; downloads
            </a>
          </div>
        </div>
      </header>
      <main id="research-content" tabIndex={-1} className="overflow-x-hidden focus:outline-none">
        <ResearchDashboard />
      </main>
      <footer className="border-t border-surface-border px-4 py-8 text-center text-xs text-ink-muted">
        GPR Equity Observatory · Research evidence and uncertainty, not a trading system.
      </footer>
    </>
  );
}
