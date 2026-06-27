import { Callout } from "@/components/Callout";
import { ChartCard } from "@/components/ChartCard";
import { DataTable } from "@/components/DataTable";
import { Details } from "@/components/Details";
import { Section } from "@/components/Section";
import {
  EventRobustnessChart,
  EventStudyChart,
  LocalProjectionChart,
  QuantileChart,
} from "@/components/charts";
import { LazyRollingBeta } from "@/components/LazyRollingBeta";
import { PANEL_ROBUSTNESS_COLUMNS, REGRESSION_TERM_COLUMNS } from "@/lib/labels";
import type { FrontendBundle, Row } from "@/lib/types";

export function HowMarketsReact({ bundle }: { bundle: FrontendBundle }) {
  const { copy } = bundle;

  return (
    <Section
      id="how-markets-react"
      eyebrow="How markets react to risk"
      title="Do markets look worse around geopolitical-risk shocks?"
      intro={copy.how_to_read["market_response"]}
    >
      <SubSection title="Market response around shock days" idAnchor="market-response">
        <ChartCard
          title="Average cumulative abnormal returns around GPR shock days"
          caption="Day 0 is the shock day. A line dropping below zero after day 0 means ETFs tended to underperform their normal market-model expectation. Bands and p-values live in the details."
        >
          <EventStudyChart rows={bundle.event_study} />
        </ChartCard>
        <Details summary="Details: event-study robustness (different shock cutoffs and windows)">
          <p className="text-xs text-ink-muted">
            This checks whether the conclusion holds when the shock threshold or the post-shock window is changed.
          </p>
          <ChartCard title="Robustness: end-of-window abnormal return">
            <EventRobustnessChart rows={bundle.event_robustness} />
          </ChartCard>
        </Details>
      </SubSection>

      <SubSection title="Regression evidence (controlled panel)" idAnchor="regression">
        <Callout variant="info" title="How to read this">
          {copy.how_to_read["regression"]}
        </Callout>
        <p className="text-xs text-ink-muted">
          The key term is the <em>emerging-market interaction</em>: the extra association between a GPR jump and
          returns for emerging-market ETFs relative to developed-market ETFs. Negative and statistically strong
          would support the idea that emerging markets react more. In the current data, this is not strong.
        </p>
        <div className="grid gap-4 md:grid-cols-2">
          <RegressionBlock title="Baseline model" rows={bundle.regression.baseline} filename="panel_regression_baseline_terms.csv" />
          <RegressionBlock title="With market controls" rows={bundle.regression.controlled} filename="panel_regression_controlled_terms.csv" />
        </div>
        <Details summary="Details: date fixed-effects model and sample robustness">
          <p className="text-xs text-ink-muted">
            The date fixed-effects model absorbs common global shocks, so its interaction is the cleanest version of
            the emerging-market question.
          </p>
          <RegressionBlock title="Date fixed-effects model" rows={bundle.regression.date_fe} filename="panel_regression_date_fe_terms.csv" />
          <h4 className="text-sm font-semibold text-ink">Sample robustness - excluding crisis windows</h4>
          <p className="text-xs text-ink-muted">
            Large sign or p-value changes would warn that one episode is driving the result.
          </p>
          <DataTable
            rows={bundle.panel_sample_robustness}
            columns={PANEL_ROBUSTNESS_COLUMNS}
            downloadFilename="panel_sample_robustness.csv"
          />
        </Details>
      </SubSection>

      <SubSection title="Downside risk - is the link stronger on bad days?" idAnchor="downside-risk">
        <Callout variant="info" title="How to read this">
          {copy.how_to_read["downside_risk"]}
        </Callout>
        <ChartCard
          title="GPR coefficients across return percentiles"
          caption="Lower percentiles describe worse return days. A more negative line on the left suggests stronger downside association, but p-values still determine strength."
        >
          <QuantileChart rows={bundle.quantile_regression} />
        </ChartCard>
      </SubSection>

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

      <SubSection title="Country sensitivity over time" idAnchor="country-sensitivity">
        <Callout variant="info" title="How to read this">
          {copy.how_to_read["country_sensitivity"]}
        </Callout>
        <ChartCard
          title="Rolling GPR sensitivity by country ETF"
          caption="Each line shows how one country ETF's return sensitivity to GPR changes as the estimation window moves through time. Use it as a diagnostic, not a stable country ranking."
        >
          <LazyRollingBeta />
        </ChartCard>
      </SubSection>
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
