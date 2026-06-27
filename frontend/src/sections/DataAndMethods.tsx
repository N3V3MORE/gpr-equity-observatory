import { Callout } from "@/components/Callout";
import { ChartCard } from "@/components/ChartCard";
import { DataTable } from "@/components/DataTable";
import { Details } from "@/components/Details";
import { Glossary } from "@/components/Glossary";
import { MetricCard } from "@/components/MetricCard";
import { Section } from "@/components/Section";
import {
  MonthlyForecastChart,
  MonthlyGprChart,
  MonthlySpreadChart,
} from "@/components/charts";
import {
  COUNTRY_COVERAGE_COLUMNS,
  LARGE_RETURNS_COLUMNS,
  MONTHLY_FORECAST_COLUMNS,
  MONTHLY_PROVENANCE_COLUMNS,
  MONTHLY_REGRESSION_COLUMNS,
} from "@/lib/labels";
import { num } from "@/lib/format";
import type { FrontendBundle } from "@/lib/types";

export function DataAndMethods({ bundle }: { bundle: FrontendBundle }) {
  const { copy, country_coverage, large_returns, monthly } = bundle;
  const notices = copy.monthly_notices;

  return (
    <Section
      id="data-and-methods"
      eyebrow="Data & methods"
      title="What's underneath, and what to watch out for"
      intro="These are checks on the research inputs and the separate monthly benchmark - not standalone findings."
    >
      <SubSection title="Data quality and coverage">
        <div className="grid gap-4 sm:grid-cols-2">
          <MetricCard label="Countries checked" value={num(country_coverage.length, "n/a")} />
          <MetricCard label="Large-return flags" value={num(large_returns.length, "n/a")} hint="Unusually large daily returns worth manual review" />
        </div>
        <Details summary="Details: country coverage" defaultOpen>
          <DataTable
            rows={country_coverage}
            columns={COUNTRY_COVERAGE_COLUMNS}
            downloadFilename="country_coverage.csv"
            downloadLabel="Download country coverage (CSV)"
          />
        </Details>
        <Details summary="Details: large daily return flags">
          <DataTable
            rows={large_returns}
            columns={LARGE_RETURNS_COLUMNS}
            downloadFilename="large_return_flags.csv"
            downloadLabel="Download large return flags (CSV)"
            emptyMessage="No large daily returns flagged."
          />
        </Details>
      </SubSection>

      <SubSection title="Monthly benchmark (separate from the daily panel)">
        <Callout variant="warning" title="Keep the daily and monthly evidence separate">
          {notices.cluster} {notices.mode_priority}
        </Callout>
        {monthly.available ? (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <MetricCard label="Mode" value={monthly.mode_label ?? "n/a"} />
              <MetricCard label="Start month" value={monthly.start_month ?? "n/a"} />
              <MetricCard label="End month" value={monthly.end_month ?? "n/a"} />
              <MetricCard label="Sources" value={num(monthly.source_count ?? 0, "n/a")} />
            </div>
            <Callout variant={monthly.mode === "sample" ? "warning" : "info"} title={monthly.mode === "sample" ? "Sample mode" : "Real mode"}>
              {monthly.mode === "sample" ? notices.sample : notices.real}
            </Callout>
            <ChartCard title="Monthly GPR shock measure">
              <MonthlyGprChart rows={monthly.month_level ?? []} />
            </ChartCard>
            <Details summary="Details: provenance, spread, regressions, and forecasts">
              <h4 className="text-sm font-semibold text-ink">Source and provenance</h4>
              <DataTable rows={monthly.provenance ?? []} columns={MONTHLY_PROVENANCE_COLUMNS} compact />
              {monthly.source_names && monthly.source_names.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {monthly.source_names.map((name) => (
                    <span key={name} className="rounded-full bg-surface-alt px-3 py-1 text-xs text-ink-soft">{name}</span>
                  ))}
                </div>
              ) : null}
              <ChartCard title="Emerging minus developed aggregate return spread">
                <MonthlySpreadChart rows={monthly.month_level ?? []} />
              </ChartCard>
              <h4 className="text-sm font-semibold text-ink">Benchmark regression table</h4>
              {monthly.regressions && monthly.regressions.length > 0 ? (
                <DataTable rows={monthly.regressions} columns={MONTHLY_REGRESSION_COLUMNS} downloadFilename="monthly_benchmark_regressions.csv" compact />
              ) : (
                <p className="text-sm text-ink-muted">Monthly benchmark regression output is not available yet.</p>
              )}
              <h4 className="text-sm font-semibold text-ink">Forecast comparison</h4>
              {monthly.forecasts && monthly.forecasts.length > 0 ? (
                <>
                  <ChartCard title="Monthly forecast out-of-sample R-squared vs historical mean">
                    <MonthlyForecastChart rows={monthly.forecasts} />
                  </ChartCard>
                  <DataTable rows={monthly.forecasts} columns={MONTHLY_FORECAST_COLUMNS} downloadFilename="monthly_benchmark_forecasts.csv" compact />
                </>
              ) : (
                <p className="text-sm text-ink-muted">Monthly benchmark forecast output is not available yet.</p>
              )}
            </Details>
          </>
        ) : (
          <Callout variant="info" title="Monthly benchmark outputs are not available yet">
            <p>Build them with:</p>
            <pre className="mt-2 overflow-x-auto rounded bg-surface-alt p-2 text-xs">{notices.empty_state_commands.join("\n")}</pre>
            <p className="mt-2 text-xs text-ink-muted">{notices.empty_state_note}</p>
          </Callout>
        )}
      </SubSection>

      <SubSection title="Glossary">
        <Glossary terms={copy.glossary} />
      </SubSection>
    </Section>
  );
}

function SubSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-ink">{title}</h3>
      {children}
    </div>
  );
}
