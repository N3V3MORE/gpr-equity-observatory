import { Callout } from "@/components/Callout";
import { ChartCard } from "@/components/ChartCard";
import { DataTable } from "@/components/DataTable";
import { Details } from "@/components/Details";
import { Glossary } from "@/components/Glossary";
import { MetricCard } from "@/components/MetricCard";
import { OptionalDataset } from "@/components/OptionalDataset";
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
  OUTPUT_FILE_READER_COLUMNS,
} from "@/lib/labels";
import { num } from "@/lib/format";
import { publicPath } from "@/lib/paths";
import type { FrontendBundle } from "@/lib/types";

export function DataAndMethods({ bundle, local = false }: { bundle: FrontendBundle; local?: boolean }) {
  const { copy, country_coverage, large_returns, monthly } = bundle;
  const notices = copy.monthly_notices;
  const methods = copy.method_map.filter((row) => local || ["Event study", "Panel regression"].includes(row.Tool));
  const glossary = Object.fromEntries(Object.entries(copy.glossary).filter(([term]) =>
    local || ["GPR", "ETF", "shock", "control", "p-value"].includes(term)));
  const downloads = bundle.manifest.publication_status === "approved" ? bundle.manifest.approved_downloads ?? [] : [];

  return (
    <Section
      id="data-and-methods"
      eyebrow="Data & methods"
      title="Methods, sources, and limitations"
    >
      <SubSection title="How the evidence is estimated">
        <div className="grid gap-4 md:grid-cols-2">
          {methods.map((row) => (
            <div key={row.Tool} className="rounded-lg border border-surface-border bg-surface p-4">
              <h4 className="text-sm font-semibold text-ink">{row.Tool}</h4>
              <p className="mt-1 text-sm text-ink-soft">{row.Question}</p>
              <p className="mt-2 text-xs text-ink-muted">{row["What to look for"]}</p>
            </div>
          ))}
        </div>
      </SubSection>

      <SubSection title="Data sources">
        <ul className="list-disc space-y-2 pl-4 text-sm text-ink-soft">
          <li>
            Geopolitical risk: the <a className="font-medium text-accent hover:underline" href="https://www.matteoiacoviello.com/gpr.htm">Caldara–Iacoviello GPR index</a>.
          </li>
          <li>
            Country ETFs: adjusted prices from Yahoo Finance through yfinance, converted to USD log returns.
            ETF inception and missing observations make country coverage uneven.
          </li>
          <li>
            Market controls: global equities (ACWI), volatility (VIX), oil (WTI), the US dollar (UUP), and a US 10-year yield proxy.
            See the <a className="font-medium text-accent hover:underline" href="https://github.com/N3V3MORE/gpr-equity-observatory/blob/main/docs/DATA_SOURCES.md">source and transformation notes</a>.
          </li>
        </ul>
      </SubSection>

      <SubSection title="Data quality and coverage">
        <p className="text-sm text-ink-soft">
          The dates above describe the full panel. The coverage table gives each ETF&apos;s own first and last
          observation and sample size.
        </p>
        {local ? <>
          {bundle.dataset_status.large_returns !== "excluded" ? (
            <MetricCard
              label="Large-return flags"
              value={bundle.dataset_status.large_returns === "available" ? num(large_returns.length) : "unavailable"}
              hint="Unusually large daily returns worth manual review"
            />
          ) : null}
        <Details summary="Details: generated files used by the app">
          <p className="text-xs text-ink-muted">
            These are processed outputs, not raw source files. The public app reads the exported JSON copy of these
            results.
          </p>
          <DataTable
            rows={bundle.reader_summaries.output_files}
            columns={OUTPUT_FILE_READER_COLUMNS}
            downloadFilename="frontend_output_files.csv"
            downloadLabel="Download output file map (CSV)"
          />
        </Details>
        </> : null}
        <Details summary="Details: country coverage">
          <DataTable
            rows={country_coverage}
            columns={COUNTRY_COVERAGE_COLUMNS}
            downloadFilename="country_coverage.csv"
            downloadLabel="Download country coverage (CSV)"
          />
        </Details>
        {local ? <OptionalDataset status={bundle.dataset_status.large_returns} label="Large-return flags">
          <Details summary="Details: large daily return flags">
          <DataTable
            rows={large_returns}
            columns={LARGE_RETURNS_COLUMNS}
            downloadFilename="large_return_flags.csv"
            downloadLabel="Download large return flags (CSV)"
            emptyMessage="No large daily returns flagged."
          />
          </Details>
        </OptionalDataset> : null}
      </SubSection>

      <SubSection title="Limitations">
        <Callout variant="warning">
          <p>
            These are observational associations for USD-traded country ETF proxies, including currency exposure;
            they do not establish causal effects on local equity markets. Weak evidence is not proof of no effect.
          </p>
          <p className="mt-2">{bundle.overview.definitions.inference}</p>
          <p className="mt-2">{copy.use_note} This is not investment advice.</p>
        </Callout>
      </SubSection>

      <SubSection title="Research downloads">
        <p className="text-sm text-ink-soft">
          Result tables and their definitions can be downloaded beside the evidence above. Coverage is available
          in the table here. These summaries are distinct from the underlying source data.
        </p>
        {downloads.length ? (
          <ul className="space-y-2 text-sm">
            {downloads.map((download) => (
              <li key={download.path}>
                <a className="font-medium text-accent hover:underline" href={publicPath(download.path)} download>
                  {download.label}
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-ink-muted">Approved data download not available for this snapshot.</p>
        )}
      </SubSection>

      {local ? <OptionalDataset status={bundle.dataset_status.monthly} label="Monthly benchmark">
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
              <MetricCard label="Sources" value={num(monthly.source_count, "n/a")} />
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
          <Callout variant="info" title="Monthly benchmark is unavailable">
            This optional section is not available in this snapshot. The daily ETF evidence remains available above.
          </Callout>
        )}
        </SubSection>
      </OptionalDataset> : null}

      <Details summary="Glossary">
        <Glossary terms={glossary} />
      </Details>
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
