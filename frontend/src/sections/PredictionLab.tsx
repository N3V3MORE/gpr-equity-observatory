import { Callout } from "@/components/Callout";
import { ChartCard } from "@/components/ChartCard";
import { DataTable } from "@/components/DataTable";
import { Details } from "@/components/Details";
import { MetricCard } from "@/components/MetricCard";
import { Section } from "@/components/Section";
import {
  CalibrationChart,
  FeatureImportanceChart,
  LiftChart,
} from "@/components/charts";
import {
  COUNTRY_RISK_COLUMNS,
  DRAWDOWN_METRICS_COLUMNS,
  FEATURE_IMPORTANCE_COLUMNS,
  MODEL_COMPARISON_COLUMNS,
  THRESHOLD_COLUMNS,
  modelName,
} from "@/lib/labels";
import { fixed, num, percent } from "@/lib/format";
import type { FrontendBundle } from "@/lib/types";

export function PredictionLab({ bundle }: { bundle: FrontendBundle }) {
  const {
    copy,
    prediction_summary,
    drawdown_calibration,
    drawdown_lift,
    drawdown_threshold_metrics,
    drawdown_country_risk_summary,
    drawdown_feature_importance,
    drawdown_metrics,
  } = bundle;
  const best = prediction_summary.best_metrics;
  const horizon = copy.prediction_lab.drawdown_horizon_days;
  const threshold = copy.prediction_lab.drawdown_threshold;

  return (
    <Section
      id="prediction-lab"
      eyebrow="Predicting drawdown risk"
      title="Can recent conditions rank short-term drawdown risk?"
      intro="Prediction Lab ranks drawdown risk for recent ETF conditions. It does not predict prices or recommend trades."
    >
      <Callout variant="warning" title="What this is - read carefully">
        This is an out-of-sample risk-classification experiment. It asks whether current GPR and market conditions
        help rank short-horizon drawdown risk. It is not a trading signal or a price forecast.
      </Callout>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label={best.auc?.label ?? "Best model ranking score"} value={best.auc?.value ?? "n/a"} hint="0.5 = no better than a coin flip" />
        <MetricCard label={best.ap?.label ?? "Best model hit rate"} value={best.ap?.value ?? "n/a"} hint="Higher = bad outcomes cluster near the top" />
        <MetricCard label={best.lift?.label ?? "Top-decile concentration"} value={best.lift?.value ?? "n/a"} hint="1x = no help; higher is better" />
        <MetricCard label="Average bad-outcome rate" value={percent(prediction_summary.mean_event_rate, 1)} hint="Share of rows that actually had a drawdown" />
      </div>

      <Callout variant="info" title="Bottom line">
        {copy.prediction_lab.conclusion}
      </Callout>

      <ChartCard title="Bad-outcome lift by risk bucket" caption="The dashed line at 1x means no better than average. Higher bars mean bad outcomes are more concentrated in that bucket.">
        <LiftChart rows={drawdown_lift} />
      </ChartCard>

      <div>
        <h3 className="text-sm font-semibold text-ink">Model comparison</h3>
        <p className="mt-1 text-xs text-ink-muted">
          Each row is a model allowed to use a different group of inputs. Hover a column header to see what the
          number means. Verdicts are cautious plain-English summaries, not endorsements.
        </p>
        <div className="mt-3">
          <DataTable
            rows={prediction_summary.model_comparison}
            columns={MODEL_COMPARISON_COLUMNS}
            downloadFilename="drawdown_model_comparison.csv"
            downloadLabel="Download model comparison (CSV)"
          />
        </div>
      </div>

      <Callout variant="info" title="How to read the scores">
        <dl className="grid gap-3 sm:grid-cols-2">
          {Object.entries(copy.prediction_metric_explanations).map(([metric, explanation]) => (
            <div key={metric}>
              <dt className="text-sm font-semibold text-ink">{metric}</dt>
              <dd className="text-sm text-ink-soft">{explanation}</dd>
            </div>
          ))}
        </dl>
      </Callout>

      <Details summary="Details: calibration - do predicted risk levels match reality?" defaultOpen>
        <ChartCard
          title="Realized bad-outcome rate by predicted-risk decile"
          caption="If a model is well calibrated, the line rises steadily: higher predicted risk buckets actually contain more bad outcomes."
        >
          <CalibrationChart rows={drawdown_calibration} />
        </ChartCard>
        <DataTable
          rows={drawdown_calibration}
          columns={CALIBRATION_COLUMNS_LOCAL}
          downloadFilename="drawdown_model_calibration.csv"
          compact
        />
      </Details>

      <Details summary="Details: lift - how concentrated are bad outcomes in the riskiest rows?">
        <DataTable rows={drawdown_lift} columns={LIFT_COLUMNS_LOCAL} downloadFilename="drawdown_model_lift.csv" compact />
      </Details>

      <Details summary="Details: threshold metrics, country risk, feature importance, and validation">
        <h4 className="text-sm font-semibold text-ink">Threshold metrics</h4>
        <DataTable rows={drawdown_threshold_metrics} columns={THRESHOLD_COLUMNS} downloadFilename="drawdown_model_threshold_metrics.csv" compact />

        <h4 className="text-sm font-semibold text-ink">Country risk summary</h4>
        <DataTable rows={drawdown_country_risk_summary} columns={COUNTRY_RISK_COLUMNS} downloadFilename="drawdown_country_risk_summary.csv" compact />

        <h4 className="text-sm font-semibold text-ink">Feature importance</h4>
        <ChartCard title="Drawdown model feature importance" caption={copy.prediction_lab.feature_importance_caption}>
          <FeatureImportanceChart rows={drawdown_feature_importance} />
        </ChartCard>
        <DataTable rows={drawdown_feature_importance} columns={FEATURE_IMPORTANCE_COLUMNS} downloadFilename="drawdown_feature_importance.csv" compact />

        <h4 className="text-sm font-semibold text-ink">{copy.prediction_lab.validation_heading}</h4>
        <p className="text-xs text-ink-muted">
          This classifier predicts whether an ETF has a forward {horizon}-trading-day cumulative log-return drawdown
          of at least {percent(Math.abs(threshold), 0)}. {copy.prediction_lab.validation_caption}
        </p>
        <DataTable rows={drawdown_metrics} columns={DRAWDOWN_METRICS_COLUMNS} downloadFilename="drawdown_model_metrics.csv" compact />
      </Details>
    </Section>
  );
}

const CALIBRATION_COLUMNS_LOCAL = [
  { key: "model_name", label: "Model", format: modelName },
  { key: "probability_decile", label: "Decile", align: "right" as const, format: (v: unknown) => num(v) },
  { key: "mean_predicted_probability", label: "Avg. predicted risk", align: "right" as const, format: (v: unknown) => percent(v) },
  { key: "realized_event_rate", label: "Realized rate", align: "right" as const, format: (v: unknown) => percent(v) },
  { key: "observation_count", label: "Observations", align: "right" as const, format: (v: unknown) => num(v) },
];

const LIFT_COLUMNS_LOCAL = [
  { key: "model_name", label: "Model", format: modelName },
  { key: "bucket", label: "Bucket" },
  { key: "lift", label: "Lift", align: "right" as const, format: (v: unknown) => fixed(v, 2) },
  { key: "event_rate", label: "Event rate", align: "right" as const, format: (v: unknown) => percent(v) },
  { key: "base_event_rate", label: "Base rate", align: "right" as const, format: (v: unknown) => percent(v) },
  { key: "observation_count", label: "Observations", align: "right" as const, format: (v: unknown) => num(v) },
];
