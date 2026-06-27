"use client";

import { useEffect, useState } from "react";

import { SectionNav } from "@/components/SectionNav";
import { Overview } from "@/sections/Overview";
import { HowMarketsReact } from "@/sections/HowMarketsReact";
import { PredictionLab } from "@/sections/PredictionLab";
import { DataAndMethods } from "@/sections/DataAndMethods";
import { loadBundle } from "@/lib/data";
import { num } from "@/lib/format";
import type { FrontendBundle } from "@/lib/types";

type State =
  | { status: "loading" }
  | { status: "ready"; bundle: FrontendBundle }
  | { status: "error"; message: string };

export default function Page() {
  const [state, setState] = useState<State>({ status: "loading" });

  useEffect(() => {
    let active = true;
    loadBundle()
      .then((bundle) => {
        if (active) setState({ status: "ready", bundle });
      })
      .catch((error: unknown) => {
        if (active) {
          const message = error instanceof Error ? error.message : "Failed to load dashboard data.";
          setState({ status: "error", message });
        }
      });
    return () => {
      active = false;
    };
  }, []);

  if (state.status === "loading") {
    return (
      <div className="mx-auto max-w-6xl px-4 py-20 text-center text-ink-muted">Loading dashboard...</div>
    );
  }

  if (state.status === "error") {
    return (
      <div className="mx-auto max-w-6xl px-4 py-20 text-center">
        <h1 className="text-xl font-semibold text-ink">Could not load the dashboard</h1>
        <p className="mt-2 text-sm text-ink-muted">{state.message}</p>
        <p className="mt-4 text-sm text-ink-soft">
          Run the exporter first: <code className="rounded bg-surface-alt px-1.5 py-0.5">python scripts/export_frontend_data.py</code>
        </p>
      </div>
    );
  }

  const { bundle } = state;

  if (!bundle.manifest.available) {
    return <MissingData bundle={bundle} />;
  }

  return (
    <main className="overflow-x-hidden">
      <Hero bundle={bundle} />
      <SectionNav />
      <Overview bundle={bundle} />
      <div className="border-t border-surface-border" />
      <HowMarketsReact bundle={bundle} />
      <div className="border-t border-surface-border" />
      <PredictionLab bundle={bundle} />
      <div className="border-t border-surface-border" />
      <DataAndMethods bundle={bundle} />
      <footer className="border-t border-surface-border py-8 text-center text-xs text-ink-muted">
        GPR Equity Observatory - a research observatory. Not investment advice or a trading system.
      </footer>
    </main>
  );
}

function Hero({ bundle }: { bundle: FrontendBundle }) {
  const { copy, manifest, overview } = bundle;
  const headline = overview.headline;

  return (
    <header className="border-b border-surface-border bg-[linear-gradient(180deg,#f8fafc_0%,#ffffff_72%)]">
      <div className="mx-auto grid max-w-6xl gap-6 px-4 py-8 lg:grid-cols-[1.4fr_0.8fr] lg:py-10">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wider text-accent">v5 unified Next.js app</p>
          <h1 className="mt-2 text-3xl font-bold text-ink sm:text-4xl">GPR Equity Observatory</h1>
          <p className="mt-3 max-w-3xl text-base leading-relaxed text-ink-soft">{copy.intro}</p>
          <div className="mt-4 rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-ink-soft">
            <span className="font-semibold text-amber-700">Research boundary:</span> {copy.use_note}
          </div>
          <p className="mt-3 text-xs text-ink-muted">
            Last built {manifest.build_date}. Data range {headline.start_date} to {headline.end_date}.
          </p>
        </div>
        <div className="grid min-w-0 gap-3 sm:grid-cols-2 lg:grid-cols-1">
          <HeroStat label="Countries" value={num(headline.country_count, "n/a")} />
          <HeroStat label="GPR shock days" value={num(headline.shock_count, "n/a")} />
          <HeroStat label="Monthly benchmark" value={manifest.monthly_mode ?? "not exported"} />
        </div>
      </div>
    </header>
  );
}

function HeroStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-surface-border bg-surface/95 p-4 shadow-sm">
      <div className="text-xs font-semibold uppercase tracking-wide text-ink-muted">{label}</div>
      <div className="mt-1 break-words text-xl font-semibold text-ink tabular-nums">{value}</div>
    </div>
  );
}

function MissingData({ bundle }: { bundle: FrontendBundle }) {
  const missing = bundle.manifest.missing_files ?? [];
  return (
    <main className="mx-auto max-w-3xl overflow-x-hidden px-4 py-20">
      <h1 className="text-2xl font-semibold text-ink">GPR Equity Observatory</h1>
      <p className="mt-2 text-sm text-ink-soft">{bundle.copy.intro || "A research observatory studying geopolitical risk and equity markets."}</p>
      <div className="mt-6 rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm">
        <p className="font-semibold text-amber-700">Processed data is not available yet.</p>
        <p className="mt-1 text-ink-soft">Build the pipeline first, then export the frontend data:</p>
        <pre className="mt-2 overflow-x-auto rounded bg-surface-alt p-2 text-xs">{`python scripts/build_all.py\npython scripts/export_frontend_data.py\ncd frontend\nnpm run dev`}</pre>
        {missing.length > 0 ? (
          <details className="mt-3">
            <summary className="cursor-pointer text-xs text-ink-muted">Missing files ({missing.length})</summary>
            <ul className="mt-2 list-disc pl-4 text-xs text-ink-muted">
              {missing.slice(0, 20).map((path) => (
                <li key={path}>{path}</li>
              ))}
            </ul>
          </details>
        ) : null}
      </div>
    </main>
  );
}
