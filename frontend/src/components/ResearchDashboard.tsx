"use client";

import { useEffect, useState } from "react";

import { SectionNav } from "@/components/SectionNav";
import { Overview } from "@/sections/Overview";
import { HowMarketsReact } from "@/sections/HowMarketsReact";
import { PredictionLab } from "@/sections/PredictionLab";
import { DataAndMethods } from "@/sections/DataAndMethods";
import { loadBundle } from "@/lib/data";
import type { FrontendBundle } from "@/lib/types";

type State =
  | { status: "loading" }
  | { status: "ready"; bundle: FrontendBundle }
  | { status: "error" };

export function ResearchDashboard({ local = false }: { local?: boolean }) {
  const [state, setState] = useState<State>({ status: "loading" });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    loadBundle(local ? { localOnly: true } : { publicOnly: true })
      .then((bundle) => {
        if (active) setState({ status: "ready", bundle });
      })
      .catch(() => {
        if (active) setState({ status: "error" });
      });
    return () => {
      active = false;
    };
  }, [local, attempt]);

  if (state.status === "loading") {
    return (
      <div role="status" aria-live="polite" className="mx-auto max-w-6xl px-4 py-12 text-sm text-ink-muted">
        Loading the research snapshot and checking its required evidence…
      </div>
    );
  }

  if (state.status === "error") {
    return (
      <div role="alert" className="mx-auto max-w-6xl px-4 py-12">
        <h2 className="text-xl font-semibold text-ink">{local ? "Local exploration unavailable" : "Research snapshot unavailable"}</h2>
        <p className="mt-2 max-w-2xl text-sm text-ink-soft">
          {local
            ? "Extended views need a valid local research snapshot. They are unavailable for a public-only snapshot."
            : "Required research data could not be loaded or validated. No findings are shown from an incomplete snapshot."}
          {" "}The research code and results brief remain available above.
        </p>
        <button
          type="button"
          className="mt-4 rounded border border-accent px-4 py-2 text-sm font-semibold text-accent hover:bg-accent-soft focus:outline-none focus:ring-2 focus:ring-accent"
          onClick={() => {
            setState({ status: "loading" });
            setAttempt((value) => value + 1);
          }}
        >
          Try loading again
        </button>
      </div>
    );
  }

  const { bundle } = state;
  if (!bundle.manifest.available) {
    return (
      <div role="status" className="mx-auto max-w-6xl px-4 py-12">
        <h2 className="text-xl font-semibold text-ink">Research findings are not available yet</h2>
        <p className="mt-2 max-w-2xl text-sm text-ink-soft">
          No research snapshot is available here. The introduction describes the study; it does not report empirical findings.
          You can read the research code and results brief above.
        </p>
      </div>
    );
  }

  return (
    <>
      <SectionNav
        prediction={local && bundle.dataset_status.prediction_summary !== "excluded"}
        rolling={local && bundle.dataset_status.rolling_beta !== "excluded"}
      />
      <Overview bundle={bundle} local={local} />
      <div className="border-t border-surface-border" />
      <HowMarketsReact bundle={bundle} local={local} />
      <div className="border-t border-surface-border" />
      {local && bundle.dataset_status.prediction_summary !== "excluded" ? (
        <>
          <PredictionLab bundle={bundle} />
          <div className="border-t border-surface-border" />
        </>
      ) : null}
      <DataAndMethods bundle={bundle} local={local} />
    </>
  );
}
