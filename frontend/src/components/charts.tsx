"use client";

import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { bps, num, percent, toNumber } from "@/lib/format";
import type { Row } from "@/lib/types";

const PALETTE = ["#4f46e5", "#0ea5e9", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#ec4899"];

const CHART_HEIGHT = 320;
const AXIS = { stroke: "#94a3b8", fontSize: 12 };
const GRID = "#e2e8f0";

function groupRowsBy(rows: Row[], key: string): Map<string, Row[]> {
  const map = new Map<string, Row[]>();
  for (const row of rows) {
    const group = String(row[key] ?? "");
    if (!map.has(group)) map.set(group, []);
    map.get(group)!.push(row);
  }
  return map;
}

function renderTooltipPercent(value: unknown) {
  return percent(value, 1);
}

// Explicit sorter and accessibilityLayer props preserve Recharts 2 chart behavior.
export function GprTimelineChart({ series, topShocks }: { series: Row[]; topShocks: Row[] }) {
  const shockDates = new Set(topShocks.map((row) => String(row.date)));
  const data = series.map((row) => ({
    date: String(row.date ?? ""),
    gpr: toNumber(row.gpr),
    shock: shockDates.has(String(row.date)) ? toNumber(row.gpr) : null,
  }));
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <ComposedChart accessibilityLayer={false} data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
        <XAxis dataKey="date" tick={AXIS} minTickGap={48} />
        <YAxis tick={AXIS} />
        {/* Recharts 3 adds Scatter's date field; retain the original value rows. */}
        <Tooltip itemSorter={() => 0}
          contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${GRID}` }}
          formatter={(value, name) => name === "date" ? null : value}
        />
        <Line type="monotone" dataKey="gpr" stroke="#4f46e5" strokeWidth={2} dot={false} connectNulls={false} name="GPR index" />
        <Scatter dataKey="shock" fill="#ef4444" name="Top shock days" />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

export function CumulativeReturnsChart({ rows }: { rows: Row[] }) {
  const groups = groupRowsBy(rows, "market_group");
  const dates = [...new Set(rows.map((row) => String(row.date ?? "")))].sort();
  const data = dates.map((date) => {
    const point: Record<string, number | string | null> = { date };
    for (const [group, groupRows] of groups) {
      const row = groupRows.find((r) => String(r.date) === date);
      point[group] = toNumber(row?.cumulative_average_return);
    }
    return point;
  });
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <LineChart accessibilityLayer={false} data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
        <XAxis dataKey="date" tick={AXIS} minTickGap={48} />
        <YAxis tick={AXIS} tickFormatter={(v) => percent(v, 0)} />
        <Tooltip itemSorter={() => 0}
          contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${GRID}` }}
          formatter={(value) => percent(value, 2)}
        />
        <Legend itemSorter={null} wrapperStyle={{ fontSize: 12 }} />
        {[...groups.keys()].map((group, index) => (
          <Line
            key={group}
            type="monotone"
            dataKey={group}
            connectNulls={false}
            stroke={PALETTE[index % PALETTE.length]}
            strokeWidth={2}
            dot={false}
            name={group === "emerging" ? "Emerging markets" : "Developed markets"}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

export function EventStudyChart({ rows }: { rows: Row[] }) {
  const groups = groupRowsBy(rows, "market_group");
  const days = [...new Set(rows.map((row) => toNumber(row.relative_day)).filter((day) => day !== null))].sort((a, b) => a - b);
  const data = days.map((day) => {
    const point: Record<string, number | string | null> = { relative_day: day };
    for (const [group, groupRows] of groups) {
      const row = groupRows.find((r) => toNumber(r.relative_day) === day);
      point[group] = toNumber(row?.cumulative_average_abnormal_return);
    }
    return point;
  });
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <LineChart accessibilityLayer={false} data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
        <XAxis
          dataKey="relative_day"
          tick={AXIS}
          tickFormatter={(v) => `${num(v)}`}
          label={{ value: "Days from shock (0 = shock day)", position: "insideBottom", offset: -2, fontSize: 11 }}
        />
        <YAxis tick={AXIS} tickFormatter={(v) => bps(v, 0)} />
        <Tooltip itemSorter={() => 0}
          contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${GRID}` }}
          formatter={(value) => bps(value, 1)}
        />
        <ReferenceLine x={0} stroke="#64748b" strokeDasharray="4 4" />
        <ReferenceLine y={0} stroke="#94a3b8" />
        <Legend itemSorter={null} wrapperStyle={{ fontSize: 12 }} />
        {[...groups.keys()].map((group, index) => (
          <Line
            key={group}
            type="monotone"
            dataKey={group}
            connectNulls={false}
            stroke={PALETTE[index % PALETTE.length]}
            strokeWidth={2}
            dot={false}
            name={group === "emerging" ? "Emerging markets" : "Developed markets"}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

export function EventRobustnessChart({ rows }: { rows: Row[] }) {
  const data = rows.map((row) => ({
    label: `${num(row.window)}d @ ${percent(row.shock_quantile, 0)}`,
    group: String(row.market_group ?? ""),
    value: toNumber(row.cumulative_average_abnormal_return),
  }));
  const groups = [...new Set(data.map((d) => d.group))];
  const labels = [...new Set(data.map((d) => d.label))];
  const merged = labels.map((label) => {
    const point: Record<string, number | string | null> = { label };
    for (const group of groups) {
      const found = data.find((d) => d.label === label && d.group === group);
      point[group] = found ? found.value : null;
    }
    return point;
  });
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <BarChart accessibilityLayer={false} data={merged} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
        <XAxis dataKey="label" tick={AXIS} />
        <YAxis tick={AXIS} tickFormatter={(v) => bps(v, 0)} />
        <Tooltip itemSorter={() => 0}
          contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${GRID}` }}
          formatter={(value) => bps(value, 1)}
        />
        <ReferenceLine zIndex={299} y={0} stroke="#94a3b8" />
        <Legend itemSorter={null} wrapperStyle={{ fontSize: 12 }} />
        {groups.map((group, index) => (
          <Bar
            key={group}
            dataKey={group}
            fill={PALETTE[index % PALETTE.length]}
            name={group === "emerging" ? "Emerging markets" : "Developed markets"}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}

export function QuantileChart({ rows }: { rows: Row[] }) {
  const terms = [...new Set(rows.map((row) => String(row.term ?? "")))];
  const quantiles = [...new Set(rows.map((row) => toNumber(row.quantile)).filter((quantile) => quantile !== null))].sort((a, b) => a - b);
  const data = quantiles.map((quantile) => {
    const point: Record<string, number | string | null> = { quantile };
    for (const term of terms) {
      const row = rows.find((r) => toNumber(r.quantile) === quantile && String(r.term) === term);
      point[term] = toNumber(row?.estimate);
    }
    return point;
  });
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <LineChart accessibilityLayer={false} data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
        <XAxis
          dataKey="quantile"
          tick={AXIS}
          tickFormatter={(v) => percent(v, 0)}
          label={{ value: "Return percentile (lower = worse days)", position: "insideBottom", offset: -2, fontSize: 11 }}
        />
        <YAxis tick={AXIS} tickFormatter={(v) => bps(v, 1)} />
        <Tooltip itemSorter={() => 0}
          contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${GRID}` }}
          formatter={(value) => bps(value, 1)}
        />
        <ReferenceLine y={0} stroke="#94a3b8" />
        <Legend itemSorter={null} wrapperStyle={{ fontSize: 12 }} />
        {terms.map((term, index) => (
          <Line
            key={term}
            type="monotone"
            dataKey={term}
            connectNulls={false}
            stroke={PALETTE[index % PALETTE.length]}
            strokeWidth={2}
            dot
            name={term === "gpr_change_z" ? "GPR jump (overall)" : "GPR jump (emerging-market extra)"}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

export function LocalProjectionChart({ rows }: { rows: Row[] }) {
  const groups = groupRowsBy(rows, "market_group");
  const horizons = [...new Set(rows.map((row) => toNumber(row.horizon)).filter((horizon) => horizon !== null))].sort((a, b) => a - b);
  const data = horizons.map((horizon) => {
    const point: Record<string, number | string | null> = { horizon };
    for (const [group, groupRows] of groups) {
      const row = groupRows.find((r) => toNumber(r.horizon) === horizon);
      point[`${group}_est`] = toNumber(row?.estimate);
      point[`${group}_low`] = toNumber(row?.ci_low);
      point[`${group}_high`] = toNumber(row?.ci_high);
    }
    return point;
  });
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <LineChart accessibilityLayer={false} data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
        <XAxis
          dataKey="horizon"
          tick={AXIS}
          label={{ value: "Days after shock", position: "insideBottom", offset: -2, fontSize: 11 }}
        />
        <YAxis tick={AXIS} tickFormatter={(v) => bps(v, 0)} />
        <Tooltip itemSorter={() => 0}
          contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${GRID}` }}
          formatter={(value) => bps(value, 1)}
        />
        <ReferenceLine y={0} stroke="#94a3b8" />
        <Legend itemSorter={null} wrapperStyle={{ fontSize: 12 }} />
        {[...groups.keys()].map((group, index) => (
          <Line
            key={`${group}-est`}
            type="monotone"
            dataKey={`${group}_est`}
            connectNulls={false}
            stroke={PALETTE[index % PALETTE.length]}
            strokeWidth={2}
            dot={false}
            name={group === "emerging" ? "Emerging markets" : "Developed markets"}
          />
        ))}
        {[...groups.keys()].map((group, index) => (
          <Line
            key={`${group}-ci`}
            type="monotone"
            dataKey={`${group}_low`}
            connectNulls={false}
            stroke={PALETTE[index % PALETTE.length]}
            strokeWidth={1}
            strokeDasharray="4 4"
            dot={false}
            legendType="none"
            name={`${group} 95% low`}
          />
        ))}
        {[...groups.keys()].map((group, index) => (
          <Line
            key={`${group}-cih`}
            type="monotone"
            dataKey={`${group}_high`}
            connectNulls={false}
            stroke={PALETTE[index % PALETTE.length]}
            strokeWidth={1}
            strokeDasharray="4 4"
            dot={false}
            legendType="none"
            name={`${group} 95% high`}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

export function RollingBetaChart({ rows }: { rows: Row[] }) {
  const { countries, data } = useMemo(() => {
    const countrySet = new Set<string>();
    const points = new Map<string, Record<string, number | string | null>>();

    // Build the index once so rendering does not repeatedly scan the full
    // rolling-beta export for every date/country pair.
    for (const row of rows) {
      const date = String(row.date ?? "");
      const country = String(row.country ?? "");
      if (!date || !country) continue;

      countrySet.add(country);
      const point = points.get(date) ?? { date };
      point[country] = toNumber(row.rolling_gpr_beta);
      points.set(date, point);
    }

    for (const point of points.values()) {
      for (const country of countrySet) point[country] ??= null;
    }

    return {
      countries: [...countrySet].sort(),
      data: [...points.values()].sort((a, b) => String(a.date).localeCompare(String(b.date))),
    };
  }, [rows]);

  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <LineChart accessibilityLayer={false} data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
        <XAxis dataKey="date" tick={AXIS} minTickGap={48} />
        <YAxis tick={AXIS} />
        <Tooltip itemSorter={() => 0} contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${GRID}` }} />
        <ReferenceLine y={0} stroke="#94a3b8" />
        <Legend itemSorter={null} wrapperStyle={{ fontSize: 11 }} />
        {countries.map((country, index) => (
          <Line
            key={country}
            type="monotone"
            dataKey={country}
            connectNulls={false}
            stroke={PALETTE[index % PALETTE.length]}
            strokeWidth={1.5}
            dot={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

export function CalibrationChart({ rows }: { rows: Row[] }) {
  const models = [...new Set(rows.map((row) => String(row.model_name ?? "")))];
  const deciles = [...new Set(rows.map((row) => toNumber(row.probability_decile)).filter((decile) => decile !== null))].sort((a, b) => a - b);
  const data = deciles.map((decile) => {
    const point: Record<string, number | string | null> = { decile };
    for (const model of models) {
      const row = rows.find((r) => toNumber(r.probability_decile) === decile && String(r.model_name) === model);
      point[model] = toNumber(row?.realized_event_rate);
    }
    return point;
  });
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <LineChart accessibilityLayer={false} data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
        <XAxis dataKey="decile" tick={AXIS} label={{ value: "Predicted-risk decile (low to high)", position: "insideBottom", offset: -2, fontSize: 11 }} />
        <YAxis tick={AXIS} tickFormatter={(v) => percent(v, 0)} />
        <Tooltip itemSorter={() => 0}
          contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${GRID}` }}
          formatter={(value) => renderTooltipPercent(value)}
        />
        <Legend itemSorter={null} wrapperStyle={{ fontSize: 12 }} />
        {models.map((model, index) => (
          <Line
            key={model}
            type="monotone"
            dataKey={model}
            connectNulls={false}
            stroke={PALETTE[index % PALETTE.length]}
            strokeWidth={2}
            dot
            name={model === "full_features" ? "All features" : model}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

export function LiftChart({ rows }: { rows: Row[] }) {
  const buckets = [...new Set(rows.map((row) => String(row.bucket ?? "")))];
  const models = [...new Set(rows.map((row) => String(row.model_name ?? "")))];
  const data = buckets.map((bucket) => {
    const point: Record<string, number | string | null> = { bucket };
    for (const model of models) {
      const row = rows.find((r) => String(r.bucket) === bucket && String(r.model_name) === model);
      point[model] = toNumber(row?.lift);
    }
    return point;
  });
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <BarChart accessibilityLayer={false} data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
        <XAxis dataKey="bucket" tick={AXIS} />
        <YAxis tick={AXIS} />
        <Tooltip itemSorter={() => 0} contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${GRID}` }} />
        <ReferenceLine zIndex={299} y={1} stroke="#94a3b8" strokeDasharray="4 4" />
        <Legend itemSorter={null} wrapperStyle={{ fontSize: 12 }} />
        {models.map((model, index) => (
          <Bar key={model} dataKey={model} fill={PALETTE[index % PALETTE.length]} name={model === "full_features" ? "All features" : model} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}

export function FeatureImportanceChart({ rows }: { rows: Row[] }) {
  const sorted = [...rows].sort((a, b) =>
    (toNumber(a.abs_coefficient) ?? Infinity) - (toNumber(b.abs_coefficient) ?? Infinity));
  const data = sorted.map((row) => ({
    feature: String(row.feature ?? ""),
    importance: toNumber(row.abs_coefficient),
  }));
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <BarChart accessibilityLayer={false} data={data} layout="vertical" margin={{ top: 8, right: 16, bottom: 8, left: 24 }}>
        <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
        <XAxis type="number" tick={AXIS} />
        <YAxis type="category" dataKey="feature" tick={AXIS} width={120} />
        <Tooltip itemSorter={() => 0} contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${GRID}` }} />
        <Bar dataKey="importance" fill="#4f46e5" />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function MonthlyGprChart({ rows }: { rows: Row[] }) {
  const data = rows.map((row) => ({ date: String(row.date_month ?? ""), value: toNumber(row.gpr_change_z) }));
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <LineChart accessibilityLayer={false} data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
        <XAxis dataKey="date" tick={AXIS} minTickGap={48} />
        <YAxis tick={AXIS} />
        <Tooltip itemSorter={() => 0} contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${GRID}` }} />
        <ReferenceLine y={0} stroke="#94a3b8" />
        <Line type="monotone" dataKey="value" stroke="#4f46e5" strokeWidth={2} dot={false} connectNulls={false} name="GPR shock (z-score)" />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function MonthlySpreadChart({ rows }: { rows: Row[] }) {
  const data = rows.map((row) => ({ date: String(row.date_month ?? ""), value: toNumber(row.spread_em_dev) }));
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <LineChart accessibilityLayer={false} data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
        <XAxis dataKey="date" tick={AXIS} minTickGap={48} />
        <YAxis tick={AXIS} tickFormatter={(v) => percent(v, 0)} />
        <Tooltip itemSorter={() => 0} contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${GRID}` }} formatter={(value) => percent(value, 2)} />
        <ReferenceLine y={0} stroke="#94a3b8" />
        <Line type="monotone" dataKey="value" stroke="#0ea5e9" strokeWidth={2} dot={false} connectNulls={false} name="Emerging minus developed" />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function MonthlyForecastChart({ rows }: { rows: Row[] }) {
  const data = rows.map((row) => ({ model: String(row.model ?? ""), oos_r2: toNumber(row.oos_r2) }));
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <BarChart accessibilityLayer={false} data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
        <XAxis dataKey="model" tick={AXIS} />
        <YAxis tick={AXIS} />
        <Tooltip itemSorter={() => 0} contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${GRID}` }} />
        <ReferenceLine zIndex={299} y={0} stroke="#94a3b8" />
        <Bar dataKey="oos_r2" fill="#4f46e5" name="Out-of-sample R-squared" />
      </BarChart>
    </ResponsiveContainer>
  );
}
