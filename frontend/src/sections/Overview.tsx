import { Callout } from "@/components/Callout";
import { ChartCard } from "@/components/ChartCard";
import { DataTable } from "@/components/DataTable";
import { Details } from "@/components/Details";
import { MetricCard } from "@/components/MetricCard";
import { OptionalDataset } from "@/components/OptionalDataset";
import { Section } from "@/components/Section";
import { GprTimelineChart, CumulativeReturnsChart } from "@/components/charts";
import { EVIDENCE_MAP_COLUMNS, SELECTED_EVENT_COLUMNS, TOP_SHOCKS_COLUMNS } from "@/lib/labels";
import { num } from "@/lib/format";
import type { FrontendBundle } from "@/lib/types";

export function Overview({ bundle, local = false }: { bundle: FrontendBundle; local?: boolean }) {
  const { copy, overview, gpr_timeline, evidence_map, group_returns } = bundle;
  const headline = overview.headline;
  const approved = bundle.manifest.publication_status === "approved";
  const answer = (
    <ul className="list-disc space-y-2 pl-4">
      {copy.current_answer_points.map((point) => <li key={point}>{point}</li>)}
    </ul>
  );

  return (
    <Section
      id="overview"
      eyebrow={approved ? "Current answer" : "Snapshot for review"}
      title={approved ? "What this snapshot supports" : "Candidate snapshot"}
    >
      {approved ? <Callout variant="info">{answer}</Callout> : (
        <>
          <p className="max-w-3xl text-sm text-ink-soft">
            A reviewed public answer is not available yet. The estimates below are available for review.
          </p>
          <Details summary="Candidate estimates">{answer}</Details>
        </>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Countries" value={num(headline.country_count, "n/a")} hint="Country ETFs in the daily panel" />
        <MetricCard label="Data through" value={headline.end_date || "n/a"} hint={`Panel begins ${headline.start_date}`} />
        <MetricCard label="Snapshot exported" value={bundle.manifest.build_date || "n/a"} hint="Export date, not the last data observation" />
        <MetricCard label="Flagged GPR shock days" value={num(headline.shock_count, "n/a")} hint="Flagged dates within the displayed panel coverage" />
      </div>

      <ChartCard
        title="Daily geopolitical risk over time"
        caption={overview.definitions.largest_jumps}
      >
        <GprTimelineChart series={gpr_timeline.series} topShocks={gpr_timeline.top_shocks} />
      </ChartCard>

      {local ? <OptionalDataset status={bundle.dataset_status.group_returns} label="Cumulative returns">
        <Details summary="Details: cumulative average returns by market group">
        <ChartCard
          title="Cumulative average ETF returns"
          caption="Developed vs emerging market ETFs, cumulative average log returns over the sample. This is descriptive context, not a risk result."
        >
          <CumulativeReturnsChart rows={group_returns} />
        </ChartCard>
        </Details>
      </OptionalDataset> : null}

      {local ? <OptionalDataset status={bundle.dataset_status.evidence_map} label="Evidence map">
        <Details summary="Details: evidence across all local methods">
          <p className="mt-1 text-xs text-ink-muted">
            These estimates and takeaways describe this snapshot. Weak evidence is not proof of no effect;
            exploratory metrics and sign stability do not establish a robust effect.
          </p>
          <div className="mt-3">
            <DataTable
              rows={evidence_map}
              columns={EVIDENCE_MAP_COLUMNS}
              downloadFilename="evidence_map.csv"
              downloadLabel="Download evidence map (CSV)"
            />
          </div>
        </Details>
      </OptionalDataset> : null}

      {gpr_timeline.top_shocks.length > 0 ? (
        <Details summary="Details: largest GPR jumps within panel coverage">
          <h3 className="text-sm font-semibold text-ink">Largest GPR jumps within panel coverage</h3>
          <div className="mt-3">
            <DataTable
              rows={gpr_timeline.top_shocks}
              columns={TOP_SHOCKS_COLUMNS}
              downloadFilename="top_gpr_shocks.csv"
              downloadLabel="Download largest GPR jumps (CSV)"
              compact
            />
          </div>
        </Details>
      ) : null}
      <Details summary="Details: flagged shock days and selected event dates">
        <p>{overview.definitions.shock_days}</p>
        <p>{overview.definitions.selected_events}</p>
        <p>
          Selected event dates within panel coverage: <strong>{num(headline.selected_event_count)}</strong>.
          {" "}Dates represented in the recorded abnormal-return windows within that coverage:
          {" "}<strong>{num(headline.represented_event_count, "unavailable")}</strong>.
          Selection does not guarantee usable return or market-model estimation data for every ETF.
        </p>
        <DataTable
          rows={gpr_timeline.selected_events}
          columns={SELECTED_EVENT_COLUMNS}
          downloadFilename="selected_event_dates.csv"
          downloadLabel="Download selected event dates (CSV)"
          emptyMessage="No event dates were selected within this snapshot's panel coverage."
          compact
        />
      </Details>
    </Section>
  );
}
