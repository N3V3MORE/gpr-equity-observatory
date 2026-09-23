import { Callout } from "@/components/Callout";
import { ChartCard } from "@/components/ChartCard";
import { DataTable } from "@/components/DataTable";
import { Details } from "@/components/Details";
import { OptionalDataset } from "@/components/OptionalDataset";
import { Section } from "@/components/Section";
import {
  EventRobustnessChart,
  EventStudyChart,
  LocalProjectionChart,
  QuantileChart,
} from "@/components/charts";
import { LazyRollingBeta } from "@/components/LazyRollingBeta";
import {
  EVENT_STUDY_COLUMNS,
  MARKET_REACTION_READER_COLUMNS,
  PANEL_ROBUSTNESS_COLUMNS,
  REGRESSION_TERM_COLUMNS,
  REGRESSION_TRANSLATION_COLUMNS,
} from "@/lib/labels";
import type { FrontendBundle, Row } from "@/lib/types";

export function HowMarketsReact({ bundle }: { bundle: FrontendBundle }) {
  const { copy } = bundle;
  const definitions = bundle.overview.definitions;
  const eventDefinitions = [
    { definition: "Event-day alignment", detail: definitions.event_alignment },
    { definition: "Accumulation window", detail: definitions.accumulation },
    { definition: "Inference limitation", detail: definitions.inference },
    { definition: "Return units", detail: definitions.return_units },
  ];

  return (
    <Section
      id="how-markets-react"
      eyebrow="How markets react to risk"
      title="Do markets look worse around geopolitical-risk shocks?"
      intro={copy.how_to_read["market_response"]}
    >
      <SubSection title="Market response around selected GPR events" idAnchor="market-response">
        <ChartCard
          title="Average cumulative abnormal returns around selected GPR events"
          caption="The cumulative path includes pre-event trading days; it is not a day-0-onward return. Values below zero describe cumulative underperformance relative to the fitted market model over the included window. No confidence bands are shown."
        >
          <EventStudyChart rows={bundle.event_study} />
        </ChartCard>
        <p className="text-xs text-ink-muted">{bundle.overview.definitions.event_alignment}</p>
        <Callout variant="warning" title="Event-study uncertainty">
          {bundle.overview.definitions.inference} Weak evidence is not proof of no effect.
        </Callout>
        <div>
          <h4 className="text-sm font-semibold text-ink">Readable event-study summary</h4>
          <p className="mt-1 text-xs text-ink-muted">
            These checkpoints come from this snapshot. The cumulative window begins before the event;
            the endpoint is a relative trading day, not the number of days accumulated from day 0.
          </p>
          <div className="mt-3">
            <DataTable
              rows={bundle.reader_summaries.market_reaction}
              columns={MARKET_REACTION_READER_COLUMNS}
              downloadFilename="market_reaction_summary.csv"
              compact
            />
          </div>
        </div>
        <Details summary="Details: event-study estimates, uncertainty, counts, and windows">
          <DataTable
            rows={eventDefinitions}
            columns={[{ key: "definition", label: "Definition" }, { key: "detail", label: "Published snapshot definition" }]}
            downloadFilename="event_study_definitions.csv"
            downloadLabel="Download event-study definitions (CSV)"
            compact
          />
          <p>
            One basis point is 0.01 percentage points of log return.
            {" "}
            Standard errors, t-statistics, and p-values refer to cumulative abnormal returns.
            Observation counts are ETF-event rows with a daily abnormal return; event counts are distinct
            event dates represented at that relative day. Counts can change across the window.
          </p>
          <DataTable
            rows={bundle.event_study}
            columns={EVENT_STUDY_COLUMNS}
            downloadFilename="event_study_inference.csv"
            downloadLabel="Download event-study estimates and inference (CSV)"
            compact
          />
        </Details>
        <OptionalDataset status={bundle.dataset_status.event_robustness} label="Event-study robustness">
          <Details summary="Details: event-study robustness (different shock cutoffs and windows)">
          <p className="text-xs text-ink-muted">
            This checks sensitivity to the shock threshold and the symmetric window around the event.
            Each endpoint includes the pre-event side of its window.
          </p>
          <ChartCard title="Robustness: cumulative abnormal return across the full event window">
            <EventRobustnessChart rows={bundle.event_robustness} />
          </ChartCard>
          </Details>
        </OptionalDataset>
      </SubSection>

      <SubSection title="Regression evidence (controlled panel)" idAnchor="regression">
        <Callout variant="info" title="How to read this">
          {copy.how_to_read["regression"]}
        </Callout>
        <p className="text-xs text-ink-muted">
          The key term is the <em>emerging-market interaction</em>: the extra association between a GPR jump and
          returns for emerging-market ETFs relative to developed-market ETFs. Read its estimate and uncertainty
          in the published snapshot below. A negative sign alone does not establish a reliable difference.
          These are associations for USD-traded country ETF proxies, not causal effects on local equity markets.
        </p>
        <div>
          <h4 className="text-sm font-semibold text-ink">Regression translation table</h4>
          <p className="mt-1 text-xs text-ink-muted">
            Start here before reading coefficient rows. The labels are cautious because these models show
            association, not cause and effect.
          </p>
          <div className="mt-3">
            <DataTable
              rows={bundle.reader_summaries.regression_translation}
              columns={REGRESSION_TRANSLATION_COLUMNS}
              downloadFilename="regression_translation.csv"
              compact
            />
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <RegressionBlock title="Baseline model" rows={bundle.regression.baseline} filename="panel_regression_baseline_terms.csv" />
          <RegressionBlock title="With market controls" rows={bundle.regression.controlled} filename="panel_regression_controlled_terms.csv" />
        </div>
        <Details summary="Details: date fixed-effects model and sample robustness">
          <p className="text-xs text-ink-muted">
            The date fixed-effects model absorbs common date-level variation. Its interaction describes a
            conditional developed-versus-emerging association, not a causal effect.
          </p>
          <RegressionBlock title="Date fixed-effects model" rows={bundle.regression.date_fe} filename="panel_regression_date_fe_terms.csv" />
          <OptionalDataset status={bundle.dataset_status.panel_sample_robustness} label="Sample robustness">
            <h4 className="text-sm font-semibold text-ink">Sample robustness - excluding crisis windows</h4>
          <p className="text-xs text-ink-muted">
            Large sign or p-value changes can indicate sensitivity to an episode. Retaining the same sign
            after exclusions does not establish a robust GPR effect; magnitude and uncertainty still matter.
          </p>
          <DataTable
            rows={bundle.panel_sample_robustness}
            columns={PANEL_ROBUSTNESS_COLUMNS}
            downloadFilename="panel_sample_robustness.csv"
          />
          </OptionalDataset>
        </Details>
      </SubSection>

      <OptionalDataset status={bundle.dataset_status.quantile_regression} label="Downside risk">
        <SubSection title="Downside risk - is the link stronger on bad days?" idAnchor="downside-risk">
        <Callout variant="info" title="How to read this">
          {copy.how_to_read["downside_risk"]}
        </Callout>
        <ChartCard
          title="GPR coefficients across return percentiles"
          caption="Lower percentiles describe worse return days. A more negative estimate on the left is a descriptive downside association. This chart does not display inference and cannot establish its statistical strength."
        >
          <QuantileChart rows={bundle.quantile_regression} />
        </ChartCard>
        </SubSection>
      </OptionalDataset>

      <OptionalDataset status={bundle.dataset_status.local_projections} label="Dynamic response">
        <SubSection title="Dynamic response - how long does the reaction last?" idAnchor="dynamic-response">
        <Callout variant="info" title="How to read this">
          {copy.how_to_read["dynamic_response"]}
        </Callout>
        <ChartCard
          title="Estimated response after a GPR shock (local projections)"
          caption="Each point estimates the cumulative abnormal-return response at a later horizon. Dashed lines are the 95% confidence bounds; bands crossing zero indicate weak evidence at that horizon."
        >
          <LocalProjectionChart rows={bundle.local_projections} />
        </ChartCard>
        </SubSection>
      </OptionalDataset>

      {bundle.dataset_status.rolling_beta !== "excluded" ? (
        <SubSection title="Country sensitivity over time" idAnchor="country-sensitivity">
        <Callout variant="info" title="How to read this">
          {copy.how_to_read["country_sensitivity"]}
        </Callout>
        <ChartCard
          title="Rolling GPR sensitivity by country ETF"
          caption="Each line shows how one country ETF's return sensitivity to GPR changes as the estimation window moves through time. Use it as a diagnostic, not a stable country ranking."
        >
          <LazyRollingBeta manifest={bundle.manifest} status={bundle.dataset_status.rolling_beta} />
        </ChartCard>
        </SubSection>
      ) : null}
    </Section>
  );
}

function SubSection({ title, idAnchor, children }: { title: string; idAnchor: string; children: React.ReactNode }) {
  return (
    <div id={idAnchor} className="scroll-mt-24 space-y-4">
      <h3 className="text-lg font-semibold text-ink">{title}</h3>
      {children}
    </div>
  );
}

// Local helper for regression blocks.

function RegressionBlock({ title, rows, filename }: { title: string; rows: Row[]; filename: string }) {
  return (
    <div>
      <h4 className="text-sm font-semibold text-ink">{title}</h4>
      <div className="mt-2">
        <DataTable rows={rows} columns={REGRESSION_TERM_COLUMNS} downloadFilename={filename} compact />
      </div>
    </div>
  );
}
