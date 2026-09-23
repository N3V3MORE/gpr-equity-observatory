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

export function Overview({ bundle }: { bundle: FrontendBundle }) {
  const { copy, overview, gpr_timeline, evidence_map, group_returns } = bundle;
  const headline = overview.headline;
  const readerPath = copy.reader_path ?? [];

  return (
    <Section
      id="overview"
      eyebrow="Overview"
      title="The big picture"
      intro={copy.intro}
    >
      <Callout variant="info" title="The one question this dashboard tries to answer">
        {copy.central_question}
      </Callout>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Countries" value={num(headline.country_count, "n/a")} hint="Country ETFs in the daily panel" />
        <MetricCard label="Start date" value={headline.start_date || "n/a"} />
        <MetricCard label="End date" value={headline.end_date || "n/a"} />
        <MetricCard label="Flagged GPR shock days" value={num(headline.shock_count, "n/a")} hint="Flagged dates within the displayed panel coverage" />
      </div>
      <p className="text-xs text-ink-muted">{overview.definitions.shock_days}</p>

      <Callout variant="warning" title="What this is - and is not">
        <p className="font-medium">{copy.main_takeaway}</p>
        <p className="mt-1 text-ink-soft">{copy.use_note}</p>
      </Callout>

      <div className="grid gap-4 md:grid-cols-2">
        {copy.job_statements.map((job) => (
          <div key={job.title} className="rounded-lg border border-surface-border bg-surface p-4">
            <div className="text-xs font-semibold uppercase tracking-wide text-accent">{job.title}</div>
            <div className="mt-1 text-sm text-ink-soft">{job.body}</div>
          </div>
        ))}
      </div>

      <div>
        <h3 className="text-sm font-semibold text-ink">Read this first</h3>
        <div className="mt-3 grid gap-3 md:grid-cols-3">
          {readerPath.map((item) => (
            <div key={item.step} className="rounded-lg border border-surface-border bg-surface p-4">
              <div className="flex items-start gap-3">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent text-sm font-semibold text-white">
                  {item.step}
                </div>
                <div className="min-w-0">
                  <div className="text-sm font-semibold text-ink">{item.title}</div>
                  <p className="mt-1 text-sm leading-relaxed text-ink-soft">{item.body}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <ChartCard
        title="Daily geopolitical risk over time"
        caption={overview.definitions.largest_jumps}
      >
        <GprTimelineChart series={gpr_timeline.series} topShocks={gpr_timeline.top_shocks} />
      </ChartCard>

      <div>
        <h3 className="text-sm font-semibold text-ink">Method map - how each part answers the question</h3>
        <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {copy.method_map.map((row) => (
            <div key={row.Tool} className="rounded-lg border border-surface-border bg-surface p-4">
              <div className="text-xs font-semibold uppercase tracking-wide text-ink-muted">{row.Tool}</div>
              <div className="mt-1 text-sm font-medium text-ink">{row.Question}</div>
              <div className="mt-2 text-xs text-ink-soft">Looks at: {row.Output}</div>
              <div className="mt-1 text-xs text-ink-muted">{row["What to look for"]}</div>
            </div>
          ))}
        </div>
      </div>

      <OptionalDataset status={bundle.dataset_status.group_returns} label="Cumulative returns">
        <Details summary="Details: cumulative average returns by market group">
        <ChartCard
          title="Cumulative average ETF returns"
          caption="Developed vs emerging market ETFs, cumulative average log returns over the sample. This is descriptive context, not a risk result."
        >
          <CumulativeReturnsChart rows={group_returns} />
        </ChartCard>
        </Details>
      </OptionalDataset>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="min-w-0 lg:col-span-2">
          <h3 className="text-sm font-semibold text-ink">Evidence map - what each method concludes, in plain English</h3>
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
        </div>
        <div className="space-y-4">
          <Callout variant="info" title="What this snapshot supports">
            <ul className="list-disc space-y-1 pl-4">
              {copy.current_answer_points.map((point) => (
                <li key={point}>{point}</li>
              ))}
            </ul>
          </Callout>
          <Callout variant="danger" title="What this does not prove">
            <ul className="list-disc space-y-1 pl-4">
              {copy.does_not_prove_points.map((point) => (
                <li key={point}>{point}</li>
              ))}
            </ul>
          </Callout>
        </div>
      </div>

      {gpr_timeline.top_shocks.length > 0 ? (
        <div>
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
        </div>
      ) : null}
      <Details summary="Details: flagged shock days and selected event dates">
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
