import type { ColumnSpec } from "./labels";
import type { Row } from "./types";

function cellValue(row: Row, column: ColumnSpec): string {
  const raw = row[column.key];
  if (column.format) {
    return column.format(raw);
  }
  if (raw === null || raw === undefined) return "";
  return String(raw);
}

export function rowsToCsv(rows: Row[], columns: ColumnSpec[]): string {
  const header = columns.map((c) => escapeCsv(c.label)).join(",");
  const body = rows.map((row) =>
    columns
      .map((column) => escapeCsv(cellValue(row, column)))
      .join(","),
  );
  return [header, ...body].join("\n");
}

function escapeCsv(value: string): string {
  if (value === "") return "";
  if (/[",\n]/.test(value)) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

export function downloadCsv(rows: Row[], columns: ColumnSpec[], filename: string): void {
  const csv = rowsToCsv(rows, columns);
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
