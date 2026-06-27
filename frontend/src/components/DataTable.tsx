"use client";

import type { ColumnSpec } from "@/lib/labels";
import { downloadCsv } from "@/lib/csv";
import type { Row } from "@/lib/types";

interface DataTableProps {
  rows: Row[];
  columns: ColumnSpec[];
  downloadFilename?: string;
  downloadLabel?: string;
  emptyMessage?: string;
  compact?: boolean;
}

export function DataTable({
  rows,
  columns,
  downloadFilename,
  downloadLabel,
  emptyMessage = "No rows to show.",
  compact = false,
}: DataTableProps) {
  if (rows.length === 0) {
    return <p className="text-sm text-ink-muted">{emptyMessage}</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-surface-border bg-surface shadow-sm">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="bg-surface-alt text-left text-ink-soft">
            {columns.map((column) => (
              <th
                key={column.key}
                title={column.tooltip}
                className={`whitespace-nowrap px-3 py-2 font-semibold ${compact ? "text-xs" : "text-sm"} ${
                  column.align === "right" ? "text-right" : "text-left"
                }`}
              >
                {column.label}
                {column.tooltip ? <span className="ml-1 text-ink-muted" aria-label={column.tooltip}>i</span> : null}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr
              key={index}
              className="border-t border-surface-border odd:bg-surface even:bg-surface-alt/60"
            >
              {columns.map((column) => (
                <td
                  key={column.key}
                  className={`px-3 py-2 align-top ${
                    column.align === "right" ? "text-right tabular-nums" : "text-left"
                  }`}
                >
                  {renderCell(row, column)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {downloadFilename ? (
        <div className="border-t border-surface-border px-3 py-2">
          <button
            type="button"
            onClick={() => downloadCsv(rows, columns, downloadFilename)}
            className="text-sm font-medium text-accent hover:underline"
          >
            {downloadLabel ?? `Download ${downloadFilename}`}
          </button>
        </div>
      ) : null}
    </div>
  );
}

function renderCell(row: Row, column: ColumnSpec): string {
  const raw = row[column.key];
  if (column.format) return column.format(raw);
  if (raw === null || raw === undefined) return "";
  return String(raw);
}
