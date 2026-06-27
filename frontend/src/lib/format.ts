// Number/value formatters for the frontend. Pure functions, no data deps.

export function num(value: unknown, fallback = "n/a"): string {
  const n = toNumber(value);
  if (n === null) return fallback;
  return n.toLocaleString(undefined, { maximumFractionDigits: 3 });
}

export function fixed(value: unknown, digits = 3, fallback = "n/a"): string {
  const n = toNumber(value);
  if (n === null) return fallback;
  return n.toFixed(digits);
}

export function percent(value: unknown, digits = 1, fallback = "n/a"): string {
  const n = toNumber(value);
  if (n === null) return fallback;
  return `${(n * 100).toFixed(digits)}%`;
}

export function bps(value: unknown, digits = 1, fallback = "n/a"): string {
  const n = toNumber(value);
  if (n === null) return fallback;
  return `${(n * 10_000).toFixed(digits)} bps`;
}

export function multiple(value: unknown, digits = 2, fallback = "n/a"): string {
  const n = toNumber(value);
  if (n === null) return fallback;
  return `${n.toFixed(digits)}x`;
}

export function signedFixed(value: unknown, digits = 3, fallback = "n/a"): string {
  const n = toNumber(value);
  if (n === null) return fallback;
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(digits)}`;
}

export function toNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === "") return null;
  const n = typeof value === "number" ? value : Number(value);
  return Number.isFinite(n) ? n : null;
}

export function str(value: unknown, fallback = ""): string {
  if (value === null || value === undefined) return fallback;
  return String(value);
}
