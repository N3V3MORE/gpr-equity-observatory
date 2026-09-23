import type { Metadata } from "next";
import { ResearchDashboard } from "@/components/ResearchDashboard";
import { publicPath } from "@/lib/paths";

export const metadata: Metadata = {
  title: "Local exploration | GPR Equity Observatory",
  robots: { index: false, follow: false },
};

export default function LocalPage() {
  return (
    <>
      <header className="mx-auto max-w-6xl px-4 py-8">
        <a className="text-sm text-accent underline underline-offset-4" href={publicPath("")}>Public research presentation</a>
        <h1 className="mt-3 text-3xl font-bold text-ink">Local research exploration</h1>
        <p className="mt-3 max-w-3xl text-sm leading-relaxed text-ink-soft">
          Extended diagnostics, Prediction Lab, and monthly benchmarks are available here when included in a local snapshot.
          Sample demonstrations validate software behavior and are not empirical evidence. Local outputs are not approved public findings.
        </p>
        <div className="mt-4 flex flex-wrap gap-5 text-sm text-accent underline underline-offset-4">
          <a href="https://github.com/N3V3MORE/gpr-equity-observatory">Research code</a>
          <a href="https://github.com/N3V3MORE/gpr-equity-observatory/blob/main/reports/RESULTS_BRIEF.md">Results brief</a>
        </div>
      </header>
      <main className="overflow-x-hidden"><ResearchDashboard local /></main>
    </>
  );
}
